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

def clean_extract(obj):
    """Estrae SOLO i veri username, scartando link, date e spazzatura"""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'value' and isinstance(v, str):
                # FILTRO DI PRECISIONE:
                # 1. Non deve essere un link (http)
                # 2. Non deve essere una data (non contiene numeri lunghi tipo timestamp)
                # 3. Non deve essere vuoto
                if v and not v.startswith('http') and not v.replace('.', '').isdigit() and len(v) < 35:
                    found.add(v.lower().strip())
            else:
                found.update(clean_extract(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(clean_extract(item))
    return found

st.title("🎯 InstaDetective Precision")
st.write("Confronto scientifico dei follower")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Analisi di precisione..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for info in z.infolist():
                    name = info.filename.lower()
                    # Ignoriamo i file che non ci servono (richieste pendenti, messaggi, ecc.)
                    if name.endswith('.json') and 'followers_and_following' in name:
                        if 'follower' in name and 'pending' not in name:
                            with z.open(info.filename) as f:
                                fols.update(clean_extract(json.load(f)))
                        elif 'following' in name:
                            with z.open(info.filename) as f:
                                fings.update(clean_extract(json.load(f)))

                # Rimuoviamo eventuali nomi di sistema o errori
                fols.discard('null'); fings.discard('null')

                if fols and fings:
                    # La logica del "chi non mi segue": chi è in FOLLOWING ma NON in FOLLOWERS
                    non_ricambiano = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti Reali", len(fings))
                    c2.metric("Followers Reali", len(fols))
                    c3.metric("Non ricambiano", len(non_ricambiano))
                    
                    if non_ricambiano:
                        st.subheader("⚠️ Lista Profili individuati")
                        df = pd.DataFrame(non_ricambiano, columns=["Username"])
                        st.table(df)
                        st.download_button("📥 Scarica Risultati (.txt)", "\n".join(non_ricambiano), "unfollowers.txt")
                    else:
                        st.success("Tutti i profili che segui ti ricambiano il follow!")
                else:
                    st.error("Dati insufficienti. Assicurati che il file ZIP contenga la cartella 'followers_and_following'.")
                    st.write(f"Debug: Follower trovati: {len(fols)} | Seguiti trovati: {len(fings)}")

        except Exception as e:
            st.error(f"Errore: {e}")
st.markdown('</div>', unsafe_allow_html=True)
