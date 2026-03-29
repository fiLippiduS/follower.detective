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

def ultra_clean_extract(obj):
    """Estrae username validi ignorando tutto il resto"""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'value' and isinstance(v, str):
                # Filtro: no link, no solo numeri, lunghezza ragionevole
                if v and not v.startswith('http') and not v.replace('.', '').isdigit() and len(v) < 32:
                    found.add(v.lower().strip())
            else:
                found.update(ultra_clean_extract(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(ultra_clean_extract(item))
    return found

st.title("🎯 InstaDetective Precision")
st.write("Analisi integrale dei dati Instagram")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Analisi integrale in corso..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for info in z.infolist():
                    name = info.filename.lower()
                    if name.endswith('.json'):
                        # Se il nome del file contiene follower ma non è una richiesta pendente
                        if 'follower' in name and 'pending' not in name:
                            with z.open(info.filename) as f:
                                fols.update(ultra_clean_extract(json.load(f)))
                        # Se il nome del file contiene following
                        elif 'following' in name:
                            with z.open(info.filename) as f:
                                fings.update(ultra_clean_extract(json.load(f)))

                if fols and fings:
                    non_ricambiano = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(non_ricambiano))
                    
                    if non_ricambiano:
                        st.table(pd.DataFrame(non_ricambiano, columns=["Username"]))
                        st.download_button("📥 Scarica Risultati", "\n".join(non_ricambiano), "unfollowers.txt")
                    else:
                        st.success("Tutti ricambiano!")
                else:
                    st.error("Dati incompleti nello ZIP.")
                    st.write(f"Debug: Rilevati {len(fols)} followers e {len(fings)} seguiti.")

        except Exception as e:
            st.error(f"Errore: {e}")
st.markdown('</div>', unsafe_allow_html=True)
