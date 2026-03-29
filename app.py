import streamlit as st
import json
import zipfile
import pandas as pd
import time

# --- CONFIGURAZIONE ELITE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- CSS AVANZATO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #2b5876, #4e4376, #000000);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
        color: white;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 25px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 50px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }
    /* Stilizzazione Tabella Risultati */
    .stDataFrame {
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
    }
    h1 { font-weight: 800; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

def get_users_from_zip(zip_file):
    followers = set()
    following = set()
    with zipfile.ZipFile(zip_file, 'r') as z:
        for filename in z.namelist():
            if filename.endswith('.json'):
                if 'followers_1' in filename.lower():
                    with z.open(filename) as f:
                        data = json.load(f)
                        for entry in data:
                            for item in entry.get('string_list_data', []):
                                followers.add(item['value'].lower())
                elif 'following' in filename.lower():
                    with z.open(filename) as f:
                        data = json.load(f)
                        entries = data.get('relationships_following', [])
                        for entry in entries:
                            for item in entry.get('string_list_data', []):
                                following.add(item['value'].lower())
    return followers, following

# --- UI ---
st.markdown("<div style='text-align: center; margin-top: 50px;'>", unsafe_allow_html=True)
st.title("💎 InstaDetective Elite Edition")
st.write("Analisi crittografica delle relazioni social")
st.markdown("</div>", unsafe_allow_html=True)
