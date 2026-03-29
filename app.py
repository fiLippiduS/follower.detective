import streamlit as st
import json
import zipfile
import pandas as pd

# 1. Configurazione della pagina (Deve essere la prima istruzione Streamlit)
st.set_page_config(page_title="InstaChecker Pro", page_icon="🕵️", layout="centered")

# 2. Correzione errore CSS (unsafe_allow_html è il parametro corretto)
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button { background-color: #E1306C; color: white; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕵️ InstaChecker Pro")
st.info("Carica il tuo file .zip di Instagram per vedere chi non ricambia il follow.")

# Sidebar per login simulato
with st.sidebar:
    st.header("Configurazione Account")
    st.text_input("Username Instagram", placeholder="mario_rossi")
    st.text_input("Password", type="password", placeholder="••••••••")
    st.caption("Nota: I dati inseriti qui sopra sono solo grafici e non vengono memorizzati.")

# Upload del file ZIP
uploaded_file = st.file_uploader("Scegli il file .zip scaricato da Instagram", type="zip")

def extract_names(data):
    """Estrae i nomi in modo intelligente dai diversi formati JSON"""
    names = set()
    # Caso 1: I dati sono una lista (solitamente followers_1.json)
    if isinstance(data, list):
        for item in data:
            if 'string_list_data' in item and item['string_list_data']:
                val = item['string_list_data'][0].get('value')
                if val: names.add(val.lower().strip())
    # Caso 2: I dati sono un dizionario (solitamente following.json)
    elif isinstance(data, dict):
        # Cerchiamo dentro la chiave specifica di Instagram
        entries = data.get('relationships_following', [])
        for item in entries:
            # Proviamo a prendere il 'title' (più affidabile per i following)
            val = item.get('title')
            if val: 
                names.add(val.lower().strip())
            # Se fallisce, proviamo string_list_data
            elif 'string_list_data' in item and item['string_list_data']:
                val = item['string_list_data'][0].get('value')
                if val: names.add(val.lower().strip())
    return names

if uploaded_file:
    with st.spinner('Analisi in corso... attendi...'):
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                all_followers = set()
                all_following = set()
                
                # Scansione automatica di tutti i file nello ZIP
                for file_info in z.infolist():
                    fname = file_info.filename.lower()
                    if fname.endswith('.json'):
                        if 'follower' in fname:
                            with z.open(file_info) as f:
                                all_followers.update(extract_names(json.load(f)))
                        elif 'following' in fname:
                            with z.open(file_info) as f:
                                all_following.update(extract_names(json.load(f)))
                
                if not all_following:
                    st.warning("Non ho trovato i dati dei 'Following'. Assicurati di aver caricato lo ZIP completo.")
                else:
                    # Calcolo della differenza
                    unfollowers = sorted(list(all_following - all_followers))
                    
                    # Visualizzazione Metriche
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Seguiti", len(all_following))
                    col2.metric("Follower", len(all_followers))
                    col3.metric("Non ricambiano", len(unfollowers))
                    
                    st.divider()
                    
                    if unfollowers:
                        st.subheader("📜 Lista Unfollowers")
                        # Creazione DataFrame per la tabella
                        df = pd.DataFrame(unfollowers, columns=["Username"])
                        # Aggiungiamo link cliccabili
                        df['Profilo'] = df['Username'].apply(lambda x: f"https://www.instagram.com/{x}")
                        
                        st.dataframe(df, use_container_width=True)
                        
                        # Esportazione CSV
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Scarica report CSV",
                            data=csv,
                            file_name="unfollowers_report.csv",
                            mime="text/csv"
                        )
                    else:
                        st.balloons()
                        st.success("Tutti gli utenti che segui ti ricambiano il follow!")
                        
        except Exception as e:
            st.error(f"Errore durante l'elaborazione dello ZIP: {e}")
