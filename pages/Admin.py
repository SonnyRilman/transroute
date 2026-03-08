import streamlit as st
import json, os
from utils.styles import inject_styles
from utils.auth import check_admin, render_sidebar

st.set_page_config(page_title="Admin | TransJogja", page_icon="🔐",
                   layout="wide", initial_sidebar_state="expanded")
inject_styles()

# ── AUTH & SIDEBAR ─────────────────────────────────────────────────────────────
check_admin()
render_sidebar()

DATA_DIR   = "data"
HALTE_FILE = os.path.join(DATA_DIR, "halte_info.json")
KOR_FILE   = os.path.join(DATA_DIR, "koridor.json")

def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# Page header
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;margin-bottom:20px;">
    <div style="width:44px;height:44px;background:linear-gradient(135deg,#f59e0b,#d97706);
                border-radius:12px;display:flex;align-items:center;justify-content:center;">
        <i class="fa-solid fa-shield-halved" style="color:white;font-size:1.1rem;"></i>
    </div>
    <div>
        <div style="font-size:1.3rem;font-weight:800;color:#e2e8f0;">Panel Administrator</div>
        <div style="font-size:.82rem;color:#64748b;">Kelola data halte, rute, dan node TransJogja Navigator</div>
    </div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Data Halte", "Rute / Koridor Bus", "Node KML (Graf)"])

# ══════════════════════════════════════════
# TAB 1 — KELOLA DATA HALTE
# ══════════════════════════════════════════
with tab1:
    halte_data = load_json(HALTE_FILE)

    st.markdown('<div style="font-size:.78rem;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;"><i class="fa-solid fa-bus-simple" style="margin-right:5px;"></i>Data Halte TransJogja</div>', unsafe_allow_html=True)

    # Add new halte
    with st.expander("Tambah Halte Baru", expanded=False):
        with st.form("add_halte"):
            c1, c2 = st.columns(2)
            with c1:
                new_name   = st.text_input("Nama Halte *", placeholder="cth: Halte Taman Sari")
                new_alamat = st.text_input("Alamat", placeholder="cth: Jl. Taman Sari No.1")
                new_jam    = st.text_input("Jam Operasi", value="05:00 - 22:00")
            with c2:
                new_fac    = st.text_area("Fasilitas (pisahkan koma)", placeholder="cth: Shelter, CCTV, Kursi Tunggu")
                new_kor    = st.text_input("Koridor (pisahkan koma)", placeholder="cth: 1A, 2A")
                new_status = st.selectbox("Status", ["Aktif", "Tidak Aktif"])
            if st.form_submit_button("Simpan Halte", use_container_width=True):
                if new_name.strip():
                    halte_data[new_name.strip()] = {
                        "alamat": new_alamat,
                        "fasilitas": [f.strip() for f in new_fac.split(",") if f.strip()],
                        "koridor":   [k.strip() for k in new_kor.split(",")  if k.strip()],
                        "jam_operasi": new_jam,
                        "status": new_status
                    }
                    save_json(HALTE_FILE, halte_data)
                    st.success(f"Halte '{new_name}' berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Nama halte wajib diisi.")

    st.markdown('<hr style="border-color:rgba(148,163,184,.07);margin:12px 0;">', unsafe_allow_html=True)

    # Display all halte with edit/delete
    for hname, hdata in list(halte_data.items()):
        with st.expander(f"{hname}  ·  {hdata.get('status','Aktif')}", expanded=False):
            with st.form(f"edit_{hname}"):
                c1, c2 = st.columns(2)
                with c1:
                    e_alamat = st.text_input("Alamat",       value=hdata.get("alamat",""))
                    e_jam    = st.text_input("Jam Operasi",  value=hdata.get("jam_operasi",""))
                    e_status = st.selectbox("Status", ["Aktif","Tidak Aktif"],
                                             index=0 if hdata.get("status","Aktif")=="Aktif" else 1)
                with c2:
                    e_fac  = st.text_area("Fasilitas (koma)",  value=", ".join(hdata.get("fasilitas",[])))
                    e_kor  = st.text_input("Koridor (koma)",   value=", ".join(hdata.get("koridor",[])))
                c_save, c_del = st.columns([3,1])
                with c_save:
                    if st.form_submit_button("Simpan Perubahan", use_container_width=True):
                        halte_data[hname] = {
                            "alamat": e_alamat,
                            "fasilitas": [f.strip() for f in e_fac.split(",") if f.strip()],
                            "koridor":   [k.strip() for k in e_kor.split(",")  if k.strip()],
                            "jam_operasi": e_jam,
                            "status": e_status
                        }
                        save_json(HALTE_FILE, halte_data)
                        st.success("Perubahan disimpan!")
                        st.rerun()
                with c_del:
                    if st.form_submit_button("Hapus Data", use_container_width=True):
                        del halte_data[hname]
                        save_json(HALTE_FILE, halte_data)
                        st.warning(f"Halte '{hname}' dihapus.")
                        st.rerun()

