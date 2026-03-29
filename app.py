import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(0,0,0,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def universal_extractor(obj):
    """Estrae ogni 'value' trovato nel JSON, indipendentemente dalla struttura"""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'value' and isinstance(v, str):
                if v and not v.startswith('http') and not v.replace('.', '').isdigit():
                    found.add(v.lower().strip())
            else:
                found.update(universal_extractor(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(universal_extractor(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Analisi Definitiva a Scansione Totale")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Analisi profonda dei file JSON..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for path in z.namelist():
                    p_lower = path.lower()
                    # Identifica i file corretti nel percorso che hai descritto
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f:
                            fols.update(universal_extractor(json.load(f)))
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f:
                            fings.update(universal_extractor(json.load(f)))

                if fings and fols:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    st.markdown("---")
                    if diff:
                        st.subheader("🕵️ Profili individuati")
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                        st.download_button("📥 Scarica Report", "\n".join(diff), "unfollowers.txt")
                    else:
                        st.success("Tutti ricambiano!")
                else:
                    st.error("⚠️ Errore di lettura profonda.")
                    st.write(f"DEBUG - Nomi estratti: {len(fols)} Followers | {len(fings)} Seguiti")
                    # Mostriamo un'anteprima del problema se è ancora 0
                    if len(fings) == 0:
                        st.info("Il file 'following.json' è stato trovato ma appare vuoto o con struttura ignota.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
