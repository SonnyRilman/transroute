import streamlit as st
import folium, os, json
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from utils.kml_parser import parse_kml
from utils.graph_logic import build_graph, find_nearest_node, find_shortest_path
from utils.styles import inject_styles
from utils.auth import check_login, render_sidebar
from haversine import haversine, Unit

st.set_page_config(page_title="Cari Rute | TransJogja", page_icon="🗺️",
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()

# ── AUTH & SIDEBAR ─────────────────────────────────────────────────────────────
check_login()
render_sidebar()


@st.cache_data
def load_data():
    kml_path = os.path.join("data", "sample_route.kml")
    if not os.path.exists(kml_path):
        return None, None, None
    nodes, edges = parse_kml(kml_path)
    G = build_graph(nodes, edges)
    return nodes, edges, G

nodes, edges, G = load_data()
if not nodes:
    st.error("File `data/sample_route.kml` tidak ditemukan.")
    st.stop()

halte_info = {}
hi_path = os.path.join("data", "halte_info.json")
if os.path.exists(hi_path):
    halte_info = json.load(open(hi_path, encoding="utf-8"))

# ── GPS ────────────────────────────────────────────────────────────────────────
st.sidebar.markdown('<p style="color:#60a5fa!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;"><i class="fa-solid fa-location-crosshairs"></i> &nbsp;Deteksi Lokasi GPS</p>', unsafe_allow_html=True)
st.sidebar.caption("Klik tombol berikut untuk mendeteksi posisi Anda.")
location = streamlit_geolocation()
user_lat, user_lon = None, None

if location and location.get("latitude") and location.get("longitude"):
    user_lat, user_lon = location["latitude"], location["longitude"]
    st.sidebar.markdown(
        f'<div style="background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);'
        f'border-radius:10px;padding:10px 14px;font-size:.82rem;color:#6ee7b7;margin:6px 0;">'
        f'<i class="fa-solid fa-circle-check" style="margin-right:6px;"></i><b>Lokasi GPS Aktif</b><br>'
        f'<span style="opacity:.7;">Lat {user_lat:.5f} | Lon {user_lon:.5f}</span></div>',
        unsafe_allow_html=True)
    nearest_w = find_nearest_node((user_lat, user_lon), nodes)
    wd_km = haversine((user_lat, user_lon), nodes[nearest_w], unit=Unit.KILOMETERS)
    st.sidebar.markdown(
        f'<div style="background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);'
        f'border-radius:10px;padding:9px 13px;font-size:.8rem;color:#fcd34d;margin:4px 0;">'
        f'<i class="fa-solid fa-person-walking" style="margin-right:5px;color:#f59e0b;"></i>'
        f'<b>Jarak ke Halte Terdekat</b><br>'
        f'<span style="opacity:.8;">{wd_km*1000:.0f} m &nbsp;'
        f'<i class="fa-solid fa-clock"></i> &plusmn;{(wd_km/5)*60:.0f} mnt jalan kaki</span></div>',
        unsafe_allow_html=True)

st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:12px 0;">', unsafe_allow_html=True)

start_opts = list(nodes.keys())
mal_nodes  = [n for n in start_opts if "Malioboro" in n]
dest_node  = mal_nodes[0] if mal_nodes else start_opts[-1]
non_mal    = [n for n in start_opts if "Malioboro" not in n]

if user_lat and user_lon:
    actual_start = find_nearest_node((user_lat, user_lon), nodes)
    st.sidebar.markdown('<p style="color:#10b981!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;"><i class="fa-solid fa-wand-magic-sparkles"></i> &nbsp;Halte Terdekat (Auto)</p>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<div style="background:linear-gradient(135deg,rgba(16,185,129,.12),rgba(5,150,105,.08));'
        f'border:1px solid rgba(16,185,129,.35);border-radius:12px;padding:12px 14px;margin-bottom:4px;">'
        f'<div style="font-size:.65rem;color:#6ee7b7;font-weight:700;text-transform:uppercase;margin-bottom:2px;">Rekomendasi Halte Mulai</div>'
        f'<div style="font-size:.9rem;font-weight:700;color:#d1fae5;">{actual_start}</div>'
        f'<div style="font-size:.72rem;color:#6ee7b7;opacity:.8;margin-top:8px;border-top:1px solid rgba(16,185,129,.15);padding-top:8px;">'
        f'<i class="fa-solid fa-circle-info" style="margin-right:4px;"></i>Halte terdekat dari GPS Anda (Haversine)</div></div>',
        unsafe_allow_html=True)
    btn_label = "Hitung Rute dari Halte Terdekat"
else:
    st.sidebar.markdown('<p style="color:#a78bfa!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;"><i class="fa-solid fa-hand-pointer"></i> &nbsp;Pilih Halte Awal</p>', unsafe_allow_html=True)
    st.sidebar.caption("GPS tidak aktif — pilih manual.")
    actual_start = st.sidebar.selectbox("Halte awal:", non_mal, index=0, label_visibility="collapsed")
    btn_label = "Cari Rute Terpendek"

st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:12px 0;">', unsafe_allow_html=True)
st.sidebar.markdown('<p style="color:#f43f5e!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px;"><i class="fa-solid fa-flag-checkered"></i> &nbsp;Tujuan</p>', unsafe_allow_html=True)
st.sidebar.markdown(
    f'<div style="background:rgba(244,63,94,.08);border:1px solid rgba(244,63,94,.25);'
    f'border-radius:10px;padding:11px 13px;color:#fda4af;margin-bottom:12px;'
    f'display:flex;align-items:center;gap:8px;">'
    f'<i class="fa-solid fa-location-dot" style="color:#f43f5e;font-size:1.1rem;"></i>'
    f'<div><div style="font-size:.65rem;color:#9f1239;font-weight:700;text-transform:uppercase;">Destinasi Akhir (Tetap)</div>'
    f'<div style="font-weight:700;font-size:.88rem;">{dest_node}</div></div></div>',
    unsafe_allow_html=True)

btn_calc = st.sidebar.button(btn_label, use_container_width=True)
st.sidebar.markdown('<div style="margin-top:20px;text-align:center;font-size:.66rem;color:#334155;border-top:1px solid rgba(148,163,184,.1);padding-top:10px;"><i class="fa-solid fa-code"></i> Dijkstra + Haversine</div>', unsafe_allow_html=True)

# ── Page header ────────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;"><i class="fa-solid fa-route" style="color:#60a5fa;margin-right:8px;"></i>Pencarian Rute Terpendek</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#64748b;margin-bottom:18px;">Rute TransJogja terpendek menuju Halte Malioboro — Algoritma Dijkstra + Haversine</div>', unsafe_allow_html=True)

# ── Build map ──────────────────────────────────────────────────────────────────
c_lat = sum(v[0] for v in nodes.values()) / len(nodes)
c_lon = sum(v[1] for v in nodes.values()) / len(nodes)
m_center = [user_lat, user_lon] if (user_lat and user_lon) else [c_lat, c_lon]
m = folium.Map(location=m_center, zoom_start=15, tiles="CartoDB dark_matter", attr="CartoDB")
if user_lat and user_lon:
    folium.Marker([user_lat, user_lon], popup="<b>Lokasi Anda</b>", tooltip="Lokasi GPS",
                  icon=folium.Icon(color="purple", icon="street-view", prefix="fa")).add_to(m)

path_nodes, total_dist = None, 0.0

if btn_calc:
    with st.spinner("Menghitung rute terpendek..."):
        path_nodes, total_dist = find_shortest_path(G, actual_start, dest_node)

    if path_nodes:
        travel_min = (total_dist / 20.0) * 60
        mid_nodes  = " \u2192 ".join(path_nodes[1:-1])
        mid_arrow  = ("\u2192 " + mid_nodes + " \u2192") if len(path_nodes) > 2 else "\u2192"

        st.markdown(
            f'<div style="background:linear-gradient(135deg,rgba(16,185,129,.15),rgba(5,150,105,.08));'
            f'border:1px solid rgba(16,185,129,.4);border-radius:16px;'
            f'padding:18px 24px;margin-bottom:16px;display:flex;'
            f'align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;">'
            f'<div style="display:flex;align-items:center;gap:14px;">'
            f'<div style="width:44px;height:44px;background:rgba(16,185,129,.2);border-radius:50%;'
            f'display:flex;align-items:center;justify-content:center;">'
            f'<i class="fa-solid fa-route" style="color:#10b981;font-size:1.1rem;"></i></div>'
            f'<div>'
            f'<div style="font-size:.62rem;color:#6ee7b7;font-weight:700;text-transform:uppercase;letter-spacing:1px;">'
            f'<i class="fa-solid fa-star" style="margin-right:3px;"></i>Rekomendasi Jalur Terpendek \u2014 Dijkstra SPK</div>'
            f'<div style="font-size:.95rem;font-weight:700;color:#d1fae5;">'
            f'{path_nodes[0]} <span style="color:#6ee7b7;font-weight:400;font-size:.82rem;margin:0 6px;">{mid_arrow}</span> {path_nodes[-1]}'
            f'</div></div></div>'
            f'<div style="display:flex;gap:18px;flex-wrap:wrap;">'
            f'<div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:#10b981;">{total_dist:.2f}</div>'
            f'<div style="font-size:.62rem;color:#6ee7b7;text-transform:uppercase;">Total KM</div></div>'
            f'<div style="width:1px;background:rgba(16,185,129,.2);"></div>'
            f'<div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:#34d399;">&plusmn;{travel_min:.0f}</div>'
            f'<div style="font-size:.62rem;color:#6ee7b7;text-transform:uppercase;">Menit</div></div>'
            f'<div style="width:1px;background:rgba(16,185,129,.2);"></div>'
            f'<div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:#34d399;">{len(path_nodes)-1}</div>'
            f'<div style="font-size:.62rem;color:#6ee7b7;text-transform:uppercase;">Segmen</div></div>'
            f'<div style="width:1px;background:rgba(16,185,129,.2);"></div>'
            f'<div style="text-align:center;"><div style="font-size:1.5rem;font-weight:800;color:#6ee7b7;">{len(path_nodes)}</div>'
            f'<div style="font-size:.62rem;color:#6ee7b7;text-transform:uppercase;">Halte</div></div>'
            f'</div></div>',
            unsafe_allow_html=True)

        for edge in edges:
            folium.PolyLine(edge["coordinates"], color="#1e3a5f", weight=2, opacity=.5).add_to(m)
        path_coords = []
        for i in range(len(path_nodes)-1):
            u, v = path_nodes[i], path_nodes[i+1]
            if G.has_edge(u, v):
                ec = G[u][v].get("path", [])
                path_coords.extend(ec if ec else [nodes[u], nodes[v]])
        if path_coords:
            folium.PolyLine(path_coords, color="#1d4ed8", weight=14, opacity=.2).add_to(m)
            try:
                from folium.plugins import AntPath
                AntPath(path_coords, color="#60a5fa", weight=5, opacity=.95, delay=800,
                        dash_array=[15,25], tooltip=f"Rute Terpendek \u2014 {total_dist:.2f} KM").add_to(m)
            except Exception:
                folium.PolyLine(path_coords, color="#60a5fa", weight=5, opacity=1).add_to(m)
    else:
        st.error("Rute tidak ditemukan. Coba pilih halte awal yang berbeda.")

# ── Node markers ───────────────────────────────────────────────────────────────
for nname, coords in nodes.items():
    hi = halte_info.get(nname, {})
    popup_html = (
        f'<div style="font-family:Outfit,sans-serif;min-width:180px;">'
        f'<b style="font-size:13px;">{nname}</b><br>'
        f'<span style="font-size:11px;color:#666;">{hi.get("alamat","—")}</span><br><br>'
        f'<span style="font-size:11px;">\u23f0 {hi.get("jam_operasi","—")}</span><br>'
        f'<span style="font-size:11px;">\U0001f68c Koridor: {", ".join(hi.get("koridor",[])) or "—"}</span><br>'
        f'<span style="font-size:11px;">\U0001f6de Fasilitas: {", ".join(hi.get("fasilitas",[])) or "—"}</span></div>')
    clr  = "red"   if "Malioboro" in nname else ("green" if nname == actual_start else "blue")
    icon = "flag-checkered" if "Malioboro" in nname else ("play" if nname == actual_start else "bus")
    folium.Marker(coords, popup=folium.Popup(popup_html, max_width=260),
                  tooltip=nname, icon=folium.Icon(color=clr, icon=icon, prefix="fa")).add_to(m)

# ── Map + Info ─────────────────────────────────────────────────────────────────
map_col, info_col = st.columns([3, 1])
with map_col:
    st.markdown('<div style="border-radius:16px;overflow:hidden;border:1px solid rgba(59,130,246,.2);box-shadow:0 10px 40px rgba(0,0,0,.4);">', unsafe_allow_html=True)
    st_folium(m, width="100%", height=530, returned_objects=[])
    st.markdown('</div>', unsafe_allow_html=True)

with info_col:
    if btn_calc and path_nodes:
        pct = min(int((total_dist / 10.0)*100), 100)
        st.markdown(
            f'<div style="background:linear-gradient(135deg,#1e3a8a,#1e293b);'
            f'border:1px solid rgba(96,165,250,.3);padding:22px 16px;'
            f'border-radius:16px;color:white;margin-bottom:12px;text-align:center;">'
            f'<div style="font-size:.7rem;font-weight:700;color:rgba(255,255,255,.4);'
            f'text-transform:uppercase;letter-spacing:1.5px;">Estimasi Jarak</div>'
            f'<div style="font-size:2.8rem;font-weight:800;'
            f'background:linear-gradient(135deg,#60a5fa,#a78bfa);'
            f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:6px 0;">{total_dist:.2f}</div>'
            f'<div style="font-size:.9rem;color:rgba(255,255,255,.35);">Kilometer</div></div>',
            unsafe_allow_html=True)
        st.markdown('<div style="font-size:.66rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;"><i class="fa-solid fa-gauge-high" style="color:#a78bfa;margin-right:4px;"></i>Efisiensi Jarak</div>', unsafe_allow_html=True)
        st.progress(pct)
        st.markdown(f'<div style="font-size:.68rem;color:#334155;margin-bottom:12px;text-align:right;">{pct}% dari maks 10 KM</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.7rem;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px;"><i class="fa-solid fa-route" style="margin-right:5px;"></i>Rute yang Dilalui</div>', unsafe_allow_html=True)
        tl_line = "background:linear-gradient(180deg,#10b981,#3b82f6,#f43f5e)" if len(path_nodes) > 2 else "background:#10b981"
        st.markdown(f'<div style="position:relative;padding-left:26px;"><div style="position:absolute;left:5px;top:6px;bottom:6px;width:2px;{tl_line};border-radius:2px;"></div>', unsafe_allow_html=True)
        for i, p in enumerate(path_nodes):
            if i == 0:
                dot, lbl, bl, label = "border:2px solid #10b981;background:#0d1117;", "color:#10b981;", "border-left:3px solid #10b981;", "Start"
            elif i == len(path_nodes)-1:
                dot, lbl, bl, label = "border:2px solid #f43f5e;background:#0d1117;", "color:#f43f5e;", "border-left:3px solid #f43f5e;", "Tujuan"
            else:
                dot, lbl, bl, label = "background:#3b82f6;", "color:#60a5fa;", "border-left:3px solid #3b82f6;", f"Transit {i}"
            st.markdown(
                f'<div style="position:relative;margin-bottom:8px;">'
                f'<div style="width:11px;height:11px;border-radius:50%;{dot}position:absolute;left:-23px;top:50%;transform:translateY(-50%);"></div>'
                f'<div style="background:#1e293b;{bl}border-top:1px solid rgba(148,163,184,.07);'
                f'border-right:1px solid rgba(148,163,184,.07);border-bottom:1px solid rgba(148,163,184,.07);'
                f'padding:9px 11px;border-radius:0 10px 10px 0;color:#e2e8f0;font-size:.83rem;font-weight:500;">'
                f'<div style="font-size:.62rem;{lbl}font-weight:700;text-transform:uppercase;letter-spacing:.8px;">{label}</div>'
                f'{p}</div></div>',
                unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1e293b;border:1px solid rgba(148,163,184,.1);
                    border-radius:14px;padding:30px 16px;text-align:center;">
            <i class="fa-solid fa-map-location-dot" style="font-size:2.2rem;color:#293548;margin-bottom:12px;display:block;"></i>
            <div style="font-weight:600;color:#475569;font-size:.88rem;">Siap Menghitung</div>
            <div style="font-size:.78rem;color:#334155;margin-top:8px;line-height:1.6;">
                Pilih halte awal, lalu klik<br>
                <span style="color:#60a5fa;font-weight:600;">Cari Rute Terpendek</span>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Detail calculation ─────────────────────────────────────────────────────────
if btn_calc and path_nodes:
    st.markdown('<hr style="border-color:rgba(148,163,184,.06);margin:20px 0 14px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#60a5fa;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;"><i class="fa-solid fa-calculator" style="margin-right:6px;"></i>Detail Perhitungan Dijkstra + Haversine</div>', unsafe_allow_html=True)

    seg_details, cum = [], 0.0
    for i in range(len(path_nodes)-1):
        u, v = path_nodes[i], path_nodes[i+1]
        d = G[u][v]["weight"] if G.has_edge(u, v) else 0.0
        cum += d
        seg_details.append((u, v, d, cum))

    if seg_details:
        scols = st.columns(len(seg_details))
        for idx, (col, (u, v, seg, ac)) in enumerate(zip(scols, seg_details)):
            tc = "#10b981" if idx == 0 else ("#f43f5e" if idx == len(seg_details)-1 else "#3b82f6")
            with col:
                st.markdown(
                    f'<div style="background:#1e293b;border:1px solid rgba(59,130,246,.12);'
                    f'border-top:3px solid {tc};border-radius:12px;padding:13px 9px;text-align:center;">'
                    f'<div style="font-size:.6rem;color:#475569;font-weight:700;text-transform:uppercase;margin-bottom:6px;">Segmen {idx+1}</div>'
                    f'<div style="font-size:.7rem;color:#94a3b8;margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{u}">{u}</div>'
                    f'<div style="font-size:.62rem;color:#334155;margin:2px 0;">&#8595;</div>'
                    f'<div style="font-size:.7rem;color:#94a3b8;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{v}">{v}</div>'
                    f'<div style="font-size:1.2rem;font-weight:800;color:#60a5fa;">{seg:.3f}</div>'
                    f'<div style="font-size:.6rem;color:#334155;margin-bottom:6px;">km</div>'
                    f'<div style="background:rgba(167,139,250,.1);border-radius:7px;padding:4px;">'
                    f'<div style="font-size:.58rem;color:#64748b;">Akumulasi &Sigma;d</div>'
                    f'<div style="font-size:.82rem;font-weight:700;color:#a78bfa;">{ac:.3f} km</div></div></div>',
                    unsafe_allow_html=True)

    with st.expander("Jejak Iterasi Dijkstra & Formula Haversine", expanded=False):
        st.markdown("""
**Formula Haversine:**
```
a = sin²(Δlat/2) + cos(lat₁)·cos(lat₂)·sin²(Δlon/2)
c = 2·atan2(√a, √(1−a))
d = 6371·c  (km)
```
**Dijkstra** memilih path dengan &Sigma;d terkecil dari seluruh kemungkinan jalur di graf.
""")
        rows = "".join(
            f"<tr style='border-bottom:1px solid rgba(148,163,184,.07);'>"
            f"<td style='padding:8px 10px;color:#64748b;font-size:.76rem;'>{i+1}</td>"
            f"<td style='padding:8px 10px;color:#e2e8f0;font-size:.78rem;'>{u}</td>"
            f"<td style='padding:8px 10px;color:#e2e8f0;font-size:.78rem;'>{v}</td>"
            f"<td style='padding:8px 10px;color:#60a5fa;font-weight:700;font-size:.78rem;'>{seg:.4f} km</td>"
            f"<td style='padding:8px 10px;color:#a78bfa;font-weight:700;font-size:.78rem;'>{ac:.4f} km</td></tr>"
            for i, (u, v, seg, ac) in enumerate(seg_details))
        st.markdown(
            f'<table style="width:100%;border-collapse:collapse;background:#1e293b;'
            f'border:1px solid rgba(148,163,184,.1);border-radius:12px;overflow:hidden;font-family:Outfit,sans-serif;">'
            f'<thead><tr style="background:rgba(59,130,246,.12);">'
            f'<th style="padding:9px 10px;color:#64748b;font-size:.68rem;text-transform:uppercase;text-align:left;">#</th>'
            f'<th style="padding:9px 10px;color:#64748b;font-size:.68rem;text-transform:uppercase;text-align:left;">Dari Halte</th>'
            f'<th style="padding:9px 10px;color:#64748b;font-size:.68rem;text-transform:uppercase;text-align:left;">Ke Halte</th>'
            f'<th style="padding:9px 10px;color:#64748b;font-size:.68rem;text-transform:uppercase;text-align:left;">Jarak d</th>'
            f'<th style="padding:9px 10px;color:#64748b;font-size:.68rem;text-transform:uppercase;text-align:left;">Total &Sigma;d</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>',
            unsafe_allow_html=True)

    # Route comparison
    st.markdown('<hr style="border-color:rgba(148,163,184,.06);margin:18px 0 12px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#a78bfa;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;"><i class="fa-solid fa-table" style="margin-right:6px;"></i>Perbandingan Semua Jalur (Bukti Dijkstra Optimal)</div>', unsafe_allow_html=True)
    try:
        all_p   = list(nx.all_simple_paths(G, source=actual_start, target=dest_node, cutoff=8))
        pd_list = sorted(
            [(p, nx.path_weight(G, p, weight="weight")) for p in all_p if len(p) >= 2],
            key=lambda x: x[1])
        if pd_list:
            rows_c = ""
            for r, (p, d) in enumerate(pd_list):
                bg     = "rgba(16,185,129,.08)" if r == 0 else "transparent"
                dcol   = "#10b981" if r == 0 else "#94a3b8"
                badge  = ('<span style="background:#10b981;color:#fff;font-size:.58rem;padding:1px 6px;'
                          'border-radius:50px;margin-left:6px;font-weight:700;">TERPENDEK \u2713</span>'
                          if r == 0 else "")
                pstr   = " \u2192 ".join(p)
                rows_c += (
                    f"<tr style='background:{bg};border-bottom:1px solid rgba(148,163,184,.07);'>"
                    f"<td style='padding:9px 11px;color:#64748b;font-size:.76rem;font-weight:700;'>{'🥇' if r==0 else r+1}</td>"
                    f"<td style='padding:9px 11px;color:#e2e8f0;font-size:.76rem;'>{pstr}{badge}</td>"
                    f"<td style='padding:9px 11px;color:{dcol};font-weight:700;font-size:.8rem;'>{d:.3f} km</td>"
                    f"<td style='padding:9px 11px;color:#64748b;font-size:.76rem;'>&plusmn;{(d/20)*60:.0f} mnt</td>"
                    f"<td style='padding:9px 11px;color:#64748b;font-size:.76rem;'>{len(p)-1} seg</td></tr>")
            st.markdown(
                f'<table style="width:100%;border-collapse:collapse;background:#1e293b;'
                f'border:1px solid rgba(148,163,184,.1);border-radius:12px;overflow:hidden;font-family:Outfit,sans-serif;">'
                f'<thead><tr style="background:rgba(167,139,250,.12);">'
                f'<th style="padding:9px 11px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">#</th>'
                f'<th style="padding:9px 11px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Jalur</th>'
                f'<th style="padding:9px 11px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Jarak</th>'
                f'<th style="padding:9px 11px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Est. Waktu</th>'
                f'<th style="padding:9px 11px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Segmen</th>'
                f'</tr></thead><tbody>{rows_c}</tbody></table>',
                unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"Perbandingan jalur tidak tersedia: {e}")

    # Graph viz
    st.markdown('<hr style="border-color:rgba(148,163,184,.06);margin:18px 0 12px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:12px;"><i class="fa-solid fa-diagram-project" style="margin-right:6px;"></i>Visualisasi Graf Dijkstra</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0d1117"); ax.set_facecolor("#0d1117")
    pos      = {n: (nodes[n][1], nodes[n][0]) for n in G.nodes()}
    sp_edges = set(zip(path_nodes, path_nodes[1:]))
    nx.draw_networkx_edges(G, pos,
        edgelist=[(u,v) for u,v in G.edges() if (u,v) not in sp_edges and (v,u) not in sp_edges],
        ax=ax, edge_color="#1e3a5f", width=2, alpha=.6)
    nx.draw_networkx_edges(G, pos,
        edgelist=[(u,v) for u,v in G.edges() if (u,v) in sp_edges or (v,u) in sp_edges],
        ax=ax, edge_color="#60a5fa", width=4, alpha=1.)
    nx.draw_networkx_edge_labels(G, pos,
        edge_labels={(u,v): f"{G[u][v]['weight']:.2f}km" for u,v in G.edges()},
        ax=ax, font_color="#475569", font_size=6.5, bbox=dict(alpha=0))
    ncol = ["#f43f5e" if "Malioboro" in n else
            ("#10b981" if n == path_nodes[0] else
             ("#3b82f6" if n in path_nodes else "#334155")) for n in G.nodes()]
    nsz  = [600 if "Malioboro" in n or n == path_nodes[0] else
            (450 if n in path_nodes else 300) for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=ncol, node_size=nsz, alpha=.95)
    nx.draw_networkx_labels(G, pos,
        labels={n: n.replace("Halte ", "") for n in G.nodes()},
        ax=ax, font_color="#e2e8f0", font_size=7.5, font_weight="bold")
    legend_items = [mpatches.Patch(color=c, label=l) for c, l in [
        ("#10b981","Awal"), ("#3b82f6","Transit"), ("#f43f5e","Tujuan"),
        ("#334155","Lain"), ("#60a5fa","Edge Terpendek"), ("#1e3a5f","Edge Lain")]]
    ax.legend(handles=legend_items, loc="upper left", framealpha=.15,
              facecolor="#1e293b", edgecolor="#334155", labelcolor="#94a3b8", fontsize=7.5)
    ax.set_title("Graf Halte TransJogja \u2014 Jalur Terpendek Dijkstra",
                 color="#60a5fa", fontsize=11, pad=12, fontweight="bold")
    ax.axis("off"); plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
