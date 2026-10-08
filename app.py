import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup
import re
import html
from difflib import SequenceMatcher

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Medibank OSHC Assistant",
    page_icon="💬",
    layout="centered"
)

# --------------------------------------------------
# BRAND-INSPIRED APPEARANCE
# --------------------------------------------------

st.markdown("""
<style>
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        background: linear-gradient(135deg, #d71920 0%, #ef3340 58%, #ff6b6b 100%);
        padding: 28px 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }

    .hero-kicker {
        color: rgba(255,255,255,0.82);
        font-size: 0.86rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero-title {
        color: white;
        font-size: 2.15rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        color: rgba(255,255,255,0.92);
        font-size: 1rem;
        margin: 0;
    }

    .trust-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin: 4px 0 22px 0;
    }

    .trust-pill {
        border: 1px solid rgba(128,128,128,0.28);
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 0.84rem;
        opacity: 0.9;
    }

    div.stButton > button {
        border-radius: 12px;
        min-height: 46px;
        font-weight: 650;
        border: 1px solid rgba(128,128,128,0.30);
        transition: 0.15s ease;
    }

    div.stButton > button:hover {
        border-color: #ef3340;
        transform: translateY(-1px);
    }

    [data-testid="stChatMessage"] {
        border-radius: 16px;
    }

    .section-label {
        font-size: 0.82rem;
        font-weight: 800;
