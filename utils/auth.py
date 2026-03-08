import streamlit as st

def check_login():
    """Verify user is logged in, else stop execution."""
    if not st.session_state.get("logged_in"):
        st.markdown("""
        <div style="text-align:center;margin-top:80px;">
            <div style="width:70px;height:70px;background:rgba(244,63,94,.1);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
                <i class="fa-solid fa-lock" style="font-size:2rem;color:#f43f5e;"></i>
            </div>
            <h3 style="color:#e2e8f0;margin-bottom:8px;">Akses Ditolak</h3>
            <p style="color:#94a3b8;font-size:.9rem;">Sistem memerlukan autentikasi terlebih dahulu.</p>
            <p style="font-size:.8rem;color:#64748b;">Silakan kembali ke halaman Beranda untuk login.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Kembali ke Beranda (Login)", use_container_width=True):
                st.switch_page("app.py")
        st.stop()

def check_admin():
    """Verify user is an admin, else stop execution."""
    check_login()
    if st.session_state.get("role") != "admin":
        st.markdown("""
        <div style="text-align:center;margin-top:80px;">
            <div style="width:70px;height:70px;background:rgba(244,63,94,.1);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
                <i class="fa-solid fa-shield-halved" style="font-size:2rem;color:#f43f5e;"></i>
            </div>
            <h3 style="color:#e2e8f0;margin-bottom:8px;">Akses Administrator Diperlukan</h3>
            <p style="color:#94a3b8;font-size:.9rem;">Halaman ini dibatasi khusus untuk Administrator.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

def render_sidebar():
    """Render custom sidebar navigation based on role."""
    role = st.session_state.get("role")
    uname = st.session_state.get("username")
    if not role: return

    # User Profile Header
    role_color = "#f59e0b" if role == "admin" else "#60a5fa"
    role_icon  = "fa-shield-halved" if role == "admin" else "fa-user"
    role_label = "Administrator" if role == "admin" else "Pengguna"

    st.sidebar.markdown(f"""
    <div style="text-align:center;padding:12px 0 8px;">
        <div style="display:inline-flex;align-items:center;gap:8px;
                    background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.3);
                    border-radius:50px;padding:6px 14px;">
            <i class="fa-solid fa-bus" style="color:#60a5fa;font-size:.9rem;"></i>
            <span style="color:#93c5fd;font-weight:700;font-size:.85rem;">TransJogja Nav</span>
        </div>
    </div>
    <hr style="border-color:rgba(148,163,184,.1);margin:6px 0 12px;">
    <div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
                border-radius:12px;padding:12px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,{role_color}22,{role_color}44);
                        border:1px solid {role_color}44;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <i class="fa-solid {role_icon}" style="color:{role_color};font-size:.95rem;"></i>
            </div>
            <div>
                <div style="font-size:.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:2px;">{role_label}</div>
                <div style="font-size:.85rem;font-weight:700;color:#e2e8f0;line-height:1.2;">{uname}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inject CSS to make page_link styling consistent with dark theme
    st.sidebar.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    .stPageLink { margin-bottom: 4px; }
    .stPageLink a { padding: 0.6rem 0.8rem; border-radius: 8px; transition: all 0.2s ease; }
    .stPageLink a:hover { background-color: rgba(96,165,250,0.1) !important; text-decoration: none !important;}
    </style>
    """, unsafe_allow_html=True)

    # Custom Navigation Links
    st.sidebar.page_link("app.py", label="Dashboard Beranda")
    
    if role == "user":
        st.sidebar.markdown('<p style="color:#64748b;font-size:0.65rem;font-weight:800;letter-spacing:1.2px;margin:24px 0 8px 6px;">FITUR PENGGUNA</p>', unsafe_allow_html=True)
        st.sidebar.page_link("pages/Cari_Rute.py", label="Cari Rute Terpendek")
        st.sidebar.page_link("pages/Peta_Halte.py", label="Peta Fasilitas Halte")
        st.sidebar.page_link("pages/Bus_Koridor.py", label="Info Bus & Koridor")

    if role == "admin":
        st.sidebar.markdown('<p style="color:#f59e0b;font-size:0.65rem;font-weight:800;letter-spacing:1.2px;margin:24px 0 8px 6px;">PENGELOLAAN DATA</p>', unsafe_allow_html=True)
        st.sidebar.page_link("pages/Admin.py", label="Panel Administrator")

    # Logout Button
    st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:24px 0 16px;">', unsafe_allow_html=True)
    if st.sidebar.button("Keluar (Logout)", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("app.py")

