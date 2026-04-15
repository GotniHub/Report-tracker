import streamlit as st
import hashlib
from datetime import datetime

# =========================================================
# CONFIG PAGE
# =========================================================
st.set_page_config(
    page_title="Report Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
import streamlit as st

def require_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("Accès refusé. Veuillez vous connecter d'abord.")
        st.switch_page("app.py")   # mets ici le vrai nom du fichier principal
        st.stop()
st.logo("Logo_Advent.png", icon_image="Logom.png")
# =========================================================
# CSS GLOBAL
# =========================================================
st.markdown("""
<style>

/* =========================
   SIDEBAR PRO
========================= */
[data-testid="stSidebar"] {
    background: rgba(248, 250, 252, 0.96);
    border-right: 1px solid #e2e8f0;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}
.sidebar-brand div {
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.sidebar-logo {
    width: 46px;
    height: 46px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1d4ed8, #60a5fa);
    color: white;
    font-size: 22px;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);;
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
    font-weight: 800;
    letter-spacing: -0.5px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 10px;
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
                        
header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}            
/* =========================
   GLOBAL
========================= */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.18), transparent 22%),
        radial-gradient(circle at 80% 18%, rgba(147, 197, 253, 0.22), transparent 20%),
        radial-gradient(circle at 50% 75%, rgba(96, 165, 250, 0.14), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #eef4ff 52%, #e9f0fb 100%);
    min-height: 100vh;
}

/* grille légère */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(37, 99, 235, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
    background-size: 42px 42px;
    pointer-events: none;
    z-index: 0;
}
.metric-card {
    transition: all 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
}
/* halo de profondeur */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    width: 900px;
    height: 900px;
    left: 50%;
    top: 42%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(59, 130, 246, 0.16) 0%, rgba(59, 130, 246, 0.06) 35%, transparent 68%);
    filter: blur(55px);
    pointer-events: none;
    z-index: 0;
}

/* pour garder le contenu au-dessus */
[data-testid="stAppViewContainer"] > [data-testid="stMain"] {
    position: relative;
    z-index: 1;
}

.block-container::before {
    content: "";
    position: fixed;
    top: 20%;
    left: 30%;
    width: 400px;
    height: 400px;
    background: rgba(37, 99, 235, 0.15);
    filter: blur(120px);
    z-index: 0;
}
.global-login-title {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    color: #0f172a;
    margin-top: 10px;
    margin-bottom: 35px;
}

.global-login-title span {
    color: #2563eb;
}

.global-login-title::after {
    content: "";
    display: block;
    width: 60px;
    height: 4px;
    background: #2563eb;
    margin: 12px auto 0;
    border-radius: 4px;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
    max-width: 1400px;
}

h1, h2, h3 {
    color: #0f172a;
}

/* =========================
   LOGIN PAGE
========================= */
.brand-panel {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #2563eb 100%);
    border-radius: 24px;
    min-height: 620px;
    padding: 48px 42px;
    color: white;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.25);
}

.brand-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 22px;
}

.brand-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 18px;
    color: white;
}

.brand-subtitle {
    font-size: 17px;
    line-height: 1.7;
    color: rgba(255,255,255,0.88);
    margin-bottom: 28px;
}

.brand-card {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 18px;
    padding: 18px 20px;
    margin-top: 14px;
    backdrop-filter: blur(10px);
}

.brand-card-title {
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 6px;
    color: white;
}

.brand-card-text {
    font-size: 14px;
    color: rgba(255,255,255,0.85);
}

/* Target ONLY the login container on the right — not all containers */
[data-testid="stVerticalBlockBorderWrapper"]:has(.login-title) {
    background: rgba(255,255,255,0.90) !important;
    border: 1px solid rgba(15,23,42,0.08) !important;
    border-radius: 24px !important;
    padding: 36px 32px !important;
    min-height: 620px !important;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.10) !important;
    backdrop-filter: blur(14px) !important;
}

/* Remove styling from ALL other bordered containers */
[data-testid="stVerticalBlockBorderWrapper"]:not(:has(.login-title)) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* Remove default form border inside the login container */
[data-testid="stVerticalBlockBorderWrapper"]:has(.login-title) div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
}

.login-title {
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
}

.login-subtitle {
    font-size: 15px;
    color: #475569;
    margin-bottom: 26px;
}

.security-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 14px 16px;
    margin-top: 20px;
}

.security-title {
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
}

.footer-note {
    text-align: center;
    color: #64748b;
    font-size: 13px;
    margin-top: 20px;
}

/* =========================
   INPUTS / BUTTONS
========================= */
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid #cbd5e1 !important;
    padding: 12px 14px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    border-radius: 14px;
    padding: 0.75rem 1rem;
    font-weight: 700;
    font-size: 15px;
    border: none;
    background: linear-gradient(90deg, #1d4ed8, #2563eb);
    color: white;
    box-shadow: 0 10px 20px rgba(37,99,235,0.22);
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(90deg, #1e40af, #1d4ed8);
    color: white;
}

/* =========================
   TOPBAR
========================= */
.topbar {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 14px 18px;
    margin-bottom: 18px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.05);
}

.topbar-title {
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
}

.topbar-sub {
    font-size: 14px;
    color: #64748b;
}

/* =========================
   HOME CARDS
========================= */
.metric-card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
}
.metric-card,
.module-card {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
}
.metric-title {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 8px;
}

.metric-value {
    font-size: 30px;
    font-weight: 800;
    color: #0f172a;
}

.metric-desc {
    font-size: 13px;
    color: #475569;
    margin-top: 6px;
}

.module-card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    min-height: 170px;
}

.module-title {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
}

.module-text {
    color: #475569;
    font-size: 14px;
    line-height: 1.6;
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
.sidebar-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;  /* 🔥 rond */
    object-fit: cover;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
.sidebar-avatar {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #2563eb;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
/* =========================
   MODAL LOGOUT
========================= */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.35);
    backdrop-filter: blur(4px);
    z-index: 9999;
}

.modal-box {
    position: fixed;
    top: 38%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 28px;
    border-radius: 20px;
    width: 380px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.25);
    text-align: center;
    z-index: 10000;
}

.modal-title {
    font-size: 20px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

.modal-text {
    font-size: 14px;
    color: #475569;
    margin-bottom: 20px;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}    
.metric-card, .module-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(37, 99, 235, 0.10);
    border-radius: 18px;
    padding: 20px 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    min-height: 150px;
}

.metric-card:hover, .module-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 18px 34px rgba(37, 99, 235, 0.16);
    border-color: rgba(37, 99, 235, 0.28);
}

.metric-title {
    font-size: 0.95rem;
    color: #64748b;
    margin-bottom: 10px;
    font-weight: 600;
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 8px;
}

.metric-desc {
    font-size: 0.92rem;
    color: #64748b;
}

.module-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

.module-text {
    font-size: 0.96rem;
    color: #64748b;
    line-height: 1.65;
}                  
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.module-card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(37, 99, 235, 0.10);
    border-radius: 18px;
    padding: 20px 18px;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);

    /* 🔥 LA CLÉ */
    min-height: 160px;

    display: flex;
    flex-direction: column;
    justify-content: space-between;

    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.module-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 18px 34px rgba(37, 99, 235, 0.16);
}
</style>
""", unsafe_allow_html=True)
# =========================================================
# AUTH HELPERS
# =========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Remplace plus tard par JSON / Excel / base SQL
USERS = {
    "igotni@adv-sud.fr": {
        "name": "Ilyass Gotni",
        "password": hash_password("admin123"),
        "role": "Admin"
    },
    "rnajem@adv-sud.fr": {
        "name": "Rihab Najem",
        "password": hash_password("rihab123"),
        "role": "Manager"
    },      
    "jlarue@adv-sud.fr": {
        "name": "Julie Larue",
        "password": hash_password("X9@bL3!Qw7#e"),
        "role": "Manager"
    },
    "abeolet@adv-sud.fr": {
        "name": "Allison Beolet",
        "password": hash_password("T!7qR3#Yp@6L"),
        "role": "Manager"
    },
    "sbernard@adv-sud.fr": {
        "name": "Sylvie Bernard",
        "password": hash_password("vR8$Tz1!mA4#"),
        "role": "User"
    },        
    "safaa": {
        "name": "Safaa",
        "password": hash_password("Safaa123!"),
        "role": "User"
    }
}

def init_session():
    defaults = {
        "authenticated": False,
        "username": "",
        "display_name": "",
        "role": "",
        "current_page": "home"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def authenticate(username: str, password: str):
    username = username.strip().lower()
    if username in USERS:
        hashed_input = hash_password(password)
        if USERS[username]["password"] == hashed_input:
            return True, USERS[username]
    return False, None

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["display_name"] = ""
    st.session_state["role"] = ""
    st.session_state["current_page"] = "home"
    st.session_state["confirm_logout"] = False
    st.session_state["show_logout_modal"] = False
    st.rerun()

# =========================================================
# LOGIN PAGE
# =========================================================
def show_login_page():
    # Masquer la sidebar tant que l'utilisateur n'est pas connecté
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="global-login-title">
        Welcome to <span>"Report Tracker"</span> Portal
    </div>
    """, unsafe_allow_html=True)
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("""
            <div class="brand-panel">
                <div class="brand-badge">Secure Workspace &bull; Report Tracker</div>
                <div class="brand-title">Pilotage intelligent des missions, budgets et performances.</div>
                <div class="brand-subtitle">
                    Connectez-vous &agrave; <b>Report Tracker</b> pour acc&eacute;der &agrave; vos espaces de reporting,
                    d&#39;importation, de suivi mission et d&#39;analyse client dans une interface professionnelle.
                </div>
                <div class="brand-card">
                    <div class="brand-card-title">&#128202; Vision centralis&eacute;e</div>
                    <div class="brand-card-text">
                        Suivez les budgets, le r&eacute;alis&eacute;, les &eacute;carts et les indicateurs cl&eacute;s dans un seul outil.
                    </div>
                </div>
                <div class="brand-card">
                    <div class="brand-card-title">&#128272; Acc&egrave;s s&eacute;curis&eacute;</div>
                    <div class="brand-card-text">
                        Gestion des utilisateurs, r&ocirc;les et contr&ocirc;le d&#39;acc&egrave;s avant l&#39;entr&eacute;e dans l&#39;application.
                    </div>
                </div>
                <div class="brand-card">
                    <div class="brand-card-title">&#9889; Exp&eacute;rience professionnelle</div>
                    <div class="brand-card-text">
                        Interface moderne con&ccedil;ue pour les &eacute;quipes op&eacute;rationnelles, finance et pilotage.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        with st.container(border=True):
            st.markdown("""
            <div class="login-title">Authentification 🔐</div>
            <div class="login-subtitle">
                Entrez vos identifiants pour acc&eacute;der &agrave; l&#39;environnement s&eacute;curis&eacute;.
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Identifiant (email)", placeholder="Ex. igotni@adv-sud.fr")
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
                submitted = st.form_submit_button("🔑 Se connecter")

            if submitted:
                ok, user = authenticate(username, password)
                if ok:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username.strip().lower()
                    st.session_state["display_name"] = user["name"]
                    st.session_state["role"] = user["role"]
                    st.session_state["confirm_logout"] = False
                    st.success(f"✅ Connexion réussie !")
                    st.success(f"Bonjour {user['name']} 👋")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

            st.markdown("""
                <div class="security-box">
                    <div class="security-title">S&eacute;curit&eacute;</div>
                    <div style="color:#475569; font-size:14px;">
                        Cette zone est r&eacute;serv&eacute;e aux utilisateurs autoris&eacute;s de l&#39;outil Report Tracker.
                    </div>
                </div>
                <div class="footer-note">
                    Report Tracker &bull; Secure Access Portal
                </div>
            """, unsafe_allow_html=True)
            
    # =========================================================
# UI APP
# =========================================================
def show_sidebar():
    with st.sidebar:
        col_logo, col_text = st.columns([0.23, 0.77])

        with col_logo:
            st.image("images/avatar.png", width=52)

        with col_text:
            st.markdown("""
                <div class="sidebar-title">Report Tracker</div>
                <div class="sidebar-subtitle">Workspace sécurisé</div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label"> Session active</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-info-card">
            <div class="sidebar-info-label">Utilisateur connecté</div>
            <div class="sidebar-info-value">👤 {st.session_state['display_name']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-info-card">
            <div class="sidebar-info-label">Profil d'accès</div>
            <div class="sidebar-info-value">🛡️ {st.session_state['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sidebar-divider"></div>
        """, unsafe_allow_html=True)

        # Etat modal
        if "show_logout_modal" not in st.session_state:
            st.session_state["show_logout_modal"] = False

        # Bouton logout
        if st.button("⇦ Se déconnecter", key="logout_sidebar"):
            st.session_state["show_logout_modal"] = True
            st.rerun()
            
        import base64

        def get_image_base64(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()

        logo_base64 = get_image_base64("Logo_Africa.png")  # ✅ Racine du projet

        st.sidebar.markdown("---")

        st.sidebar.markdown(
            f"""
            <div style="text-align: center; padding: 15px 10px; font-family: 'Segoe UI', sans-serif;">
                <p style="font-size: 12px; color: #888; margin: 0 0 6px 0; letter-spacing: 0.5px;">
                    Developed by
                </p>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <p style="font-size: 15px; font-weight: 700; color: #0033A0; margin: 0; letter-spacing: 1px;">
                        Ilyass GOTNI
                    </p>
                    <img src="data:image/png;base64,{logo_base64}" style="height: 35px; width: auto; object-fit: contain;"/>
                </div>
                <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 8px 0;">
                <p style="font-size: 10px; color: #aaa; margin: 0; letter-spacing: 0.3px;">
                    © 2026 · All Rights Reserved<br>
                    Unauthorized use prohibited
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
@st.dialog("🔒 Déconnexion")
def show_logout_dialog():
    st.markdown(
        "<p style='text-align:center; color:#475569; font-size:15px;'>"
        "Voulez-vous vraiment vous déconnecter ?</p>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.button("❌ Annuler", key="logout_cancel_dialog", use_container_width=True):
            st.session_state["show_logout_modal"] = False
            st.rerun()
    with c2:
        if st.button("✅ Oui, déconnecter", key="logout_confirm_dialog", use_container_width=True):
            st.session_state["show_logout_modal"] = False
            logout()

def show_topbar():
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">Report Tracker</div>
        <div class="topbar-sub">
            Bienvenue {st.session_state['display_name']} • Rôle : {st.session_state['role']} • Session : {now_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGES
# =========================================================
def show_home():
    show_topbar()

    st.markdown("""
    <h1 style='font-size:46px; font-weight:800; color:#1e3a8a; margin-top:10px;'>
        Welcome to Report Tracker 👋
    </h1>
    <p style='font-size:18px; color:#475569; margin-bottom:24px;'>
        Votre plateforme professionnelle de suivi des missions, budgets, reporting client et analyses de performance.
    </p>
    """, unsafe_allow_html=True)

    st.info("💡 Commencez par importer vos données avant d'accéder aux modules d'analyse.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Statut plateforme</div>
            <div class="metric-value">Active</div>
            <div class="metric-desc">Espace sécurisé opérationnel</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">Utilisateur connecté</div>
            <div class="metric-value">1</div>
            <div class="metric-desc">Session en cours</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Rôle actif</div>
            <div class="metric-value">{st.session_state['role']}</div>
            <div class="metric-desc">Droits appliqués selon le profil</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown("""
        <div class="module-card">
            <div class="module-title">📥 Importation</div>
            <div class="module-text">
                Chargez vos fichiers sources, préparez vos données et alimentez vos tableaux de bord.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.page_link(
            "pages/0_Importation.py",
            label="📥 Étape 1 : Accéder à l'importation",
            use_container_width=True
        )

    with m2:
        st.markdown("""
        <div class="module-card">
            <div class="module-title">📈 Customer report</div>
            <div class="module-text">
                Analysez les indicateurs clients, les budgets, les écarts et les données de performance.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.page_link(
            "pages/1_Customer_report.py",
            label="👉 Accéder au rapport client",
            use_container_width=True
        )
    with m3:
        st.markdown("""
        <div class="module-card">
            <div class="module-title">📈 Mission view</div>
            <div class="module-text">
                Suivez le réalisé, le budget, le reste à faire et les évolutions mission par mission.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.page_link(
            "pages/3_Mission_view.py",
            label="👉 Accéder à la vue mission",
            use_container_width=True
        )
    with m4:
        st.markdown("""
        <div class="module-card">
            <div class="module-title">📈 Synthesis Report</div>
            <div class="module-text">
                Consultez une vision globale par client avec les synthèses des rapports globaux d’activité.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.page_link(
            "pages/Synthesis_Report.py",
            label="👉 Accéder au rapport global client",
            use_container_width=True
        )
    st.markdown("---")
    st.success("🟢 Connexion validée. Vous pouvez naviguer dans les modules autorisés.")

def show_importation():
    show_topbar()
    st.title("Importation")
    st.write("Intègre ici le contenu actuel de ta page Importation.")

def show_customer_report():
    show_topbar()
    st.title("Customer report")
    st.write("Intègre ici le contenu actuel de ta page Customer report.")

def show_mission_view():
    show_topbar()
    st.title("Mission view")
    st.write("Intègre ici le contenu actuel de ta page Mission view.")

def show_synthesis_report():
    show_topbar()
    st.title("Synthesis Report")
    st.write("Intègre ici le contenu actuel de ta page Synthesis Report.")

# =========================================================
# MAIN
# =========================================================
init_session()

if not st.session_state["authenticated"]:
    show_login_page()
    st.stop()

show_sidebar()
if st.session_state.get("show_logout_modal", False):
    show_logout_dialog()

page = st.session_state["current_page"]

show_home()
