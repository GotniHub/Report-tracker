import streamlit as st
import pandas as pd
import time
from app import require_auth

st.set_page_config(page_title="Importation", page_icon="📊", layout="wide")
st.logo("Logo_Advent.png", icon_image="Logom.png")
require_auth()
# if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
#     st.warning("Veuillez vous connecter.")
#     st.stop()
# if not st.session_state.get("authenticated", False):
#     st.switch_page("app.py")  # 🔥 redirection auto    
st.markdown("""
<style>
/* =========================
   GLOBAL / BACKGROUND
========================= */
header[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stDecoration"] {
    display: none !important;
}
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 22%),
        radial-gradient(circle at 80% 18%, rgba(147, 197, 253, 0.16), transparent 20%),
        radial-gradient(circle at 50% 75%, rgba(96, 165, 250, 0.10), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #eef4ff 52%, #e9f0fb 100%);
    min-height: 100vh;
}

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

[data-testid="stAppViewContainer"] > [data-testid="stMain"] {
    position: relative;
    z-index: 1;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* =========================
   IMPORT PAGE
========================= */
.import-hero {
    margin-top: 8px;
    margin-bottom: 24px;
}

.import-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(37, 99, 235, 0.10);
    color: #1d4ed8;
    border: 1px solid rgba(37, 99, 235, 0.18);
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 16px;
}

.import-title {
    font-size: 44px;
    font-weight: 800;
    line-height: 1.08;
    color: #0f172a;
    margin-bottom: 12px;
}

.import-subtitle {
    font-size: 17px;
    color: #475569;
    line-height: 1.7;
    max-width: 900px;
    margin-bottom: 18px;
}

.import-toolbar,
.import-upload-card,
.preview-card,
.info-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 22px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
    backdrop-filter: blur(10px);
}

.import-toolbar {
    padding: 18px 20px;
    margin-bottom: 18px;
}

.import-upload-card {
    padding: 22px;
    margin-bottom: 22px;
}

.preview-card {
    padding: 18px;
    margin-top: 18px;
}

.info-card {
    padding: 18px 20px;
    margin-bottom: 18px;
}

.section-title {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 6px;
}

.section-subtitle {
    font-size: 14px;
    color: #64748b;
    margin-bottom: 14px;
}

.kpi-mini {
    background: rgba(255,255,255,0.75);
    border: 1px solid rgba(226,232,240,0.95);
    border-radius: 18px;
    padding: 16px 18px;
    box-shadow: 0 8px 20px rgba(15,23,42,0.04);
}

.kpi-mini-title {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 8px;
}

.kpi-mini-value {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
}

.kpi-mini-desc {
    font-size: 13px;
    color: #475569;
    margin-top: 6px;
}

.dataframe-title {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

/* Inputs / boutons */
div[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.78);
    border: 1px dashed #93c5fd;
    border-radius: 18px;
    padding: 10px;
}

div.stButton > button,
div[data-testid="stDownloadButton"] > button {
    border-radius: 14px;
    padding: 0.75rem 1rem;
    font-weight: 700;
    border: none;
    background: linear-gradient(90deg, #1d4ed8, #2563eb);
    color: white;
    box-shadow: 0 10px 20px rgba(37,99,235,0.18);
}

div.stButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(90deg, #1e40af, #1d4ed8);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HELPERS
# =========================================================
def load_sheets(file):
    """Charge les feuilles nécessaires depuis un fichier Excel."""
    excel_data = pd.ExcelFile(file)
    data_plan_prod = excel_data.parse("Data Plan Prod")
    data_float = excel_data.parse("Data Float")
    rates = excel_data.parse("Rates", header=1)
    return data_plan_prod, data_float, rates


def preprocess_data(data_plan_prod, data_float, rates):
    """Nettoyage et transformation des données."""
    data_plan_prod = data_plan_prod.rename(columns={
        "Montant Devis": "Budget (PV)",
    })

    data_float = data_float.rename(columns={
        "Code Territoire": "Code Territoire",
        "Logged Billable hours": "Heures facturées",
        "Logged Non-billable hours": "Heures non facturées",
        "Logged fee": "Coût"
    })

    rates = rates.rename(columns={"Nom complet": "Acteur"})

    data_plan_prod["Code Mission"] = data_plan_prod["Nom de la mission"].str.extract(r"\[(\w+)\]")
    data_float["Code Mission"] = data_float["Nom de la mission"].str.extract(r"\[(\w+)\]")

    data_plan_prod["Code Mission"] = data_plan_prod["Code Mission"].fillna("Unknown")
    data_float["Code Mission"] = data_float["Code Mission"].fillna("Unknown")

    def add_unique_identifier(row, idx):
        if row["Code Mission"] == "Unknown":
            return f"Unknown-{idx}"
        return row["Code Mission"]

    data_plan_prod["Code Mission"] = [
        add_unique_identifier(row, idx) for idx, row in data_plan_prod.iterrows()
    ]
    data_float["Code Mission"] = [
        add_unique_identifier(row, idx) for idx, row in data_float.iterrows()
    ]

    data_plan_prod["Nom de la mission"] = data_plan_prod.apply(
        lambda row: f"[{row['Code Mission']}] {row['Nom de la mission']}"
        if f"[{row['Code Mission']}]" not in row["Nom de la mission"] else row["Nom de la mission"],
        axis=1
    )

    data_float["Nom de la mission"] = data_float.apply(
        lambda row: f"[{row['Code Mission']}] {row['Nom de la mission']}"
        if f"[{row['Code Mission']}]" not in row["Nom de la mission"] else row["Nom de la mission"],
        axis=1
    )

    data_plan_prod["Budget (PV)"] = pd.to_numeric(
        data_plan_prod["Budget (PV)"], errors="coerce"
    ).fillna(0)

    data_float["Heures facturées"] = pd.to_numeric(
        data_float["Heures facturées"], errors="coerce"
    ).fillna(0)

    data_float["Heures non facturées"] = pd.to_numeric(
        data_float["Heures non facturées"], errors="coerce"
    ).fillna(0)

    data_float["Coût"] = pd.to_numeric(
        data_float["Coût"], errors="coerce"
    ).fillna(0)

    data_float["Total Hours"] = data_float["Heures facturées"] + data_float["Heures non facturées"]

    real_days = data_float.groupby("Code Mission")["Total Hours"].sum().reset_index()
    real_days["Real Days Worked"] = real_days["Total Hours"] / 8

    merged_data = pd.merge(
        data_plan_prod,
        real_days,
        on="Code Mission",
        how="left"
    )

    return data_plan_prod, data_float, merged_data, rates

# =========================================================
# UI
# =========================================================
from app import require_auth
from ui import inject_shared_css, show_sidebar

inject_shared_css()
show_sidebar()
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
st.markdown("""
<div class="import-hero">
    <div class="import-badge">📂 Data Intake • Import Workspace</div>
    <div class="import-title">Importation des données</div>
    <div class="import-subtitle">
        Chargez votre fichier source, contrôlez les feuilles attendues et préparez les données
        pour l’analyse <b>Budget vs Réel</b> dans un environnement propre, lisible et professionnel.
    </div>
</div>
""", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class="kpi-mini">
        <div class="kpi-mini-title">Format attendu</div>
        <div class="kpi-mini-value">XLSX</div>
        <div class="kpi-mini-desc">Template standardisé Report Tracker</div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class="kpi-mini">
        <div class="kpi-mini-title">Feuilles attendues</div>
        <div class="kpi-mini-value">3</div>
        <div class="kpi-mini-desc">Data Plan Prod, Data Float, Rates</div>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class="kpi-mini">
        <div class="kpi-mini-title">Objectif</div>
        <div class="kpi-mini-value">Budget / Réel</div>
        <div class="kpi-mini-desc">Préparation des données avant restitution</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="import-toolbar">
    <div class="section-title">Modèle de données</div>
    <div class="section-subtitle">
        Téléchargez le fichier modèle avant import si vous souhaitez respecter la structure attendue.
    </div>
</div>
""", unsafe_allow_html=True)

