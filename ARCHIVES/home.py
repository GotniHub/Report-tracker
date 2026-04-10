import streamlit as st
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="Report Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CONFIG / STYLE
# =========================================================
st.markdown("""
<style>
/* Global */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f5f7fb 0%, #eef2ff 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}

/* Login wrapper */
.login-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding-top: 20px;
}

/* Left branding panel */
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
}

.brand-card-text {
    font-size: 14px;
    color: rgba(255,255,255,0.85);
}

/* Login card */
.login-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 24px;
    padding: 36px 32px;
    min-height: 620px;
    box-shadow: 0 20px 40px rgba(15, 23, 42, 0.10);
    backdrop-filter: blur(14px);
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

/* Inputs */
div[data-testid="stTextInput"] input {
    border-radius: 12px !important;
    border: 1px solid #cbd5e1 !important;
    padding: 12px 14px !important;
}

div[data-testid="stTextInput"] input:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 1px #2563eb !important;
}

/* Buttons */
div.stButton > button {
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

div.stButton > button:hover {
    background: linear-gradient(90deg, #1e40af, #1d4ed8);
    color: white;
}

/* Top app bar helpers */
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
</style>
""", unsafe_allow_html=True)


# =========================================================
# AUTH HELPERS
# =========================================================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Base locale simple
# Plus tard tu pourras déplacer ça dans un Excel / JSON / base SQL
USERS = {
    "admin": {
        "name": "Administrateur",
        "password": hash_password("Admin123!"),
        "role": "Admin"
    },
    "ilyass": {
        "name": "Ilyass",
        "password": hash_password("Ilyass123!"),
        "role": "Manager"
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
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def authenticate(username: str, password: str):
    username = username.strip().lower()
    if username in USERS:
        hashed = hash_password(password)
        if USERS[username]["password"] == hashed:
            return True, USERS[username]
    return False, None


def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.session_state["display_name"] = ""
    st.session_state["role"] = ""
    st.session_state["current_page"] = "home"
    st.rerun()


# =========================================================
# LOGIN PAGE
# =========================================================
def show_login_page():
    col_left, col_right = st.columns([1.15, 0.85], gap="large")

    with col_left:
        st.markdown("""
        <div class="brand-panel">
            <div class="brand-badge">Secure Workspace • Report Tracker</div>
            <div class="brand-title">Pilotage intelligent des missions, budgets et performances.</div>
            <div class="brand-subtitle">
                Connectez-vous à <b>Report Tracker</b> pour accéder à vos espaces de reporting,
                d'importation, de suivi mission et d'analyse client dans une interface professionnelle.
            </div>

            <div class="brand-card">
                <div class="brand-card-title">📊 Vision centralisée</div>
                <div class="brand-card-text">
                    Suivez les budgets, le réalisé, les écarts et les indicateurs clés dans un seul outil.
                </div>
            </div>

            <div class="brand-card">
                <div class="brand-card-title">🔐 Accès sécurisé</div>
                <div class="brand-card-text">
                    Gestion des utilisateurs, rôles et contrôle d'accès avant l'entrée dans l'application.
                </div>
            </div>

            <div class="brand-card">
                <div class="brand-card-title">⚡ Expérience professionnelle</div>
                <div class="brand-card-text">
                    Interface moderne conçue pour les équipes opérationnelles, finance et pilotage.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="login-card">
            <div class="login-title">Welcome to Report Tracker</div>
            <div class="login-subtitle">
                Entrez vos identifiants pour accéder à l'environnement de reporting.
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Identifiant", placeholder="Ex. ilyass")
            password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
            submitted = st.form_submit_button("Se connecter")

        if submitted:
            ok, user = authenticate(username, password)
            if ok:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username.strip().lower()
                st.session_state["display_name"] = user["name"]
                st.session_state["role"] = user["role"]
                st.success(f"Connexion réussie. Bienvenue {user['name']} 👋")
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect.")

        st.markdown("""
            <div class="security-box">
                <div class="security-title">Sécurité</div>
                <div style="color:#475569; font-size:14px;">
                    Cette zone est réservée aux utilisateurs autorisés de l’outil Report Tracker.
                </div>
            </div>
            <div class="footer-note">
                Report Tracker • Secure Access Portal
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# APP CONTENT
# =========================================================
def show_sidebar():
    with st.sidebar:
        st.markdown("## Report Tracker")
        st.caption(f"Connecté : {st.session_state['display_name']}")
        st.caption(f"Rôle : {st.session_state['role']}")
        st.markdown("---")

        pages = ["home", "Importation", "Customer report", "Mission view", "Synthesis Report"]
        page = st.radio("Navigation", pages, index=pages.index(st.session_state.get("current_page", "home")))
        st.session_state["current_page"] = page

        st.markdown("---")
        if st.button("Se déconnecter"):
            logout()


def show_topbar():
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">Report Tracker</div>
        <div class="topbar-sub">
            Bienvenue {st.session_state['display_name']} • Rôle : {st.session_state['role']} • Dernière connexion : {now_str}
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_home():
    show_topbar()
    st.markdown("""
    <h1 style='font-size: 46px; font-weight: 800; color: #1e3a8a; margin-top: 10px;'>
        Welcome to Report Tracker 👋
    </h1>
    <p style='font-size: 18px; color: #475569; margin-bottom: 24px;'>
        Votre plateforme professionnelle de suivi des missions, budgets, reporting client et analyses de performance.
    </p>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**Importation**\n\nChargez et préparez vos données sources.")
    with c2:
        st.info("**Customer report**\n\nAnalysez les indicateurs de vos clients.")
    with c3:
        st.info("**Mission view**\n\nSuivez budget, réalisé et écarts par mission.")

    st.markdown("---")
    st.success("Espace sécurisé actif. Vous pouvez maintenant accéder aux modules autorisés.")


def show_importation():
    show_topbar()
    st.subheader("Importation")
    st.write("Ici tu mets le contenu actuel de ta page Importation.")


def show_customer_report():
    show_topbar()
    st.subheader("Customer report")
    st.write("Ici tu mets le contenu actuel de ta page Customer report.")


def show_mission_view():
    show_topbar()
    st.subheader("Mission view")
    st.write("Ici tu mets le contenu actuel de ta page Mission view.")


def show_synthesis_report():
    show_topbar()
    st.subheader("Synthesis Report")
    st.write("Ici tu mets le contenu actuel de ta page Synthesis Report.")


# =========================================================
# MAIN
# =========================================================
init_session()

if not st.session_state["authenticated"]:
    show_login_page()
else:
    show_sidebar()

    page = st.session_state["current_page"]

    if page == "home":
        show_home()
    elif page == "Importation":
        show_importation()
    elif page == "Customer report":
        show_customer_report()
    elif page == "Mission view":
        show_mission_view()
    elif page == "Synthesis Report":
        show_synthesis_report()