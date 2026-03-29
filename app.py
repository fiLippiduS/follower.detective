import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(255,255,255,0.1); padding: 2.5rem; border-radius: 25px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); }
    .stMetric { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

def deep_extract(obj):
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'value' and isinstance(v, str) and v and not v.startswith('http'):
                found.add(v.lower())
            else:
                found.update(deep_extract(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(deep_extract(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Analisi Universale (S-Safe Edition)")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Trascina lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Scansione file in corso..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for info in z.infolist():
                    name = info.filename.lower()
                    if name.endswith('.json'):
                        # Cerca 'follower' (prende follower, followers, followers_1)
                        if 'follower' in name and 'pending' not in name:
                            with z.open(info.filename) as f:
                                fols.update(deep_extract(json.load(f)))
                        # Cerca 'following' (prende following, following_1)
                        elif 'following' in name:
                            with z.open(info.filename) as f:
                                fings.update(deep_extract(json.load(f)))

                if fols and fings:
                    diff = sorted(list(fings - fols))
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    if diff:
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                        st.download_button("📥 Scarica Lista", "\n".join(diff), "traditori.txt")
                    else:
                        st.success("Tutti ricambiano!")
                else:
                    st.error("Dati non trovati. Hai scaricato il file in formato JSON?")
                    st.write(f"Debug: Trovati {len(fols)} followers e {len(fings)} following.")
        except Exception as e:
            st.error(f"Errore: {e}")
st.markdown('</div>', unsafe_allow_html=True)
