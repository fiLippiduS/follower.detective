import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def extract_names(data):
    """Estrae i nomi in modo intelligente in base alla struttura Instagram"""
    names = set()
    # Se è la struttura dei 'Following'
    if isinstance(data, dict) and 'relationships_following' in data:
        for item in data['relationships_following']:
            for sub in item.get('string_list_data', []):
                names.add(sub.get('value').lower())
    # Se è la struttura dei 'Followers' (lista semplice)
    elif isinstance(data, list):
        for item in data:
            for sub in item.get('string_list_data', []):
                names.add(sub.get('value').lower())
    return names

st.title("💎 InstaDetective Elite")
st.write("Analisi incrociata dei database Instagram")

with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    file = st.file_uploader("Carica lo ZIP scaricato da Instagram", type="zip")
    
    if file:
        with st.spinner("Confronto liste in corso..."):
            try:
                with zipfile.ZipFile(file, 'r') as z:
                    fols = set()
                    fings = set()
                    
                    for name in z.namelist():
                        if name.endswith('.json'):
                            # Cerca followers
                            if 'follower' in name.lower() and 'pending' not in name.lower():
                                with z.open(name) as f:
                                    fols.update(extract_names(json.load(f)))
                            # Cerca following
                            elif 'following' in name.lower():
                                with z.open(name) as f:
                                    fings.update(extract_names(json.load(f)))
                
                # Pulizia
                fols.discard(None); fings.discard(None)

                if fings and fols:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    if diff:
                        st.subheader("⚠️ Chi non ti ricambia:")
                        df = pd.DataFrame(diff, columns=["Username"])
                        st.table(df)
                    else:
                        st.balloons()
                        st.success("Grande! Tutti i profili che segui ti ricambiano.")
                else:
                    st.error("❌ Errore di lettura.")
                    st.write(f"Dati trovati -> Follower: {len(fols)} | Seguiti: {len(fings)}")
                    st.info("Assicurati di aver scaricato 'Tutti i tempi' e formato 'JSON'.")
                        
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
