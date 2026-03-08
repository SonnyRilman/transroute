import streamlit as st
import json, os
from utils.styles import inject_styles
from utils.auth import check_login, render_sidebar

st.set_page_config(page_title="Bus & Koridor | TransJogja", page_icon="🚌",
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()

# ── AUTH & SIDEBAR ─────────────────────────────────────────────────────────────
check_login()
render_sidebar()


# Load data
koridor_path = os.path.join("data", "koridor.json")
if not os.path.exists(koridor_path):
    st.error("File koridor.json tidak ditemukan.")
    st.stop()
koridor_list = json.load(open(koridor_path, encoding="utf-8"))

# Page header
st.markdown('<div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;"><i class="fa-solid fa-bus" style="color:#10b981;margin-right:8px;"></i>Bus & Koridor TransJogja</div>', unsafe_allow_html=True)
st.markdown('<div style="font-size:.85rem;color:#64748b;margin-bottom:20px;">Informasi koridor bus TransJogja yang melayani kawasan Malioboro dan sekitarnya</div>', unsafe_allow_html=True)

# Summary cards
c1, c2, c3 = st.columns(3)
for col, icon, color, val, label in [
    (c1, "fa-road",         "#10b981", str(len(koridor_list)), "Total Koridor"),
    (c2, "fa-money-bill",   "#60a5fa", "Rp 3.500",             "Tarif Flat"),
    (c3, "fa-clock",        "#a78bfa", "05:00–23:00",          "Jam Operasional"),
]:
    with col:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1e293b,#0f172a);
                    border:1px solid rgba(59,130,246,.18);border-radius:14px;
                    padding:18px;text-align:center;margin-bottom:20px;">
            <i class="fa-solid {icon}" style="font-size:1.4rem;color:{color};margin-bottom:8px;display:block;"></i>
            <div style="font-size:1.4rem;font-weight:700;color:{color};">{val}</div>
            <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;margin-top:3px;">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr style="border-color:rgba(148,163,184,.07);margin:0 0 20px;">', unsafe_allow_html=True)

# Sidebar filter
st.sidebar.markdown('<p style="color:#10b981!important;font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;"><i class="fa-solid fa-filter"></i> &nbsp;Filter Koridor</p>', unsafe_allow_html=True)
kode_list = ["Semua"] + [k["kode"] for k in koridor_list]
selected = st.sidebar.selectbox("Pilih koridor:", kode_list, label_visibility="collapsed")

display = koridor_list if selected == "Semua" else [k for k in koridor_list if k["kode"] == selected]

# Koridor cards
for k in display:
    warna = k.get("warna", "#60a5fa")
    halte_badges = "".join(
        f'<span style="background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);'
        f'padding:3px 9px;border-radius:50px;font-size:.72rem;color:#e2e8f0;margin:3px;">{h}</span>'
        for h in k.get("halte", [])
    )
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#1e293b,#0f172a);
                border:1px solid rgba(148,163,184,.1);border-left:4px solid {warna};
                border-radius:14px;padding:22px 24px;margin-bottom:16px;
                box-shadow:0 4px 20px rgba(0,0,0,.3);">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:14px;">
            <div style="display:flex;align-items:center;gap:14px;">
                <div style="width:44px;height:44px;background:{warna};border-radius:12px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:.85rem;font-weight:800;color:white;flex-shrink:0;">
                    {k['kode']}
                </div>
                <div>
                    <div style="font-size:1rem;font-weight:700;color:#e2e8f0;">{k['nama']}</div>
                    <div style="font-size:.78rem;color:#64748b;margin-top:2px;">
                        <i class="fa-solid fa-route" style="margin-right:5px;"></i>{k['rute']}
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div style="text-align:center;">
                    <div style="font-size:.6rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;">Tarif</div>
                    <div style="font-size:.9rem;font-weight:700;color:#10b981;">{k['tarif']}</div>
                </div>
                <div style="width:1px;background:rgba(148,163,184,.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:.6rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;">Interval</div>
                    <div style="font-size:.9rem;font-weight:700;color:#60a5fa;">{k['interval']}</div>
                </div>
                <div style="width:1px;background:rgba(148,163,184,.1);"></div>
                <div style="text-align:center;">
                    <div style="font-size:.6rem;color:#64748b;text-transform:uppercase;letter-spacing:.8px;">Operasi</div>
                    <div style="font-size:.9rem;font-weight:700;color:#a78bfa;">{k['jam_operasi']}</div>
                </div>
            </div>
        </div>
        <div style="font-size:.7rem;color:#475569;font-weight:600;text-transform:uppercase;
                    letter-spacing:.8px;margin-bottom:8px;">
            <i class="fa-solid fa-map-marker-alt" style="margin-right:5px;color:{warna};"></i>
            Halte yang Dilalui ({len(k.get('halte',[]))} halte)
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:4px;">{halte_badges}</div>
    </div>""", unsafe_allow_html=True)

# Info note
st.markdown("""
<div style="background:rgba(59,130,246,.06);border:1px solid rgba(59,130,246,.2);
            border-radius:12px;padding:14px 18px;margin-top:8px;
            display:flex;align-items:flex-start;gap:12px;">
    <i class="fa-solid fa-circle-info" style="color:#60a5fa;font-size:1.1rem;margin-top:2px;flex-shrink:0;"></i>
    <div style="font-size:.82rem;color:#94a3b8;line-height:1.7;">
        <b style="color:#93c5fd;">Informasi Layanan TransJogja:</b><br>
        Semua koridor TransJogja dioperasikan oleh Pemerintah Daerah Istimewa Yogyakarta.
        Tarif <b style="color:#10b981;">Rp 3.500</b> berlaku flat untuk semua jarak.
        Bus beroperasi setiap hari termasuk hari libur nasional. Untuk informasi lebih lengkap,
        kunjungi website resmi TransJogja atau hubungi call center.
    </div>
</div>""", unsafe_allow_html=True)
