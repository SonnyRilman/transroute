import streamlit as st
import os, json
from utils.styles import inject_styles
from utils.auth import render_sidebar

st.set_page_config(
    page_title="TransJogja Navigator",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
if "logged_in"  not in st.session_state: st.session_state.logged_in  = True
if "role"       not in st.session_state: st.session_state.role       = "user"
if "username"   not in st.session_state: st.session_state.username   = "Guest"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

# ══════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN — shown when not yet logged in
# ══════════════════════════════════════════════════════════════════════════════
# Access is now direct. Admin login moved to Admin page / Sidebar trigger.

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP — shown after login
# ══════════════════════════════════════════════════════════════════════════════

# 1. Render Custom Sidebar
render_sidebar()

# 2. Render Page Headers/Dashboards based on Role
role = st.session_state.role
uname = st.session_state.username

# Read basic data for stats
koridor_path = os.path.join("data", "koridor.json")
halte_path   = os.path.join("data", "halte_info.json")
n_koridor    = len(json.load(open(koridor_path, encoding="utf-8"))) if os.path.exists(koridor_path) else 0
n_halte      = len(json.load(open(halte_path,   encoding="utf-8"))) if os.path.exists(halte_path)   else 0

if role == "user":
    # ── BERANDA PENGGUNA ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 60%,#1d4ed8 100%);
                padding:44px 40px;border-radius:20px;color:white;text-align:center;
                margin-bottom:24px;box-shadow:0 20px 60px rgba(30,58,138,.5);
                border:1px solid rgba(96,165,250,.2);position:relative;overflow:hidden;">
        <div style="position:absolute;inset:0;border-radius:20px;pointer-events:none;
                    background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.05),rgba(255,255,255,0));
                    background-size:400% auto;animation:shimmer 3.5s linear infinite;"></div>
        <div style="font-size:2.8rem;color:#60a5fa;margin-bottom:10px;display:inline-block;
                    animation:heroFloat 4s ease-in-out infinite;position:relative;z-index:1;">
            <i class="fa-solid fa-bus"></i>
        </div>
        <div style="font-size:2.4rem;font-weight:800;
                    background:linear-gradient(135deg,#93c5fd,#ffffff,#c4b5fd);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    margin-bottom:10px;position:relative;z-index:1;">
            Halo, {uname}!
        </div>
        <div style="font-size:.92rem;color:rgba(255,255,255,.7);max-width:520px;
                    margin:0 auto 18px;line-height:1.7;position:relative;z-index:1;">
            Mau pergi ke Malioboro hari ini? Temukan rute bus TransJogja terpendek dan tercepat
            berbasis <b style="color:#93c5fd;">Algoritma Dijkstra</b> + <b style="color:#c4b5fd;">Haversine</b>.
        </div>
        <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;position:relative;z-index:1;">
            <span style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
                         padding:5px 14px;border-radius:50px;font-size:.76rem;color:rgba(255,255,255,.85);">
                <i class="fa-solid fa-bolt" style="margin-right:5px;"></i>Pencarian Instan
            </span>
            <span style="background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
                         padding:5px 14px;border-radius:50px;font-size:.76rem;color:rgba(255,255,255,.85);">
                <i class="fa-solid fa-map-pin" style="margin-right:5px;"></i>GPS Otomatis
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav Cards (User Only)
    c1, c2, c3 = st.columns(3)
    user_nav = [
        (c1, "fa-route", "#60a5fa", "Cari Rute Terpendek", "Hitung jalur bus paling optimal dari posisi Anda menuju kawasan Malioboro."),
        (c2, "fa-map-location-dot", "#10b981", "Peta Titik Halte", "Lihat sebaran seluruh tempat tunggu TransJogja beserta fasilitasnya."),
        (c3, "fa-bus", "#a78bfa", "Informasi Koridor Bus", "Cek rute lengkap, armada yang beroperasi, dan jam layanan harian."),
    ]
    for col, icon, color, title, desc in user_nav:
        with col:
            st.markdown(f"""
            <div style="background:#1e293b;border:1px solid rgba(148,163,184,.08);
                        border-top:3px solid {color};border-radius:16px;padding:22px 18px;
                        text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.2);min-height:165px;">
                <div style="font-size:1.8rem;color:{color};margin-bottom:10px;"><i class="fa-solid {icon}"></i></div>
                <div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:8px;">{title}</div>
                <div style="font-size:.77rem;color:#64748b;line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<hr style="border-color:rgba(148,163,184,.07);margin:28px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#60a5fa;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;"><i class="fa-solid fa-circle-info" style="margin-right:6px;"></i>Cara Kerja Sistem</div>', unsafe_allow_html=True)
    
    # Step-by-step
    steps = [
        ("1","#60a5fa","fa-location-crosshairs","Deteksi Lokasi","Sistem membaca posisi GPS Anda dengan cepat."),
        ("2","#a78bfa","fa-walkie-talkie","Cari Halte","Mencari tempat tunggu bus terdekat dari lokasi Anda."),
        ("3","#10b981","fa-diagram-project","Hitung Graf","Jalur dicarikan menggunakan algoritma rute optimal Dijkstra."),
        ("4","#f59e0b","fa-flag-checkered","Hasil Rute","Menampilkan satu rute bus tercepat beserta estimasi waktu."),
    ]
    scols = st.columns(4)
    for col, (num, color, icon, title, desc) in zip(scols, steps):
        with col:
            st.markdown(f"""
            <div style="background:#0d1117;border:1px solid rgba(148,163,184,.08);
                        border-radius:14px;padding:18px 14px;text-align:center;">
                <div style="width:30px;height:30px;background:{color};border-radius:50%;
                            display:flex;align-items:center;justify-content:center;margin:0 auto 10px;
                            font-size:.78rem;font-weight:800;color:#fff;">{num}</div>
                <div style="font-size:1.1rem;color:{color};margin-bottom:8px;"><i class="fa-solid {icon}"></i></div>
                <div style="font-size:.8rem;font-weight:700;color:#e2e8f0;margin-bottom:5px;">{title}</div>
                <div style="font-size:.7rem;color:#64748b;line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

elif role == "admin":
    # ── BERANDA ADMINISTRATOR ───────────────────────────────────────────────────
    st.markdown("""
    <div style="background:linear-gradient(135deg,#451a03 0%,#b45309 100%);
                padding:36px;border-radius:20px;color:white;
                margin-bottom:24px;box-shadow:0 10px 40px rgba(180,83,9,.3);
                border:1px solid rgba(245,158,11,.3);display:flex;align-items:center;gap:24px;">
        <div style="width:80px;height:80px;background:rgba(255,255,255,.15);border-radius:20px;
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;border:1px solid rgba(255,255,255,.2);">
            <i class="fa-solid fa-server" style="font-size:2.4rem;color:#fde68a;"></i>
        </div>
        <div>
            <div style="font-size:.85rem;color:#fde68a;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">Dashboard Administrator</div>
            <div style="font-size:2.2rem;font-weight:800;color:white;line-height:1.1;margin-bottom:8px;">Control Panel Sistem</div>
            <div style="font-size:.9rem;color:rgba(255,255,255,.8);max-width:600px;">
                Selamat datang! Anda memiliki akses penuh untuk memperbarui basis data rute, halte, dan koridor TransJogja yang digunakan oleh pengguna.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Admin Quick Stats
    st.markdown('<div style="font-size:.78rem;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;"><i class="fa-solid fa-chart-pie" style="margin-right:6px;"></i>Statistik Database Aktif</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div style="background:#1e293b;border:1px solid rgba(245,158,11,.15);border-radius:14px;padding:20px;text-align:center;"><div style="font-size:1.4rem;color:#f59e0b;margin-bottom:8px;"><i class="fa-solid fa-bus-simple"></i></div><div style="font-size:1.8rem;font-weight:800;color:#fcd34d;">{n_halte}</div><div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;margin-top:2px;">Data Halte</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="background:#1e293b;border:1px solid rgba(244,63,94,.15);border-radius:14px;padding:20px;text-align:center;"><div style="font-size:1.4rem;color:#f43f5e;margin-bottom:8px;"><i class="fa-solid fa-road"></i></div><div style="font-size:1.8rem;font-weight:800;color:#fda4af;">{n_koridor}</div><div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;margin-top:2px;">Koridor Bus</div></div>', unsafe_allow_html=True)
    with c3:
        nodes, edges = 0, 0
        kml_p = os.path.join("data", "sample_route.kml")
        if os.path.exists(kml_p):
            from utils.kml_parser import parse_kml
            n_dic, e_lis = parse_kml(kml_p)
            nodes, edges = len(n_dic), len(e_lis)
        st.markdown(f'<div style="background:#1e293b;border:1px solid rgba(167,139,250,.15);border-radius:14px;padding:20px;text-align:center;"><div style="font-size:1.4rem;color:#a78bfa;margin-bottom:8px;"><i class="fa-solid fa-circle-nodes"></i></div><div style="font-size:1.8rem;font-weight:800;color:#c4b5fd;">{nodes}</div><div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;margin-top:2px;">Node Graf</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div style="background:#1e293b;border:1px solid rgba(59,130,246,.15);border-radius:14px;padding:20px;text-align:center;"><div style="font-size:1.4rem;color:#60a5fa;margin-bottom:8px;"><i class="fa-solid fa-diagram-project"></i></div><div style="font-size:1.8rem;font-weight:800;color:#93c5fd;">{edges}</div><div style="font-size:.7rem;color:#94a3b8;text-transform:uppercase;margin-top:2px;">Edge Terhubung</div></div>', unsafe_allow_html=True)

    # Admin Quick Actions
    st.markdown('<hr style="border-color:rgba(148,163,184,.07);margin:24px 0;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.78rem;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px;"><i class="fa-solid fa-compass-drafting" style="margin-right:6px;"></i>Aksi Cepat</div>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    with ac1:
        st.markdown("""
        <div style="background:rgba(245,158,11,.05);border:1px solid rgba(245,158,11,.2);border-radius:12px;padding:20px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:40px;height:40px;background:#f59e0b;border-radius:10px;display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-shield-halved" style="color:white;font-size:1.1rem;"></i></div>
                <div><div style="font-size:1rem;color:#fcd34d;font-weight:700;">Panel Administrator Utama</div><div style="font-size:.75rem;color:#64748b;">Akses CRUD Halte dan Koridor</div></div>
            </div>
            <p style="font-size:.8rem;color:#94a3b8;line-height:1.5;">Gunakan Panel Admin untuk menambah halte baru, mengedit lintasan koridor, memeriksa status operasional, dan meninjau data KML mentah secara real-time.</p>
        </div>
        """, unsafe_allow_html=True)
    with ac2:
        st.markdown("""
        <div style="background:rgba(16,185,129,.05);border:1px solid rgba(16,185,129,.2);border-radius:12px;padding:20px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <div style="width:40px;height:40px;background:#10b981;border-radius:10px;display:flex;align-items:center;justify-content:center;"><i class="fa-solid fa-eye" style="color:white;font-size:1.1rem;"></i></div>
                <div><div style="font-size:1rem;color:#6ee7b7;font-weight:700;">Tinjau Sisi Pengguna</div><div style="font-size:.75rem;color:#64748b;">Simulasi Peta Interaktif</div></div>
            </div>
            <p style="font-size:.8rem;color:#94a3b8;line-height:1.5;">Anda tidak perlu logout untuk melihat hasil perubahan. Semua navigasi pengguna (Cari Rute, Peta Halte) tersedia di sidebar sebelah kiri.</p>
        </div>
        """, unsafe_allow_html=True)