with open("CustomerReport_Template.xlsx", "rb") as template_file:
    template_data = template_file.read()

st.download_button(
    label="📥 Télécharger le modèle de données",
    data=template_data,
    file_name="CustomerReport_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="import-upload-card">
    <div class="section-title">Zone d’importation</div>
    <div class="section-subtitle">
        Importez votre fichier Excel pour lancer automatiquement le chargement,
        le prétraitement et la préparation des tables nécessaires.
    </div>
</div>
""", unsafe_allow_html=True)

if "reset_import" not in st.session_state:
    st.session_state["reset_import"] = False

if st.session_state["reset_import"]:
    keys_to_remove = [
        "uploaded_file", "data_plan_prod", "data_float", "merged_data", "rates"
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["reset_import"] = False
    st.rerun()

uploaded_file = st.file_uploader(
    "Importer un fichier Excel",
    type=["xlsx"],
    help="Le fichier doit contenir les feuilles Data Plan Prod, Data Float et Rates."
)

if uploaded_file:
    try:
        with st.spinner("📥 Chargement et traitement des données en cours..."):
            data_plan_prod, data_float, rates = load_sheets(uploaded_file)
            data_plan_prod, data_float, merged_data, rates = preprocess_data(
                data_plan_prod, data_float, rates
            )

            st.session_state["uploaded_file"] = uploaded_file
            st.session_state["data_plan_prod"] = data_plan_prod
            st.session_state["data_float"] = data_float
            st.session_state["merged_data"] = merged_data
            st.session_state["rates"] = rates

        st.success("✅ Fichier importé et traité avec succès.")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(f"""
            <div class="kpi-mini">
                <div class="kpi-mini-title">Lignes Plan Prod</div>
                <div class="kpi-mini-value">{len(data_plan_prod)}</div>
                <div class="kpi-mini-desc">Données budget</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div class="kpi-mini">
                <div class="kpi-mini-title">Lignes Float</div>
                <div class="kpi-mini-value">{len(data_float)}</div>
                <div class="kpi-mini-desc">Données réel</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
            <div class="kpi-mini">
                <div class="kpi-mini-title">Lignes Rates</div>
                <div class="kpi-mini-value">{len(rates)}</div>
                <div class="kpi-mini-desc">PV intervenants</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class="kpi-mini">
                <div class="kpi-mini-title">Données fusionnées</div>
                <div class="kpi-mini-value">{len(merged_data)}</div>
                <div class="kpi-mini-desc">Prêtes pour analyse</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Aperçu des données", "Actions"])

        with tab1:
            st.markdown('<div class="preview-card">', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-title">📊 Données Plan Prod (Budget)</div>', unsafe_allow_html=True)
            st.dataframe(data_plan_prod.head(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="preview-card">', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-title">🧾 Données Float (Réel)</div>', unsafe_allow_html=True)
            st.dataframe(data_float.head(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="preview-card">', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-title">💶 Données Rates (PV intervenants)</div>', unsafe_allow_html=True)
            st.dataframe(rates.head(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="preview-card">', unsafe_allow_html=True)
            st.markdown('<div class="dataframe-title">🔗 Données fusionnées</div>', unsafe_allow_html=True)
            st.dataframe(merged_data.head(), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown("""
            <div class="info-card">
                <div class="section-title">Actions disponibles</div>
                <div class="section-subtitle">
                    Réinitialisez l’import en cas de changement de fichier ou de retraitement complet.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("♻️ Réinitialiser l'importation", use_container_width=True):
                st.session_state["reset_import"] = True
                st.toast("✅ Les données ont été réinitialisées.", icon="✅")
                time.sleep(1)
                st.rerun()

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement des données : {e}")