import streamlit as st
import pandas as pd
import plotly.express as px
import pdfkit
from jinja2 import Template
import os
import plotly.graph_objects as go
import re
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components  # Ajout de l'import correct
import locale
import unicodedata

# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# 1. Upload fichier Excel
fichier = st.sidebar.file_uploader("📤 Importer le fichier contenant les formations (ex: Formations 2025)", type=["xlsx"])


def display_customer_report(data_plan_prod, data_float, rates):
    #logo_path = "Logo_Advent.jpg"
    # Injecter le CSS pour les cards
    st.markdown("""
        <style>
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
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            flex: 1;
        }
        .metric {
            font-size: 2rem;
            font-weight: bold;
        }
        .delta {
            font-size: 1.2rem;
            margin-top: 5px;
        }
        .label {
            font-size: 1rem;
            color: #555;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Vérification du fichier
    if fichier:
            # 🟢 **Initialiser les variables avec les données complètes**
        final_plan_prod = data_plan_prod.copy()
        final_float = data_float.copy()
        try:
            df_formations = pd.read_excel(fichier, sheet_name="Formations 2025", header=2)

            # Vérifier colonnes attendues
            colonnes_attendues = ["Date de début", "Nombre de jour"]
            if not all(col in df_formations.columns for col in colonnes_attendues):
                st.error("❌ Le fichier ne contient pas les colonnes requises : 'Date de début' et 'Nombre de jour'")
                st.stop()

            df_formations["Nombre de jour"] = pd.to_numeric(df_formations["Nombre de jour"], errors="coerce")
            jours_formation = df_formations["Nombre de jour"].sum()

            formateurs = df_formations['Formateur 1'].dropna().unique().tolist()

            st.sidebar.info(f"ℹ️ Total des jours de formation planifiés : **{jours_formation:.1f} jours**")
            st.sidebar.info(f"ℹ️ Nombre de formateurs identifiés : **{len(formateurs)}**")

            # 4. Récupérer les jours réalisés depuis session (Stocké depuis Customer Report)
            mission_logged_days = st.session_state.get("mission_logged_days", None)

            if mission_logged_days is None:
                st.warning("⚠️ Les jours réalisés ne sont pas encore disponibles. Veuillez consulter d'abord la page 'Customer Report'.")
                st.stop()
            mission_code = final_plan_prod['Code Mission'].iloc[0] if not final_plan_prod.empty else "N/A"
            # Si la mission est Sales Academy (238010), stocker les jours réalisés
            if str(mission_code) == "238010":
                st.session_state["mission_logged_days"] = mission_logged_days
            jours_ingenieurie = mission_logged_days - jours_formation
            jours_ingenieurie = max(jours_ingenieurie, 0)  # éviter négatif
            #st.write("\n")

        except Exception as e:
            st.error(f"❌ Erreur lors du traitement : {e}")
    else:
        st.info("Veuillez importer un fichier Excel contenant la feuille 'Formations 2025'.")
        # 🔹 Conversion de la colonne "Date" en format datetime
    data_float["Date"] = pd.to_datetime(data_float["Date"], errors="coerce")

    # Renommer les colonnes si elles existent sous d'autres noms
    if 'Heures facturées' in data_float.columns:
        data_float = data_float.rename(columns={'Heures facturées': 'Logged Billable hours'})
    if 'Heures non facturées' in data_float.columns:
        data_float = data_float.rename(columns={'Heures non facturées': 'Logged Non-billable hours'})
    if 'Coût total' in data_float.columns:
        data_float = data_float.rename(columns={'Coût total': 'Coût'})

    # Ajouter des colonnes par défaut si elles sont absentes
    if 'Logged Billable hours' not in data_float.columns:
        data_float['Logged Billable hours'] = 0
    if 'Logged Non-billable hours' not in data_float.columns:
        data_float['Logged Non-billable hours'] = 0
    if 'Coût' not in data_float.columns:
        data_float['Coût'] = 0

    # Vérifier la présence des colonnes nécessaires dans data_plan_prod
    required_columns_plan = ['Code Mission', 'Nom de la mission', 'Budget (PV)']
    for col in required_columns_plan:
        if col not in data_plan_prod.columns:
            st.error(f"Colonne manquante dans data_plan_prod : {col}")

            return
    rates = st.session_state.get("rates", pd.DataFrame())  # Récupérer Rates depuis session_state


    # Conversion des colonnes de dates
    data_float['Date'] = pd.to_datetime(data_float['Date'], errors='coerce')

    # 🟢 **Créer une colonne "Mois" au format "YYYY-MM"**
    data_float['Mois'] = data_float['Date'].dt.strftime('%Y-%m')

    # 🟢 **Initialiser les variables avec les données complètes**
    final_plan_prod = data_plan_prod.copy()
    final_float = data_float.copy()

    # 🟢 **Filtres interactifs**
    st.sidebar.header("Filtres")

    mission_code = final_plan_prod['Code Mission'].iloc[0] if not final_plan_prod.empty else "N/A"
      # Si la mission est Sales Academy (238010), stocker les jours réalisés
    if str(mission_code) == "238010":
        st.session_state["mission_logged_days"] = mission_logged_days
    # 🔹 **Filtre de Mission**
    mission_code  = st.sidebar.selectbox(
        "🎯 Sélectionnez la mission (seule la 238010 est autorisée)",
        options=data_plan_prod['Code Mission'].unique(),
        format_func=lambda x: f"{x} - {data_plan_prod[data_plan_prod['Code Mission'] == x]['Nom de la mission'].iloc[0]}"
    )
    if mission_code != "238010":
        st.error("❌ Cette page est uniquement pour la mission 238010 - Sales Academy.")
        st.stop()
    # **Appliquer le filtre de mission**
    filtered_plan_prod = data_plan_prod[data_plan_prod['Code Mission'] == mission_code ]
    filtered_float = data_float[data_float['Code Mission'] == mission_code ]

    # Vérifier si les données existent après le filtre de mission
    if filtered_plan_prod.empty or filtered_float.empty:
        st.warning("Aucune donnée disponible pour la mission sélectionnée.")
        st.stop()

    
    # 🔹 **Ajouter les filtres de période**
    date_min = filtered_float["Date"].min()
    date_max = filtered_float["Date"].max()

    date_debut = st.sidebar.date_input("📅 Date Début", value=date_min)
    date_fin = st.sidebar.date_input("📅 Date Fin", value=date_max)

    # 🔹 Convertir les dates choisies en format datetime
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)

    # 🟢 **Application du Filtre de Période**
    if date_debut and date_fin:
        filtered_float = filtered_float[(filtered_float["Date"] >= date_debut) & (filtered_float["Date"] <= date_fin)]
    else:
        filtered_float = data_float.copy()

        # 🔹 Vérification de la présence des données après filtrage
    if filtered_float.empty:
        st.warning("⚠️ Aucune donnée disponible pour la période sélectionnée.")
        st.stop()
        
        # 🟢 Appliquer aussi le filtre de période sur df_formations
    if 'df_formations' in locals() and not df_formations.empty and "Date de début" in df_formations.columns:
        df_formations['Date de début'] = pd.to_datetime(df_formations['Date de début'], errors='coerce')
        df_formations = df_formations[
            (df_formations["Date de début"] >= date_debut) &
            (df_formations["Date de début"] <= date_fin)
        ]


    # df_formations["Module"] = df_formations["Module"].astype(str).str.strip()
    # df_formations = df_formations[df_formations["Module"] != ""]
    with st.sidebar.expander("🎛️ Filtres avancés", expanded=True):

                            # 🎯 Appliquer le filtre de module avant tout calcul
        if "Module" in df_formations.columns:
            modules_disponibles = df_formations["Module"].dropna()
            modules_disponibles = modules_disponibles[modules_disponibles.str.strip() != ""].unique().tolist()

            modules_disponibles.sort()
            module_selectionne = st.multiselect("📚 Filtrer par Module", options=modules_disponibles, default=modules_disponibles)
            df_formations = df_formations[df_formations["Module"].isin(module_selectionne)]

        df_formations["Nombre de jour"] = pd.to_numeric(df_formations["Nombre de jour"], errors="coerce")
        jours_formation = df_formations["Nombre de jour"].sum()

        formateurs = df_formations['Formateur 1'].dropna().unique().tolist()
        # Appliquer filtre de mission
        filtered_plan_prod = data_plan_prod[data_plan_prod['Code Mission'] == mission_code]
        filtered_float = data_float[data_float['Code Mission'] == mission_code]

        # ✅ Appliquer filtre de date (si déjà fait)
        filtered_float = filtered_float[(filtered_float["Date"] >= date_debut) & (filtered_float["Date"] <= date_fin)]

        # ✅ Extraire uniquement les intervenants de la mission filtrée
        intervenants_disponibles = sorted(filtered_float['Acteur'].dropna().unique().tolist())

        # ✅ Afficher le filtre multi-sélection juste ici
        intervenants_selectionnes = st.multiselect(
            "👤 Filtrer par Intervenant",
            options=intervenants_disponibles,
            default=intervenants_disponibles
        )

        # ✅ Appliquer le filtre à final_float
        filtered_float = filtered_float[filtered_float["Acteur"].isin(intervenants_selectionnes)]

    # 🔹 **Finaliser les variables**
    final_plan_prod = filtered_plan_prod.copy()
    final_float = filtered_float.copy()

    # 📌 Fusion avec PV si ce n’est pas déjà fait
    final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
    final_float['PV'] = final_float['PV'].fillna(0)

    # 📌 Calcul des jours réalisés
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    # 📌 Jours de formation par formateur (via Excel importé)
    jours_formation_par_formateur = {}
    if df_formations is not None and "Formateur 1" in df_formations.columns:
        grouped_formateurs = df_formations.groupby("Formateur 1")["Nombre de jour"].sum()
        jours_formation_par_formateur = grouped_formateurs.to_dict()

    # 📌 Agrégation des jours réalisés et PV
    intervenants = final_float.groupby("Acteur").agg({
        "Jours Réalisés": "sum",
        "PV": "first"
    }).reset_index()
    def clean_nom(nom):
        if pd.isna(nom):
            return ""
        # Supprimer les accents et mettre en minuscule
        nom = str(nom).strip().lower()
        nom = unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('utf-8')
        return nom

    # Nettoyer les noms dans rates (pour éviter de le faire 1000 fois dans la boucle)
    rates_cleaned = rates.copy()
    rates_cleaned["Acteur_clean"] = rates_cleaned["Acteur"].apply(clean_nom)

    ca_engage_formateurs = 0
    for formateur, jours_form in jours_formation_par_formateur.items():
        formateur_clean = clean_nom(formateur)
        pv_match = rates_cleaned.loc[rates_cleaned["Acteur_clean"] == formateur_clean, "PV"].values
        if len(pv_match) > 0:
            ca_engage_formateurs += jours_form * pv_match[0]


    # 🔁 CA engagé total = tous les jours réalisés × PV
    ca_engage_total = (intervenants["Jours Réalisés"] * intervenants["PV"]).sum()

    # 🔁 CA ingenieurie = Total - Formation
    ca_engage_ingenieurie = ca_engage_total - ca_engage_formateurs
    ca_engage_ingenieurie = max(ca_engage_ingenieurie, 0)

    # 📌 Totaux généraux
    mission_logged_days = intervenants["Jours Réalisés"].sum()
    jours_ingenieurie = mission_logged_days - sum(jours_formation_par_formateur.values())
    # juste après le calcul
    st.sidebar.info(f"ℹ️ CA engagé total (incl. formation) : **{ca_engage_total:,.0f} €**")

    # 🧮 Budget & ratios
    mission_budget = final_plan_prod['Budget (PV)'].sum()
    budget_remaining = mission_budget - ca_engage_ingenieurie
    percentage_budget_used = (ca_engage_ingenieurie / mission_budget) * 100 if mission_budget else 0
    percentage_budget_remaining = 100 - percentage_budget_used


    # 🔽 Section : Détail CA Engagé pour les Formateurs

    # Calculs principauxà partir
    mission_budget = final_plan_prod['Budget (PV)'].sum()
    mission_logged_hours = final_float['Logged Billable hours'].sum()
    mission_logged_days = mission_logged_hours / 8  # Conversion en jours
    budget_remaining = mission_budget - ca_engage_total
    percentage_budget_used = (ca_engage_total / mission_budget) * 100 if mission_budget != 0 else 0
    percentage_budget_remaining = (budget_remaining / mission_budget) * 100 if mission_budget != 0 else 0

      # Si la mission est Sales Academy (238010), stocker les jours réalisés
    if str(mission_code) == "238010":
        st.session_state["mission_logged_days"] = mission_logged_days
    # Fonction pour déterminer la classe CSS de la flèche (positive ou negative)
    def get_delta_class(delta):
        return "positive" if delta >= 0 else "negative"
    
    # Extraire les informations de la mission sélectionnée
    if 'Client' in final_float.columns and not final_float.empty:
        mission_client = final_float['Client'].iloc[0]
    else:
        mission_client = "N/A"


    mission_budget = mission_budget  # Déjà calculé comme "CA Budget"

    # Extraire le nom de la mission après le code (ex: "[24685] - Encadrement RCM" -> "Encadrement RCM")

    mission_full_name = final_plan_prod['Nom de la mission'].iloc[0] if not final_plan_prod.empty else "N/A"
    # Supprimer tout ce qui est entre crochets + les crochets + espace ou tiret qui suit
    mission_name_cleaned = re.sub(r"^\[[^\]]+\]\s*[-_]?\s*", "", mission_full_name).strip()
    mission_name = mission_name_cleaned

    # 🔹 Forcer l'affichage avec un seul chiffre après la virgule
    mission_budget = round(mission_budget, 0)
    ca_engage_total = round(ca_engage_total, 0)
    budget_remaining = round(budget_remaining, 0)
    mission_logged_days = round(mission_logged_days, 1)


    # Affichage des informations sous forme de tableau stylisé
    col1,col2,col3 = st.columns(3) 
    with col1: 
        st.markdown(f"""
            <style>
                .mission-info-container {{
                    display: flex;
                    flex-direction: column;
                    margin-bottom: 20px;
                }}
                .mission-info-table {{
                    border: 2px solid black;
                    border-collapse: collapse;
                    width: 400px;
                    font-size: 1rem;
                    border-radius: 8px;  /* ✅ Coins arrondis */
                    overflow: hidden;    /* ✅ Important pour appliquer le radius proprement */
                    border: 2px solid #0033A0;           /* ✅ Bordure bleue Advent */
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); /* ✅ Ombre légère */
                }}
                .mission-info-table td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: left;
                    font-weight: bold;
                }}
                    
                .mission-info-table td:nth-child(1) {{
                    background-color: rgba(0, 51, 160, 0.2);  /* ✅ Bleu ADVENT avec opacité douce *;  /* Colonne libellé à gauche */
                    color: black;
                    text-align: left;
                }}
                .mission-info-table td:nth-child(2) {{
                    background-color: #E6E7E8;  /* Colonne valeur à droite */
                    color: black;
                    text-align: right;
                }}
            </style>
            <div class="mission-info-container">
                <table class="mission-info-table">
                    <tr><td>Client</td><td>{mission_client}</td></tr>
                    <tr><td>Mission</td><td>{mission_name}</td></tr>
                    <tr><td>Code Mission</td><td>{mission_code}</td></tr>
                    <tr><td>Budget Mission</td><td>{format(mission_budget, ",.0f").replace(",", " ")} €</td></tr>
                </table>
            </div>
        """, unsafe_allow_html=True)
    with col2 : 
        st.write("")
    with col3 : 
        # 🔥 Créer l'affichage de la période en "Mois Année"
        mois_debut = date_debut.strftime("%B %Y").capitalize()
        mois_fin = date_fin.strftime("%B %Y").capitalize()
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
            # ✅ Nouveau calcul basé uniquement sur les jours de ingenieurie

    # col1,col2 = st.columns(2)

    # with col1:
    # Nettoyer les noms
    final_float['Acteur_clean'] = final_float['Acteur'].apply(clean_nom)
    df_formations['Formateur_clean'] = df_formations['Formateur 1'].apply(clean_nom)

    # Convertir les dates
    final_float['Date'] = pd.to_datetime(final_float['Date'], errors='coerce')
    df_formations['Date de début'] = pd.to_datetime(df_formations['Date de début'], errors='coerce')

    # Ajouter le mois dans chaque fichier
    final_float['Mois'] = final_float['Date'].dt.strftime('%Y-%m')
    df_formations['Mois'] = df_formations['Date de début'].dt.strftime('%Y-%m')

    # Calculer les jours réalisés (Jours Réalisés = heures facturées / 8)
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    # Grouper les jours réalisés par intervenant et mois
    jours_realises_par_mois = final_float.groupby(['Code Mission', 'Acteur', 'Acteur_clean', 'Mois'])['Jours Réalisés'].sum().reset_index()

    # Grouper les jours de formation par formateur et mois
    jours_formations_par_mois = df_formations.groupby(['Formateur_clean', 'Mois'])['Nombre de jour'].sum().reset_index()

    # Fusionner les deux tables par Acteur_clean et Mois
    df_merged = jours_realises_par_mois.merge(
        jours_formations_par_mois,
        how='left',
        left_on=['Acteur_clean', 'Mois'],
        right_on=['Formateur_clean', 'Mois']
    )

    # Remplacer NaN par 0 pour les formateurs sans formation ce mois-là
    df_merged['Nombre de jour'] = df_merged['Nombre de jour'].fillna(0)

    # Calculer les jours d'ingénierie
    df_merged['Jours Ingénierie'] = df_merged['Jours Réalisés'] - df_merged['Nombre de jour']
    df_merged['Jours Ingénierie'] = df_merged['Jours Ingénierie'].apply(lambda x: max(x, 0))

    # Créer le pivot final
    tableau_cumul_jours_ingenierie = df_merged.pivot_table(
        index=['Code Mission', 'Acteur'],
        columns='Mois',
        values='Jours Ingénierie',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Ajouter la colonne Total
    tableau_cumul_jours_ingenierie['Total'] = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum(axis=1)

    # Réorganiser les colonnes
    colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours_ingenierie.columns[2:-1]) + ['Total']
    tableau_cumul_jours_ingenierie = tableau_cumul_jours_ingenierie[colonnes_ordre]

    # Ligne total général
    total_general = tableau_cumul_jours_ingenierie.iloc[:, 2:].sum()
    total_general['Code Mission'] = 'Total Général'
    total_general['Acteur'] = ''
    tableau_cumul_jours_ingenierie = pd.concat([tableau_cumul_jours_ingenierie, pd.DataFrame([total_general])], ignore_index=True)

    # Formatage
    tableau_cumul_jours_ingenierie.iloc[:, 2:] = tableau_cumul_jours_ingenierie.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")
    # 🔹 Liste des formateurs (cleanés)
    formateurs_clean = df_formations['Formateur_clean'].unique().tolist()

    # 🔹 Ajouter une colonne temporaire "Est_formateur" pour style
    tableau_cumul_jours_ingenierie['Est_formateur'] = tableau_cumul_jours_ingenierie['Acteur'].apply(
        lambda x: clean_nom(x) in formateurs_clean if pd.notna(x) else False
    )

    # 🔹 Ajouter une colonne pour identifier la ligne "Total Général"
    tableau_cumul_jours_ingenierie["is_total_general"] = tableau_cumul_jours_ingenierie["Code Mission"] == "Total Général"

    # 🔹 Fonction de style combinée
    def style_personnalise(row):
        styles = []
        for col in tableau_cumul_jours_ingenierie.columns:
            style = ""
            if row["is_total_general"]:  # Surligner ligne Total Général
                style += "background-color: #FFCCCC;"
            elif row.get("Est_formateur", False):  # Surligner ligne formateur
                style += "background-color: #FFF2CC;"
            if col == "Total":  # Surligner colonne Total
                style += "background-color: #D9D9D9;"
            styles.append(style)
        return styles


    # 🔹 Appliquer le style AVANT de supprimer la colonne
    styled_df = tableau_cumul_jours_ingenierie.style.apply(style_personnalise, axis=1)


    # 📌 Affichage
    st.subheader("Cumul Jours d'Ingénierie réalisés (formateurs surlignés)")
    st.dataframe(styled_df, use_container_width=True)
    # 🔹 Liste des formateurs (noms cleanés)
    formateurs_clean = df_formations['Formateur_clean'].unique().tolist()

    # 🔹 Ajouter une colonne temporaire "Est_formateur"
    tableau_cumul_jours_ingenierie['Est_formateur'] = tableau_cumul_jours_ingenierie['Acteur'].apply(
        lambda x: clean_nom(x) in formateurs_clean if pd.notna(x) else False
    )

    # 🔹 Formateurs visibles avec jours d’ingénierie > 0
    formateurs_visibles = tableau_cumul_jours_ingenierie[
        tableau_cumul_jours_ingenierie['Est_formateur'] & 
        (tableau_cumul_jours_ingenierie['Total'].astype(float) > 0)
    ]['Acteur'].tolist()

    # 🔸 Bloc Warning Stylisé si formateurs visibles
    if formateurs_visibles:
        # Construire le contenu de la liste HTML
        liste_html = "".join([f"<li style='margin-bottom: 4px;'>{nom}</li>" for nom in formateurs_visibles])
        
        # Contenu complet du bloc stylisé
        message_html = f"""
        <div style='
            background-color: #fff3cd;
            border-left: 6px solid #ffc107;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        '>
            <h4 style='margin: 0 0 10px 0;'>⚠️ Les intervenants ayant également réalisé des jours de formations pendant la periode selectionnée :</h4>
            <ul style='margin: 0; padding-left: 20px;'>{liste_html}</ul>
        </div>
        """

        # Affichage dans Streamlit
        st.markdown(message_html, unsafe_allow_html=True)
    else:
        st.info("Aucun formateur n'a réalisé de jours d'ingénierie pendant la période sélectionnée.")



    # # Affichage
    # st.subheader("Cumul Jours d'Ingénierie réalisés")
    # st.table(tableau_cumul_jours_ingenierie)


    # with col2:
    # Vérifier que les PV sont bien fusionnés
    if 'PV' not in final_float.columns:
        final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
    final_float['PV'] = final_float['PV'].fillna(0)

    # Nettoyage des noms
    final_float['Acteur_clean'] = final_float['Acteur'].apply(clean_nom)
    df_formations['Formateur_clean'] = df_formations['Formateur 1'].apply(clean_nom)

    # Dates au format datetime
    final_float['Date'] = pd.to_datetime(final_float['Date'], errors='coerce')
    df_formations['Date de début'] = pd.to_datetime(df_formations['Date de début'], errors='coerce')

    # Ajouter Mois
    final_float['Mois'] = final_float['Date'].dt.strftime('%Y-%m')
    df_formations['Mois'] = df_formations['Date de début'].dt.strftime('%Y-%m')

    # Jours réalisés
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    # Grouper jours réalisés
    jours_realises = final_float.groupby(['Code Mission', 'Acteur', 'Acteur_clean', 'Mois', 'PV'])['Jours Réalisés'].sum().reset_index()

    # Grouper jours formation
    jours_formations = df_formations.groupby(['Formateur_clean', 'Mois'])['Nombre de jour'].sum().reset_index()

    # Fusion pour soustraction
    df_ca = jours_realises.merge(
        jours_formations,
        how='left',
        left_on=['Acteur_clean', 'Mois'],
        right_on=['Formateur_clean', 'Mois']
    )
    df_ca['Nombre de jour'] = df_ca['Nombre de jour'].fillna(0)

    # Jours ingénierie
    df_ca['Jours Ingénierie'] = df_ca['Jours Réalisés'] - df_ca['Nombre de jour']
    df_ca['Jours Ingénierie'] = df_ca['Jours Ingénierie'].apply(lambda x: max(x, 0))

    # 📌 Calcul CA Ingénierie
    df_ca['CA Ingénierie'] = df_ca['Jours Ingénierie'] * df_ca['PV']

    # Pivot
    tableau_cumul_ca_ingenierie = df_ca.pivot_table(
        index=['Code Mission', 'Acteur'],
        columns='Mois',
        values='CA Ingénierie',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Total
    tableau_cumul_ca_ingenierie['Total'] = tableau_cumul_ca_ingenierie.iloc[:, 2:].sum(axis=1)

    # Réorganisation
    colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_ca_ingenierie.columns[2:-1]) + ['Total']
    tableau_cumul_ca_ingenierie = tableau_cumul_ca_ingenierie[colonnes_ordre]

    # Ligne total général
    total_general_ca = tableau_cumul_ca_ingenierie.iloc[:, 2:].sum()
    total_general_ca['Code Mission'] = 'Total Général'
    total_general_ca['Acteur'] = ''
    tableau_cumul_ca_ingenierie = pd.concat([tableau_cumul_ca_ingenierie, pd.DataFrame([total_general_ca])], ignore_index=True)

    # Formatage (montants)
    tableau_cumul_ca_ingenierie.iloc[:, 2:] = tableau_cumul_ca_ingenierie.iloc[:, 2:].applymap(lambda x: f"{x:,.0f}".replace(",", " "))

    # Surligner les formateurs
    formateurs_clean = df_formations['Formateur_clean'].unique().tolist()
    tableau_cumul_ca_ingenierie['Est_formateur'] = tableau_cumul_ca_ingenierie['Acteur'].apply(
        lambda x: clean_nom(x) in formateurs_clean if pd.notna(x) else False
    )
    # 🔹 Ajouter une colonne pour identifier la ligne "Total Général"
    tableau_cumul_ca_ingenierie["is_total_general"] = tableau_cumul_ca_ingenierie["Code Mission"] == "Total Général"

    # 🔹 Fonction de style combinée
    def style_personnalise(row):
        styles = []
        for col in tableau_cumul_ca_ingenierie.columns:
            style = ""
            if row["is_total_general"]:  # Surligner ligne Total Général
                style += "background-color: #FFCCCC;"
            elif row.get("Est_formateur", False):  # Surligner ligne formateur
                style += "background-color: #FFF2CC;"
            if col == "Total":  # Surligner colonne Total
                style += "background-color: #D9D9D9;"
            styles.append(style)
        return styles


    # 🔹 Appliquer le style AVANT de supprimer la colonne
    styled_ca_df = tableau_cumul_ca_ingenierie.style.apply(style_personnalise, axis=1)

    # 📌 Affichage
    st.subheader("Cumul du CA Engagé Ingénierie (formateurs surlignés)")
    st.dataframe(styled_ca_df, use_container_width=True)

    # ✅ Récupérer les bons totaux depuis les tableaux (hors "Total Général" s’il y est)
    try:
        df_jours_filtered = tableau_cumul_jours_ingenierie[tableau_cumul_jours_ingenierie["Code Mission"] != "Total Général"]
        jours_realises_total = df_jours_filtered["Total"].astype(float).sum()
    except:
        jours_realises_total = 0

    try:
        df_ca_filtered = tableau_cumul_ca_ingenierie[tableau_cumul_ca_ingenierie["Code Mission"] != "Total Général"]
        ca_engage_ingenieurie_total = df_ca_filtered["Total"].replace(" ", "", regex=True).astype(float).sum()
    except:
        ca_engage_ingenieurie_total = 0

    # ✅ Met à jour les métriques globales avec les bonnes valeurs
    mission_logged_days = jours_realises_total
    ca_engage_ingenieurie = ca_engage_ingenieurie_total
    jours_ingenieurie = mission_logged_days - jours_formation
        # Section Budget (cards)
    st.subheader("Budget")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)

    pourcentage_formation = (jours_formation / mission_logged_days) * 100 if mission_logged_days else 0
    pourcentage_ingenieurie = (jours_ingenieurie / mission_logged_days) * 100 if mission_logged_days else 0

    col1,col2,col3 = st.columns(3)
    with col1 :
        st.markdown(f"""
            <div class="card">
                <div class="metric">{mission_budget:,.0f} €</div>
                <div class="label">CA Budget</div>
                <div class="delta positive">100%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    with col2: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{ca_engage_ingenieurie:,.0f} €</div>
                <div class="label">CA Engagé Ingénierie</div>
                <div class="delta {get_delta_class(percentage_budget_used)}">{percentage_budget_used:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)
    with col3: 

        st.markdown(f"""
            <div class="card">
                <div class="metric">{budget_remaining:,.0f} €</div>
                <div class="label">Solde Restant</div>
                <div class="delta {get_delta_class(percentage_budget_remaining)}">{percentage_budget_remaining:.0f}%</div>
            </div>
        """.replace(",", " "), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Section Jours (cards)
    st.subheader("Jours ")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)


    col1,col2,col3 = st.columns(3)
    with col1: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{mission_logged_days:.1f} jours</div>
                <div class="label">Jours Réalisés</div>
                <div class="delta positive">100%</div>
            </div>
        """, unsafe_allow_html=True)

    with col2: 
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_formation:.1f} jours</div>
                <div class="label">Jours de Formation</div>
                <div class="delta positive">{pourcentage_formation:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="card">
                <div class="metric">{jours_ingenieurie:.1f} jours</div>
                <div class="label">Jours d'Ingénierie</div>
                <div class="delta positive">{pourcentage_ingenieurie:.0f}%</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")

    col1,col2= st.columns(2)
    with col1: 

        # 📌 Repartir depuis df_merged pour garder la logique correcte
        intervenants = df_merged.groupby('Acteur').agg({
            'Jours Ingénierie': 'sum'
        }).reset_index()

        # 🔁 Ajouter les heures facturables (depuis final_float brut)
        heures_facturables = final_float.groupby('Acteur')['Logged Billable hours'].sum().reset_index()
        intervenants = intervenants.merge(heures_facturables, on='Acteur', how='left')

        # 🔁 Ajouter les PV
        intervenants = intervenants.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
        intervenants['PV'] = intervenants['PV'].fillna(0)

        # 🔁 Calculer CA engagé
        intervenants['CA Engagé'] = intervenants['Jours Ingénierie'] * intervenants['PV']

        # ✅ Formatage
        intervenants["Jours Ingénierie"] = intervenants["Jours Ingénierie"].round(1)
        intervenants["CA Engagé"] = intervenants["CA Engagé"].round(0).astype(int)
        intervenants["PV"] = intervenants["PV"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
        intervenants = intervenants.rename(columns={
            "Logged Billable hours": "Heures facturables enregistrées",
            "Jours Ingénierie": "Jours Réalisés"
        })

        # 🟨 Ajout colonne 
        intervenants["Est_formateur"] = intervenants["Acteur"].apply(
            lambda x: clean_nom(x) in formateurs_clean if pd.notna(x) else False
        )

        intervenants["Jours Réalisés"] = intervenants["Jours Réalisés"].map(lambda x: f"{x:.1f}")
        intervenants["Heures facturables enregistrées"] = intervenants["Heures facturables enregistrées"].map(lambda x: f"{x:.1f}")
        # 🎨 Surlignage formateurs
        def highlight_formateurs(row):
            return ['background-color: #FFF2CC' if row.get('Est_formateur', False) else '' for _ in row]

        # 📊 Affichage
        st.subheader("Détails générales des intervenants en Ingénierie")
        st.dataframe(intervenants.style.apply(highlight_formateurs, axis=1), use_container_width=True)


    
    # with col2:
    #     st.subheader("Détails du CA Engagé pour les Formateurs")

    #     if jours_formation_par_formateur:
    #         # Nettoyer les noms des formateurs (mêmes règles que pour les Acteurs)
    #         def clean_nom(nom):
    #             if pd.isna(nom):
    #                 return ""
    #             # Supprimer les accents et mettre en minuscule
    #             nom = str(nom).strip().lower()
    #             nom = unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('utf-8')
    #             return nom

    #         formateur_details = []
    #         for nom_formateur, jours_realises in jours_formation_par_formateur.items():
    #             nom_clean = clean_nom(nom_formateur)
    #             pv = rates_cleaned.loc[rates_cleaned["Acteur_clean"] == nom_clean, "PV"].values
    #             pv = pv[0] if len(pv) > 0 else 0
    #             ca_engage = jours_realises * pv
    #             formateur_details.append({
    #                 "Formateur": nom_formateur,
    #                 "Jours Formation": round(jours_realises, 1),
    #                 "PV (€)": round(pv, 0),
    #                 "CA Engagé (€)": round(ca_engage, 0)
    #             })

    #         df_formateurs = pd.DataFrame(formateur_details)
    #         # ➕ Ajouter ligne de total général
    #         total_jours = df_formateurs["Jours Formation"].sum()
    #         total_ca = df_formateurs["CA Engagé (€)"].sum()
    #         df_formateurs.loc["Total Général"] = {
    #             "Formateur": "🧮 Total Général",
    #             "Jours Formation": round(total_jours, 1),
    #             "PV (€)": "",
    #             "CA Engagé (€)": round(total_ca, 0)
    #         }

    #         # ➕ Mise en forme
    #         df_formateurs["PV (€)"] = df_formateurs["PV (€)"].apply(lambda x: f"{x:,.0f}".replace(",", " ") if x != "" else "")
    #         df_formateurs["CA Engagé (€)"] = df_formateurs["CA Engagé (€)"].apply(lambda x: f"{x:,.0f}".replace(",", " ") if x != "" else "")
            
    #         st.dataframe(df_formateurs)
    #     else:
    #         st.info("Aucun formateur trouvé dans les données importées.")

    # Graphiques
    st.subheader("Visualisations")
    col6, col7 = st.columns(2)

    # Répartition des coûts
    with col6:
        # 5. Affichage comparatif
        st.subheader("Répartition Jours : Formation vs Ingenierie")
        data = pd.DataFrame({
            "Type": ["Formation", "ingenieurie"],
            "Jours": [jours_formation, jours_ingenieurie]
        })

        fig = px.pie(data, names="Type", values="Jours", title="Part des jours consacrés aux Formations vs Ingenierie",
                    color_discrete_sequence=["#2a9df4", "#9b59b6"])
        st.plotly_chart(fig)

    # # Répartition des heures réalisées
    with col7:
                # ✅ Vérification de la colonne Module
        if "Module" in df_formations.columns:
            # Filtrer les lignes valides
            df_formations_valid = df_formations.dropna(subset=["Module", "Nombre de jour"])

            # Grouper par module et sommer les jours
            module_jours = df_formations_valid.groupby("Module")["Nombre de jour"].sum().sort_values(ascending=True)

            # 📊 Affichage du graphique
            st.subheader(" Répartition des jours de formation par module")
            fig_module = px.bar(
                module_jours,
                x="Nombre de jour",
                y=module_jours.index,
                orientation='h',
                labels={"index": "Module", "Nombre de jour": "Jours de Formation"},
                color=module_jours,
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_module)
        else:
            st.warning("La colonne 'Module' est manquante dans le fichier des formations.")

    import plotly.graph_objects as go

    # 📌 Récupérer les données CA Engagé Ingénierie cumulées par mois
    cumul_df = df_ca.copy()
    cumul_df["Mois"] = pd.to_datetime(cumul_df["Mois"], errors="coerce")
    cumul_df = cumul_df.dropna(subset=["Mois"])  # S'assurer qu'il n'y a pas de NaT
    cumul_df = cumul_df.groupby("Mois")["CA Ingénierie"].sum().reset_index()
    cumul_df = cumul_df.sort_values(by="Mois")
    cumul_df["CA Engagé Cumulé"] = cumul_df["CA Ingénierie"].cumsum()

    # Budget mission (valeur constante)
    budget_mission = final_plan_prod["Budget (PV)"].sum()
    cumul_df["Budget Mission"] = budget_mission

    # Format mois en string lisible
    cumul_df["Mois"] = cumul_df["Mois"].dt.strftime("%Y-%m")

    # 📊 Création du graphique avec annotations visibles
    fig = go.Figure()

    # ➕ Courbe CA Engagé Cumulé
    fig.add_trace(go.Scatter(
        x=cumul_df["Mois"],
        y=cumul_df["CA Engagé Cumulé"],
        mode='lines+markers+text',
        name='CA Engagé Cumulé',
        text=[f"{v:,.0f} €" for v in cumul_df["CA Engagé Cumulé"]],
        textposition="top center",
        line=dict(color="blue"),
        marker=dict(size=6)
    ))

    # ➕ Courbe Budget constant
    fig.add_trace(go.Scatter(
        x=cumul_df["Mois"],
        y=cumul_df["Budget Mission"],
        mode='lines+markers+text',
        name='Budget Mission',
        text=[f"{budget_mission:,.0f} €"] * len(cumul_df),
        textposition="top center",
        line=dict(color="lightblue", dash='dash'),
        marker=dict(size=6)
    ))

    # 🎨 Mise en forme
    fig.update_layout(
        title=f"Évolution du CA Engagé cumulé vs Budget ({mission_code})",
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        legend_title="Type",
        template="plotly_white",
        hovermode="x unified"
    )

    # ✅ Affichage Streamlit
    st.subheader("Évolution du CA Engagé cumulé vs Budget (Dynamique) 📈")
    st.plotly_chart(fig, use_container_width=True)


    # if not cumul_ca.empty:
    #     # Création du graphique avec Matplotlib
    #     evofig, ax = plt.subplots(figsize=(8, 4))  # Ajuster la taille
        
    #     # Tracer les courbes
    #     ax.plot(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"], marker='o', label="CA Engagé Cumulé", linestyle='-', color='darkblue')
    #     ax.plot(cumul_ca["Mois"], cumul_ca["Budget Mission"], marker='o', label="Budget Mission", linestyle='-', color='lightblue')
    #         # Ajouter les valeurs au-dessus des points
    #     for x, y in zip(cumul_ca["Mois"], cumul_ca["CA Engagé Cumulé"]):
    #         ax.text(x, y, f'{y:,.0f}', ha='right', va='bottom', fontsize=8)
    #     for x, y in zip(cumul_ca["Mois"], cumul_ca["Budget Mission"]):
    #         ax.text(x, y, f'{y:,.0f}', ha='left', va='bottom', fontsize=8)
    #     # Ajouter les labels et le titre
    #     ax.set_xlabel("Mois")
    #     ax.set_ylabel("Montant (€)")
    #     ax.set_title(f"Évolution du CA Engagé cumulé vs Budget ({mission_code})")
        
    #     # Ajouter une légende
    #     ax.legend(title="Type")
        
    #     # Personnaliser l'affichage
    #     plt.xticks(rotation=45)  # Rotation des labels de l'axe X si nécessaire
    #     plt.grid(True, linestyle='--', alpha=0.6)
        
    #     # Afficher le graphique dans Streamlit
    #     st.subheader("Évolution du CA Engagé cumulé vs Budget")
    #     evo_chart_path = os.path.abspath("evo_chart.png")  # Absolute path
    #     plt.savefig(evo_chart_path, bbox_inches='tight', dpi=300)
    #     st.pyplot(evofig)
    # else:
    #     st.write("Aucune donnée disponible pour afficher le graphique.")
st.markdown("<div class='title'><b>Tableau de bord - Customer Report</b></div>", unsafe_allow_html=True)
st.image("Logo_Advent.jpg", width=300)
st.subheader("📘 Formation vs ingénierie - Sales Academy (238010)")
# Vérifiez si les données sont disponibles dans la session
if "data_plan_prod" in st.session_state and "data_float" in st.session_state:
    data_plan_prod = st.session_state["data_plan_prod"]
    data_float = st.session_state["data_float"]
    rates = st.session_state["rates"]


    # Afficher le rapport client avec les données existantes
    display_customer_report(data_plan_prod, data_float, rates)
else:
    st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")