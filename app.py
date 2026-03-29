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

# --- 🟢 SMART LINKS ADSTERRA ---
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# --- CACHE & LOGICA ESTRAZIONE ---
@st.cache_data(show_spinner=False)
def process_zip(file_bytes):
    try:
        with zipfile.ZipFile(file_bytes, 'r') as z:
            fols, fings = set(), set()
            for path in z.namelist():
                if path.lower().endswith('followers_1.json'):
                    with z.open(path) as f: fols.update(raw_text_extract(f.read()))
                elif path.lower().endswith('following.json') and 'hashtag' not in path.lower():
                    with z.open(path) as f: fings.update(raw_text_extract(f.read()))
            return fols, fings
    except: return set(), set()

def raw_text_extract(text_bytes):
    text = text_bytes.decode('utf-8', errors='ignore')
    potentials = re.findall(r'"([^"]*)"', text)
    found = set()
    blacklist = {'value', 'href', 'timestamp', 'string_list_data', 'relationships_following', 'title', 'true', 'false', 'none'}
    for p in potentials:
        clean = p.strip().lower()
        if (clean and len(clean) < 31 and clean not in blacklist and not clean.startswith('http') and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

# --- INIZIALIZZAZIONE STATI ---
if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False

# --- DESIGN ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 20px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 15px; }
    .guide-box { background: rgba(212, 175, 55, 0.05); border-left: 4px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 0.9em; }
    .timer-val { font-size: 3.5rem; font-weight: 900; color: #d4af37; text-align: center; margin: 10px 0; }
    .premium-btn { 
        display: block; width: 100%; padding: 15px; background: #d4af37; color: black !important; 
        text-align: center; border-radius: 12px; font-weight: 800; text-decoration: none; margin-bottom: 10px;
    }
    .ad-btn { 
        display: block; width: 100%; padding: 15px; background: transparent; color: #d4af37 !important; 
        text-align: center; border-radius: 12px; font-weight: 800; border: 1px solid #d4af37; text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>PREMIUM ANALYTICS SYSTEM</p>", unsafe_allow_html=True)

# 1. GUIDA FISSA
with st.container():
    st.markdown("""
    <div class="guide-box">
        <b>📘 GUIDA:</b> Scarica lo ZIP da Instagram (JSON, 'Dall'inizio'). 
        Carica lo ZIP qui sotto per vedere chi non ti segue o i tuoi Fan. 
        Usa lo <b>Snapshot</b> per monitorare i cambiamenti nel tempo.
    </div>
    """, unsafe_allow_html=True)

# 2. CARICAMENTO & STORICO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Carica ZIP Instagram", type="zip")
with c2: historical_file = st.file_uploader("⏳ Carica Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    fols, fings = process_zip(uploaded_file)
    non_ricambiano = sorted(list(fings - fols))
    fan = sorted(list(fols - fings))

    # Logica confronto storico
    if historical_file:
        try:
            old_data = json.load(historical_file)
            old_fols = set(old_data.get("followers", []))
            persi = sorted(list(old_fols - fols))
            if persi: st.error(f"🚨 ALERT: {len(persi)} utenti ti hanno rimosso!")
            else: st.success("✅ Nessun nuovo unfollower rilevato.")
        except: st.warning("Snapshot non valido.")

    st.write("---")
    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA"])

    # FUNZIONE SBLOCCO (MOBILE FRIENDLY)
    def render_unlock(data_list, session_key, ad_link):
        if not st.session_state[session_key]:
            st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <p style="opacity:0.8;">Lista protetta ({len(data_list)} profili)</p>
                    <a href="https://paypal.me/TUOUSER/0.99" class="premium-btn">SBLOCCA SUBITO 0,99€</a>
                    <p style="font-size:0.7em; margin:10px 0;">oppure</p>
                    <a href="{ad_link}" target="_blank" class="ad-btn">1. APRI PUBBLICITÀ</a>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("2. AVVIA TIMER SBLOCCO", key="timer_"+session_key):
                placeholder = st.empty()
                for i in range(30, -1, -1):
                    with placeholder.container():
                        st.markdown(f'<div class="timer-val">{i}s</div>', unsafe_allow_html=True)
                        st.progress((30-i)/30)
                        st.write("⏳ Verifica visione... Resta su questa pagina.")
                    time.sleep(1)
                st.session_state[session_key] = True
                st.rerun()
        else:
            st.success("✅ Dati Sbloccati")
            st.dataframe(pd.DataFrame(data_list, columns=["Username"]), use_container_width=True)

    with t1: render_unlock(non_ricambiano, 'unf_unlocked', LINK_UNFOLLOWERS)
    with t2: render_unlock(fan, 'fan_unlocked', LINK_FAN_SEGRETI)
    with t3:
        snap = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
        st.download_button("📥 GENERA SNAPSHOT .INSTA", json.dumps(snap), "mio_profilo.insta")

# BANNER FISSO FOOTER
st.write("---")
components.html("""<div style="display:flex; justify-content:center;"><script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script></div>""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
