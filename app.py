import streamlit as st

pg = st.navigation([
    st.Page("pages/02_funil.py",     title="Funil Comercial", icon="📊"),
    st.Page("pages/03_contratos.py", title="Contratos",       icon="📄"),
])

pg.run()
