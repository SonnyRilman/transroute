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
def load_all_halte():
    hi_path = os.path.join("data", "halte_info.json")
    if os.path.exists(hi_path):
        return json.load(open(hi_path, encoding="utf-8"))
    return {}

@st.cache_data
def load_routes():
    kml_path = os.path.join("data", "sample_route_v3.kml")
    if not os.path.exists(kml_path):
        kml_path = os.path.join("data", "Jalur Rute.kml")
    if not os.path.exists(kml_path): return []
    _, edges = parse_kml(kml_path)
    return edges

halte_info = load_all_halte()
edges = load_routes()

# Page header
st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;"><i class="fa-solid fa-map-location-dot" style="color:#a78bfa;margin-right:8px;"></i>Peta Halte TransJogja v3</div>', unsafe_allow_html=True)
st.markdown(f'<div style="font-size:.85rem;color:#64748b;margin-bottom:18px;">Dashboard halte interaktif dengan total <b>{len(halte_info)}</b> titik. Telusuri rute dan tujuan setiap bus secara real-time.</div>', unsafe_allow_html=True)

# Sidebar: halte selector
halte_names = sorted(list(halte_info.keys()))
st.sidebar.markdown('<p style="color:#a78bfa!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;"><i class="fa-solid fa-magnifying-glass"></i> &nbsp;Cari Halte</p>', unsafe_allow_html=True)
selected_halte = st.sidebar.selectbox("Pilih halte:", ["— Semua Halte —"] + halte_names, label_visibility="collapsed")
st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:12px 0;">', unsafe_allow_html=True)

