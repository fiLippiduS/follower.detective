import streamlit as st
import json
import zipfile
import pandas as pd
import re
import time
import hashlib
import streamlit.components.v1 as components
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- 🟢 SMART LINKS ADSTERRA ---
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# --- LOGICA ESTRAZIONE & SICUREZZA ---
def get_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

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

# --- GESTIONE STATI ---
if 'last_file_hash' not in st.session_state: st.session_state.last_file_hash = None
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
    .timer-val { font-size: 3.5rem; font-weight: 900; color: #d4af37; text-align: center; }
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; background: #d4af37 !important; color: black !important; height: 55px; border:none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>ULTIMATE SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# 1. GUIDA FISSA
st.markdown('<div class="guide-box"><b>📘 ISTRUZIONI:</b> Carica lo ZIP. Se cambi file, lo sblocco si resetta per sicurezza.</div>', unsafe_allow_html=True)

# 2. CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Carica ZIP Instagram", type="zip")
with c2: historical_file = st.file_uploader("⏳ Carica Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # --- LOGICA RESET AUTOMATICO ---
    current_hash = get_file_hash(uploaded_file.getvalue())
    if st.session_state.last_file_hash != current_hash:
        st.session_state.unf_unlocked = False
        st.session_state.fan_unlocked = False
        st.session_state.last_file_hash = current_hash

    fols, fings = process_zip(uploaded_file)
    non_ricambiano = sorted(list(fings - fols))
    fan = sorted(list(fols - fings))

    # Storico
    if historical_file:
        try:
            old_data = json.load(historical_file)
            old_fols = set(old_data.get("followers", []))
            persi = sorted(list(old_fols - fols))
            if persi: st.error(f"🚨 ALERT: {len(persi)} utenti ti hanno rimosso!")
        except: pass

    st.write("---")
    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA"])

    # FUNZIONE SBLOCCO UNIFICATA (ONE-CLICK)
    def render_unlock(data_list, session_key, ad_link):
        if not st.session_state[session_key]:
            st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <p>Contenuto Protetto ({len(data_list)} profili)</p>
                    <a href="https://paypal.me/TUOUSER/0.99" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; padding:12px; background:#d4af37; color:black; border-radius:10px; font-weight:bold; border:none; margin-bottom:15px; cursor:pointer;">SBLOCCA SUBITO 0,99€</button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            # IL TASTO MAGICO: Apre link e attiva timer
            if st.button("📺 GUARDA ADS E SBLOCCA GRATIS", key="oneclick_"+session_key):
                # Script per aprire pubblicità
                components.html(f"<script>window.open('{ad_link}', '_blank');</script>", height=0)
                
                # Countdown immediato
                placeholder = st.empty()
                for i in range(30, -1, -1):
                    with placeholder.container():
                        st.markdown(f'<div class="timer-val">{i}s</div>', unsafe_allow_html=True)
                        st.progress((30-i)/30)
                        st.write("⏳ Analisi in corso... Resta su questa scheda!")
                    time.sleep(1)
                st.session_state[session_key] = True
                st.rerun()
        else:
            st.success("✅ Dati Sbloccati per questo file")
            st.dataframe(pd.DataFrame(data_list, columns=["Username"]), use_container_width=True)

    with t1: render_unlock(non_ricambiano, 'unf_unlocked', LINK_UNFOLLOWERS)
    with t2: render_unlock(fan, 'fan_unlocked', LINK_FAN_SEGRETI)
    with t3:
        snap = {"followers": list(fols)}
        st.download_button("📥 GENERA SNAPSHOT", json.dumps(snap), "mio.insta")

# BANNER FISSO FOOTER
st.write("---")
components.html("""<div style="display:flex; justify-content:center;"><script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script></div>""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
