import pandas as pd
import streamlit as st
import plotly.express as px
import os
import plotly.graph_objects as go
import re
import numpy as np
import streamlit.components.v1 as components  # Ajout de l'import correct
import locale

# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

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
    
    # 🔒 Missions Synodis (sélection automatique, sans filtre manuel)
    missions_synodis_codes = ["24692", "24030", "A113002"]

    # Filtrer directement les deux bases sur ces codes
    final_plan_prod = data_plan_prod[data_plan_prod["Code Mission"].isin(missions_synodis_codes)].copy()
    final_float = data_float[data_float["Code Mission"].isin(missions_synodis_codes)].copy()

    # Forcer le budget de la mission 24692 à zéro
    final_plan_prod.loc[final_plan_prod["Code Mission"] == "24692", "Budget (PV)"] = 0


        
    # 🔹 **Ajouter les filtres de période**
    date_min = final_float["Date"].min()
    date_max = final_float["Date"].max()

    date_debut = st.sidebar.date_input("📅 Date Début", value=date_min)
    date_fin = st.sidebar.date_input("📅 Date Fin", value=date_max)

    # 🔹 Convertir les dates choisies en format datetime
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)

    # 🟢 **Application du Filtre de Période**
    if date_debut and date_fin:
        final_float = final_float[(final_float["Date"] >= date_debut) & (final_float["Date"] <= date_fin)]
    else:
        final_float = data_float.copy()

        # 🔹 Vérification de la présence des données après filtrage
    if final_float.empty:
        st.warning("⚠️ Aucune donnée disponible pour la période sélectionnée.")
        st.stop()

    # 🔹 **Finaliser les variables**
    # final_plan_prod = final_plan_prod.copy()
    final_float = final_float.copy()

    
    # 📌 Calcul des jours réalisés par intervenant
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    # ✅ AJOUT ICI :
    final_float["Mission fusionnée"] = final_float["Code Mission"].apply(
        lambda x: "24692_A113002" if x in ["24692", "A113002"] else x
    )

    # 📌 Fusionner les données avec "Rates" pour récupérer le PV par acteur
    merged_data = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')

    # Remplacer les valeurs manquantes de PV par 0
    merged_data['PV'] = merged_data['PV'].fillna(0)

    # 📌 Calcul du CA Engagé
    merged_data['CA Engagé'] = merged_data['Jours Réalisés'] * merged_data['PV']
    ca_engage_total = merged_data['CA Engagé'].sum()

    # ✅ Toggle pour ajouter manuellement un budget supplémentaire
    ajouter_budget_manuel = st.sidebar.toggle("➕ Ajouter un budget manuellement")

    budget_manuel = 0  # Valeur par défaut

    if ajouter_budget_manuel:
        budget_manuel = st.sidebar.number_input(
            "Montant à ajouter (Reste budget à affecter) en €",
            min_value=0,
            step=1000
        )

    # 🟢 Générer le tableau HTML avec pandas
    missions_resume = final_plan_prod[["Code Mission", "Nom de la mission", "Budget (PV)"]].copy()
    # ✅ Permettre la modification manuelle des budgets existants
    modifier_budgets = st.sidebar.toggle("📝 Modifier les budgets des missions sélectionnées")

    if modifier_budgets:
        st.sidebar.markdown("**Modification des budgets par mission :**")
        for idx, row in missions_resume.iterrows():
            nouveau_budget = st.sidebar.number_input(
                f"{row['Nom de la mission']} (Code {row['Code Mission']})",
                min_value=0,
                value=int(row['Budget (PV)']),
                step=1000,
                key=f"budget_modif_{idx}"
            )
            missions_resume.at[idx, "Budget (PV)"] = nouveau_budget

    # ➕ Ajouter la ligne "Reste budget à affecter" si besoin
    if budget_manuel > 0:
        nouvelle_ligne = pd.DataFrame({
            "Code Mission": ["-"],
            "Nom de la mission": ["Reste budget à affecter"],
            "Budget (PV)": [budget_manuel]
        })
        missions_resume = pd.concat([missions_resume, nouvelle_ligne], ignore_index=True)

    # Calcul du total général
    total_budget = missions_resume["Budget (PV)"].sum()

    # ➕ Ajouter la ligne Total Général
    total_row = pd.DataFrame({
        "Code Mission": ["–"],
        "Nom de la mission": ["Total Général"],
        "Budget (PV)": [total_budget]
    })

    missions_resume = pd.concat([missions_resume, total_row], ignore_index=True)

    # Forcer la colonne Budget (PV) en numérique (au cas où)
    missions_resume["Budget (PV)"] = pd.to_numeric(missions_resume["Budget (PV)"], errors="coerce").fillna(0)

    # Ensuite appliquer le format
    missions_resume["Budget (PV)"] = missions_resume["Budget (PV)"].apply(
        lambda x: f"{x:,.0f} €".replace(",", " ")
    )

    # ✅ Et maintenant on recalcule mission_budget pour les indicateurs
    mission_budget = missions_resume[missions_resume["Nom de la mission"] != "Total Général"]["Budget (PV)"].str.replace(" €","").str.replace(" ","").astype(float).sum()

    # Puis tes autres calculs restent inchangés
    mission_logged_hours = final_float['Logged Billable hours'].sum()
    mission_logged_days = mission_logged_hours / 8
    budget_remaining = mission_budget - ca_engage_total
    percentage_budget_used = (ca_engage_total / mission_budget) * 100 if mission_budget != 0 else 0
    percentage_budget_remaining = (budget_remaining / mission_budget) * 100 if mission_budget != 0 else 0

    #percentage_days_used = (mission_logged_days / 20) * 100 if mission_logged_days != 0 else 0

    # Fonction pour déterminer la classe CSS de la flèche (positive ou negative)
    def get_delta_class(delta):
        return "positive" if delta >= 0 else "negative"
    
    # Extraire les informations de la mission sélectionnée
    if 'Client' in final_float.columns and not final_float.empty:
        mission_client = final_float['Client'].iloc[0]
    else:
        mission_client = "N/A"

    mission_code = final_plan_prod['Code Mission'].iloc[0] if not final_plan_prod.empty else "N/A"

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
    col1,col2,col3 = st.columns([2,1,2])
    with col1: 
        # Supposons que `final_plan_prod` contient toutes les missions sélectionnées
        st.markdown(f"""
            <style>
                .multi-mission-container {{
                    display: flex;
                    flex-direction: column;
                    margin-bottom: 20px;
                }}
                .multi-mission-table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 1rem;
                    border-radius: 8px;
                    overflow: hidden;
                    border: 2px solid #0033A0;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
                }}
                .multi-mission-table th, .multi-mission-table td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: left;
                    font-weight: bold;
                }}
                .multi-mission-table th {{
                    background-color: rgba(0, 51, 160, 0.2);
                    color: black;
                    text-align: left;
                }}
                .multi-mission-table td:nth-child(2) {{
                    background-color: #E6E7E8;
                    color: black;
                }}
        """, unsafe_allow_html=True)

        # Affichage HTML final avec Streamlit
        st.markdown(f"""
            <div class="multi-mission-container">
                <h4>📋 Liste des missions sélectionnées :</h4>
                {missions_resume.to_html(index=False, classes="multi-mission-table", justify="left")}
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.write("")

    with col3 : 
        # 🔥 Créer l'affichage de la période en "Mois Année"
        mois_debut = date_debut.strftime("%B %Y").capitalize()
        mois_fin = date_fin.strftime("%B %Y").capitalize()
        st.markdown(f"""
            <style>
            .info-container {{
                display: flex;
                gap: 30px;
            }}
            .client-container, .periode-container {{
                border: 2px solid #0033A0;
                border-radius: 15px;
                padding: 15px 25px;
                background-color: #E6E7E8;
                box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.5);
                text-align: center;
            }}
            .client-label, .periode-text {{
                font-size: 1.2rem;
                font-weight: bold;
                color: #333;
            }}
            .client-name, .periode-date {{
                color: #0033A0;
                font-size: 1.3rem;
                font-weight: bold;
                margin-top: 5px;
            }}
            </style>
            <div class="info-container">
                <div class="client-container">
                    <div class="client-label">🏷️ Client :</div>
                    <div class="client-name">SINODIS (SHANGHAI) Co. Ltd</div>
                </div>
                <div class="periode-container">
                    <div class="periode-text">📅 Période sélectionnée :</div>
                    <div class="periode-date">{mois_debut} - {mois_fin}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Section Budget (cards)
    st.subheader("Budget")
    st.markdown('<div class="card-container">', unsafe_allow_html=True)

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
                <div class="metric">{ca_engage_total:,.0f} €</div>
                <div class="label">CA Engagé</div>
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
            </div>
        """, unsafe_allow_html=True)

    with col2: 
        st.write("")

    with col3:
        st.write("")
        
    st.write("")

    # col1,col2 = st.columns(2)

    # with col1:
    # 📌 Préparer les données communes (AVANT le radio)
    final_float['Mois'] = pd.to_datetime(final_float['Date']).dt.strftime('%Y-%m')
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    # ➕ Fusionner UNE SEULE FOIS au départ (avant le radio)
    if 'Nom de la mission' not in final_float.columns:
        final_float = final_float.merge(
            final_plan_prod[['Code Mission', 'Nom de la mission']],
            on='Code Mission',
            how='left'
        )

    # 📍 Choix du type d'affichage
    mode_affichage = st.sidebar.radio(
        "👁️ Mode d'affichage des jours réalisés",
        options=["Par intervenant", "Par mission"],
        index=1
    )

    if mode_affichage == "Par intervenant":
        # ➕ Tableau croisé par intervenant
        tableau_cumul_jours = final_float.pivot_table(
            index=['Mission fusionnée', 'Acteur'],
            columns='Mois',
            values='Jours Réalisés',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        tableau_cumul_jours.rename(columns={"Mission fusionnée": "Code Mission"}, inplace=True)


        tableau_cumul_jours["Total"] = tableau_cumul_jours.iloc[:, 2:].sum(axis=1)
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours.columns[2:-1]) + ['Total']
        tableau_cumul_jours = tableau_cumul_jours[colonnes_ordre]

        total_general_jours = tableau_cumul_jours.iloc[:, 2:].sum()
        total_general_jours["Code Mission"] = "Total Général"
        total_general_jours["Acteur"] = ""
        tableau_cumul_jours = pd.concat([tableau_cumul_jours, pd.DataFrame([total_general_jours])], ignore_index=True)
        tableau_cumul_jours["is_total_general"] = tableau_cumul_jours["Code Mission"] == "Total Général"

    else:
        # ➕ Tableau croisé par mission
        tableau_cumul_jours = final_float.pivot_table(
            index=['Nom de la mission'],
            columns='Mois',
            values='Jours Réalisés',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        tableau_cumul_jours['Total'] = tableau_cumul_jours.iloc[:, 1:].sum(axis=1)
        total_general_jours = tableau_cumul_jours.iloc[:, 1:].sum()
        total_general_row = pd.DataFrame([['Total Général'] + list(total_general_jours)], columns=tableau_cumul_jours.columns)
        tableau_cumul_jours = pd.concat([tableau_cumul_jours, total_general_row], ignore_index=True)
        tableau_cumul_jours["is_total_general"] = tableau_cumul_jours["Nom de la mission"] == "Total Général"

    # 🎨 Mise en forme finale
    def style_personnalise(row):
        styles = []
        for col in tableau_cumul_jours.columns:
            style = ""
            if row["is_total_general"]:
                style += "background-color: #FFCCCC;"
            elif col in ["Code Mission", "Acteur", "Nom de la mission"]:
                style += "background-color: #E6E7E8;"
            elif col == "Total":
                style += "background-color: #FFCCCC;"
            else:  # Colonnes Mois
                style += "background-color: rgba(0, 51, 160, 0.2);"
            styles.append(style)
        return styles

    styled_df = (
        tableau_cumul_jours
        .style
        .apply(style_personnalise, axis=1)
        .format(precision=1)
    )

    # 📌 Affichage final
    titre = "Cumul Jours de production réalisés"
    if mode_affichage == "Par mission":
        titre += " par mission"
    else:
        titre += " par intervenant"

    st.subheader(titre)
    st.dataframe(styled_df, use_container_width=True)


    # with col2:

    # 📌 Fusion des données AVANT (normalement déjà fusionné dans final_float plus haut)
    # (inutile de refusionner ici puisque c'est déjà fait une seule fois)

    # 📍 Choix du type d'affichage pour le CA Engagé
    mode_affichage_ca = st.sidebar.radio(
        "👁️ Mode d'affichage du CA Engagé",
        options=["Par intervenant", "Par mission"],
        index=1
    )

    # On recalcule les CA Engagés avant le pivot :
    final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
    final_float['PV'] = final_float['PV'].fillna(0)
    final_float['CA Engagé'] = final_float['Jours Réalisés'] * final_float['PV']

    if mode_affichage_ca == "Par intervenant":
        # ➕ Tableau croisé par intervenant
        tableau_cumul_ca = final_float.pivot_table(
            index=['Mission fusionnée', 'Acteur'],
            columns='Mois',
            values='CA Engagé',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        tableau_cumul_ca.rename(columns={"Mission fusionnée": "Code Mission"}, inplace=True)

        tableau_cumul_ca["Total"] = tableau_cumul_ca.iloc[:, 2:].sum(axis=1)
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_ca.columns[2:-1]) + ['Total']
        tableau_cumul_ca = tableau_cumul_ca[colonnes_ordre]

        total_general_ca = tableau_cumul_ca.iloc[:, 2:].sum()
        total_general_ca["Code Mission"] = "Total Général"
        total_general_ca["Acteur"] = ""
        tableau_cumul_ca = pd.concat([tableau_cumul_ca, pd.DataFrame([total_general_ca])], ignore_index=True)
        tableau_cumul_ca["is_total_general"] = tableau_cumul_ca["Code Mission"] == "Total Général"

    else:
        # ➕ Tableau croisé par mission
        tableau_cumul_ca = final_float.pivot_table(
            index=['Nom de la mission'],
            columns='Mois',
            values='CA Engagé',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        tableau_cumul_ca['Total'] = tableau_cumul_ca.iloc[:, 1:].sum(axis=1)
        total_general_ca = tableau_cumul_ca.iloc[:, 1:].sum()
        total_general_row = pd.DataFrame([['Total Général'] + list(total_general_ca)], columns=tableau_cumul_ca.columns)
        tableau_cumul_ca = pd.concat([tableau_cumul_ca, total_general_row], ignore_index=True)
        tableau_cumul_ca["is_total_general"] = tableau_cumul_ca["Nom de la mission"] == "Total Général"

    # 🎨 Mise en forme finale avec les couleurs demandées
    def style_personnalise_ca(row):
        styles = []
        for col in tableau_cumul_ca.columns:
            style = ""
            if row["is_total_general"]:
                style += "background-color: #FFCCCC;"
            elif col in ["Code Mission", "Acteur", "Nom de la mission"]:
                style += "background-color: #E6E7E8;"
            elif col == "Total":
                style += "background-color: #FFCCCC;"
            else:  # Colonnes Mois
                style += "background-color: rgba(0, 51, 160, 0.2);"
            styles.append(style)
        return styles
    # ➕ Formatage des colonnes numériques avec l'euro
    def format_euro(val):
        try:
            val_float = float(val)
            return f"{val_float:,.0f} €".replace(",", " ")
        except:
            return val

    # ➕ Colonnes à formater (tout sauf Code Mission et Acteur)
    colonnes_a_formater = [col for col in tableau_cumul_ca.columns if col not in ['Code Mission', 'Acteur', 'Nom de la mission', 'is_total_general']]

    styled_ca_df = (
        tableau_cumul_ca
        .style
        .apply(style_personnalise_ca, axis=1)
        .format({col: format_euro for col in colonnes_a_formater})
    )

    # 📌 Affichage final
    titre_ca = "Cumul du CA Engagé"
    if mode_affichage_ca == "Par mission":
        titre_ca += " par mission"
    else:
        titre_ca += " par intervenant"

    st.subheader(titre_ca)
    st.dataframe(styled_ca_df, use_container_width=True)

        # Détails des intervenants
    st.subheader("Détails générales des intervenants ")

    # 📌 Calcul des jours réalisés par acteur
    intervenants = final_float.groupby('Acteur').agg({
        'Logged Billable hours': 'sum'
    }).reset_index()

    intervenants['Jours Réalisés'] = intervenants['Logged Billable hours'] / 8

    # 📌 Fusionner avec Rates pour récupérer le PV
    intervenants = intervenants.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')

    # Remplacer les valeurs manquantes de PV par 0
    intervenants['PV'] = intervenants['PV'].fillna(0)

    # 📌 Calculer le CA Engagé pour chaque intervenant
    intervenants['CA Engagé'] = intervenants['Jours Réalisés'] * intervenants['PV']    # Si tu as des tableaux à afficher :
    intervenants["Jours Réalisés"] = intervenants["Jours Réalisés"].round(1)
    
    # ➔ Jours Réalisés
    intervenants['Jours Réalisés'] = intervenants['Jours Réalisés'].apply(
        lambda x: f"{x:.1f}".rstrip('0').rstrip('.') if x % 1 != 0 else f"{int(x)}"
    )
    # ➔ PV et CA engagé avec €
    intervenants['PV'] = intervenants['PV'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
    intervenants['CA Engagé'] = intervenants['CA Engagé'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
    # 📌 Renommer la colonne en français
    intervenants = intervenants.rename(columns={"Logged Billable hours": "Heures facturables enregistrées"})
    # ➔ Heures facturables enregistrées (même logique de suppression du .0 si entier)
    intervenants['Heures facturables enregistrées'] = intervenants['Heures facturables enregistrées'].apply(
        lambda x: f"{x:.1f}".rstrip('0').rstrip('.') if x % 1 != 0 else f"{int(x)}"
    )

    # 📌 Afficher les résultats sous forme de tableau
    # 📌 Formater les colonnes numériques avec un seul chiffre après la virgule
    # intervenants.iloc[:, 1:] = intervenants.iloc[:, 1:].applymap(lambda x: f"{x:.1f}" if isinstance(x, (int, float)) else x)

    # ➕ Style personnalisé
    def style_intervenants(row):
        styles = []
        for col in intervenants.columns:
            style = ""
            if col == "Acteur":
                style += "background-color: #E6E7E8;"
            else:
                style += "background-color: rgba(0, 51, 160, 0.2);"
            styles.append(style)
        return styles

    # 📌 Appliquer le style
    styled_intervenants = intervenants.style.apply(style_intervenants, axis=1)

    # 📌 Affichage
    st.dataframe(styled_intervenants, use_container_width=True)

    # Graphiques
    st.subheader("Visualisations")

    # Vérifier si "Jours Réalisés" et "PV Unitaire" existent avant de les utiliser
    if "Jours Réalisés" not in final_float.columns:
        final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

    if "PV" not in final_float.columns:
        # Fusionner les PV depuis Rates pour chaque intervenant
        final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')

    # Remplacer les valeurs NaN par 0 pour éviter les erreurs
    final_float['PV'] = final_float['PV'].fillna(0)


    # Calculer "CA Engagé" en multipliant les jours réalisés par le PV unitaire
    final_float['CA Engagé'] = final_float['Jours Réalisés'] * final_float['PV']

    # Remplacer les valeurs NaN par 0 (au cas où)
    final_float['CA Engagé'] = final_float['CA Engagé'].fillna(0)

    # 📌 Regrouper les données pour obtenir le cumul du CA Engagé par mois
    cumul_ca = final_float.groupby("Mois")["CA Engagé"].sum().reset_index()

    # 📌 Trier les mois dans l'ordre chronologique
    cumul_ca = cumul_ca.sort_values(by="Mois")

    # 📌 Ajouter une colonne de cumul progressif
    cumul_ca["CA Engagé Cumulé"] = cumul_ca["CA Engagé"].cumsum()

    # 📌 Récupérer le budget total de la mission sélectionnée
    budget_mission = final_plan_prod["Budget (PV)"].sum()

    # 📌 Ajouter une colonne Budget pour comparaison (ligne horizontale)
    cumul_ca["Budget Mission"] = budget_mission  # Valeur constante pour comparer avec le CA engagé

    if not cumul_ca.empty:
                # 📊 Création du graphique Plotly
        fig = go.Figure()

        # ➕ Courbe CA Engagé Cumulé
        fig.add_trace(go.Scatter(
            x=cumul_ca["Mois"],
            y=cumul_ca["CA Engagé Cumulé"],
            mode='lines+markers+text',
            name='CA Engagé Cumulé',
            text=[f"{v:,.0f} €" for v in cumul_ca["CA Engagé Cumulé"]],
            textposition="top center",
            line=dict(color="blue"),
            marker=dict(size=6)
        ))

        # ➕ Courbe Budget constant
        fig.add_trace(go.Scatter(
            x=cumul_ca["Mois"],
            y=cumul_ca["Budget Mission"],
            mode='lines+markers+text',
            name='Budget Mission',
            text=[f"{budget_mission:,.0f} €"] * len(cumul_ca),
            textposition="top center",
            line=dict(color="lightblue", dash='dash'),
            marker=dict(size=6)
        ))

        # 🎨 Mise en forme
        fig.update_layout(
            title=f"Évolution du CA Engagé cumulé vs Budget ({missions_synodis_codes})",
            xaxis_title="Mois",
            yaxis_title="Montant (€)",
            legend_title="Type",
            template="plotly_white",
            hovermode="x unified"
        )

        # ✅ Affichage Streamlit
        st.subheader("Évolution du CA Engagé cumulé vs Budget (Dynamique) 📈")
        st.plotly_chart(fig, use_container_width=True)
       
    else:
        st.write("Aucune donnée disponible pour afficher le graphique.")

st.markdown("<div class='title'><b> Tableau de bord - Customer Report</b></div>", unsafe_allow_html=True)
st.image("Logo_Advent.jpg", width=300)
# Vérifiez si les données sont disponibles dans la session
if "data_plan_prod" in st.session_state and "data_float" in st.session_state:
    data_plan_prod = st.session_state["data_plan_prod"]
    data_float = st.session_state["data_float"]
    rates = st.session_state["rates"]


    # Afficher le rapport client avec les données existantes
    display_customer_report(data_plan_prod, data_float, rates)
else:
    st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")
