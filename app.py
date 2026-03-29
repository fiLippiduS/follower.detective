import streamlit as st
import json
import zipfile
import pandas as pd
import re
import time
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- 🟢 SMART LINKS ADSTERRA ---
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# --- LOGICA ESTRAZIONE ---
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

# --- STATI ---
if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False
if 'last_file_hash' not in st.session_state: st.session_state.last_file_hash = None

# --- DESIGN ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 20px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 15px; }
    .timer-display { font-size: 4rem; font-weight: 900; color: #d4af37; text-align: center; }
    .guide-box { background: rgba(212, 175, 55, 0.1); border-left: 4px solid #d4af37; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>MOBILE-FIRST ARCHITECTURE</p>", unsafe_allow_html=True)

# 1. GUIDA FISSA
st.markdown('<div class="guide-box"><b>📖 GUIDA:</b> Carica lo ZIP. Clicca sul tasto dorato: la pubblicità si aprirà e il timer partirà automaticamente qui sotto.</div>', unsafe_allow_html=True)

# 2. CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Archivio ZIP", type="zip")
with c2: historical_file = st.file_uploader("⏳ Storico .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    current_hash = get_file_hash(uploaded_file.getvalue())
    if st.session_state.last_file_hash != current_hash:
        st.session_state.unf_unlocked = False
        st.session_state.fan_unlocked = False
        st.session_state.last_file_hash = current_hash

    fols, fings = process_zip(uploaded_file)
    non_ricambiano = sorted(list(fings - fols))
    fan = sorted(list(fols - fings))

    st.write("---")
    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA"])

    def render_smart_unlock(data_list, session_key, ad_link):
        if not st.session_state[session_key]:
            # --- COMPONENTE IBRIDO (TIMER + LINK) ---
            # Questo blocco HTML gestisce TUTTO localmente sul telefono dell'utente
            components.html(f"""
                <div id="unlock-container" style="text-align:center; font-family:sans-serif; color:white;">
                    <p style="font-size:14px; opacity:0.7;">Sblocca {len(data_list)} profili</p>
                    
                    <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=TUO_EMAIL_PAYPAL&currency_code=EUR&amount=0.99" 
                       target="_blank" style="display:block; background:#222; color:#d4af37; padding:15px; border-radius:12px; text-decoration:none; font-weight:bold; border:1px solid #d4af37; margin-bottom:10px;">
                        🚀 SBLOCCA ORA 0,99€
                    </a>

                    <button id="main-ad-btn" style="width:100%; padding:18px; background:#d4af37; color:black; border-radius:12px; font-weight:800; border:none; cursor:pointer; font-size:16px;">
                        📺 GUARDA ADS E SBLOCCA GRATIS
                    </button>

                    <div id="timer-box" style="display:none; margin-top:20px;">
                        <div id="countdown" style="font-size:50px; font-weight:900; color:#d4af37;">30</div>
                        <p style="font-size:14px; color:#d4af37;">Verifica visione in corso...</p>
                    </div>
                </div>

                <script>
                    const btn = document.getElementById('main-ad-btn');
                    const timerBox = document.getElementById('timer-box');
                    const countdownEl = document.getElementById('countdown');
                    const container = document.getElementById('unlock-container');

                    btn.addEventListener('click', function() {{
                        // 1. Apri Pubblicità (Azione fisica ammessa dal telefono)
                        window.open('{ad_link}', '_blank');

                        // 2. Nascondi tasti e mostra Timer immediatamente
                        btn.style.display = 'none';
                        timerBox.style.display = 'block';

                        // 3. Avvia Countdown locale
                        let timeLeft = 30;
                        const timer = setInterval(function() {{
                            timeLeft--;
                            countdownEl.textContent = timeLeft;
                            if (timeLeft <= 0) {{
                                clearInterval(timer);
                                // Invia segnale a Streamlit per mostrare i dati reali
                                window.parent.postMessage({{type: 'streamlit:set_component_value', value: 'FINISH'}}, '*');
                            }}
                        }}, 1000);
                    }});
                </script>
            """, height=220)

            # Ricezione del segnale di fine timer dal Javascript
            if st.session_state.get(f"trigger_{session_key}") == "FINISH":
                st.session_state[session_key] = True
                st.session_state[f"trigger_{session_key}"] = None
                st.rerun()
        else:
            st.success("✅ Lista Sbloccata")
            st.dataframe(pd.DataFrame(data_list, columns=["Username"]), use_container_width=True)

    with t1: render_smart_unlock(non_ricambiano, 'unf_unlocked', LINK_UNFOLLOWERS)
    with t2: render_smart_unlock(fan, 'fan_unlocked', LINK_FAN_SEGRETI)
    with t3:
        snap = {"followers": list(fols)}
        st.download_button("📥 GENERA SNAPSHOT", json.dumps(snap), "mio.insta")

# BANNER FISSO FOOTER
st.write("---")
components.html("""<div style="display:flex; justify-content:center;"><script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script></div>""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
