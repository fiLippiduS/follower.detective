import streamlit as st
import json
import zipfile
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="InstaAnalyzer Pro", page_icon="🕵️", layout="centered")

# --- CSS PER L'INTERFACCIA ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
        color: white;
    }
    .main-card {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 30px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    label, p, h1, h2 { color: white !important; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def extract_names(data):
    """Estrae i nomi utente dai JSON di Instagram"""
    names = set()
    if isinstance(data, list):
        for item in data:
            if 'string_list_data' in item and item['string_list_data']:
                names.add(item['string_list_data'][0].get('value').lower())
    elif isinstance(data, dict):
        # Gestione per il formato following.json
        entries = data.get('relationships_following', [])
        for item in entries:
            if 'string_list_data' in item and item['string_list_data']:
                names.add(item['string_list_data'][0].get('value').lower())
    return names

# --- INTERFACCIA PRINCIPALE ---
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.title("🕵️ Analisi Unfollowers")
st.write("Carica lo ZIP dei tuoi dati Instagram per vedere chi non ti ricambia il follow.")

uploaded_file = st.file_uploader("Trascina qui il file .zip", type="zip")

if uploaded_file:
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            followers = set()
            following = set()
            
            # Cerca i file corretti nello zip
            for path in z.namelist():
                if 'followers_and_following/followers.json' in path:
                    with z.open(path) as f:
                        followers = extract_names(json.load(f))
                if 'followers_and_following/following.json' in path:
                    with z.open(path) as f:
                        following = extract_names(json.load(f))
            
            if followers and following:
                # Calcolo chi non ricambia (Following - Followers)
                not_following_back = sorted(list(following - followers))
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Seguiti", len(following))
                col2.metric("Follower", len(followers))
                col3.metric("Non ricambiano", len(not_following_back))
                
                st.subheader("Usernames che non ti seguono:")
                df = pd.DataFrame(not_following_back, columns=["Username"])
                st.dataframe(df, use_container_width=True)
            else:
                st.error("Assicurati che lo ZIP contenga i file followers.json e following.json nella cartella corretta.")
                
    except Exception as e:
        st.error(f"Si è verificato un errore durante l'analisi: {e}")

st.markdown("</div>", unsafe_allow_html=True)
