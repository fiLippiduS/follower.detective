import streamlit as st
import json
import zipfile
import pandas as pd
import re
import time
import streamlit.components.v1 as components
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }

    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    
    .section-card {
        background: #0a0a0a;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #1a1a1a;
        margin-bottom: 20px;
    }

    .premium-choice {
        background: linear-gradient(145deg, #1a1a1a, #000);
        border: 1px solid #d4af37;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 15px;
    }

    .stButton>button {
        border-radius: 12px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        width: 100% !important;
    }

    /* Stile personalizzato per i messaggi di sblocco */
    .unlock-loading {
        color: #d4af37;
        font-weight: 600;
        text-align: center;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE ESTRAZIONE DATI ---
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

# --- LOGICA APP ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>ADS & PREMIUM SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# 1. ESPANDER GUIDA
with st.expander("📖 Come ottenere i dati (Guida Rapida)", expanded=False):
    st.write("1. Apri Instagram > Centro Account > Scarica informazioni.")
    st.write("2. Seleziona 'Follower e seguiti', formato JSON, intervallo 'Dall'inizio'.")
    st.write("3. Carica lo ZIP ricevuto qui sotto.")

# 2. AREA CARICAMENTO
st.markdown('<div class="section-card" style="border: 1px solid rgba(212,175,55,0.3);">', unsafe_allow_html=True)
col_zip, col_inst = st.columns(2)
with col_zip:
    uploaded_file = st.file_uploader("📂 Carica ZIP Aggiornato", type="zip")
with col_inst:
    historical_file = st.file_uploader("⏳ Carica Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
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

                # --- RISULTATI ---
                st.write("---")
                
                # Check Storico
                if historical_file:
                    old_data = json.load(historical_file)
                    old_fols = set(old_data.get("followers", []))
                    persi = sorted(list(old_fols - fols))
                    if persi:
                        st.error(f"🚨 ALERT: {len(persi)} utenti hanno smesso di seguirti! \n\n {', '.join(persi)}")
                    else:
                        st.success("✅ Nessun nuovo unfollower rilevato.")

                # Dashboard Metriche
                m1, m2, m3 = st.columns(3)
                m1.metric("Seguiti", len(fings))
                m2.metric("Followers", len(fols))
                m3.metric("Non Ricambiano", len(non_ricambiano))

                st.write("###")
                t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN SEGRETI", "💾 SALVA .INSTA"])

                with t1:
                    st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                with t2:
                    if 'unlocked' not in st.session_state:
                        st.session_state.unlocked = False

                    if not st.session_state.unlocked:
                        st.markdown(f"### 🔒 Hai {len(fan)} Fan Segreti")
                        st.write("Scegli come sbloccare la lista dei profili che ti seguono:")
                        
                        c_pay, c_ad = st.columns(2)
                        with c_pay:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("💰 **Fast Pass**")
                            st.markdown('<a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;"><button style="background:#d4af37; color:black; border:none; padding:12px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">PAGA 1,29€</button></a>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        with c_ad:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("📺 **Ad-Support**")
                            if st.button("SBLOCCA GRATIS"):
                                st.session_state.loading_ad = True
                            st.markdown('</div>', unsafe_allow_html=True)

                        if 'loading_ad' in st.session_state and st.session_state.loading_ad:
                            st.markdown('<div class="unlock-loading">Apertura pubblicità in corso... attendi 20 secondi</div>', unsafe_allow_html=True)
                            
                            # TRUCCO: Usiamo il tuo script Adsterra come Reward
                            components.html(f'<script src="https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js"></script>', height=0)
                            
                            bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.2) # Timer totale circa 20 secondi
                                bar.progress(i + 1)
                            
                            st.session_state.unlocked = True
                            st.session_state.loading_ad = False
                            st.rerun()
                    else:
                        st.success("✅ Fan Segreti Sbloccati")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    st.markdown("##### Crea Snapshot Storico")
                    snap_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                    st.download_button("📥 SCARICA FILE .INSTA", json.dumps(snap_data), "mio_profilo.insta")

    except Exception:
        st.error("Errore nell'analisi dello ZIP.")

# --- FOOTER CON PUBBLICITÀ FISSA ---
st.write("---")
st.markdown('<p style="text-align:center; opacity:0.3; font-size:0.6em; letter-spacing:2px;">SPONSORED CONTENT</p>', unsafe_allow_html=True)

# Iniezione dello script Adsterra nel footer
components.html(f"""
    <div style="display:flex; justify-content:center; align-items:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)

st.markdown('<p style="text-align:center; opacity:0.1; font-size:0.6em;">GOLD ENGINE v7.0 | ENCRYPTED ACCESS</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
