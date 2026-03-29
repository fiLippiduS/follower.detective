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

def extract_from_json(data, key_type):
    """Estrae i nomi seguendo la struttura esatta di Instagram"""
    names = set()
    try:
        if key_type == 'followers':
            # I followers sono una lista di oggetti
            if isinstance(data, list):
                for item in data:
                    for sub in item.get('string_list_data', []):
                        val = sub.get('value')
                        if val: names.add(val.lower().strip())
        elif key_type == 'following':
            # I following sono dentro la chiave 'relationships_following'
            entries = data.get('relationships_following', [])
            for item in entries:
                for sub in item.get('string_list_data', []):
                    val = sub.get('value')
                    if val: names.add(val.lower().strip())
    except Exception:
        pass
    return names

st.title("🎯 InstaDetective Precision")
st.write("Confronto dei dati originali Instagram")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Analisi dei file originali..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for info in z.infolist():
                    name = info.filename.lower()
                    
                    # FILTRO RIGIDO SUI NOMI FILE:
                    # Instagram usa nomi standard. Se il file non è quello giusto, lo ignoriamo.
                    if name.endswith('.json'):
                        # Cerca il file dei follower (spesso followers_1.json)
                        if 'followers_1.json' in name or 'followers.json' in name:
                            with z.open(info.filename) as f:
                                fols.update(extract_from_json(json.load(f), 'followers'))
                        
                        # Cerca il file dei seguiti (following.json)
                        elif 'following.json' in name:
                            with z.open(info.filename) as f:
                                fings.update(extract_from_json(json.load(f), 'following'))

                if fols and fings:
                    # Calcolo: chi seguo (fings) ma non mi segue (fols)
                    non_ricambiano = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(non_ricambiano))
                    
                    if non_ricambiano:
                        st.subheader("⚠️ Elenco profili")
                        df = pd.DataFrame(non_ricambiano, columns=["Username"])
                        st.table(df)
                        st.download_button("📥 Scarica Risultati", "\n".join(non_ricambiano), "unfollowers.txt")
                    else:
                        st.success("Tutti i profili ti seguono!")
                else:
                    st.error("Errore di rilevamento dati.")
                    st.write(f"Rilevati: {len(fols)} Followers | {len(fings)} Seguiti")
                    st.info("Verifica che lo ZIP contenga i file 'followers_1.json' e 'following.json'.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
