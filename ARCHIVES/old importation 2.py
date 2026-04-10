import streamlit as st
import pandas as pd 
import time

def load_sheets(file):
        # Injecter le CSS pour les cards
    st.markdown("""
        <style>
        .title {
            font-family: 'Arial', sans-serif;
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)
    """Charge les feuilles nécessaires depuis un fichier Excel."""
    excel_data = pd.ExcelFile(file)
    data_plan_prod = excel_data.parse('Data Plan Prod')  # Prend la 1ère ligne comme en-tête
    data_float = excel_data.parse('Data Float')
    rates = excel_data.parse('Rates', header=1)
    return data_plan_prod, data_float,rates

def preprocess_data(data_plan_prod, data_float,rates):
    """Nettoyage et transformation des données."""
    # Exemple : renommer les colonnes et filtrer les lignes utiles
    # Renommer les colonnes pour harmoniser avec l'ancien code
    data_plan_prod = data_plan_prod.rename(columns={
        'Montant Devis': 'Budget (PV)',
         # Assurer la cohérence avec l'ancien format
    })

    data_float = data_float.rename(columns={
        'Code Territoire': 'Code Territoire',
        'Logged Billable hours': 'Heures facturées',
        'Logged Non-billable hours': 'Heures non facturées',
        'Logged fee': 'Coût'

    })
    rates = rates.rename(columns={'Nom complet': 'Acteur'})

    # Extraire les codes de mission
    data_plan_prod['Code Mission'] = data_plan_prod['Nom de la mission'].str.extract(r'\[(\w+)\]')
    data_float['Code Mission'] = data_float['Nom de la mission'].str.extract(r'\[(\w+)\]')

    # Remplir les codes de mission manquants par une valeur par défaut (par exemple : 'Unknown')
    data_plan_prod['Code Mission'] = data_plan_prod['Code Mission'].fillna('Unknown')
    data_float['Code Mission'] = data_float['Code Mission'].fillna('Unknown')

    # Gérer les missions `[Unknown]` avec un identifiant unique
    def add_unique_identifier(row, idx):
        if row['Code Mission'] == 'Unknown':
            return f"Unknown-{idx}"
        return row['Code Mission']

    # Appliquer un identifiant unique aux missions `Unknown`
    data_plan_prod['Code Mission'] = [
        add_unique_identifier(row, idx) for idx, row in data_plan_prod.iterrows()
    ]
    data_float['Code Mission'] = [
        add_unique_identifier(row, idx) for idx, row in data_float.iterrows()
    ]

    # Ajouter le code de mission au début du nom si manquant
    data_plan_prod['Nom de la mission'] = data_plan_prod.apply(
        lambda row: f"[{row['Code Mission']}] {row['Nom de la mission']}" 
        if f"[{row['Code Mission']}]" not in row['Nom de la mission'] else row['Nom de la mission'], 
        axis=1
    )
    data_float['Nom de la mission'] = data_float.apply(
        lambda row: f"[{row['Code Mission']}] {row['Nom de la mission']}" 
        if f"[{row['Code Mission']}]" not in row['Nom de la mission'] else row['Nom de la mission'], 
        axis=1
    )
    # Conversion des colonnes nécessaires en numérique
    data_plan_prod['Budget (PV)'] = pd.to_numeric(data_plan_prod['Budget (PV)'], errors='coerce').fillna(0)
    data_float['Heures facturées'] = pd.to_numeric(data_float['Heures facturées'], errors='coerce').fillna(0)
    data_float['Coût'] = pd.to_numeric(data_float['Coût'], errors='coerce').fillna(0)

    # Calculer le réel en jours travaillés
    data_float['Total Hours'] = data_float['Heures facturées'] + data_float['Heures non facturées']
    real_days = data_float.groupby('Code Mission')['Total Hours'].sum().reset_index()
    real_days['Real Days Worked'] = real_days['Total Hours'] / 8

    # Fusionner les données
    merged_data = pd.merge(
        data_plan_prod,
        real_days,
        on='Code Mission',
        how='left'
    )
    return data_plan_prod, data_float, merged_data,rates


#st.markdown("<div class='title'>📊 Importation des données - Comparaison Budget vs Réel</div>", unsafe_allow_html=True)
st.title("📊 Importation des données - Comparaison Budget vs Réel")
    # Bouton pour télécharger le template
with open("CustomerReport_Template.xlsx", "rb") as template_file:
    template_data = template_file.read()

st.download_button(
    label="📥Télécharger le modèle de données",
    data=template_data,
    file_name="CustomerReport_Template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

if "reset_import" not in st.session_state:
    st.session_state["reset_import"] = False

if st.session_state["reset_import"]:
    st.session_state.clear()
    st.session_state["reset_import"] = False
    st.rerun()

# Upload du fichier (uniquement si reset_import est False)
if not st.session_state["reset_import"]:
    uploaded_file = st.file_uploader("Importer un fichier Excel 📂", type=["xlsx"])

    if uploaded_file:
        try:
            with st.spinner("📥⏳ Chargement et traitement des données..."):
                # Charger et prétraiter les données
                data_plan_prod, data_float,rates = load_sheets(uploaded_file)
                data_plan_prod, data_float, merged_data,rates = preprocess_data(data_plan_prod, data_float,rates)
                
                # Sauvegarder les données dans la session pour utilisation ultérieure
                st.session_state["uploaded_file"] = uploaded_file
                st.session_state["data_plan_prod"] = data_plan_prod
                st.session_state["data_float"] = data_float
                st.session_state["merged_data"] = merged_data
                st.session_state["rates"] = rates

            # Message de succès
            st.success("✅ Fichier importé et traité avec succès !")
        
            # Afficher les DataFrames dans la page d'importation
            st.write("### Données Plan Prod ( Budget ):", data_plan_prod.head())
            st.write("### Données Float ( Réel ) :", data_float.head())
            st.write("### Données Rates ( PV intervenants ) :", rates.head())
            st.write("### Données Fusionnées :", merged_data.head())

        except Exception as e:
            st.error(f"❌ Erreur lors du traitement des données : {e}")
            
        # Bouton de réinitialisation
        if st.button("♻️ Réinitialiser l'importation"):
            st.session_state["reset_import"] = True
            st.toast("Les données ont été réinitialisées. Veuillez importer un nouveau fichier.", icon="✅")
            time.sleep(3) 
            st.rerun()