# ══════════════════════════════════════════
# TAB 2 — KELOLA DATA RUTE / KORIDOR
# ══════════════════════════════════════════
with tab2:
    koridor_data = load_json(KOR_FILE)
    if isinstance(koridor_data, list):
        koridor_dict = {k["kode"]: k for k in koridor_data}
    else:
        koridor_dict = koridor_data

    st.markdown('<div style="font-size:.78rem;color:#10b981;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;"><i class="fa-solid fa-road" style="margin-right:5px;"></i>Data Koridor Bus</div>', unsafe_allow_html=True)

    with st.expander("Tambah Koridor Baru", expanded=False):
        with st.form("add_koridor"):
            c1, c2 = st.columns(2)
            with c1:
                nk_kode = st.text_input("Kode Koridor *", placeholder="cth: 5D")
                nk_nama = st.text_input("Nama Koridor",  placeholder="cth: Koridor 5D - Senopati")
                nk_rute = st.text_input("Deskripsi Rute", placeholder="cth: Terminal A → Malioboro → Terminal B")
            with c2:
                nk_halte    = st.text_area("Daftar Halte (koma)", placeholder="cth: Halte A, Halte B")
                nk_jam      = st.text_input("Jam Operasi",  value="05:30 - 21:00")
                nk_interval = st.text_input("Interval",     value="20-30 menit")
            if st.form_submit_button("Simpan Koridor", use_container_width=True):
                if nk_kode.strip():
                    koridor_dict[nk_kode] = {
                        "kode": nk_kode, "nama": nk_nama, "rute": nk_rute,
                        "halte": [h.strip() for h in nk_halte.split(",") if h.strip()],
                        "jam_operasi": nk_jam, "tarif": "Rp 3.500",
                        "interval": nk_interval, "warna": "#60a5fa"
                    }
                    save_json(KOR_FILE, list(koridor_dict.values()))
                    st.success(f"Koridor '{nk_kode}' berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("Kode koridor wajib diisi.")

    st.markdown('<hr style="border-color:rgba(148,163,184,.07);margin:12px 0;">', unsafe_allow_html=True)

    for kode, kdata in list(koridor_dict.items()):
        with st.expander(f"Koridor {kode} — {kdata.get('nama','')}", expanded=False):
            with st.form(f"edit_kor_{kode}"):
                c1, c2 = st.columns(2)
                with c1:
                    ek_nama = st.text_input("Nama",      value=kdata.get("nama",""))
                    ek_rute = st.text_input("Rute",      value=kdata.get("rute",""))
                    ek_jam  = st.text_input("Jam Op.",   value=kdata.get("jam_operasi",""))
                with c2:
                    ek_halte    = st.text_area("Halte (koma)", value=", ".join(kdata.get("halte",[])))
                    ek_interval = st.text_input("Interval",    value=kdata.get("interval",""))
                c_s, c_d = st.columns([3,1])
                with c_s:
                    if st.form_submit_button("Simpan Perubahan", use_container_width=True):
                        koridor_dict[kode].update({
                            "nama": ek_nama, "rute": ek_rute, "jam_operasi": ek_jam,
                            "halte": [h.strip() for h in ek_halte.split(",") if h.strip()],
                            "interval": ek_interval
                        })
                        save_json(KOR_FILE, list(koridor_dict.values()))
                        st.success("Koridor diperbarui!")
                        st.rerun()
                with c_d:
                    if st.form_submit_button("Hapus Data", use_container_width=True):
                        del koridor_dict[kode]
                        save_json(KOR_FILE, list(koridor_dict.values()))
                        st.warning(f"Koridor '{kode}' dihapus.")
                        st.rerun()

# ══════════════════════════════════════════
# TAB 3 — KELOLA NODE (KML-based, read-only)
# ══════════════════════════════════════════
with tab3:
    from utils.kml_parser import parse_kml
    kml_path = os.path.join("data", "sample_route.kml")
    st.markdown('<div style="font-size:.78rem;color:#a78bfa;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;"><i class="fa-solid fa-circle-nodes" style="margin-right:5px;"></i>Data Node (Graf Halte)</div>', unsafe_allow_html=True)

    if os.path.exists(kml_path):
        nodes, edges = parse_kml(kml_path)
        st.markdown(f"""
        <div style="background:rgba(167,139,250,.08);border:1px solid rgba(167,139,250,.2);
                    border-radius:12px;padding:14px 18px;margin-bottom:14px;
                    display:flex;gap:24px;">
            <div><div style="font-size:1.4rem;font-weight:800;color:#a78bfa;">{len(nodes)}</div>
                 <div style="font-size:.68rem;color:#64748b;text-transform:uppercase;">Total Node</div></div>
            <div style="width:1px;background:rgba(148,163,184,.1);"></div>
            <div><div style="font-size:1.4rem;font-weight:800;color:#60a5fa;">{len(edges)}</div>
                 <div style="font-size:.68rem;color:#64748b;text-transform:uppercase;">Total Edge</div></div>
            <div style="width:1px;background:rgba(148,163,184,.1);"></div>
            <div style="display:flex;align-items:center;gap:8px;">
                <i class="fa-solid fa-circle-info" style="color:#f59e0b;"></i>
                <div style="font-size:.78rem;color:#94a3b8;">Node diekstrak otomatis dari file <b style="color:#f59e0b;">sample_route.kml</b></div>
            </div>
        </div>""", unsafe_allow_html=True)

        rows_n = "".join(
            f"<tr style='border-bottom:1px solid rgba(148,163,184,.07);'>"
            f"<td style='padding:9px 12px;color:#64748b;font-size:.76rem;'>{i+1}</td>"
            f"<td style='padding:9px 12px;color:#e2e8f0;font-size:.8rem;font-weight:600;'>{nname}</td>"
            f"<td style='padding:9px 12px;color:#60a5fa;font-size:.78rem;'>{coords[0]:.6f}</td>"
            f"<td style='padding:9px 12px;color:#a78bfa;font-size:.78rem;'>{coords[1]:.6f}</td>"
            f"<td style='padding:9px 12px;'><span style='background:{'rgba(244,63,94,.15)' if 'Malioboro' in nname else 'rgba(59,130,246,.12)'};color:{'#fda4af' if 'Malioboro' in nname else '#93c5fd'};font-size:.65rem;padding:2px 9px;border-radius:50px;font-weight:700;'>{'Tujuan' if 'Malioboro' in nname else 'Transit'}</span></td>"
            f"</tr>"
            for i,(nname,coords) in enumerate(nodes.items())
        )
        st.markdown(f"""
        <table style="width:100%;border-collapse:collapse;background:#1e293b;
                      border:1px solid rgba(148,163,184,.1);border-radius:12px;overflow:hidden;font-family:Outfit,sans-serif;">
            <thead><tr style="background:rgba(167,139,250,.12);">
                <th style="padding:9px 12px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">#</th>
                <th style="padding:9px 12px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Nama Node</th>
                <th style="padding:9px 12px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Latitude</th>
                <th style="padding:9px 12px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Longitude</th>
                <th style="padding:9px 12px;color:#a78bfa;font-size:.68rem;text-transform:uppercase;text-align:left;">Tipe</th>
            </tr></thead>
            <tbody>{rows_n}</tbody>
        </table>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);
                    border-radius:10px;padding:12px 16px;margin-top:12px;
                    font-size:.8rem;color:#fcd34d;line-height:1.6;">
            <i class="fa-solid fa-triangle-exclamation" style="margin-right:7px;"></i>
            <b>Catatan:</b> Data node diekstrak langsung dari file KML dan tidak dapat diubah melalui panel ini.
            Untuk menambah/mengubah node, edit file <code>data/sample_route.kml</code> dan restart aplikasi.
        </div>""", unsafe_allow_html=True)
    else:
        st.error("File KML tidak ditemukan.")
