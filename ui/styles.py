import streamlit as st
from ui.theme import FONTS_URL, COLORS, FONTS


def inject_styles():
    """Inject global CSS design tokens and utility classes."""
    
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}

    .stApp {
        background-color: #f8fafc !important;
    }
    .main .block-container {
        padding-top: 24px !important;
        padding-bottom: 80px !important;
        max-width: 980px !important;
    }
    [data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    [data-testid="stRadio"] label div p,
    [data-testid="stRadio"] label span p {
        font-size: 14px !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    [data-testid="stBaseButton-primary"] {
        background: #1a3d6e !important;
        border-radius: 12px !important;
        height: 52px !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(26,61,110,0.25) !important;
    }
    [data-testid="stBaseButton-primary"] p,
    [data-testid="stBaseButton-primary"] span {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
