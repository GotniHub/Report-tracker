import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import re
import locale
import os
from auth import require_auth
require_auth()
try:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
except locale.Error:
    pass
st.logo("Logo_Advent.png", icon_image="Logom.png")
# (garde ton CSS ici comme tu l'as déjà)
# st.markdown(""" <style> ... </style> """, unsafe_allow_html=True)
# Injecter le CSS pour les cards
st.markdown("""
    <style>
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
    .card-container {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
    }
    .title {
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 20px;
        color: #333;
    }
    .card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.94) 100%);
        border: 1px solid rgba(226, 232, 240, 0.95);
        border-radius: 22px;
        padding: 24px 22px;
        text-align: center;
        flex: 1;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        backdrop-filter: blur(10px);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    /* halo léger dans la card */
    .card::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at top right, rgba(59,130,246,0.12), transparent 35%);
        pointer-events: none;
    }

    /* ligne brillante en haut */
    .card::after {
        content: "";
        position: absolute;
        top: 0;
        left: 18px;
        right: 18px;
        height: 4px;
        border-radius: 999px;
        background: linear-gradient(90deg, #60a5fa, #2563eb, #1d4ed8);
        opacity: 0.9;
    }

    /* effet dynamique */
    .card:hover {
        transform: translateY(-6px);
        border-color: rgba(37, 99, 235, 0.25);
        box-shadow: 0 18px 40px rgba(37, 99, 235, 0.14);
    }

    /* chiffre principal */
    .metric {
        position: relative;
        z-index: 1;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.03em;
        margin-bottom: 8px;
    }

    /* libellé */
    .label {
        position: relative;
        z-index: 1;
        font-size: 1rem;
        font-weight: 500;
        color: #64748b;
        margin-bottom: 10px;
    }

    /* delta */
    .delta {
        position: relative;
        z-index: 1;
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 6px;
        background: rgba(15, 23, 42, 0.04);
    }

    .positive {
        color: #15803d;
        background: rgba(34, 197, 94, 0.12);
    }

    .negative {
        color: #dc2626;
        background: rgba(239, 68, 68, 0.12);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ✅ Box 3D identique à Customer Report */
.mission-box{
  border: 2px solid #0033A0;
  border-radius: 12px;
  overflow: hidden;                 
  background: #fff;
  box-shadow: 0 10px 18px rgba(0, 0, 0, 0.45);
  display: inline-block;
}

/* ✅ Table : supprime espace blanc inutile */
.mission-box table{
  border-collapse: collapse;
  width: 420px;
  font-size: 1rem;
  margin: 0 !important;
}

.mission-box td{
  border: 1px solid #cfcfcf;
  padding: 12px 14px;
  font-weight: bold;
  line-height: 1.1;          /* ✅ enlève l’espace vertical */
  vertical-align: middle;    /* ✅ centre le contenu */
}

/* ✅ Colonne labels (comme ancien) */
.mission-box td:nth-child(1){
  background-color: rgba(0, 51, 160, 0.20);
  color: black;
  text-align: left;
  width: 55%;
}

/* ✅ Colonne valeurs */
.mission-box td:nth-child(2){
  background-color: #E6E7E8;
  color: black;
  text-align: right;
}
</style>
""", unsafe_allow_html=True)

# ✅ Mapping Entreprise (Rates) -> fichier logo (dans ton root)
COMPANY_LOGO_MAP = {
    "Advent +": "Logo_Advent.png",
    "Advent+": "Logo_Advent.png",
    "Advent": "Logo_Advent.png",

    "Adventae": "Logo_Adventae.png",

    "Advent + Africa": "Logo_Africa.jpg",
    "Advent+ Africa": "Logo_Africa.jpg",
    "Advent Africa": "Logo_Africa.jpg",
    "Africa": "Logo_Africa.jpg",

    "Adventage Sud": "Logo_Adventage_Sud.png",
    "Advantage": "Logo_Adventage_Sud.png",

    # optionnel si tu as des partenaires
    "Partner": "Logo_Partner.png",
}

DEFAULT_LOGO = "Logo_Advent.png"  # fallback (ou "Logom.png")


