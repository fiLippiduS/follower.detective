import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- DESIGN SYSTEM "ALL-IN-ONE" ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }

    .main-container {
        max-width: 800px;
        margin: auto;
        padding: 10px;
    }

    /* Blocchi Sezione */
    .section-card {
        background: #0a0a0a;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #1a1a1a;
        margin-bottom: 20px;
    }

    .gold-border {
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
    }

    /* Bottoni e Input */
    .stButton>button {
        background: #d4af37 !important;
        color: black !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
    }

    .guide-box {
        background: rgba(255,255,255,0.03);
        padding: 20px;
        border-radius: 15px;
        border-left: 4px solid #d4af37;
        font-size: 0.85em;
        margin-bottom: 25px;
    }

    .step-num {
        color: #d4af37;
        font-weight: 800;
        margin-right: 10px;
    }

    .premium-banner {
        background: linear-gradient(135deg, #d4af37 0%, #aa8928 100%);
        color: black;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-weight: 800;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def raw_text_extract(file_content):
    text = file_content.decode('utf-8', errors='ignore')
    potentials = re.findall(r'"([^"]*)"', text)
    found = set()
    blacklist = {'value', 'href', 'timestamp', 'string_list_data', 'relationships_following', 'title', 'true', 'false', 'none'}
    for p in potentials:
        clean = p.strip().lower()
        if (clean and len(clean) < 31 and clean not in blacklist and 
            not clean.startswith('http') and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

# --- UI START ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# HEADER
st.markdown("<h1 style='text-align:center; font-weight:800; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; letter-spacing:3px; font-size:0.7em; margin-bottom:40px;'>PREMIUM SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# 1. GUIDA (Sempre presente in alto per i nuovi utenti)
with st.expander("📖 Guida Rapida: Come ottenere i tuoi dati", expanded=False):
    st.markdown("""
    <div class="guide-box">
    <span class="step-num">01</span> Apri <b>Instagram</b> > Impostazioni > Centro Account.<br>
    <span class="step-num">02</span> <b>Scarica informazioni</b> > Seleziona 'Follower e seguiti'.<br>
    <span class="step-num">03</span> Formato: <b>JSON</b> | Intervallo: <b>Dall'inizio</b>.<br>
    <span class="step-num">04</span> Carica lo ZIP qui sotto appena ricevi l'email.
    </div>
    """, unsafe_allow_html=True)

# 2. PANNELLO DI CARICAMENTO (Il cuore dell'app)
st.markdown('<div class="section-card gold-border">', unsafe_allow_html=True)
st.markdown("##### 📥 1. Carica Archivio Recente (.zip)")
uploaded_file = st.file_uploader("ZIP", type="zip", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("##### ⏳ 2. Confronto Storico (Opzionale)")
st.caption("Carica un file .insta salvato in precedenza per vedere chi ti ha rimosso il segui.")
historical_file = st.file_uploader("Snapshot", type="insta", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# 3. LOGICA DI ANALISI
if uploaded_file:
    with st.spinner("Analisi in corso..."):
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                fols, fings = set(), set()
                for path in z.namelist():
                    p_lower = path.lower()
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f: fols.update(raw_text_extract(f.read()))
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f: fings.update(raw_text_extract(f.read()))

                if fings and fols:
                    non_ricambiano = sorted(list(fings - fols))
                    fan = sorted(list(fols - fings))
                    comuni = fings.intersection(fols)

                    # --- RISULTATI ---
                    st.write("---")
                    
                    # Alert Storico se presente
                    if historical_file:
                        old_data = json.load(historical_file)
                        old_fols = set(old_data.get("followers", []))
                        persi = sorted(list(old_fols - fols))
                        if persi:
                            st.error(f"🚨 ALERT: {len(persi)} utenti hanno smesso di seguirti! \n\n {', '.join(persi)}")
                        else:
                            st.success("✅ Nessun nuovo unfollower rilevato dallo storico.")

                    # Metriche veloci
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Seguiti", len(fings))
                    m2.metric("Followers", len(fols))
                    m3.metric("Non Ricambiano", len(non_ricambiano))

                    # Tab Risultati
                    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA STORICO"])

                    with t1:
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)
                    
                    with t2:
                        st.markdown(f"""
                        <div style="text-align:center; padding:20px;">
                            <h3 style="color:#d4af37;">Lista Fan Segreti</h3>
                            <p>Abbiamo trovato {len(fan)} persone che ti seguono.</p>
                            <a href="https://www.paypal.me/TUO_USER/1.29" style="text-decoration:none;">
                                <div class="premium-banner">SBLOCCA ORA 1,29€</div>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

                    with t3:
                        st.markdown("##### Crea Snapshot per il futuro")
                        st.write("Scarica questo file per poter fare il confronto tra una settimana.")
                        snap_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                        st.download_button("📥 SCARICA FILE .INSTA", json.dumps(snap_data), "mio_profilo.insta")

        except Exception as e:
            st.error("Errore durante l'analisi del file.")

# FOOTER MONETIZZAZIONE SEMPRE VISIBILE
st.write("---")
st.markdown("""
    <div style="text-align:center; opacity:0.6; font-size:0.8em;">
        💎 <b>InstaDetective Elite v5.5</b><br>
        Sviluppato per la massima privacy. Nessun dato viene salvato.<br><br>
        <a href="https://www.paypal.me/TUO_USER" style="color:#d4af37; text-decoration:none;">Offrimi un caffè per supportare il lavoro</a>
    </div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
