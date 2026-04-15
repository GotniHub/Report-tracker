import streamlit as st

def require_auth():
    if not st.session_state.get("authenticated", False):
        st.warning("Accès refusé. Veuillez vous connecter d'abord.")
        st.switch_page("app.py")
        st.stop()