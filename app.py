import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# UI Styling
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def recursive_extract(obj):
    """Estrae i nomi utente cercando la chiave 'value' in tutto il JSON"""
    found = set()
    if isinstance(obj, dict):
        if 'value' in obj:
            val = str(obj['value']).lower()
            # Escludiamo link o date, prendiamo solo username probabili
            if not val.startswith('http') and not val.replace('.', '').isdigit():
                found.add(val)
        for v in obj.values():
            found.update(recursive_extract(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(recursive_extract(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Scansione universale dei file JSON di Instagram")

with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    file = st.file_uploader("Trascina qui lo ZIP", type="zip")
    
    if file:
        with st.spinner("Ricerca file in corso..."):
            try:
                with zipfile.ZipFile(file, 'r') as z:
                    fols = set()
                    fings = set()
                    
                    # Scansioniamo TUTTI i file nello ZIP
                    for info in z.infolist():
                        fname = info.filename.lower()
                        
                        # Se è un JSON e contiene parole chiave
                        if fname.endswith('.json'):
                            if 'follower' in fname:
                                with z.open(info.filename) as f:
                                    fols.update(recursive_extract(json.load(f)))
                            elif 'following' in fname:
                                with z.open(info.filename) as f:
                                    fings.update(recursive_extract(json.load(f)))
                
                # Rimuoviamo eventuali "null" o stringhe vuote
                fols.discard('null'); fings.discard('null')

                if fings and fols:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    if diff:
                        st.subheader("Profili individuati:")
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                    else:
                        st.success("Tutti i profili ti seguono!")
                else:
                    st.warning("⚠️ File trovati ma sembrano vuoti o non contengono nomi validi.")
                    # Debug per te: mostriamo cosa ha trovato
                    st.write(f"Debug - File letti: Follower ({len(fols)} nomi), Seguiti ({len(fings)} nomi)")
                        
            except Exception as e:
                st.error(f"Errore di lettura: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
