import streamlit as st
import json
import zipfile
import pandas as pd
import re

st.set_page_config(page_title="InstaDetective Elite", page_icon="💎")

# --- UI STYLING ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; }
    .main-box { background: rgba(0,0,0,0.2); padding: 2rem; border-radius: 20px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

def raw_text_extract(file_content):
    """Estrae username usando espressioni regolari dal testo grezzo del JSON"""
    # Cerca stringhe tra virgolette che non siano link o date
    # Tipicamente gli username sono dopo "value": "nome" o simili
    text = file_content.decode('utf-8', errors='ignore')
    # Trova tutto ciò che è tra virgolette
    potentials = re.findall(r'"([^"]*)"', text)
    
    found = set()
    blacklist = {'value', 'href', 'timestamp', 'string_list_data', 'relationships_following', 'title'}
    
    for p in potentials:
        clean = p.strip().lower()
        # Filtro username: lunghezza 1-30, no spazi, no link, no solo numeri
        if (clean and 
            len(clean) < 31 and 
            clean not in blacklist and 
            not clean.startswith('http') and 
            not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

st.title("💎 InstaDetective Elite")
st.write("Scansione Testuale Avanzata (Modalità Compatibilità)")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

if file:
    with st.spinner("Estrazione dati in corso..."):
        try:
            with zipfile.ZipFile(file, 'r') as z:
                fols, fings = set(), set()
                
                for path in z.namelist():
                    p_lower = path.lower()
                    
                    # Estrazione Followers
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f:
                            fols.update(raw_text_extract(f.read()))
                    
                    # Estrazione Following
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f:
                            fings.update(raw_text_extract(f.read()))

                # Pulizia set: rimuoviamo termini tecnici che sfuggono alla blacklist
                fols.discard('true'); fols.discard('false')
                fings.discard('true'); fings.discard('false')

                if fings and fols:
                    diff = sorted(list(fings - fols))
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non ricambiano", len(diff))
                    
                    st.markdown("---")
                    if diff:
                        st.subheader("🕵️ Utenti individuati")
                        st.table(pd.DataFrame(diff, columns=["Username"]))
                        st.download_button("📥 Scarica Report .txt", "\n".join(diff), "unfollowers.txt")
                    else:
                        st.balloons()
                        st.success("Tutti i profili ti seguono!")
                else:
                    st.error("⚠️ Errore critico di lettura.")
                    st.write(f"DEBUG: Trovati {len(fols)} followers | {len(fings)} seguiti.")
                    st.info("Se i seguiti sono ancora 0, il file 'following.json' potrebbe essere vuoto nello ZIP.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
st.markdown('</div>', unsafe_allow_html=True)
