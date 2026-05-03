import streamlit as st


def apply_page_4_css():
    st.markdown("""
<style>
button {
    background-color: white !important;
    color: #0054A4 !important;
    border: 2px solid #0054A4 !important;
    font-weight: 600 !important;
}

button:hover {
    background-color: #E8F1FB !important;
    border-color: #0054A4 !important;
    box-shadow: 0 2px 8px rgba(0, 84, 164, 0.15) !important;
}

button:active {
    background-color: #D1E3F7 !important;
    border-color: #003D7A !important;
    color: #003D7A !important;
}
</style>
""", unsafe_allow_html=True)
