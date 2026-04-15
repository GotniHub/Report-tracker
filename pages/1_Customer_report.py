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
import locale
import plotly.graph_objects as go
from streamlit_option_menu import option_menu # type: ignore
from auth import require_auth

require_auth()

try:
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
except locale.Error:
    pass  # Ignore l’erreur sur Streamlit Cloud

st.set_page_config(page_title="Customer Report", page_icon="📊", layout="wide")
st.logo("Logo_Advent.png", icon_image="Logom.png")
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
        gap: 22px;
        margin-bottom: 22px;
    }

    .title {
        font-family: 'Arial', sans-serif;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 20px;
        color: #1f2937;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .card {
        position: relative;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(37, 99, 235, 0.10);
        border-radius: 22px;
        padding: 28px 24px 22px 24px;
        text-align: center;
        box-shadow:
            0 10px 30px rgba(15, 23, 42, 0.08),
            0 2px 8px rgba(37, 99, 235, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        flex: 1;
        min-height: 128px;
        transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
        overflow: hidden;
    }

    .card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #2563eb, #60a5fa);
        opacity: 0.95;
    }

    .card:hover {
        transform: translateY(-6px);
        box-shadow:
            0 18px 38px rgba(15, 23, 42, 0.12),
            0 8px 18px rgba(37, 99, 235, 0.08);
        border-color: rgba(37, 99, 235, 0.22);
    }

    .metric {
        font-size: 2.35rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
        margin-bottom: 10px;
        letter-spacing: -0.8px;
    }

    .label {
        font-size: 1rem;
        color: #6b7280;
        font-weight: 500;
        margin-top: 2px;
        margin-bottom: 8px;
    }

    .delta {
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 8px;
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.04);
    }

    .positive {
        color: #15803d;
        background: rgba(34, 197, 94, 0.10);
    }

    .negative {
        color: #b91c1c;
        background: rgba(239, 68, 68, 0.10);
    }

    @media print {

        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > [data-testid="stMain"] {
            background: white !important;
        }

        [data-testid="stAppViewContainer"]::before {
            display: none !important;
            content: none !important;
        }

        .block-container {
            padding-top: 10px !important;
            padding-bottom: 10px !important;
            padding-left: 20px !important;
            padding-right: 20px !important;
        }

        .card-container {
            display: flex !important;
            gap: 12px !important;
            width: 100% !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            margin-bottom: 12px !important;
        }

        .card {
            background: white !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            backdrop-filter: none !important;
            -webkit-backdrop-filter: none !important;
            transform: none !important;
            min-height: auto !important;
            width: 100% !important;
            flex: 1 1 0 !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            overflow: visible !important;
        }

        .card::before {
            display: none !important;
            content: none !important;
        }

        .card:hover {
            transform: none !important;
            box-shadow: none !important;
        }

        .metric {
            color: #111827 !important;
            font-size: 24px !important;
        }

        .label {
            color: #374151 !important;
            font-size: 13px !important;
        }

        .delta {
            background: none !important;
            padding: 0 !important;
            font-size: 13px !important;
        }

        .positive {
            color: #15803d !important;
            background: none !important;
        }

        .negative {
            color: #b91c1c !important;
            background: none !important;
        }

        h1, h2, h3, .mission-info-container, .periode-container, .card-container, .card {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# st.markdown("""
#     <style>
#     [data-testid="stAppViewContainer"] {
#         background:
#             radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 22%),
#             radial-gradient(circle at 80% 18%, rgba(147, 197, 253, 0.16), transparent 20%),
#             radial-gradient(circle at 50% 75%, rgba(96, 165, 250, 0.10), transparent 28%),
#             linear-gradient(180deg, #f8fbff 0%, #eef4ff 52%, #e9f0fb 100%);
#         min-height: 100vh;
#     }

#     [data-testid="stAppViewContainer"]::before {
#         content: "";
#         position: fixed;
#         inset: 0;
#         background-image:
#             linear-gradient(rgba(37, 99, 235, 0.05) 1px, transparent 1px),
#             linear-gradient(90deg, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
#         background-size: 42px 42px;
#         pointer-events: none;
#         z-index: 0;
#     }

#     [data-testid="stAppViewContainer"] > [data-testid="stMain"] {
#         position: relative;
#         z-index: 1;
#     }
#     .card-container {
#         display: flex;
#         gap: 20px;
#         margin-bottom: 20px;
#     }
#     .title {
#         font-family: 'Arial', sans-serif;
#         font-size: 2.5rem;
#         text-align: center;
#         margin-bottom: 20px;
#         color: #333;
#     }
#     .card {
#         background-color: #f9f9f9;
#         border-radius: 10px;
#         padding: 20px;
#         text-align: center;
#         box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
#         flex: 1;
#     }
#     .metric {
#         font-size: 2rem;
#         font-weight: bold;
#     }
#     .delta {
#         font-size: 1.2rem;
#         margin-top: 5px;
#     }
#     .label {
#         font-size: 1rem;
#         color: #555;
#     }
#     .positive {
#         color: green;
#     }
#     .negative {
#         color: red;
#     }
#     </style>
# """, unsafe_allow_html=True)

def display_customer_report(data_plan_prod, data_float, rates, selected_intervenants):
    #logo_path = "Logo_Advent.png"

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

    # # 🟢 **Filtres interactifs**
    # st.sidebar.header("Filtres")

    # # 🔹 **Filtre de Mission**
    # mission_filter = st.sidebar.selectbox(
    #     "Sélectionnez une mission 🎯",
    #     options=data_plan_prod['Code Mission'].unique(),
    #     format_func=lambda x: f"{x} - {data_plan_prod[data_plan_prod['Code Mission'] == x]['Nom de la mission'].iloc[0]}"
    # )
    # 🔹 Budget initial depuis le fichier
    budget_initial = data_plan_prod[data_plan_prod['Code Mission'] == mission_filter]['Budget (PV)'].sum()

    # 🔄 Toggle pour activer la modification manuelle
    toggle_budget = st.sidebar.toggle("💶 Modifier manuellement le budget (optionnel)")

    # 💬 Affichage conditionnel de l’entrée manuelle
    if toggle_budget:
        budget_modifie = st.sidebar.number_input(
            "Entrez le budget manuellement (€)",
            min_value=0,
            value=int(budget_initial),
            step=1000,
            help="Ce budget remplacera celui issu du fichier."
        )
    else:
        budget_modifie = int(budget_initial)



    # **Appliquer le filtre de mission**
    filtered_plan_prod = data_plan_prod[data_plan_prod['Code Mission'] == mission_filter]
    filtered_float = data_float[data_float['Code Mission'] == mission_filter]
    # 🧠 Appliquer le filtre des intervenants si défini
    if selected_intervenants:
        filtered_float = filtered_float[filtered_float['Acteur'].isin(selected_intervenants)]
        
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
    # ✅ Utiliser le budget modifié (ou initial)
    mission_budget = budget_modifie

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

    mission_full_name = final_plan_prod['Nom de la mission'].iloc[0] if not final_plan_prod.empty else "N/A"
    # Supprimer tout ce qui est entre crochets + les crochets + espace ou tiret qui suit
    mission_name_cleaned = re.sub(r"^\[[^\]]+\]\s*[-_]?\s*", "", mission_full_name).strip()
    mission_name = mission_name_cleaned

        # Si la mission est Sales Academy (238010), stocker les jours réalisés
    if str(mission_code) == "238010":
        st.session_state["mission_logged_days"] = mission_logged_days


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

    
    # ✅ Formatage numérique AVANT styling
    tableau_cumul_jours.iloc[:, 2:] = tableau_cumul_jours.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")

    # 🔹 Fonction de style sans colonne technique
    def style_personnalise(row):
        styles = []
        is_total_row = row.name == len(tableau_cumul_jours) - 1  # dernière ligne

        for col in tableau_cumul_jours.columns:
            style = ""
            if is_total_row:
                style += "background-color: #FFCCCC;"
            elif col in ["Code Mission", "Acteur"]:
                style += "background-color: #E6E7E8;"
            elif col != "Total":
                style += "background-color: rgba(0, 51, 160, 0.2);"

            if col == "Total":
                style += "background-color: #FFCCCC;"

            styles.append(style)
        return styles

    styled_df = tableau_cumul_jours.style.apply(style_personnalise, axis=1).hide(axis="index")

    st.subheader("Cumul Jours de production réalisés")
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    #st.table(tableau_cumul_jours)
    #st.dataframe(tableau_cumul_jours)

    # with col2:

    # 📌 Calcul du CA Engagé
    final_float = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')
    final_float['CA Engagé'] = final_float['Jours Réalisés'] * final_float['PV']

    # 📌 Création du tableau croisé dynamique (CA Engagé par mission et acteur)
    tableau_cumul_ca = final_float.pivot_table(
        index=['Code Mission', 'Acteur'],
        columns='Mois',
        values='CA Engagé',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # 📌 Ajouter une colonne Total
    tableau_cumul_ca["Total"] = tableau_cumul_ca.iloc[:, 2:].sum(axis=1)

    # 📌 Réorganiser les colonnes
    colonnes_ordre = ['Code Mission', 'Acteur'] + sorted(tableau_cumul_ca.columns[2:-1]) + ['Total']
    tableau_cumul_ca = tableau_cumul_ca[colonnes_ordre]

    # 📌 Ajouter la ligne Total Général
    total_general_ca = tableau_cumul_ca.iloc[:, 2:].sum(axis=0)
    total_general_ca["Code Mission"] = "Total Général"
    total_general_ca["Acteur"] = ""

    tableau_cumul_ca = pd.concat(
        [tableau_cumul_ca, pd.DataFrame([total_general_ca])],
        ignore_index=True
    )

    # ✅ Fonction robuste de formatage €
    def format_euro(x):
        if pd.isna(x):
            return "0 €"
        if isinstance(x, str):
            x = x.replace("€", "").replace(" ", "").replace(",", ".").strip()
        try:
            return f"{int(round(float(x))):,} €".replace(",", " ")
        except:
            return "0 €"

    # ✅ Formater seulement à la fin
    tableau_cumul_ca.iloc[:, 2:] = tableau_cumul_ca.iloc[:, 2:].applymap(format_euro)

    # 🔹 Style sans colonne technique
    def style_personnalise_ca(row):
        styles = []
        is_total_row = row.name == len(tableau_cumul_ca) - 1

        for col in tableau_cumul_ca.columns:
            style = ""
            if is_total_row:
                style += "background-color: #FFCCCC;"
            elif col in ["Code Mission", "Acteur"]:
                style += "background-color: #E6E7E8;"
            elif col != "Total":
                style += "background-color: rgba(0, 51, 160, 0.2);"

            if col == "Total":
                style += "background-color: #FFCCCC;"

            styles.append(style)
        return styles

    styled_ca_df = tableau_cumul_ca.style.apply(style_personnalise_ca, axis=1).hide(axis="index")

    st.subheader("Cumul du CA Engagé")
    st.dataframe(styled_ca_df, use_container_width=True, hide_index=True)



        #st.table(tableau_cumul_ca)
        #st.dataframe(tableau_cumul_ca)

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
    intervenants['CA Engagé'] = intervenants['CA Engagé'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))

    intervenants['PV'] = intervenants['PV'].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
    # 📌 Renommer la colonne en français
    intervenants = intervenants.rename(columns={"Logged Billable hours": "Heures facturables enregistrées"})
    # 🔹 Fonction de style pour ce tableau simple
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

    # Fonction de formatage intelligent pour les heures et jours
    def format_intelligent(x):
        if x == int(x):
            return f"{int(x)}"
        else:
            return f"{x:.1f}"

    # 📌 Affichage stylisé avec format dynamique
    styled_intervenants = intervenants.style.apply(style_intervenants, axis=1).format({
        'Heures facturables enregistrées': format_intelligent,
        'Jours Réalisés': format_intelligent
    })

    st.dataframe(styled_intervenants, use_container_width=True, hide_index=True)

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
            title=f"Évolution du CA Engagé cumulé vs Budget ({mission_filter})",
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
        
    st.session_state["final_float"] = final_float
    st.session_state["intervenants"] = intervenants
    st.session_state["final_plan_prod"] = final_plan_prod
    st.session_state["mission_filter"] = mission_filter
    st.session_state["rates"] = rates

st.markdown("<div class='title'><b>Tableau de bord - Customer Report</b></div>", unsafe_allow_html=True)
    
navbar=st.container()
# with navbar:
#     selected = option_menu(
#         menu_title=None,
#         options=["Rapport Client","Plus de Visualisations","Rapport Jours"],
#         icons=["house","book","book"], menu_icon="cast", default_index=0, orientation="horizontal",
#         styles={
#             "nav-link-selected": {"background-color": "#0033A0", "color": "white"},  # Couleur de l'élément sélectionné
#         }
#     )
selected = "Rapport Client"  # ou "Plus de Visualisations", selon ce que tu veux afficher
    
# st.image("Logo_Advent.png", width=300)    
# 🔄 Afficher le bon logo selon le code mission

from ui import inject_shared_css, show_sidebar

inject_shared_css()
show_sidebar()
# 🧠 Contenu des pages
if selected == "Rapport Client":
    # Vérifiez si les données sont disponibles dans la session
    if "data_plan_prod" in st.session_state and "data_float" in st.session_state:
        data_plan_prod = st.session_state["data_plan_prod"]
        data_float = st.session_state["data_float"]
        rates = st.session_state["rates"]
        # 🟢 **Filtres interactifs**
        st.sidebar.header("Filtres")

        # # 🔹 **Filtre de Mission**
        # mission_filter = st.sidebar.selectbox(
        #     "Sélectionnez une mission 🎯",
        #     options=data_plan_prod['Code Mission'].unique(),
        #     format_func=lambda x: f"{x} - {data_plan_prod[data_plan_prod['Code Mission'] == x]['Nom de la mission'].iloc[0]}"
        # )
        # 🔹 On propose ici directement le choix de la mission AVANT d'afficher le logo
        mission_filter = st.sidebar.selectbox(
            "Sélectionnez une mission 🎯",
            options=data_plan_prod['Code Mission'].unique(),
            format_func=lambda x: f"{x} - {data_plan_prod[data_plan_prod['Code Mission'] == x]['Nom de la mission'].iloc[0]}",
            key="mission_selector"  # important pour le bon rafraîchissement du widget
        )
        # 🔹 Extraire les intervenants disponibles pour la mission sélectionnée
        intervenants_disponibles = data_float[data_float['Code Mission'] == mission_filter]['Acteur'].dropna().unique()

        # 🔹 Ajouter le filtre multi-sélection des intervenants
        selected_intervenants = st.sidebar.multiselect(
            "👤 Filtrer par intervenant(s) (optionnel)",
            options=intervenants_disponibles,
            default=intervenants_disponibles,  # Par défaut tous sont sélectionnés
            key="intervenant_selector"
        )

        # Par défaut
        logo_path = "Logo_Advent.png"
        first_letter = str(mission_filter)[0].upper()

        if first_letter == "A":
            logo_path = "Logo_Advent.png"
        elif first_letter == "F":
            logo_path = "Logo_Africa.jpg"
        elif first_letter == "P":
            logo_path = "Logo_Partner.png"
        elif first_letter == "S":
            logo_path = "Logo_Adventage_Sud.png"
        elif first_letter in ["L", "O", "M"]:
            logo_path = "Logo_Adventae.png"

        st.image(logo_path, width=300)

        # Afficher le rapport client avec les données existantes
        display_customer_report(data_plan_prod, data_float, rates, selected_intervenants)
    else:
        st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")

elif selected == "Plus de Visualisations":
    st.subheader("📈 Plus de Visualisations")
    col6, col7 = st.columns(2)
    if "final_float" in st.session_state and "intervenants" in st.session_state and "final_plan_prod" in st.session_state:
        final_float = st.session_state["final_float"]
        intervenants = st.session_state["intervenants"]
        final_plan_prod = st.session_state["final_plan_prod"]
        mission_filter = st.session_state["mission_filter"]
        rates = st.session_state["rates"] 
    else:
        st.warning("Veuillez d'abord consulter le Rapport Client pour générer les données.")

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
    st.subheader("Heatmap des Heures Facturées par Intervenant ")
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
        title="Contribution du CA Engagé par Mois ",
        xaxis_title="Mois",
        yaxis_title="CA Engagé (€)",
        template="plotly_white",
    )

    # 📌 Affichage du graphique dans Streamlit
    st.subheader("Contribution du CA Engagé par Mois ")
    st.plotly_chart(waterfall_fig)

elif selected == "Rapport Jours":

    def display_customer_report(data_plan_prod, data_float, rates):
        #logo_path = "Logo_Advent.png"

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
            "Sélectionnez une mission 🎯",
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
            
        # 🔹 Intervenants disponibles pour cette mission
        intervenants_list = filtered_float["Acteur"].dropna().unique()

        # 🔹 Filtre multisélection
        selected_intervenants = st.sidebar.multiselect(
            "👥 Filtrer par Intervenant(s)",
            options=intervenants_list,
            default=intervenants_list
        )

        # 🔹 Application du filtre
        filtered_float = filtered_float[filtered_float["Acteur"].isin(selected_intervenants)]

        # 🔹 **Finaliser les variables**
        final_plan_prod = filtered_plan_prod.copy()
        final_float = filtered_float.copy()

        
        # 📌 Calcul des jours réalisés par intervenant
        final_float['Jours Réalisés'] = final_float['Logged Billable hours'] / 8


        # 📌 Fusionner les données avec "Rates" pour récupérer le PV par acteur
        merged_data = final_float.merge(rates[['Acteur', 'PV']], on='Acteur', how='left')

        # Remplacer les valeurs manquantes de PV par 0
        merged_data['PV'] = merged_data['PV'].fillna(0)

        # Calculs principaux
        mission_budget = final_plan_prod['Budget (PV)'].sum()
        mission_logged_hours = final_float['Logged Billable hours'].sum()
        mission_logged_days = mission_logged_hours / 8  # Conversion en jours


        
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

            # Si la mission est Sales Academy (238010), stocker les jours réalisés
        if str(mission_code) == "238010":
            st.session_state["mission_logged_days"] = mission_logged_days


        # 🔹 Forcer l'affichage avec un seul chiffre après la virgule
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


        # Section Jours (cards)
        st.subheader("Jours ")
        st.markdown('<div class="card-container">', unsafe_allow_html=True)

        objectif_jours = st.sidebar.number_input(
            "🎯 Objectif de jours à réaliser (Jours budget)",
            min_value=1,
            max_value=1000,
            value=60,
            step=1
        )
        mission_logged_days = round(mission_logged_days, 1)
        jours_restants = round(objectif_jours - mission_logged_days, 1)
        pourcentage_realise = (mission_logged_days / objectif_jours) * 100 if objectif_jours > 0 else 0
        pourcentage_restants = 100 - pourcentage_realise
        # 🧠 Classe CSS dynamique
        def get_delta_class(delta):
            return "positive" if delta >= 0 else "negative"
        
        col1,col2,col3,col4 = st.columns(4)
        with col1: 
            st.markdown(f"""
                <div class="card">
                    <div class="metric">{objectif_jours:.1f} jours</div>
                    <div class="label">Jours Budget</div>
                    <div class="delta positive">100%</div>
                </div>
            """, unsafe_allow_html=True)

        with col2: 
            st.markdown(f"""
                <div class="card">
                    <div class="metric">{mission_logged_days:.1f} jours</div>
                    <div class="label">Jours Réalisés</div>
                    <div class="delta {get_delta_class(pourcentage_realise)}">{pourcentage_realise:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="card">
                    <div class="metric">{jours_restants:.1f} jours</div>
                    <div class="label">Jours Restants</div>
                    <div class="delta {get_delta_class(pourcentage_restants)}">{pourcentage_restants:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col4: 
            st.markdown(f"""
                <div class="card">
                    <div class="metric">{pourcentage_realise:.1f}%</div>
                    <div class="label"> Avancement</div>
                    <div class="delta {'positive' if pourcentage_realise >= 100 else 'negative'}">- {jours_restants:.1f} j restants</div>
                </div>
            """, unsafe_allow_html=True)

            
        st.write("")


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

        
        # ✅ Formatage numérique AVANT styling
        
        tableau_cumul_jours.iloc[:, 2:] = tableau_cumul_jours.iloc[:, 2:].applymap(lambda x: f"{x:.1f}")
        # 🔹 Ajouter une colonne pour identifier la ligne "Total Général"
        tableau_cumul_jours["is_total_general"] = tableau_cumul_jours["Code Mission"] == "Total Général"

        # 🔹 Fonction de style combinée
        def style_personnalise(row):
            styles = []
            for col in tableau_cumul_jours.columns:
                style = ""
                if row["is_total_general"]:  # Surligner ligne Total Général
                    style += "background-color: #FFCCCC;"
                if col == "Total":  # Surligner colonne Total
                    style += "background-color: #D9D9D9;"
                styles.append(style)
            return styles

        # 🔹 Appliquer le style après formatage
        styled_df = tableau_cumul_jours.style.apply(style_personnalise, axis=1)

        # 📌 Affichage
        st.subheader("Cumul Jours de production réalisés")
        st.dataframe(styled_df, use_container_width=True)

        #st.table(tableau_cumul_jours)
        #st.dataframe(tableau_cumul_jours)

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
        intervenants["CA Engagé"] = intervenants["CA Engagé"].round(0).astype(int)

        intervenants["PV"] = intervenants["PV"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
        # 📌 Renommer la colonne en français
        intervenants = intervenants.rename(columns={"Logged Billable hours": "Heures facturables enregistrées"})
        # 📌 Afficher les résultats sous forme de tableau
        st.write(intervenants)

        # Graphiques
        st.subheader("Visualisations")
        import plotly.express as px
        bar_chart = px.bar(
            intervenants,
            x='Acteur',
            y='Jours Réalisés',
            title="Jours Réalisés par Intervenant"
        )
        st.plotly_chart(bar_chart)

        heatmap_data = final_float.pivot_table(
            index="Acteur",
            columns="Mois",
            values="Jours Réalisés",
            aggfunc="sum",
            fill_value=0
        )

        heatmap_fig = px.imshow(
            heatmap_data.values,
            labels=dict(x="Mois", y="Acteur", color="Jours Réalisés"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="blues",
        )
        heatmap_fig.update_layout(title="Heatmap des Jours Réalisés par Intervenant")
        st.plotly_chart(heatmap_fig)

        objectif_jours = 60  # ou une valeur extraite de `data_plan_prod`
        pourcentage_realise = (mission_logged_days / objectif_jours) * 100
        st.metric("Avancement", f"{pourcentage_realise:.1f}%", delta=None)

        gantt_df = final_float.copy()
        gantt_df["Start"] = gantt_df["Date"]
        gantt_df["End"] = gantt_df["Date"]

        fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Acteur", color="Acteur")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig)

    
        # Vérifiez si les données sont disponibles dans la session
    if "data_plan_prod" in st.session_state and "data_float" in st.session_state:
        data_plan_prod = st.session_state["data_plan_prod"]
        data_float = st.session_state["data_float"]
        rates = st.session_state["rates"]


        # Afficher le rapport client avec les données existantes
        display_customer_report(data_plan_prod, data_float, rates)
    else:
        st.warning("Aucune donnée disponible. Veuillez importer un fichier dans la page d'importation.")