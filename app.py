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

# --- LOGICA CORE ---
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

# --- STATI DI SESSIONE ---
if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False
if 'last_file_hash' not in st.session_state: st.session_state.last_file_hash = None
if 'clicked_ad' not in st.session_state: st.session_state.clicked_ad = None

# --- STILE CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 20px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 15px; }
    .timer-val { font-size: 4rem; font-weight: 900; color: #d4af37; text-align: center; }
    .ad-link-btn {
        display: block; width: 100%; padding: 18px; background: transparent; 
        color: #d4af37 !important; border: 2px solid #d4af37; border-radius: 12px; 
        font-weight: 800; text-align: center; text-decoration: none; margin-bottom: 15px;
    }
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; background: #d4af37 !important; color: black !important; border:none; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>ADVANCED ANALYTICS</p>", unsafe_allow_html=True)

# 1. GUIDA FISSA
st.markdown('<div style="background:rgba(212,175,55,0.1); padding:15px; border-radius:10px; margin-bottom:20px; border-left:4px solid #d4af37; font-size:0.85em;"><b>📖 GUIDA:</b> 1. Carica lo ZIP. 2. Clicca sul bordo dorato "GUARDA ADS". 3. Conferma il caricamento cliccando sul tasto pieno che apparirà.</div>', unsafe_allow_html=True)

# 2. CARICAMENTO & STORICO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Archivio ZIP", type="zip")
with c2: historical_file = st.file_uploader("⏳ Storico .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Auto-Reset su nuovo file
    current_hash = get_file_hash(uploaded_file.getvalue())
    if st.session_state.last_file_hash != current_hash:
        st.session_state.unf_unlocked = False
        st.session_state.fan_unlocked = False
        st.session_state.clicked_ad = None
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
            if persi: st.error(f"🚨 {len(persi)} persone non ti seguono più!")
        except: pass

    st.write("---")
    
    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA"])

    def render_unlock_section(data_list, session_key, ad_link):
        if not st.session_state[session_key]:
            st.markdown(f"""
                <div style="text-align:center; padding:15px;">
                    <h3 style="color:#d4af37;">🔒 Lista Protetta</h3>
                    <p style="font-size:0.8em; opacity:0.7; margin-bottom:20px;">Sblocca i {len(data_list)} profili qui sotto.</p>
                    
                    <a href="https://paypal.me/TUOUSER/0.99" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; padding:15px; background:#d4af37; color:black; border-radius:12px; font-weight:bold; border:none; cursor:pointer; margin-bottom:10px;">PAGA 0,99€ (IMMEDIATO)</button>
                    </a>
                    
                    <p style="font-size:0.7em; margin-bottom:15px;">OPPURE</p>
                    
                    <a href="{ad_link}" target="_blank" class="ad-link-btn" onclick="document.getElementById('timer-trigger-{session_key}').click();">
                        📺 1. GUARDA ADS (APRI TAB)
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            # Tasto "Invisibile" di Streamlit che viene mostrato solo per avviare il timer
            if st.button(f"🚀 2. CONFERMA E AVVIA TIMER", key=f"start_{session_key}"):
                placeholder = st.empty()
                for i in range(30, -1, -1):
                    with placeholder.container():
                        st.markdown(f'<div class="timer-val">{i}s</div>', unsafe_allow_html=True)
                        st.progress((30-i)/30)
                        st.info("⏳ Sto verificando l'interazione... resta qui!")
                    time.sleep(1)
                st.session_state[session_key] = True
                st.rerun()
        else:
            st.success("✅ Dati Sbloccati")
            st.dataframe(pd.DataFrame(data_list, columns=["Username"]), use_container_width=True)

    with t1: render_unlock_section(non_ricambiano, 'unf_unlocked', LINK_UNFOLLOWERS)
    with t2: render_unlock_section(fan, 'fan_unlocked', LINK_FAN_SEGRETI)
    with t3:
        snap = {"followers": list(fols)}
        st.download_button("📥 SALVA SNAPSHOT", json.dumps(snap), "mio.insta")

# BANNER FISSO FOOTER
st.write("---")
components.html("""<div style="display:flex; justify-content:center;"><script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script></div>""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
