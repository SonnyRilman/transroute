import streamlit as st

def check_login():
    """Safety check, but now users enter directly by default."""
    if not st.session_state.get("logged_in"):
        st.session_state.logged_in = True
        st.session_state.role = "user"
        st.session_state.username = "Guest"
    return True

def check_admin():
    """Verify user is an admin. If not, show a dedicated admin login form."""
    if st.session_state.get("role") != "admin":
        st.markdown("""
        <div style="text-align:center;margin-top:50px;margin-bottom:30px;">
            <div style="width:70px;height:70px;background:rgba(245,158,11,.1);border-radius:50%;
                        display:flex;align-items:center;justify-content:center;margin:0 auto 20px;">
                <i class="fa-solid fa-shield-halved" style="font-size:2rem;color:#f59e0b;"></i>
            </div>
            <h3 style="color:#e2e8f0;margin-bottom:8px;">Akses Administrator</h3>
            <p style="color:#94a3b8;font-size:.9rem;">Silakan login untuk mengelola database sistem.</p>
        </div>
        """, unsafe_allow_html=True)
        
        _, center, _ = st.columns([1, 1.2, 1])
        with center:
            with st.form("admin_login_inline"):
                u = st.text_input("Admin ID", placeholder="admin")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                if st.form_submit_button("Masuk sebagai Admin", use_container_width=True):
                    if u == "admin" and p == "admin123":
                        st.session_state.logged_in = True
                        st.session_state.role = "admin"
                        st.session_state.username = "Administrator"
                        st.success("Login Berhasil!")
                        st.rerun()
                    else:
                        st.error("Kredensial salah.")
        st.stop()

def render_sidebar():
    """Render custom sidebar navigation based on role."""
    check_login()
    role = st.session_state.get("role")
    uname = st.session_state.get("username")

    # User Profile Header
    role_color = "#f59e0b" if role == "admin" else "#60a5fa"
    role_icon  = "fa-shield-halved" if role == "admin" else "fa-user"
    role_label = "Administrator" if role == "admin" else "Tamu / Pengguna"

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

    # Inject CSS for custom sidebar styling
    st.sidebar.markdown("""
    <style>
    /* Style the custom links to look more premium */
    .stPageLink { margin-bottom: 4px; }
    .stPageLink a { 
        padding: 0.6rem 0.8rem !important; 
        border-radius: 8px !important; 
        transition: all 0.2s ease !important;
        background-color: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        color: #e2e8f0 !important;
    }
    .stPageLink a:hover { 
        background-color: rgba(59,130,246,0.1) !important; 
        border-color: rgba(59,130,246,0.3) !important;
        text-decoration: none !important;
        color: #60a5fa !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Custom Navigation Links
    st.sidebar.page_link("app.py", label="Beranda")
    
    st.sidebar.markdown('<p style="color:#64748b;font-size:0.65rem;font-weight:800;letter-spacing:1.2px;margin:24px 0 8px 6px;">FITUR NAVIGASI</p>', unsafe_allow_html=True)
    st.sidebar.page_link("pages/Cari_Rute.py", label="Cari Rute Terpendek")
    st.sidebar.page_link("pages/Peta_Halte.py", label="Peta Fasilitas Halte")
    st.sidebar.page_link("pages/Bus_Koridor.py", label="Info Bus & Koridor")

    # Admin Panel only visible if already admin
    if role == "admin":
        st.sidebar.markdown('<p style="color:#f59e0b;font-size:0.65rem;font-weight:800;letter-spacing:1.2px;margin:24px 0 8px 6px;">ADMINISTRATOR</p>', unsafe_allow_html=True)
        st.sidebar.page_link("pages/Admin.py", label="Admin Panel")

    # Footer Actions
    st.sidebar.markdown('<hr style="border-color:rgba(148,163,184,.1);margin:24px 0 16px;">', unsafe_allow_html=True)
    if role == "admin":
        if st.sidebar.button("Keluar Admin (ke Tamu)", use_container_width=True):
            st.session_state.role = "user"
            st.session_state.username = "Guest"
            st.rerun()
    else:
        # Check if the user is asking for admin mode via query params (optional secret)
        # Or just leave it hidden for manual URL entry.
        st.sidebar.markdown('<div style="font-size:0.6rem;color:#334155;text-align:center;">TransJogja Navigator v3.1</div>', unsafe_allow_html=True)