def normalize_company(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip()
    s = " ".join(s.split())  # supprime espaces doubles
    return s


def get_actor_company(rates: pd.DataFrame, actor_name: str) -> str:
    """Retourne Entreprise de l'acteur depuis Rates."""
    if rates is None or rates.empty:
        return ""

    r = rates.copy()
    r.columns = r.columns.str.strip()

    if "Acteur" not in r.columns or "Entreprise" not in r.columns:
        return ""

    actor_name = str(actor_name).strip()
    m = r["Acteur"].astype(str).str.strip() == actor_name
    if not m.any():
        return ""

    comp = r.loc[m, "Entreprise"].iloc[0]
    return normalize_company(comp)


def get_logo_path_for_company(company: str) -> str:
    """Trouve le fichier logo selon Entreprise."""
    company = normalize_company(company)

    filename = COMPANY_LOGO_MAP.get(company, DEFAULT_LOGO)

    # Comme tes logos sont dans le root, pas besoin de dossier
    if os.path.exists(filename):
        return filename

    # fallback 1
    if os.path.exists(DEFAULT_LOGO):
        return DEFAULT_LOGO

    # fallback 2 (au cas où)
    if os.path.exists("Logom.png"):
        return "Logom.png"

    return ""  # si rien trouvé


def show_company_logo_for_actor(rates: pd.DataFrame, actor_name: str, width: int = 220):
    company = get_actor_company(rates, actor_name)
    logo_path = get_logo_path_for_company(company)

    if logo_path:
        st.image(logo_path, width=width)
    else:
        # si aucun fichier trouvé, on n'affiche rien (pas d'erreur)
        st.write("")

def color_ecart(val):
    """
    Colore en rouge si négatif, vert si positif.
    Rouge/vert clair (pas trop foncé).
    """
    try:
        # Nettoyage (enlève € et %)
        v = str(val).replace("€", "").replace("%", "").replace(" ", "").strip()
        v = float(v)

        if v < 0:
            return "color: #d62728;"  # rouge clair
        elif v > 0:
            return "color: #2ca02c;"  # vert clair
        else:
            return ""
    except:
        return ""
    
def style_budget_tables(row):

    styles = []

    for col in row.index:

        s = ""

        # Code mission / nom mission
        if col in ["Code Mission", "Nom de la mission"]:
            s += "background-color:#E6E7E8;"

        # Budget annuel
        elif "Budget Annuel" in col:
            s += "background-color: rgba(100, 130, 160, 0.35); font-weight:bold;"

        # Restant cumulé
        elif "Restant Cumulé" in col:
            s += "background-color: rgba(100, 130, 160, 0.35); font-weight:bold;"

        # Budget mensuel
        elif "Budget" in col and "Annuel" not in col:
            s += "background-color: rgba(222, 184, 135, 0.35);"

        # Réalisé / Produit 
        elif "Réalisé" in col or "Produit" in col:
            s += "background-color:rgba(46,125,50,0.35);"

        # Restant
        elif "Restant" in col:
            s += "background-color: rgba(255, 193, 7, 0.35);"

        styles.append(s)

    return styles

# =========================================================
# ✅ NOUVELLE PAGE : VUE ACTEUR (Intervenant -> Ses missions)
# =========================================================

def display_actor_report(data_plan_prod, data_float, rates, acteur_filter, selected_missions, pv_acteur):
    # -----------------------
    # ✅ Préparations / sécurités
    # -----------------------
    data_plan_prod = data_plan_prod.copy()
    data_float = data_float.copy()
    rates = rates.copy()

    data_plan_prod.columns = data_plan_prod.columns.str.strip()
    data_float.columns = data_float.columns.str.strip()
    rates.columns = rates.columns.str.strip()

    # Date
    if "Date" in data_float.columns:
        data_float["Date"] = pd.to_datetime(data_float["Date"], errors="coerce")
    else:
        st.error("Colonne 'Date' manquante dans Data Float.")
        st.stop()

    # 🔹 Sécuriser Code Mission (évite problèmes int/str)
    data_float["Code Mission"] = data_float["Code Mission"].astype(str).str.strip()
    data_plan_prod["Code Mission"] = data_plan_prod["Code Mission"].astype(str).str.strip()

    # Renommer colonnes float si FR
    if "Heures facturées" in data_float.columns:
        data_float = data_float.rename(columns={"Heures facturées": "Logged Billable hours"})
    if "Heures non facturées" in data_float.columns:
        data_float = data_float.rename(columns={"Heures non facturées": "Logged Non-billable hours"})

    if "Logged Billable hours" not in data_float.columns:
        data_float["Logged Billable hours"] = 0

    data_float["Logged Billable hours"] = pd.to_numeric(data_float["Logged Billable hours"], errors="coerce").fillna(0)

    # Mois (si tu réutilises des graphes)
    data_float["Mois"] = data_float["Date"].dt.strftime("%Y-%m")

    # -----------------------
    # ✅ Filtre principal : acteur
    # -----------------------
    filtered_float = data_float[data_float["Acteur"].astype(str).str.strip() == str(acteur_filter).strip()].copy()

    if filtered_float.empty:
        st.warning("Aucune donnée FLOAT pour cet intervenant.")
        st.stop()

    if selected_missions:
        filtered_float = filtered_float[
            filtered_float["Code Mission"].isin([str(x).strip() for x in selected_missions])
        ].copy()


    if filtered_float.empty:
        st.warning("Aucune donnée FLOAT après filtre missions.")
        st.stop()

    # -----------------------
    # ✅ Filtre période (sur FLOAT)
    # -----------------------
    date_min = filtered_float["Date"].min()
    date_max = filtered_float["Date"].max()

    date_debut = st.sidebar.date_input("📅 Date Début", value=date_min)
    date_fin = st.sidebar.date_input("📅 Date Fin", value=date_max)

    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)

    filtered_float = filtered_float[(filtered_float["Date"] >= date_debut) & (filtered_float["Date"] <= date_fin)].copy()

    if filtered_float.empty:
        st.warning("⚠️ Aucune donnée disponible pour la période sélectionnée.")
        st.stop()

    # ✅ Filtrer FINANCE (plan prod) sur les missions sélectionnées (union budget/réalisé)
    missions_acteur = [str(x).strip() for x in (selected_missions if selected_missions else [])]

    if missions_acteur:
        filtered_plan = data_plan_prod[data_plan_prod["Code Mission"].isin(missions_acteur)].copy()
    else:
        filtered_plan = data_plan_prod.copy()
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
    # -----------------------
    # ✅ Calculs globaux acteur
    # -----------------------
    filtered_float["Réalisé (Jour)"] = filtered_float["Logged Billable hours"] / 8
    jours_realises_total = filtered_float["Réalisé (Jour)"].sum()
    ca_engage_total = jours_realises_total * pv_acteur

    # Budget jours (depuis FINANCE) = somme colonne acteur_filter
    if acteur_filter not in filtered_plan.columns:
        st.error(f"⚠️ La colonne acteur '{acteur_filter}' n'existe pas dans Data Plan Prod.")
        st.write("Colonnes plan prod:", filtered_plan.columns.tolist())
        st.stop()

    tmp_plan = filtered_plan.copy()
    tmp_plan[acteur_filter] = pd.to_numeric(tmp_plan[acteur_filter], errors="coerce").fillna(0)

    jours_budget_total = tmp_plan[acteur_filter].sum()
    ca_budget_total = jours_budget_total * pv_acteur

    solde_ca = ca_budget_total - ca_engage_total
    pct_used = (ca_engage_total / ca_budget_total * 100) if ca_budget_total > 0 else 0
    pct_remaining = (solde_ca / ca_budget_total * 100) if ca_budget_total > 0 else 0


    # -----------------------
    # ✅ En-tête
    # -----------------------
    st.markdown("<div class='title'><b>Tableau de bord - Vue Intervenant</b></div>", unsafe_allow_html=True)
        # ✅ logo selon entreprise de l'acteur
    show_company_logo_for_actor(rates, acteur_filter, width=260)
    # nb missions où l'acteur a du réalisé (jours > 0 via FLOAT)
    nb_missions_realise = filtered_float.loc[filtered_float["Réalisé (Jour)"] > 0, "Code Mission"].nunique()

    # nb missions où l'acteur a du budget (jours budget > 0 via PLAN PROD)
    tmp_plan_cnt = filtered_plan.copy()
    tmp_plan_cnt[acteur_filter] = pd.to_numeric(tmp_plan_cnt[acteur_filter], errors="coerce").fillna(0)
    nb_missions_budget = tmp_plan_cnt.loc[tmp_plan_cnt[acteur_filter] > 0, "Code Mission"].nunique()

    # Affichage des informations sous forme de tableau stylisé
    col1,col2,col3 = st.columns(3) 
    with col1: 
        st.markdown(f"""
        <div class="mission-box">
        <table>
            <tr><td>Intervenant</td><td>{acteur_filter}</td></tr>
            <tr><td>Nbr. Missions intervenues</td><td>{nb_missions_realise}</td></tr>
            <tr><td>Nbr. Missions budgétées</td><td>{nb_missions_budget}</td></tr>
            <tr><td>Facturation Journalière</td><td>{int(round(pv_acteur,0)):,} €</td></tr>
        </table>
        </div>
        """.replace(",", " "), unsafe_allow_html=True)


    with col2 : 
        st.write("")
    with col3 : 
        # 🔥 Créer l'affichage de la période en "Mois Année"
        mois_debut = date_debut.strftime("%d %B %Y").capitalize()
        mois_fin = date_fin.strftime("%d %B %Y").capitalize()

        # 🎨 CSS stylisé avec effet 3D
        st.markdown("""
            <style>
            .periode-container {
                border: 2px solid #0033A0;
                border-radius: 15px;
                padding: 15px 25px;
                margin-top: 20px;
                margin-bottom: 20px;
                background-color: #E6E7E8;
                box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5);
                display: inline-block;
            }
            .periode-text {
                font-size: 1.2rem;
                font-weight: bold;
                color: #333;
                text-align: center;
            }
            .periode-date {
                color: #0033A0;
                font-size: 1.3rem;
                font-weight: bold;
                margin-top: 5px;
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # 💬 Affichage
        st.markdown(f"""
            <div class="periode-container">
                <div class="periode-text">📅 Période sélectionnée :</div>
                <div class="periode-date">{mois_debut} - {mois_fin}</div>
            </div>
        """, unsafe_allow_html=True)

    # -----------------------
    # ✅ CARDS Budget
    # -----------------------
    def get_delta_class(x):
        return "positive" if x >= 0 else "negative"

    st.subheader("Budget (Intervenant)")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{ca_budget_total:,.0f} €</div>
                <div class="label">CA Budget</div>
                <div class="delta positive">100%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{ca_engage_total:,.0f} €</div>
                <div class="label">CA Produit (CA Engagé)</div>
                <div class="delta {get_delta_class(pct_used)}">{pct_used:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{solde_ca:,.0f} €</div>
                <div class="label">Solde restant</div>
                <div class="delta {get_delta_class(pct_remaining)}">{pct_remaining:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # ✅ CARDS Jours
    # -----------------------
    jours_restants = jours_budget_total - jours_realises_total
    pct_jours = (jours_realises_total / jours_budget_total * 100) if jours_budget_total > 0 else 0
    pct_jours_restants = 100 - pct_jours

    st.subheader("Jours (Intervenant)")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_budget_total:.1f} jours</div>
                <div class="label">Jours Budget</div>
                <div class="delta positive">100%</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_realises_total:.1f} jours</div>
                <div class="label">Jours Réalisés</div>
                <div class="delta positive">{pct_jours:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_restants:.1f} jours</div>
                <div class="label">Jours Restants</div>
                <div class="delta {get_delta_class(jours_restants)}">{pct_jours_restants:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{pct_jours:.1f}%</div>
                <div class="label">Avancement</div>
                <div class="delta {'negative' if pct_jours >= 100 else 'positive'}">- {jours_restants:.1f} j restants</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------
    # ✅ TABLE EXCEL-LIKE : PAR MISSION
    # -----------------------
    st.subheader("Détails généraux Budget annuel par mission")

    # --- Budget par mission (depuis FINANCE)
    df_budget_mission = (
        tmp_plan.groupby(["Code Mission", "Nom de la mission"], as_index=False)[acteur_filter]
        .sum()
        .rename(columns={acteur_filter: "Budget (Jour)"})
    )

    # --- Réalisé par mission (depuis FLOAT)
    df_real_mission = (
        filtered_float.groupby("Code Mission", as_index=False)
        .agg(**{
            "Heures": ("Logged Billable hours", "sum"),
            "Réalisé (Jour)": ("Réalisé (Jour)", "sum"),
        })
    )

    # Merge
    df = df_budget_mission.merge(df_real_mission, on="Code Mission", how="left")
    df["Nom de la mission"] = df["Nom de la mission"].fillna("")
    df["Budget (Jour)"] = pd.to_numeric(df["Budget (Jour)"], errors="coerce").fillna(0)
    df["Réalisé (Jour)"] = pd.to_numeric(df["Réalisé (Jour)"], errors="coerce").fillna(0)
    df["Heures"] = pd.to_numeric(df["Heures"], errors="coerce").fillna(0)
    # ✅ Supprimer les missions où Budget = 0 ET Réalisé = 0
    df = df[~(
        (df["Budget (Jour)"] == 0) &
        (df["Réalisé (Jour)"] == 0)
    )]

    # PV constant
    df["PV"] = pv_acteur

    # écarts jours
    df["Ecart (Jour)"] = df["Budget (Jour)"] - df["Réalisé (Jour)"] 
    df["Ecart % (Jour)"] = df.apply(lambda r: (r["Ecart (Jour)"] / r["Budget (Jour)"] * 100) if r["Budget (Jour)"] > 0 else 0, axis=1)

    # CA
    df["CA Budget"] = df["Budget (Jour)"] * df["PV"]
    df["CA Produit"] = df["Réalisé (Jour)"] * df["PV"]  # = CA Engagé
    df["Ecart"] =  df["CA Budget"] - df["CA Produit"]
    df["Ecart %"] = df.apply(lambda r: (r["Ecart"] / r["CA Budget"] * 100) if r["CA Budget"] > 0 else 0, axis=1)

    # Totaux
    budget_j_total = df["Budget (Jour)"].sum()
    realise_j_total = df["Réalisé (Jour)"].sum()
    ecart_j_total = budget_j_total - realise_j_total

    ca_budget_total = df["CA Budget"].sum()
    ca_facture_total = df["CA Produit"].sum()
    ecart_ca_total = ca_budget_total - ca_facture_total

    total = {
        "Code Mission": "TOTAL",
        "Nom de la mission": "",
        "Budget (Jour)": budget_j_total,
        "Réalisé (Jour)": realise_j_total,
        "Heures": df["Heures"].sum(),
        "Ecart (Jour)": ecart_j_total,
        "Ecart % (Jour)": (ecart_j_total / budget_j_total * 100) if budget_j_total > 0 else 0,
        "PV": "",
        "CA Budget": ca_budget_total,
        "CA Produit": ca_facture_total,
        "Ecart": ecart_ca_total,
        "Ecart %": (ecart_ca_total / ca_budget_total * 100) if ca_budget_total > 0 else 0,
    }
    df = pd.concat([df, pd.DataFrame([total])], ignore_index=True)

    # -----------------------
    # ✅ Formatage affichage (comme ton format clean)
    # -----------------------
    def fmt_num(x):
        try:
            x = float(x)
            if pd.isna(x):
                return ""
            return f"{x:.2f}".rstrip("0").rstrip(".")
        except:
            return x

    def fmt_eur(x):
        try:
            return f"{int(round(float(x), 0)):,.0f} €".replace(",", " ")
        except:
            return x

    def fmt_pct(x):
        try:
            return f"{int(round(float(x), 0))}%"
        except:
            return x

    df_display = df.copy()

    for c in ["Budget (Jour)", "Réalisé (Jour)", "Heures", "Ecart (Jour)"]:
        df_display[c] = df_display[c].apply(fmt_num)

    for c in ["PV", "CA Budget", "CA Produit", "Ecart"]:
        df_display[c] = df_display[c].apply(fmt_eur)

    for c in ["Ecart % (Jour)", "Ecart %"]:
        df_display[c] = df_display[c].apply(fmt_pct)

    cols_order = [
        "Code Mission",
        "Nom de la mission",
        "Budget (Jour)",
        "Réalisé (Jour)",
        "Heures",
        "Ecart (Jour)",
        "Ecart % (Jour)",
        "PV",
        "CA Budget",
        "CA Produit",
        "Ecart",
        "Ecart %",
    ]
    df_display = df_display[cols_order]

    def style_excel_like(row):
        styles = []
        is_total = (row["Code Mission"] == "TOTAL")
        for col in df_display.columns:
            s = ""
            if is_total:
                s += "background-color: rgba(0, 51, 160, 0.40); font-weight: bold;"
            elif col in ["Code Mission", "Nom de la mission"]:
                s += "background-color: #E6E7E8;"
            else:
                s += "background-color: rgba(0, 51, 160, 0.20);"
            styles.append(s)
        return styles

    # styled = df_display.style.apply(style_excel_like, axis=1)
    # st.dataframe(styled, use_container_width=True)

    styled = (
    df_display.style
    .apply(style_excel_like, axis=1)
    .map(color_ecart, subset=[
        "Ecart (Jour)",
        "Ecart",
        "Ecart % (Jour)",
        "Ecart %"
    ])
)

    nb_lignes = len(df_display)
    hauteur_tableau = min(max((nb_lignes + 1) * 35, 120), 650)

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        height=hauteur_tableau
    )

    st.subheader(" Suivi détaillé Budget mensuel / Réalisé / Restant par mission")
    st.caption("ℹ️ Budget mensuel calculé à partir du budget annuel divisé par 12.")
    # ============================
    # Base budget mission
    # ============================
    df_budget_base = df_budget_mission.copy()
    df_budget_base["Budget (Jour)"] = pd.to_numeric(df_budget_base["Budget (Jour)"], errors="coerce").fillna(0)

    # Budget mensuel = budget annuel / 12
    df_budget_base["Budget Mensuel"] = df_budget_base["Budget (Jour)"] / 12

    # ============================
    # Base réalisé mission/mois
    # ============================
    tmp_real = filtered_float.copy()
    tmp_real["Réalisé (Jour)"] = pd.to_numeric(tmp_real["Logged Billable hours"], errors="coerce").fillna(0) / 8
    tmp_real["Mois_dt"] = tmp_real["Date"].dt.to_period("M").dt.to_timestamp()

    df_real_month = (
        tmp_real.groupby(["Code Mission", "Mois_dt"], as_index=False)["Réalisé (Jour)"]
        .sum()
    )

    # ============================
    # Timeline complète
    # ============================
    months = pd.date_range(
        date_debut.to_period("M").to_timestamp(),
        date_fin.to_period("M").to_timestamp(),
        freq="MS"
    )

    missions_list = df_budget_base["Code Mission"].dropna().astype(str).unique().tolist()

    grid = pd.MultiIndex.from_product(
        [missions_list, months],
        names=["Code Mission", "Mois_dt"]
    ).to_frame(index=False)

    # ============================
    # Fusion budget + réalisé
    # ============================
    df_track = grid.merge(
        df_budget_base[["Code Mission", "Nom de la mission", "Budget (Jour)", "Budget Mensuel"]],
        on="Code Mission",
        how="left"
    ).merge(
        df_real_month,
        on=["Code Mission", "Mois_dt"],
        how="left"
    )

    df_track["Budget (Jour)"] = df_track["Budget (Jour)"].fillna(0)
    df_track["Budget Mensuel"] = df_track["Budget Mensuel"].fillna(0)
    df_track["Réalisé (Jour)"] = df_track["Réalisé (Jour)"].fillna(0)

    # ✅ Garder seulement les missions ayant au moins un budget mensuel non nul
    #    ou un réalisé non nul sur au moins un mois de la période
    missions_to_keep_jours = (
        df_track.groupby("Code Mission")[["Budget Mensuel", "Réalisé (Jour)"]]
        .apply(lambda g: ((g != 0).any()).any())
    )
    missions_to_keep_jours = missions_to_keep_jours[missions_to_keep_jours].index.tolist()
    df_track = df_track[df_track["Code Mission"].isin(missions_to_keep_jours)].copy()
    
    # Restant du mois = budget mensuel - réalisé du mois
    df_track["Restant Mois"] = df_track["Budget Mensuel"] - df_track["Réalisé (Jour)"]

    # Réalisé cumulé et restant cumulé
    df_track = df_track.sort_values(["Code Mission", "Mois_dt"])
    df_track["Réalisé Cumulé"] = df_track.groupby("Code Mission")["Réalisé (Jour)"].cumsum()
    df_track["Restant Cumulé"] = df_track["Budget (Jour)"] - df_track["Réalisé Cumulé"]

    # Label mois
    df_track["Mois"] = df_track["Mois_dt"].dt.strftime("%Y-%m")

    # ============================
    # Construire tableau final
    # ============================
    rows = []
    for _, row in df_track.iterrows():
        rows.append({
            "Code Mission": row["Code Mission"],
            "Nom de la mission": row["Nom de la mission"],
            "Budget Annuel": round(row["Budget (Jour)"], 2),
            "Mois": row["Mois"],
            "Budget Mensuel": round(row["Budget Mensuel"], 2),
            "Réalisé": round(row["Réalisé (Jour)"], 2),
            "Restant Mois": round(row["Restant Mois"], 2),
            "Restant Cumulé": round(row["Restant Cumulé"], 2),
        })

    df_long = pd.DataFrame(rows)

    # Pivot mensuel
    pivot_budget_mensuel = df_long.pivot_table(
        index=["Code Mission", "Nom de la mission", "Budget Annuel"],
        columns="Mois",
        values="Budget Mensuel",
        aggfunc="first"
    )

    pivot_real = df_long.pivot_table(
        index=["Code Mission", "Nom de la mission", "Budget Annuel"],
        columns="Mois",
        values="Réalisé",
        aggfunc="first"
    )

    pivot_rest_mois = df_long.pivot_table(
        index=["Code Mission", "Nom de la mission", "Budget Annuel"],
        columns="Mois",
        values="Restant Mois",
        aggfunc="first"
    )

    pivot_rest_cum = df_long.groupby(
        ["Code Mission", "Nom de la mission", "Budget Annuel"],
        as_index=True
    )["Restant Cumulé"].last()

    # Construire tableau final
    final_df = pd.DataFrame(index=pivot_budget_mensuel.index)


    for mois in sorted(df_long["Mois"].unique()):
        final_df[f"{mois} | Budget"] = pivot_budget_mensuel.get(mois)
        final_df[f"{mois} | Réalisé"] = pivot_real.get(mois)
        final_df[f"{mois} | Restant"] = pivot_rest_mois.get(mois)

    final_df["Restant Cumulé"] = pivot_rest_cum

    final_df = final_df.reset_index()

    # Ligne TOTAL
    total_row = {
        "Code Mission": "",
        "Nom de la mission": "TOTAL",
        "Budget Annuel": final_df["Budget Annuel"].sum()
    }

    for col in final_df.columns:
        if col not in ["Code Mission", "Nom de la mission", "Budget Annuel"]:
            total_row[col] = final_df[col].sum()

    final_df = pd.concat([final_df, pd.DataFrame([total_row])], ignore_index=True)
    # ============================
    # Formatage
    # ============================
    def fmt_num(x):
        try:
            x = float(x)
            return f"{x:.2f}".rstrip("0").rstrip(".")
        except:
            return x

    def color_remaining(val):
        try:
            v = float(val)
            if v < 0:
                return "color: #c62828; font-weight: 600;"
            return "color: #2e7d32; font-weight: 600;"
        except:
            return ""

    df_display = final_df.copy()

    # format numbers
    for col in df_display.columns[2:]:
        df_display[col] = df_display[col].apply(fmt_num)

    # colonnes à colorer
    cols_color = [c for c in df_display.columns if " | Restant" in c or c == "Restant Cumulé"]

    styled_jours = (
        df_display
        .style
        .apply(style_budget_tables, axis=1)
        .map(color_remaining, subset=[c for c in df_display.columns if "Restant" in c])
    )

    st.dataframe(styled_jours, use_container_width=True, hide_index=True, height=650)

    st.subheader("Suivi détaillé CA mensuel / Produit / Restant par mission")
    st.caption("ℹ️ Budget mensuel calculé à partir du budget annuel divisé par 12.")
    # ============================
    # Base budget mission (CA)
    # ============================
    df_budget_ca = df_budget_mission.copy()
    df_budget_ca["Budget (Jour)"] = pd.to_numeric(df_budget_ca["Budget (Jour)"], errors="coerce").fillna(0)

    # CA Budget annuel
    df_budget_ca["CA Budget Annuel"] = df_budget_ca["Budget (Jour)"] * pv_acteur

    # CA Budget mensuel
    df_budget_ca["CA Budget Mensuel"] = df_budget_ca["CA Budget Annuel"] / 12


    # ============================
    # Réalisé CA par mission / mois
    # ============================
    tmp_real_ca = filtered_float.copy()
    tmp_real_ca["Réalisé (Jour)"] = pd.to_numeric(tmp_real_ca["Logged Billable hours"], errors="coerce").fillna(0) / 8
    tmp_real_ca["CA Produit"] = tmp_real_ca["Réalisé (Jour)"] * pv_acteur
    tmp_real_ca["Mois_dt"] = tmp_real_ca["Date"].dt.to_period("M").dt.to_timestamp()

    df_real_ca_month = (
        tmp_real_ca.groupby(["Code Mission", "Mois_dt"], as_index=False)["CA Produit"]
        .sum()
    )

    # ============================
    # Timeline
    # ============================
    months = pd.date_range(
        date_debut.to_period("M").to_timestamp(),
        date_fin.to_period("M").to_timestamp(),
        freq="MS"
    )

    missions_list = df_budget_ca["Code Mission"].dropna().astype(str).unique().tolist()

    grid = pd.MultiIndex.from_product(
        [missions_list, months],
        names=["Code Mission", "Mois_dt"]
    ).to_frame(index=False)

    # ============================
    # Fusion budget + réalisé
    # ============================
    df_track_ca = grid.merge(
        df_budget_ca[["Code Mission", "Nom de la mission", "CA Budget Annuel", "CA Budget Mensuel"]],
        on="Code Mission",
        how="left"
    ).merge(
        df_real_ca_month,
        on=["Code Mission", "Mois_dt"],
        how="left"
    )

    df_track_ca["CA Budget Annuel"] = df_track_ca["CA Budget Annuel"].fillna(0)
    df_track_ca["CA Budget Mensuel"] = df_track_ca["CA Budget Mensuel"].fillna(0)
    df_track_ca["CA Produit"] = df_track_ca["CA Produit"].fillna(0)

    missions_to_keep_ca = (
        df_track_ca.groupby("Code Mission")[["CA Budget Mensuel", "CA Produit"]]
        .apply(lambda g: ((g != 0).any()).any())
    )
    missions_to_keep_ca = missions_to_keep_ca[missions_to_keep_ca].index.tolist()
    df_track_ca = df_track_ca[df_track_ca["Code Mission"].isin(missions_to_keep_ca)].copy()

    # Restant du mois
    df_track_ca["CA Restant Mois"] = df_track_ca["CA Budget Mensuel"] - df_track_ca["CA Produit"]

    # Cumul
    df_track_ca = df_track_ca.sort_values(["Code Mission", "Mois_dt"])
    df_track_ca["CA Produit Cumulé"] = df_track_ca.groupby("Code Mission")["CA Produit"].cumsum()
    df_track_ca["CA Restant Cumulé"] = df_track_ca["CA Budget Annuel"] - df_track_ca["CA Produit Cumulé"]

    df_track_ca["Mois"] = df_track_ca["Mois_dt"].dt.strftime("%Y-%m")

    # ============================
    # Construction tableau
    # ============================
    rows = []
    for _, row in df_track_ca.iterrows():
        rows.append({
            "Code Mission": row["Code Mission"],
            "Nom de la mission": row["Nom de la mission"],
            "CA Budget Annuel": round(row["CA Budget Annuel"], 0),
            "Mois": row["Mois"],
            "Budget Mensuel": round(row["CA Budget Mensuel"], 0),
            "Produit": round(row["CA Produit"], 0),
            "Restant Mois": round(row["CA Restant Mois"], 0),
            "Restant Cumulé": round(row["CA Restant Cumulé"], 0),
        })

    df_long_ca = pd.DataFrame(rows)

    # Pivot
    pivot_budget = df_long_ca.pivot_table(
        index=["Code Mission", "Nom de la mission", "CA Budget Annuel"],
        columns="Mois",
        values="Budget Mensuel",
        aggfunc="first"
    )

    pivot_real = df_long_ca.pivot_table(
        index=["Code Mission", "Nom de la mission", "CA Budget Annuel"],
        columns="Mois",
        values="Produit",
        aggfunc="first"
    )

    pivot_rest = df_long_ca.pivot_table(
        index=["Code Mission", "Nom de la mission", "CA Budget Annuel"],
        columns="Mois",
        values="Restant Mois",
        aggfunc="first"
    )

    pivot_rest_cum = df_long_ca.groupby(
        ["Code Mission", "Nom de la mission", "CA Budget Annuel"],
        as_index=True
    )["Restant Cumulé"].last()

    # Table finale
    final_df_ca = pd.DataFrame(index=pivot_budget.index)

    for mois in sorted(df_long_ca["Mois"].unique()):
        final_df_ca[f"{mois} | Budget"] = pivot_budget.get(mois)
        final_df_ca[f"{mois} | Produit"] = pivot_real.get(mois)
        final_df_ca[f"{mois} | Restant"] = pivot_rest.get(mois)

    final_df_ca["Restant Cumulé"] = pivot_rest_cum

    final_df_ca = final_df_ca.reset_index()
    
    # Ligne TOTAL
    total_row_ca = {
        "Code Mission": "",
        "Nom de la mission": "TOTAL",
        "CA Budget Annuel": final_df_ca["CA Budget Annuel"].sum()
    }

    for col in final_df_ca.columns:
        if col not in ["Code Mission", "Nom de la mission", "CA Budget Annuel"]:
            total_row_ca[col] = final_df_ca[col].sum()

    final_df_ca = pd.concat([final_df_ca, pd.DataFrame([total_row_ca])], ignore_index=True)
    # ============================
    # Format € et couleurs
    # ============================
    def fmt_eur(x):
        try:
            return f"{int(round(float(x),0)):,.0f} €".replace(",", " ")
        except:
            return x

    def color_remaining(val):
        try:
            v = float(str(val).replace("€","").replace(" ",""))
            if v < 0:
                return "color:#c62828; font-weight:600;"
            return "color:#2e7d32; font-weight:600;"
        except:
            return ""

    df_display_ca = final_df_ca.copy()

    for col in df_display_ca.columns[2:]:
        df_display_ca[col] = df_display_ca[col].apply(fmt_eur)

    cols_color = [c for c in df_display_ca.columns if "Restant" in c]

    styled_ca = (
        df_display_ca
        .style
        .apply(style_budget_tables, axis=1)
        .map(color_remaining, subset=[c for c in df_display_ca.columns if "Restant" in c])
    )

    st.dataframe(styled_ca, use_container_width=True, hide_index=True, height=650)
    # ============================
    # 📈 CHARTS CUMULÉS (Jours + CA)
    # ============================

    # Assure la colonne Réalisé (Jour)
    filtered_float["Réalisé (Jour)"] = pd.to_numeric(filtered_float["Logged Billable hours"], errors="coerce").fillna(0) / 8

    # Colonne Mois (datetime -> début de mois)
    filtered_float["Mois_dt"] = filtered_float["Date"].dt.to_period("M").dt.to_timestamp()

    # --- Réalisé par mois (jours)
    realise_mois = (
        filtered_float.groupby("Mois_dt", as_index=False)["Réalisé (Jour)"]
        .sum()
        .rename(columns={"Réalisé (Jour)": "Jours Réalisés"})
    )

    # --- Budget total (jours) (sur les missions sélectionnées)
    tmp_plan_chart = filtered_plan.copy()
    tmp_plan_chart["Code Mission"] = tmp_plan_chart["Code Mission"].astype(str).str.strip()
    tmp_plan_chart[acteur_filter] = pd.to_numeric(tmp_plan_chart[acteur_filter], errors="coerce").fillna(0)

    jours_budget_total_chart = tmp_plan_chart[acteur_filter].sum()
    ca_budget_total_chart = jours_budget_total_chart * pv_acteur

    # --- Timeline complète (entre date_debut et date_fin)
    months = pd.date_range(date_debut.to_period("M").to_timestamp(),
                        date_fin.to_period("M").to_timestamp(),
                        freq="MS")

    timeline = pd.DataFrame({"Mois_dt": months})
    df_chart = timeline.merge(realise_mois, on="Mois_dt", how="left")
    df_chart["Jours Réalisés"] = df_chart["Jours Réalisés"].fillna(0)

    # Cumuls
    df_chart["Jours Réalisés Cumulé"] = df_chart["Jours Réalisés"].cumsum()

    # Budget cumulé "linéaire" (réparti sur nb mois)
    n_months = max(len(df_chart), 1)
    df_chart["Jours Budget Mensuel"] = jours_budget_total_chart / n_months
    df_chart["Jours Budget Cumulé"] = df_chart["Jours Budget Mensuel"].cumsum()

    # CA mensuel / cumulé
    df_chart["CA Réalisé"] = df_chart["Jours Réalisés"] * pv_acteur
    df_chart["CA Réalisé Cumulé"] = df_chart["CA Réalisé"].cumsum()

    df_chart["CA Budget Mensuel"] = ca_budget_total_chart / n_months
    df_chart["CA Budget Cumulé"] = df_chart["CA Budget Mensuel"].cumsum()

    # Labels Mois
    df_chart["Mois"] = df_chart["Mois_dt"].dt.strftime("%b %Y")

    st.subheader("Visualisations [Évolution dans le temps (Dynamique)]")
    
    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("📈 Évolution des Jours cumulés vs Budget")

        fig_jours = go.Figure()

        fig_jours.add_trace(go.Scatter(
            x=df_chart["Mois"],
            y=df_chart["Jours Réalisés Cumulé"],
            mode="lines+markers+text",
            name="Jours Réalisés Cumulé",
            text=[f"{v:.1f} j" for v in df_chart["Jours Réalisés Cumulé"]],
            textposition="top center"
        ))

        fig_jours.add_trace(go.Scatter(
            x=df_chart["Mois"],
            y=df_chart["Jours Budget Cumulé"],
            mode="lines+markers+text",
            name="Budget Jours Cumulé",
            line=dict(dash="dash"),
            text=[f"{v:.1f} j" for v in df_chart["Jours Budget Cumulé"]],
            textposition="top center"
        ))

        fig_jours.update_layout(
            xaxis_title="Mois",
            yaxis_title="Jours",
            hovermode="x unified",
            legend_title="Type",
            height=420
        )

        st.plotly_chart(fig_jours, use_container_width=True)
    with col2:
        st.subheader("📈 Évolution du CA cumulé vs Budget")

        fig_ca = go.Figure()

        fig_ca.add_trace(go.Scatter(
            x=df_chart["Mois"],
            y=df_chart["CA Réalisé Cumulé"],
            mode="lines+markers+text",
            name="CA Engagé Cumulé",
            text=[f"{v:,.0f} €".replace(",", " ") for v in df_chart["CA Réalisé Cumulé"]],
            textposition="top center"
        ))

        fig_ca.add_trace(go.Scatter(
            x=df_chart["Mois"],
            y=df_chart["CA Budget Cumulé"],
            mode="lines+markers+text",
            name="Budget CA Cumulé",
            line=dict(dash="dash"),
            text=[f"{v:,.0f} €".replace(",", " ") for v in df_chart["CA Budget Cumulé"]],
            textposition="top center"
        ))

        fig_ca.update_layout(
            xaxis_title="Mois",
            yaxis_title="Montant (€)",
            hovermode="x unified",
            legend_title="Type",
            height=420
        )

        st.plotly_chart(fig_ca, use_container_width=True)

    # -----------------------
    # ✅ Session state (si tu veux réutiliser ailleurs)
    # -----------------------
    st.session_state["final_float_acteur"] = filtered_float
    st.session_state["final_plan_prod_acteur"] = filtered_plan
    st.session_state["acteur_filter"] = acteur_filter
    st.session_state["selected_missions"] = selected_missions
    st.session_state["df_missions_acteur"] = df


# =========================================================
# ✅ MAIN : lecture session_state + sidebar inversée + appel
# =========================================================
from ui import inject_shared_css, show_sidebar

inject_shared_css()
show_sidebar()

if "data_plan_prod" in st.session_state and "data_float" in st.session_state and "rates" in st.session_state:
    data_plan_prod = st.session_state["data_plan_prod"]
    data_float = st.session_state["data_float"]
    rates = st.session_state["rates"]

    st.sidebar.header("Filtres")

    # --- Acteurs disponibles = colonnes acteurs dans plan prod (match Rates)
    data_plan_prod.columns = data_plan_prod.columns.str.strip()
    rates.columns = rates.columns.str.strip()

    rates_acteurs = set(rates["Acteur"].dropna().astype(str).str.strip().unique())
    actor_cols = [c for c in data_plan_prod.columns if c.strip() in rates_acteurs]

    if len(actor_cols) == 0:
        st.error("Aucun acteur détecté dans Data Plan Prod (colonnes acteurs).")
        st.stop()

    acteur_filter = st.sidebar.selectbox(
        "Sélectionnez un intervenant 🎯",
        options=sorted(actor_cols),
        key="acteur_selector"
    )
    # -----------------------
    # ✅ PV base depuis Rates
    # -----------------------
    pv_base = 0.0
    if {"Acteur", "PV"}.issubset(rates.columns):
        s = rates.loc[
            rates["Acteur"].astype(str).str.strip() == str(acteur_filter).strip(),
            "PV"
        ]
        if len(s) > 0:
            pv_base = pd.to_numeric(s.iloc[0], errors="coerce")
            pv_base = 0.0 if pd.isna(pv_base) else float(pv_base)

    # -----------------------
    # ✅ Override PV (sidebar sous intervenant)
    # -----------------------
    if "pv_overrides" not in st.session_state:
        st.session_state["pv_overrides"] = {}

    key_pv = str(acteur_filter).strip()
    pv_default = float(st.session_state["pv_overrides"].get(key_pv, pv_base))

    pv_acteur = st.sidebar.number_input(
        "💶 PV (Facturation journalière)",
        min_value=0.0,
        value=float(pv_default),
        step=10.0,
        format="%.0f",
        key=f"pv_input_{key_pv}"
    )
    st.sidebar.markdown("---")
    st.session_state["pv_overrides"][key_pv] = float(pv_acteur)
    # --- Missions où cet acteur a soit du BUDGET (plan prod) soit du RÉALISÉ (float)

    # 1) Missions avec budget > 0
    # 1) Missions présentes dans PLAN PROD (budget, même si = 0)
    # ============================
    # ✅ Missions disponibles (sidebar)
    #   = missions présentes dans PLAN PROD
    #   ET (budget>0 OU réalisé>0)
    # ============================

    # --- PLAN PROD : budget par mission pour cet acteur
    tmp = data_plan_prod.copy()
    tmp.columns = tmp.columns.str.strip()
    tmp["Code Mission"] = tmp["Code Mission"].astype(str).str.strip()

    tmp[acteur_filter] = pd.to_numeric(tmp[acteur_filter], errors="coerce").fillna(0)

    budget_by_mission = (
        tmp.groupby("Code Mission", as_index=False)[acteur_filter]
        .sum()
        .rename(columns={acteur_filter: "Budget_J"})
    )

    # --- FLOAT : réalisé (heures) par mission pour cet acteur
    tmp_f = data_float.copy()
    tmp_f.columns = tmp_f.columns.str.strip()

    # si colonnes FR
    if "Heures facturées" in tmp_f.columns:
        tmp_f = tmp_f.rename(columns={"Heures facturées": "Logged Billable hours"})
    if "Logged Billable hours" not in tmp_f.columns:
        tmp_f["Logged Billable hours"] = 0

    tmp_f["Acteur"] = tmp_f["Acteur"].astype(str).str.strip()
    tmp_f["Code Mission"] = tmp_f["Code Mission"].astype(str).str.strip()
    tmp_f["Logged Billable hours"] = pd.to_numeric(tmp_f["Logged Billable hours"], errors="coerce").fillna(0)

    real_by_mission = (
        tmp_f.loc[tmp_f["Acteur"] == str(acteur_filter).strip()]
        .groupby("Code Mission", as_index=False)["Logged Billable hours"]
        .sum()
        .rename(columns={"Logged Billable hours": "Heures"})
    )

    # --- Merge : on garde UNIQUEMENT les missions du PLAN PROD (how="left")
    m = budget_by_mission.merge(real_by_mission, on="Code Mission", how="left")
    m["Heures"] = m["Heures"].fillna(0)

    # ✅ critère final : (budget>0) OU (heures>0)
    m = m[(m["Budget_J"] > 0) | (m["Heures"] > 0)]

    missions_disponibles = sorted(m["Code Mission"].unique().tolist())

    selected_missions = st.sidebar.multiselect(
        "📌 Filtrer par mission(s) (optionnel)",
        options=missions_disponibles,
        default=missions_disponibles,
        key="missions_selector"
    )

    # ✅ Appel vue acteur
    display_actor_report(
    data_plan_prod,
    data_float,
    rates,
    acteur_filter,
    selected_missions,
    pv_acteur
)

else:
    st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")
