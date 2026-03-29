import streamlit as st
import json
import zipfile
import pandas as pd

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(0,0,0,0.2); padding: 2rem; border-radius: 20px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def deep_scan(obj):
    """Estrae ogni stringa possibile che non sia un link o una data"""
    found = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                # Pulizia stringa
                clean_v = v.strip().lower()
                # Filtri: No link, no date (timestamp lunghi), no vuoti, lunghezza ragionevole
                if clean_v and not clean_v.startswith('http') and not (clean_v.isdigit() and len(clean_v) > 5) and len(clean_v) < 32:
                    # Escludiamo chiavi di sistema comuni
                    if k not in ['href', 'title', 'timestamp']:
                        found.add(clean_v)
            else:
                found.update(deep_scan(v))
    elif isinstance(obj, list):
        for item in obj:
            found.update(deep_scan(item))
    return found

st.title("💎 InstaDetective Elite")
st.write("Scansione Profonda e Correzione Automatica")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Analisi in corso..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for path in z.namelist():
                    p_lower = path.lower()
                    
                    # File Followers
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f:
                            fols.update(deep_scan(json.load(f)))
                    
                    # File Following (Versione ultra-permissiva)
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f:
                            fings.update(deep_scan(json.load(f)))

                # Rimuoviamo parole di sistema che potrebbero essere state catturate
                garbage = {'follower', 'following', 'true', 'false', 'relationships_following', 'string_list_data'}
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
                        st.subheader("🕵️ Profili che non ti seguono")
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                        st.download_button("📥 Scarica Lista", "\n".join(diff), "lista_unfollowers.txt")
                    else:
                        st.balloons()
                        st.success("Tutti ricambiano il follow!")
                else:
                    st.error("⚠️ Dati non estratti correttamente dal file 'following.json'.")
                    st.write(f"DEBUG: Trovati {len(fols)} followers | {len(fings)} seguiti.")
                    
                    # ULTIMA SPIAGGIA: Se seguiti è ancora 0, mostriamo i nomi delle chiavi del JSON
                    if len(fings) == 0:
                        st.warning("Analisi d'emergenza: Il file dei seguiti sembra avere una struttura ignota.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
