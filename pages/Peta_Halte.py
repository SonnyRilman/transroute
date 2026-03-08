import streamlit as st
import folium, json, os
from streamlit_folium import st_folium
from haversine import haversine, Unit
from utils.kml_parser import parse_kml
from utils.styles import inject_styles
from utils.auth import check_login, render_sidebar

st.set_page_config(page_title="Peta Halte | TransJogja", page_icon="📍",
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()

# ── AUTH & SIDEBAR ─────────────────────────────────────────────────────────────
check_login()
render_sidebar()


# Load data
@st.cache_data
def load_nodes():
    from utils.graph_logic import build_graph
    kml_path = os.path.join("data", "sample_route.kml")
    if not os.path.exists(kml_path): return {}, []
    nodes, edges = parse_kml(kml_path)
    return nodes, edges

nodes, edges = load_nodes()
halte_info = {}
hi_path = os.path.join("data", "halte_info.json")
if os.path.exists(hi_path):
    halte_info = json.load(open(hi_path, encoding="utf-8"))

# Page header
st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;"><i class="fa-solid fa-map-location-dot" style="color:#a78bfa;margin-right:8px;"></i>Peta Halte TransJogja</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#64748b;margin-bottom:18px;">Telusuri posisi dan informasi fasilitas setiap halte. Klik marker untuk melihat detail.</div>', unsafe_allow_html=True)

# Sidebar: halte selector
halte_names = list(nodes.keys())
st.sidebar.markdown('<p style="color:#a78bfa!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;"><i class="fa-solid fa-magnifying-glass"></i> &nbsp;Cari Halte</p>', unsafe_allow_html=True)
selected_halte = st.sidebar.selectbox("Pilih halte:", ["— Semua Halte —"] + halte_names, label_visibility="collapsed")
st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:12px 0;">', unsafe_allow_html=True)

# Build map
if nodes:
    c_lat = sum(v[0] for v in nodes.values()) / len(nodes)
    c_lon = sum(v[1] for v in nodes.values()) / len(nodes)
    focus_node = selected_halte if selected_halte != "— Semua Halte —" else None
    map_center = list(nodes[focus_node]) if focus_node else [c_lat, c_lon]
    zoom = 17 if focus_node else 15

    m = folium.Map(location=map_center, zoom_start=zoom,
                   tiles="CartoDB dark_matter", attr="CartoDB")

    # Draw all edge lines
    for edge in edges:
        folium.PolyLine(edge["coordinates"], color="#1e3a5f", weight=2, opacity=.6).add_to(m)

    # Add markers
    for nname, coords in nodes.items():
        hi = halte_info.get(nname, {})
        fac_list = "".join(f"<li>{f}</li>" for f in hi.get("fasilitas", []))
        kor_badges = "".join(
            f'<span style="background:#3b82f6;color:#fff;font-size:10px;padding:1px 7px;border-radius:50px;margin-right:3px;">{k}</span>'
            for k in hi.get("koridor", []))
        popup_html = f"""
        <div style="font-family:Outfit,sans-serif;min-width:200px;max-width:240px;">
            <div style="font-size:13px;font-weight:700;margin-bottom:4px;">{nname}</div>
            <div style="font-size:11px;color:#666;margin-bottom:8px;">{hi.get('alamat','Koordinat: '+str(coords))}</div>
            <div style="font-size:11px;margin-bottom:4px;">🚌 Koridor: {kor_badges or '—'}</div>
            <div style="font-size:11px;margin-bottom:4px;">⏰ {hi.get('jam_operasi','—')}</div>
            <div style="font-size:11px;">🛞 Fasilitas:<ul style="margin:3px 0 0 14px;padding:0;">{fac_list or '<li>—</li>'}</ul></div>
        </div>"""
        is_focus = (nname == focus_node)
        is_mal   = "Malioboro" in nname
        clr  = "red" if is_mal else ("green" if is_focus else "blue")
        icn  = "flag-checkered" if is_mal else ("star" if is_focus else "bus")
        folium.Marker(coords, popup=folium.Popup(popup_html, max_width=260),
                      tooltip=nname, icon=folium.Icon(color=clr, icon=icn, prefix="fa")).add_to(m)
        if is_focus:
            folium.Circle(coords, radius=80, color="#a78bfa", fill=True,
                          fill_color="#a78bfa", fill_opacity=.15).add_to(m)

    map_col, detail_col = st.columns([3, 1])
    with map_col:
        st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(167,139,250,.2);box-shadow:0 10px 40px rgba(0,0,0,.4);">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=540, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    with detail_col:
        if focus_node and focus_node in halte_info:
            hi = halte_info[focus_node]
            fac_items = "".join(
                f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">'
                f'<i class="fa-solid fa-check-circle" style="color:#10b981;font-size:.75rem;"></i>'
                f'<span style="font-size:.8rem;color:#cbd5e1;">{f}</span></div>'
                for f in hi.get("fasilitas", []))
            kor_b = "".join(
                f'<span style="background:rgba(59,130,246,.2);border:1px solid rgba(59,130,246,.3);'
                f'color:#93c5fd;font-size:.72rem;padding:3px 10px;border-radius:50px;margin:2px;">{k}</span>'
                for k in hi.get("koridor", []))
            status_col = "#10b981" if hi.get("status","")=="Aktif" else "#f43f5e"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e293b,#0f172a);
                        border:1px solid rgba(167,139,250,.25);border-top:3px solid #a78bfa;
                        border-radius:16px;padding:20px 16px;">
                <div style="font-size:.62rem;color:#a78bfa;font-weight:700;text-transform:uppercase;
                            letter-spacing:1px;margin-bottom:8px;">
                    <i class="fa-solid fa-map-pin" style="margin-right:4px;"></i>Info Halte
                </div>
                <div style="font-size:.95rem;font-weight:700;color:#e2e8f0;margin-bottom:10px;">{focus_node}</div>
                <div style="font-size:.75rem;color:#64748b;margin-bottom:14px;line-height:1.5;">
                    <i class="fa-solid fa-location-dot" style="margin-right:5px;color:#a78bfa;"></i>{hi.get('alamat','—')}
                </div>
                <div style="margin-bottom:12px;">
                    <div style="font-size:.62rem;color:#475569;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Koridor</div>
                    <div style="display:flex;flex-wrap:wrap;gap:4px;">{kor_b or '<span style="color:#64748b;font-size:.8rem;">—</span>'}</div>
                </div>
                <div style="margin-bottom:12px;">
                    <div style="font-size:.62rem;color:#475569;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Jam Operasi</div>
                    <div style="font-size:.82rem;color:#93c5fd;"><i class="fa-solid fa-clock" style="margin-right:5px;"></i>{hi.get('jam_operasi','—')}</div>
                </div>
                <div style="margin-bottom:12px;">
                    <div style="font-size:.62rem;color:#475569;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Fasilitas</div>
                    {fac_items or '<div style="font-size:.8rem;color:#64748b;">—</div>'}
                </div>
                <div style="background:rgba(16,185,129,.08);border:1px solid rgba(16,185,129,.2);
                            border-radius:8px;padding:8px 12px;text-align:center;">
                    <span style="font-size:.7rem;font-weight:700;color:{status_col};">
                        <i class="fa-solid fa-circle" style="font-size:.5rem;margin-right:5px;"></i>
                        Status: {hi.get('status','Aktif')}
                    </span>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            # List all halte
            st.markdown('<div style="font-size:.7rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;"><i class="fa-solid fa-list" style="margin-right:5px;"></i>Semua Halte</div>', unsafe_allow_html=True)
            for nname in halte_names:
                hi = halte_info.get(nname, {})
                is_mal = "Malioboro" in nname
                col = "#f43f5e" if is_mal else "#3b82f6"
                st.markdown(f"""
                <div style="background:#1e293b;border:1px solid rgba(148,163,184,.08);
                            border-left:3px solid {col};border-radius:0 10px 10px 0;
                            padding:9px 12px;margin-bottom:7px;">
                    <div style="font-size:.8rem;font-weight:600;color:#e2e8f0;">{nname}</div>
                    <div style="font-size:.68rem;color:#475569;margin-top:2px;">
                        {', '.join(hi.get('koridor',[])) or '—'}
                    </div>
                </div>""", unsafe_allow_html=True)
else:
    st.error("Data halte tidak tersedia.")