# Build map
if halte_info:
    # Calculate center based on all stops if none selected
    if selected_halte != "— Semua Halte —":
        hi_sel = halte_info[selected_halte]
        map_center = [hi_sel['lat'], hi_sel['lon']]
        zoom = 17
    else:
        lats = [h['lat'] for h in halte_info.values()]
        lons = [h['lon'] for h in halte_info.values()]
        map_center = [sum(lats)/len(lats), sum(lons)/len(lons)]
        zoom = 13

    m = folium.Map(location=map_center, zoom_start=zoom,
                   tiles="CartoDB dark_matter", attr="CartoDB")

    # Draw edge lines
    for edge in edges:
        folium.PolyLine(edge["coordinates"], color="#3b82f6", weight=1.5, opacity=.3).add_to(m)

    # Use MarkerCluster for performance
    from folium.plugins import MarkerCluster
    cluster = MarkerCluster().add_to(m)

    for nname, hi in halte_info.items():
        coords = [hi['lat'], hi['lon']]
        
        # Tujuan Labels (Neat blue labels)
        tujuan_html = "".join(
            f'<div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); '
            f'color:#60a5fa; font-size:10px; padding:3px 8px; border-radius:6px; margin-bottom:3px; display:flex; align-items:center;">'
            f'<i class="fa-solid fa-bus" style="margin-right:6px; font-size:8px;"></i>{t}</div>'
            for t in hi.get("tujuan", [])
        )
        
        popup_html = f"""
        <div style="font-family:Outfit,sans-serif;min-width:240px;max-width:300px;padding:5px;">
            <div style="font-size:14px;font-weight:800;color:#1e293b;margin-bottom:2px;">{nname}</div>
            <div style="font-size:10px;color:#94a3b8;font-weight:600;text-transform:uppercase;margin-bottom:10px;">
                <i class="fa-solid fa-location-dot" style="margin-right:4px;"></i>{hi.get('wilayah','Yogyakarta')}
            </div>
            <div style="font-size:11px;font-weight:700;color:#475569;margin-bottom:6px;">RUTE & TUJUAN:</div>
            <div style="max-height:120px; overflow-y:auto; padding-right:5px;">
                {tujuan_html or '<div style="color:#94a3b8; font-size:10px;">Data rute tidak tersedia</div>'}
            </div>
            <div style="margin-top:10px; padding-top:8px; border-top:1px solid #f1f5f9; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:10px; color:#64748b;"><i class="fa-solid fa-clock"></i> {hi.get('jam_operasi','05:30-21:00')}</span>
                <span style="font-size:9px; background:#10b981; color:white; padding:2px 6px; border-radius:4px; font-weight:700;">AKTIF</span>
            </div>
        </div>"""
        
        is_focus = (nname == selected_halte)
        clr = "green" if is_focus else "blue"
        icn = "star" if is_focus else "bus"
        
        folium.Marker(coords, popup=folium.Popup(popup_html, max_width=320),
                      tooltip=nname, icon=folium.Icon(color=clr, icon=icn, prefix="fa")).add_to(cluster)
        
        if is_focus:
            folium.Circle(coords, radius=120, color="#a78bfa", fill=True,
                          fill_color="#a78bfa", fill_opacity=.25).add_to(m)

    map_col, detail_col = st.columns([3, 1])
    with map_col:
        st.markdown('<div style="border-radius:20px;overflow:hidden;border:1px solid rgba(167,139,250,.2);box-shadow:0 20px 50px rgba(0,0,0,.5);">', unsafe_allow_html=True)
        st_folium(m, width="100%", height=580, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)

    with detail_col:
        if selected_halte != "— Semua Halte —" and selected_halte in halte_info:
            hi = halte_info[selected_halte]
            # Sidebar Arrow Icons
            tujuan_items = "".join(
                f'<div style="background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.15);'
                f'border-radius:10px;padding:12px 14px;margin-bottom:8px;font-size:.82rem;color:#93c5fd;display:flex;align-items:center;">'
                f'<i class="fa-solid fa-circle-arrow-right" style="margin-right:10px;color:#60a5fa;font-size:1rem;"></i>{t}</div>'
                for t in hi.get("tujuan", []))
            
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,#1e293b,#0f172a);
                        border:1px solid rgba(167,139,250,.25);border-top:4px solid #a78bfa;
                        border-radius:20px;padding:24px 20px;box-shadow:0 10px 30px rgba(0,0,0,.3);">
                <div style="font-size:.65rem;color:#a78bfa;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">Detail Informasi</div>
                <div style="font-size:1.2rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;line-height:1.3;">{selected_halte}</div>
                <div style="font-size:.78rem;color:#64748b;margin-bottom:24px;display:flex;align-items:center;gap:6px;">
                    <i class="fa-solid fa-map-location-dot" style="color:#a78bfa;"></i>{hi.get('wilayah','Kota Yogyakarta')}
                </div>
                
                <div style="margin-bottom:20px;">
                    <div style="font-size:.65rem;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Peta Rute & Tujuan</div>
                    {tujuan_items or '<div style="color:#475569;font-size:.8rem;font-style:italic;">Data rute tidak tersedia</div>'}
                </div>
                
                <div style="display:flex;gap:10px;margin-bottom:20px;">
                    <div style="flex:1;background:rgba(30,41,59,0.5);border-radius:12px;padding:10px;text-align:center;">
                        <div style="font-size:.55rem;color:#64748b;text-transform:uppercase;margin-bottom:4px;">Jam Operasi</div>
                        <div style="font-size:.75rem;color:#cbd5e1;font-weight:700;">05:30-21:00</div>
                    </div>
                     <div style="flex:1;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:10px;text-align:center;">
                        <div style="font-size:.55rem;color:#10b981;text-transform:uppercase;margin-bottom:4px;">Status</div>
                        <div style="font-size:.75rem;color:#34d399;font-weight:700;">TERSEDIA</div>
                    </div>
                </div>
                
                <button style="width:100%;background:linear-gradient(135deg,#3b82f6,#2563eb);color:white;border:none;border-radius:12px;padding:12px;font-weight:700;font-size:.85rem;cursor:pointer;box-shadow:0 4px 15px rgba(37,99,235,0.3);">
                    <i class="fa-solid fa-route" style="margin-right:8px;"></i>Lihat Semua Koridor
                </button>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:rgba(15,23,42,.4);border:1px solid rgba(148,163,184,.08);
                        border-radius:20px;padding:40px 24px;text-align:center;height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;">
                <div style="width:64px;height:64px;background:rgba(167,139,250,.1);border-radius:20px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;">
                    <i class="fa-solid fa-map-pin" style="font-size:1.8rem;color:#a78bfa;"></i>
                </div>
                <div style="font-size:.95rem;font-weight:700;color:#94a3b8;margin-bottom:8px;">Eksplorasi Halte</div>
                <div style="font-size:.75rem;color:#64748b;line-height:1.6;">Pilih salah satu halte di peta atau gunakan fitur pencarian di sidebar untuk melihat detail rute bus.</div>
            </div>""", unsafe_allow_html=True)
else:
    st.error("Data halte tidak tersedia.")
