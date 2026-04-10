import streamlit as st


def inject_shared_css():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: rgba(248, 250, 252, 0.96);
        border-right: 1px solid #e2e8f0;
    }
    .sidebar-title {
        font-size: 26px;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 2px;
        line-height: 1.1;
    }
    .sidebar-subtitle {
        font-size: 13px;
        color: #64748b;
        margin-bottom: 18px;
    }
    .sidebar-section-label {
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #16a34a;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .sidebar-section-label::before {
        content: "";
        width: 8px;
        height: 8px;
        background: #22c55e;
        border-radius: 50%;
        display: inline-block;
    }
    .sidebar-info-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }
    .sidebar-info-label {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 4px;
    }
    .sidebar-info-value {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
    }
    .sidebar-divider {
        height: 1px;
        background: #e2e8f0;
        margin: 18px 0 20px 0;
    }
    .sidebar-avatar {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #2563eb;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }
    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        border-radius: 16px;
        padding: 0.85rem 1rem;
        font-weight: 700;
        border: none;
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        color: white;
        box-shadow: 0 10px 20px rgba(37,99,235,0.20);
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(90deg, #1e40af, #1d4ed8);
        color: white;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
                
    [data-testid="stSidebar"] {
        background: rgba(248, 250, 252, 0.96);
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] div.stButton > button {
        width: 100%;
        border-radius: 16px;
        padding: 0.85rem 1rem;
        font-weight: 700;
        border: none;
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        color: white;
        box-shadow: 0 10px 20px rgba(37,99,235,0.20);
    }

    [data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(90deg, #1e40af, #1d4ed8);
        color: white;
    }

    /* ===== DIALOG LOGOUT ===== */
    div[data-testid="stDialog"] div.stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-weight: 700;
        border: none;
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        color: white;
        box-shadow: 0 10px 20px rgba(37,99,235,0.20);
    }

    div[data-testid="stDialog"] div.stButton > button:hover {
        background: linear-gradient(90deg, #1e40af, #1d4ed8);
        color: white;
    }

    </style>
    """, unsafe_allow_html=True)


def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["display_name"] = ""
    st.session_state["role"] = ""
    st.session_state["current_page"] = "home"
    st.session_state["show_logout_modal"] = False
    st.switch_page("app.py")


@st.dialog("🔒 Déconnexion")
def show_logout_dialog():
    st.markdown(
        "<p style='text-align:center; color:#475569; font-size:15px;'>"
        "Voulez-vous vraiment vous déconnecter ?</p>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Annuler", use_container_width=True):
            st.session_state["show_logout_modal"] = False
            st.rerun()
    with c2:
        if st.button("✅ Oui, déconnecter", use_container_width=True):
            logout()


def show_sidebar():
    if "show_logout_modal" not in st.session_state:
        st.session_state["show_logout_modal"] = False

    with st.sidebar:
        col_logo, col_text = st.columns([0.23, 0.77])
        with col_logo:
            st.image("images/avatar.png", width=52)
        with col_text:
            st.markdown("""
                <div class="sidebar-title">Report Tracker</div>
                <div class="sidebar-subtitle">Workspace sécurisé</div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label">Session active</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-info-card">
            <div class="sidebar-info-label">Utilisateur connecté</div>
            <div class="sidebar-info-value">👤 {st.session_state.get('display_name', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-info-card">
            <div class="sidebar-info-label">Profil d'accès</div>
            <div class="sidebar-info-value">🛡️ {st.session_state.get('role', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("🔒 Se déconnecter"):
            st.session_state["show_logout_modal"] = True
            st.rerun()

    # Appelé HORS du bloc sidebar pour que le dialog s'affiche au centre
    if st.session_state.get("show_logout_modal", False):
        show_logout_dialog()