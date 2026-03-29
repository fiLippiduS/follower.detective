import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Precision", page_icon="🎯")

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(255,255,255,0.1); padding: 2.5rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def extract_names_logic(data, is_followers=True):
    """Logica di estrazione specifica per la struttura JSON di Instagram"""
    names = set()
    try:
        if is_followers:
            # Followers: è una lista di oggetti
            if isinstance(data, list):
                for entry in data:
                    for item in entry.get('string_list_data', []):
                        val = item.get('value')
                        if val: names.add(val.lower().strip())
        else:
            # Following: è un dizionario con chiave 'relationships_following'
            if isinstance(data, dict):
                entries = data.get('relationships_following', [])
                for entry in entries:
                    for item in entry.get('string_list_data', []):
                        val = item.get('value')
                        if val: names.add(val.lower().strip())
    except Exception:
        pass
    return names

st.title("🎯 InstaDetective Precision")
st.write("Analisi accurata della struttura 'Connections'")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Navigazione tra le cartelle dello ZIP..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                # Analizziamo ogni file cercando il match esatto del nome finale
                for full_path in z.namelist():
                    filename = full_path.lower()
                    
                    # 1. CERCA I FOLLOWERS (Solo followers_1.json)
                    if filename.endswith('followers_1.json'):
                        with z.open(full_path) as f:
                            fols.update(extract_names_logic(json.load(f), is_followers=True))
                    
                    # 2. CERCA I SEGUITI (Solo following.json, ignorando hashtag e suggerimenti)
                    elif filename.endswith('following.json') and 'hashtags' not in filename:
                        with z.open(full_path) as f:
                            fings.update(extract_names_logic(json.load(f), is_followers=False))

                if fols and fings:
                    # Calcolo matematico
                    non_ricambiano = sorted(list(fings - fols))
                    
                    c1, col_gap, c2, col_gap2, c3 = st.columns([1, 0.2, 1, 0.2, 1])
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Unfollowers", len(non_ricambiano))
                    
                    st.markdown("---")
                    
                    if non_ricambiano:
                        st.subheader("🕵️ Elenco profili individuati")
                        df = pd.DataFrame(non_ricambiano, columns=["Username"])
                        st.table(df)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Scarica Risultati (CSV)", csv, "unfollowers.csv", "text/csv")
                    else:
                        st.balloons()
                        st.success("Ottimo! Tutti i profili che segui ti ricambiano.")
                else:
                    st.error("⚠️ File individuati ma non letti correttamente.")
                    st.write(f"DEBUG - Percorsi trovati: {len(fols)} followers | {len(fings)} following")
                    st.info("Assicurati che lo ZIP contenga i file JSON originali.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
