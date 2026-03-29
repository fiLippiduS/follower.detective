import streamlit as st
import json
import zipfile
import pandas as pd
import re

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(0,0,0,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def brute_force_extract(obj):
    """Estrae QUALSIASI stringa che assomigli a un username nel JSON"""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (str, dict, list)):
                # Se il valore è una stringa, verifichiamo se è un username
                if isinstance(v, str):
                    # Filtro: no link, no date, no nomi troppo lunghi, no numeri puri
                    if v and not v.startswith('http') and not v.replace('.', '').isdigit() and len(v) < 32:
                        if k not in ['title', 'href']: # Escludiamo metadati comuni
                            found.add(v.lower().strip())
                found.update(brute_force_extract(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(brute_force_extract(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Analisi con Scansione Euristica Totale")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Scansione euristica dei file..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for path in z.namelist():
                    p_lower = path.lower()
                    
                    # Filtro file followers
                    if p_lower.endswith('followers_1.json') or p_lower.endswith('followers.json'):
                        with z.open(path) as f:
                            fols.update(brute_force_extract(json.load(f)))
                    
                    # Filtro file following (escludendo hashtag)
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f:
                            fings.update(brute_force_extract(json.load(f)))

                # Pulizia finale: rimuoviamo termini comuni che non sono username
                garbage = {'follower', 'following', 'true', 'false', 'none', 'relationships_following'}
                fols -= garbage
                fings -= garbage

                if fings and fols:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    st.markdown("---")
                    if diff:
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                        st.download_button("📥 Scarica Report", "\n".join(diff), "unfollowers.txt")
                    else:
                        st.success("Tutti ricambiano!")
                else:
                    st.error("⚠️ Nessun dato estratto dai file.")
                    st.write(f"DEBUG: File analizzati correttamente, ma trovati {len(fols)} followers e {len(fings)} seguiti.")
                    st.info("Se i seguiti sono ancora 0, apri il file 'following.json' e controlla se vedi i nomi dei tuoi amici.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
