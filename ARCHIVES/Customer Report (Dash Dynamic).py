import pandas as pd
import streamlit as st
import plotly.express as px
import pdfkit
from jinja2 import Template
import os
import plotly.graph_objects as go
import re
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components  # Ajout de l'import correct


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

    # 🟢 **Filtres interactifs**
    st.sidebar.header("Filtres")

    # 🔹 **Filtre de Mission**
    mission_filter = st.sidebar.selectbox(
        "Sélectionnez une mission",
        options=data_plan_prod['Code Mission'].unique(),
        format_func=lambda x: f"{x} - {data_plan_prod[data_plan_prod['Code Mission'] == x]['Nom de la mission'].iloc[0]}"
    )

    # **Appliquer le filtre de mission**
    filtered_plan_prod = data_plan_prod[data_plan_prod['Code Mission'] == mission_filter]
    filtered_float = data_float[data_float['Code Mission'] == mission_filter]

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

    # 🔹 **Finaliser les variables**
    final_plan_prod = filtered_plan_prod.copy()
    final_float = filtered_float.copy()

    
    # 📌 Calcul des jours réalisés par intervenant
    final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8


    # 📌 Fusionner les données avec "Rates" pour récupérer le PV par acteur
    merged_data = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')

    # Remplacer les valeurs manquantes de PV par 0
    merged_data['PV'] = merged_data['PV'].fillna(0)

    # 📌 Calcul du CA Engagé
    merged_data['CA Engagé'] = merged_data['Jours Réalisés'] * merged_data['PV']
    ca_engage_total = merged_data['CA Engagé'].sum()

    # Calculs principaux
    mission_budget = final_plan_prod['Budget (PV)'].sum()
    mission_logged_hours = final_float['Logged Billable hours'].sum()
    mission_logged_days = mission_logged_hours / 8  # Conversion en jours
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

    mission_full_name = final_plan_prod['Code Mission'].iloc[0] if not final_plan_prod.empty else "N/A"
    mission_name_match = re.search(r"\]-(.*)", mission_full_name)
    mission_name = mission_name_match.group(1).strip() if mission_name_match else mission_full_name

    # 🔹 Forcer l'affichage avec un seul chiffre après la virgule
    mission_budget = round(mission_budget, 0)
    ca_engage_total = round(ca_engage_total, 0)
    budget_remaining = round(budget_remaining, 0)
    mission_logged_days = round(mission_logged_days, 1)


    # Affichage des informations sous forme de tableau stylisé
    col1,col2 = st.columns(2) 
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
                }}
                .mission-info-table td {{
                    border: 1px solid black;
                    padding: 8px;
                    text-align: left;
                    font-weight: bold;
                }}
                .mission-info-table td:nth-child(2) {{
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


    # Section Budget (cards)
    st.subheader("Budget 💵💰")
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
    st.subheader("Jours 📆 ")
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

    col1,col2 = st.columns(2)

    with col1:
        # 📌 Extraire et transformer les données
        final_float['Mois'] = pd.to_datetime(final_float['Date']).dt.strftime('%Y-%m')
        final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8

        # 📌 Création du tableau croisé dynamique (cumul des jours réalisés par mission et acteur)
        tableau_cumul_jours = final_float.pivot_table(
            index=['Code Mission', 'Acteur'],
            columns='Mois',
            values='Jours Réalisés',
            aggfunc='sum',
            fill_value=0  # Remplace les NaN par 0
        ).reset_index()

        # 📌 Ajouter une colonne "Total Jours Réalisés"
        tableau_cumul_jours["Total"] = tableau_cumul_jours.iloc[:, 2:].sum(axis=1)

        # 📌 Réorganiser les colonnes pour afficher 'Total' après 'Acteur'
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_jours.columns[2:-1]) + ['Total']
        tableau_cumul_jours = tableau_cumul_jours[colonnes_ordre]

        # 📌 Ajouter une ligne "Total Général" en bas du tableau des jours réalisés
        total_general_jours = tableau_cumul_jours.iloc[:, 2:].sum(axis=0)  # Somme des jours réalisés par mois
        total_general_jours["Code Mission"] = "Total Général"
        total_general_jours["Acteur"] = ""

        # 📌 Ajouter la ligne au DataFrame
        tableau_cumul_jours = pd.concat([tableau_cumul_jours, pd.DataFrame([total_general_jours])], ignore_index=True)

        tableau_cumul_jours.iloc[:, 2:] = tableau_cumul_jours.iloc[:, 2:].round(1)
    
        # 📌 Affichage du tableau dans Streamlit
        st.subheader("Cumul Jours de production réalisés 📆")
        st.dataframe(tableau_cumul_jours)

    with col2:

        # 📌 Calcul du CA Engagé
        final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
        final_float['CA Engagé'] = final_float['Jours Réalisés'] * final_float['PV']

        # 📌 Création du tableau croisé dynamique (CA Engagé par mission et acteur)
        tableau_cumul_ca = final_float.pivot_table(
            index=['Code Mission', 'Acteur'],
            columns='Mois',
            values='CA Engagé',
            aggfunc='sum',
            fill_value=0  # Remplace les NaN par 0
        ).reset_index()

        # 📌 Ajouter une colonne "Total CA Engagé"
        tableau_cumul_ca["Total"] = tableau_cumul_ca.iloc[:, 2:].sum(axis=1)

        # 📌 Réorganiser les colonnes pour afficher 'Total' après 'Acteur'
        colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_ca.columns[2:-1]) + ['Total']
        tableau_cumul_ca = tableau_cumul_ca[colonnes_ordre]

        # 📌 Ajouter une ligne "Total Général" en bas du tableau du CA engagé
        total_general_ca = tableau_cumul_ca.iloc[:, 2:].sum(axis=0)  # Somme des CA engagés par mois
        total_general_ca["Code Mission"] = "Total Général"
        total_general_ca["Acteur"] = ""

        # 📌 Ajouter la ligne au DataFrame
        tableau_cumul_ca = pd.concat([tableau_cumul_ca, pd.DataFrame([total_general_ca])], ignore_index=True)
        
        #tableau_cumul_ca.iloc[:, 2:] = tableau_cumul_ca.iloc[:, 2:].round(0)
        # Appliquer le formatage pour les montants
        tableau_cumul_ca.iloc[:, 2:] = tableau_cumul_ca.iloc[:, 2:].applymap(lambda x: f"{x:,.0f}".replace(",", " "))

        # 📌 Affichage du tableau dans Streamlit
        st.subheader("Cumul du CA Engagé 💵💰")
        st.dataframe(tableau_cumul_ca)

        # Détails des intervenants
    st.subheader("Détails générales des intervenants 📋👥")

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
    intervenants["CA Engagé"] = intervenants["CA Engagé"].round(0).astype(int)

    intervenants["PV"] = intervenants["PV"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
    # 📌 Renommer la colonne en français
    intervenants = intervenants.rename(columns={"Logged Billable hours": "Heures facturables enregistrées"})
    # 📌 Afficher les résultats sous forme de tableau
    st.write(intervenants)

    # Graphiques
    st.subheader("Visualisations 📊")
    col6, col7 = st.columns(2)

    # Répartition des coûts
    with col6:
        if not final_float.empty:
            pie_chart = px.pie(
                intervenants,
                values='CA Engagé',  # 📌 Utiliser le CA Engagé pour la répartition
                names='Acteur',
                title="Répartition des coûts par intervenant",
                hover_data={'Jours Réalisés': True},  # 📌 Ajouter le nombre de jours réalisés en hover
                labels={'CA Engagé': 'CA Engagé (€)', 'Jours Réalisés': 'Jours Réalisés'}
            )

            # Activer le pourcentage et le CA Engagé sur le camembert
            pie_chart.update_traces(
                textinfo='percent+label',  # 📌 Afficher le pourcentage + nom de l'intervenant
                hoverinfo='label+value+percent+text',  # 📌 Ajouter l'info CA Engagé (€) et le %
                textposition='inside'
            )

            # 📌 Afficher le graphique
            st.plotly_chart(pie_chart)
            
        else:
            st.warning("Aucune donnée disponible pour afficher la répartition des coûts.")

    # Répartition des heures réalisées
    with col7:
        bar_chart = px.bar(
            intervenants,
            x='Acteur',
            y='Jours Réalisés',
            title="Jours Réalisés par Intervenant"
        )

        st.plotly_chart(bar_chart)

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


        # 📌 Création du graphique avec Plotly
    fig = px.line(
        cumul_ca,
        x="Mois",
        y=["CA Engagé Cumulé", "Budget Mission"],
        markers=True,
        title=f"Évolution du CA Engagé cumulé vs Budget ({mission_filter})",
        labels={"value": "Montant (€)", "Mois": "Mois", "variable": "Type"},
    )

    # 📌 Personnaliser le style du graphique
    fig.update_layout(
        title={"x": 0.5, "xanchor": "center"},
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        legend_title="Type",
        template="plotly_white",
    )

    # 📌 Affichage du graphique dans Streamlit
    st.subheader("Évolution du CA Engagé cumulé vs Budget ( Dynamique ) 📈")
    st.plotly_chart(fig)

    import plotly.figure_factory as ff
    # 📌 Calculer les jours réalisés (Logged Billable hours / 8)
    final_float["Jours Réalisés"] = final_float["Logged Billable hours"] / 8

    # 📌 Création d'une table pivotée : intervenants en ligne, mois en colonne
    heatmap_data = final_float.pivot_table(
        index="Acteur",
        columns="Mois",
        values="Jours Réalisés",
        aggfunc="sum",
        fill_value=0
    )

    # 📌 Création de la heatmap avec Plotly
    heatmap_fig = px.imshow(
        heatmap_data.values,
        labels=dict(x="Mois", y="Acteur", color="Jours Réalisés"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="blues",
    )

    # 📌 Personnalisation du visuel
    heatmap_fig.update_layout(
        title="Heatmap des Heures Facturées par Intervenant",
        xaxis_title="Mois",
        yaxis_title="Intervenants",
        template="plotly_white",
    )

    # 📌 Affichage du graphique
    st.subheader("Heatmap des Heures Facturées par Intervenant 🔥")
    st.plotly_chart(heatmap_fig)

    # 📌 Préparer les données : contribution de chaque mois au CA total
    waterfall_data = final_float.groupby("Mois")["CA Engagé"].sum().reset_index()

    # 📌 Calcul du total correct (somme de toutes les contributions par mois)
    total_ca_engage = waterfall_data["CA Engagé"].sum()

    # 📌 Définition des mesures (toutes en "relative" sauf le total qui est "total")
    measures = ["relative"] * len(waterfall_data) + ["total"]

    # 📌 Création du graphique Waterfall
    waterfall_fig = go.Figure(go.Waterfall(
        name="CA Engagé",
        orientation="v",
        measure=measures,  # Appliquer les mesures correctes
        x=waterfall_data["Mois"].tolist() + ["Total"],  # Ajouter le total dans l'axe X
        y=waterfall_data["CA Engagé"].tolist() + [total_ca_engage],  # Ajouter le vrai total dans Y
        connector={"line": {"color": "rgb(63, 63, 63)"}},  # Ligne de connexion entre les barres
    ))

    # 📌 Personnalisation du visuel
    waterfall_fig.update_layout(
        title="Contribution du CA Engagé par Mois 💰",
        xaxis_title="Mois",
        yaxis_title="CA Engagé (€)",
        template="plotly_white",
    )

    # 📌 Affichage du graphique dans Streamlit
    st.subheader("Contribution du CA Engagé par Mois 💰")
    st.plotly_chart(waterfall_fig)


st.markdown("<div class='title'><b>📊 Tableau de bord - Customer Report</b></div>", unsafe_allow_html=True)
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
