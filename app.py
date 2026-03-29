import streamlit as st
import json
import zipfile
import pandas as pd
import time

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# CSS Migliorato
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    stMetric { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

def extract_values(obj):
    """Funzione magica: estrae tutti i nomi utente ovunque siano nel JSON"""
    found = set()
    if isinstance(obj, dict):
        if 'value' in obj:
            found.add(obj['value'].lower())
        for k, v in obj.items():
            found.update(extract_values(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(extract_values(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Analisi professionale dei dati Instagram")

with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    file = st.file_uploader("Trascina qui lo ZIP dei dati Instagram", type="zip")
    
    if file:
        with st.spinner("Scansione profonda dei metadati..."):
            try:
                with zipfile.ZipFile(file, 'r') as z:
                    fols = set()
                    fings = set()
                    
                    for name in z.namelist():
                        # Cerca i file corretti
                        if 'followers_1.json' in name:
                            with z.open(name) as f:
                                fols.update(extract_values(json.load(f)))
                        if 'following.json' in name:
                            with z.open(name) as f:
                                fings.update(extract_values(json.load(f)))
                
                if not fings or not fols:
                    st.error("⚠️ Attenzione: Non ho trovato dati validi nello ZIP. Assicurati di aver scaricato i dati in formato JSON e non HTML.")
                else:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    if diff:
                        st.subheader("Profili che non ti seguono:")
                        # Creiamo una tabella pulita senza indici strani
                        df = pd.DataFrame(diff, columns=["Username Instagram"])
                        st.table(df)
                    else:
                        st.balloons()
                        st.success("Tutti i profili che segui ti ricambiano!")
                        
            except Exception as e:
                st.error(f"Errore tecnico durante la lettura: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
