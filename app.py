import streamlit as st
import json
import zipfile
import pandas as pd
import time

# Configurazione base
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# CSS Semplificato per evitare blocchi
st.markdown("""
    <style>
    .stApp { background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); color: white; }
    .stMarkdown, .stText { color: white !important; }
    .main-box { background: rgba(0,0,0,0.5); padding: 2rem; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 InstaDetective Elite Edition")
st.write("Analisi crittografica delle relazioni social")

with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    
    # Questo è il componente che deve apparire
    uploaded_file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")
    
    if uploaded_file:
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i + 1)
            
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                # Logica di estrazione semplificata
                fols = set()
                fings = set()
                for n in z.namelist():
                    if 'followers_1.json' in n:
                        data = json.load(z.open(n))
                        for e in data: [fols.add(i['value'].lower()) for i in e['string_list_data']]
                    if 'following.json' in n:
                        data = json.load(z.open(n))
                        for e in data.get('relationships_following', []): [fings.add(i['value'].lower()) for i in e['string_list_data']]
                
                if fings:
                    diff = sorted(list(fings - fols))
                    st.success(f"Analisi completata! {len(diff)} utenti non ti seguono.")
                    st.table(pd.DataFrame(diff, columns=["Username"]))
                else:
                    st.warning("File JSON non trovati nello ZIP. Controlla il formato.")
        except Exception as e:
            st.error(f"Errore: {e}")
            
    st.markdown('</div>', unsafe_allow_html=True)
