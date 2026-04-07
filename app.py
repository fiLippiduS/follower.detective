import streamlit as st
import json
import zipfile
import pandas as pd
import re
import hashlib
import base64

# --- CONFIGURAZIONE PROFESSIONALE ---
st.set_page_config(
    page_title="FollowerDetective Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- COSTANTI ---
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# --- LOGICA DI BUSINESS (ESTRAZIONE DATI) ---
class InstagramParser:
    """Classe dedicata al parsing dei dati Instagram con validazione robusta."""
    
    @staticmethod
    def extract_usernames(text_bytes):
        try:
            text = text_bytes.decode('utf-8', errors='ignore')
            # Regex migliorata per catturare valori JSON validi
            potentials = re.findall(r'"value":\s*"([^"]*)"|"(?:href|string_list_data)":\s*"([^"]*)"', text)
            found = set()
            blacklist = {'value', 'href', 'timestamp', 'string_list_data', 'relationships_following', 'title'}
            
            for p in potentials:
                # Flattening della regex (gruppo 1 o gruppo 2)
                match = p[0] if p[0] else p[1]
                clean = match.strip().lower()
                if clean and 2 < len(clean) < 31 and clean not in blacklist:
                    if not clean.startswith(('http', 'https', 'www.')):
                        found.add(clean)
            return found
        except Exception as e:
            st.error(f"Errore nel parsing del testo: {e}")
            return set()

    @staticmethod
    @st.cache_data(show_spinner=False)
    def process_archive(file_bytes):
        """Processa lo ZIP e restituisce (followers, following)."""
        followers, following = set(), set()
        try:
            with zipfile.ZipFile(file_bytes, 'r') as z:
                for path in z.namelist():
                    if 'followers_1.json' in path.lower():
                        with z.open(path) as f:
                            followers.update(InstagramParser.extract_usernames(f.read()))
                    elif 'following.json' in path.lower() and 'hashtag' not in path.lower():
                        with z.open(path) as f:
                            following.update(InstagramParser.extract_usernames(f.read()))
            return followers, following
        except zipfile.BadZipFile:
            st.error("Il file caricato non è un archivio ZIP valido.")
            return set(), set()

# --- INTERFACCIA UTENTE (STYLING) ---
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&family=Inter:wght@400;600&display=swap');
    
    :root {
        --primary: #f5a623;
        --bg-dark: #0d0d0f;
        --card-bg: #1a1a1e;
        --text-main: #ffffff;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-dark);
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(180deg, #16161a 0%, #0d0d0f 100%);
        border-bottom: 1px solid #333;
        margin-bottom: 2rem;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: var(--card-bg);
        border: 1px solid var(--primary);
        color: var(--primary);
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: var(--primary);
        color: black;
    }

    /* Nasconde elementi Streamlit superflui */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- COMPONENTE REWARDED AD (CORRETTO) ---
def render_ad_component(session_key, ad_link, label, count):
    """
    Risolve il problema del callback: 
    Usa un tasto nativo Streamlit per lo sblocco post-timer simulato, 
    garantendo che lo stato Python si aggiorni correttamente.
    """
    with st.container(border=True):
        st.markdown(f"### 🔒 {label}")
        st.write(f"Trovati {count} profili. Guarda la pubblicità per sbloccare la lista.")
        
        col1, col2 = st.columns(2)
        with col1:
            # Pulsante che apre l'ad
            st.link_button("📺 Apri Pubblicità", ad_link, use_container_width=True)
        with col2:
            # Il segreto: un pulsante di conferma che Streamlit può "sentire"
            if st.button("✅ Ho finito, sblocca!", key=f"btn_{session_key}"):
                st.session_state[session_key] = True
                st.rerun()

# --- MAIN APP ---
def main():
    apply_custom_css()
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1 style='color:#f5a623; font-family:Space Grotesk;'>FollowerDetective 🔍</h1>
            <p style='color:#888;'>Analisi sicura e anonima dei tuoi dati Instagram</p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize Session State
    if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
    if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False

    # Upload Section
    uploaded_file = st.file_uploader("Carica lo ZIP scaricato da Instagram", type="zip")

    if uploaded_file:
        fols, fings = InstagramParser.process_archive(uploaded_file)
        
        if not fols and not fings:
            st.warning("Non sono stati trovati dati validi. Assicurati di aver selezionato il formato JSON durante il download da Instagram.")
            return

        unfollowers = sorted(list(fings - fols))
        fans = sorted(list(fols - fings))

        # Statistiche Rapide
        c1, c2, c3 = st.columns(3)
        c1.metric("Followers", len(fols))
        c2.metric("Seguiti", len(fings))
        c3.metric("Non Ricambiano", len(unfollowers), delta_color="inverse")

        st.divider()

        # Tab Logic
        t1, t2, t3 = st.tabs(["👻 Non Ricambiano", "❤️ Fan Segreti", "💾 Backup"])

        with t1:
            if st.session_state.unf_unlocked:
                st.success(f"Sbloccati {len(unfollowers)} profili")
                st.dataframe(pd.DataFrame(unfollowers, columns=["Username"]), use_container_width=True)
            else:
                render_ad_component('unf_unlocked', LINK_UNFOLLOWERS, "Non Ricambiano", len(unfollowers))

        with t2:
            if st.session_state.fan_unlocked:
                st.success(f"Sbloccati {len(fans)} profili")
                st.dataframe(pd.DataFrame(fans, columns=["Username"]), use_container_width=True)
            else:
                render_ad_component('fan_unlocked', LINK_FAN_SEGRETI, "Fan Segreti", len(fans))
        
        with t3:
            st.info("Scarica un file JSON di backup per confronti futuri.")
            snap = {"followers": list(fols), "following": list(fings)}
            st.download_button("📥 Scarica Snapshot", data=json.dumps(snap), file_name="ig_snapshot.json")

    else:
        st.info("👋 Benvenuto! Carica il file ZIP per iniziare l'analisi.")
        with st.expander("📖 Come ottenere i dati?"):
            st.write("""
            1. Vai su Instagram -> Impostazioni -> Centro Account.
            2. Scarica le tue informazioni -> Seleziona 'Follower e Following'.
            3. **IMPORTANTE:** Scegli il formato **JSON** (non HTML).
            """)

if __name__ == "__main__":
    main()
