import streamlit as st
import json
import zipfile
import pandas as pd
import re
import time
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- 🟢 SMART LINKS ADSTERRA ---
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# --- LOGICA ESTRAZIONE DATI ---
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
if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False
if 'last_file_hash' not in st.session_state: st.session_state.last_file_hash = None
if 'timer_running' not in st.session_state: st.session_state.timer_running = None

# --- DESIGN & CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 20px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 15px; }
    .timer-val { font-size: 4rem; font-weight: 900; color: #d4af37; text-align: center; margin: 20px 0; }
    
    /* Bottone Mobile-Safe */
    .mobile-ad-btn {
        display: block; width: 100%; padding: 18px; background: #d4af37; color: black !important; 
        text-align: center; border-radius: 12px; font-weight: 800; text-decoration: none; border: none; cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>MOBILE-OPTIMIZED ANALYTICS</p>", unsafe_allow_html=True)

# GUIDA
st.markdown('<div style="background:rgba(212,175,55,0.1); padding:15px; border-radius:10px; margin-bottom:20px; border-left:4px solid #d4af37; font-size:0.85em;"><b>📱 MOBILE READY:</b> Carica lo ZIP. Tocca il tasto dorato: la pubblicità si aprirà e il timer inizierà il countdown qui sotto.</div>', unsafe_allow_html=True)

# CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Archivio ZIP", type="zip")
with c2: historical_file = st.file_uploader("⏳ Storico .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Reset automatico se file diverso
    current_hash = get_file_hash(uploaded_file.getvalue())
    if st.session_state.last_file_hash != current_hash:
        st.session_state.unf_unlocked = False
        st.session_state.fan_unlocked = False
        st.session_state.last_file_hash = current_hash

    fols, fings = process_zip(uploaded_file)
    non_ricambiano = sorted(list(fings - fols))
    fan = sorted(list(fols - fings))

    if historical_file:
        try:
            old_data = json.load(historical_file)
            old_fols = set(old_data.get("followers", []))
            persi = sorted(list(old_fols - fols))
            if persi: st.error(f"🚨 ALERT: {len(persi)} utenti rimosso!")
        except: pass

    st.write("---")

    # --- LOGICA TIMER (TRIGGERATA DA JAVASCRIPT) ---
    if st.session_state.timer_running:
        placeholder = st.empty()
        target_key = st.session_state.timer_running
        for i in range(30, -1, -1):
            with placeholder.container():
                st.markdown(f'<div class="timer-val">{i}s</div>', unsafe_allow_html=True)
                st.progress((30-i)/30)
                st.info("⏳ Validazione... Guarda la pubblicità!")
            time.sleep(1)
        st.session_state[target_key] = True
        st.session_state.timer_running = None
        st.rerun()

    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA"])

    def render_unlock(data_list, session_key, ad_link):
        if not st.session_state[session_key]:
            # Pulsante PayPal (Standard)
            st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=TUO_EMAIL_PAYPAL&currency_code=EUR&amount=0.99&item_name=Sblocco_Lista" 
                       target="_blank" class="mobile-ad-btn" style="background:#222; color:#d4af37 !important; border:1px solid #d4af37; margin-bottom:15px;">
                        🚀 SBLOCCA ORA 0,99€
                    </a>
                </div>
            """, unsafe_allow_html=True)

            # --- IL TASTO UNICO PER SMARTPHONE (HTML + JS BRIDGE) ---
            # Questo tasto apre il link PUBBLICITÀ e comunica a Streamlit di far partire il timer
            components.html(f"""
                <div style="display: flex; justify-content: center;">
                    <button id="trigger-btn" style="width:100%; padding:18px; background:#d4af37; color:black; border-radius:12px; font-weight:800; cursor:pointer; font-size:16px; border:none; font-family:sans-serif;">
                        📺 GUARDA ADS E SBLOCCA GRATIS
                    </button>
                </div>
                <script>
                    const btn = document.getElementById('trigger-btn');
                    btn.addEventListener('click', function() {{
                        // Apre la pubblicità (Azione fisica ammessa dal telefono)
                        window.open('{ad_link}', '_blank');
                        // Invia il segnale a Streamlit per far partire il timer Python
                        window.parent.postMessage({{type: 'streamlit:set_component_value', value: '{session_key}'}}, '*');
                    }});
                </script>
            """, height=80)

            # Ricezione segnale dal tasto HTML
            trigger_val = st.session_state.get(f"trigger_{session_key}")
            if trigger_val == session_key:
                st.session_state.timer_running = session_key
                st.session_state[f"trigger_{session_key}"] = None
                st.rerun()
                
        else:
            st.success("✅ Accesso Autorizzato")
            st.dataframe(pd.DataFrame(data_list, columns=["Username"]), use_container_width=True)

    with t1: render_unlock(non_ricambiano, 'unf_unlocked', LINK_UNFOLLOWERS)
    with t2: render_unlock(fan, 'fan_unlocked', LINK_FAN_SEGRETI)
    with t3:
        snap = {"followers": list(fols)}
        st.download_button("📥 GENERA SNAPSHOT", json.dumps(snap), "mio_profilo.insta")

# BANNER FISSO FOOTER
st.write("---")
components.html("""<div style="display:flex; justify-content:center;"><script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script></div>""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
