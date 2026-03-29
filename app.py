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

if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False

# --- DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 25px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 20px; }
    
    .ad-overlay-card {
        background: #111;
        border: 2px solid #d4af37;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
    }
    
    .timer-text { font-size: 3rem; font-weight: 800; color: #d4af37; margin: 10px 0; }
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; background: #d4af37 !important; color: black !important; border: none !important; padding: 15px; }
    
    .btn-secondary {
        background: #222 !important; color: #d4af37 !important; border: 1px solid #d4af37 !important;
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
        if (clean and len(clean) < 31 and clean not in blacklist and not clean.startswith('http') and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; font-weight:800; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:40px;'>MONETIZED ANALYTICS</p>", unsafe_allow_html=True)

# CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Carica lo ZIP di Instagram", type="zip")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            fols, fings = set(), set()
            for path in z.namelist():
                if path.lower().endswith('followers_1.json'):
                    with z.open(path) as f: fols.update(raw_text_extract(f.read()))
                elif path.lower().endswith('following.json') and 'hashtag' not in path.lower():
                    with z.open(path) as f: fings.update(raw_text_extract(f.read()))

            if fings and fols:
                non_ricambiano = sorted(list(fings - fols))
                fan = sorted(list(fols - fings))

                t1, t2 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)"])

                # --- LOGICA SBLOCCO OTTIMIZZATA ---
                def handle_unlock(label, link, session_key):
                    if not st.session_state[session_key]:
                        st.markdown(f"""
                        <div class="ad-overlay-card">
                            <h3 style="color:#d4af37;">🔒 {label}</h3>
                            <p style="font-size:0.9em;">Per sbloccare la lista gratuitamente:</p>
                            <ol style="text-align:left; display:inline-block; font-size:0.8em; margin-bottom:20px;">
                                <li>Clicca il tasto oro qui sotto (apre la pubblicità).</li>
                                <li><b>Torna subito su questa pagina</b>.</li>
                                <li>Attendi il termine del countdown.</li>
                            </ol>
                            <a href="{link}" target="_blank" style="text-decoration:none;">
                                <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">1. CLICCA E GUARDA ADS</button>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("2. HO CLICCATO, AVVIA CONTEGGIO", key="btn_"+session_key):
                            placeholder = st.empty()
                            for i in range(30, 0, -1):
                                with placeholder.container():
                                    st.markdown(f'<div class="timer-text">{i}s</div>', unsafe_allow_html=True)
                                    st.progress( (30-i)/30 )
                                    st.write("⏳ Verifica interazione in corso... resta qui!")
                                time.sleep(1)
                            st.session_state[session_key] = True
                            st.rerun()
                        return False
                    return True

                with t1:
                    if handle_unlock(f"Unfollowers ({len(non_ricambiano)})", LINK_UNFOLLOWERS, 'unf_unlocked'):
                        st.success("✅ Lista Sbloccata")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                with t2:
                    if handle_unlock(f"Fan Segreti ({len(fan)})", LINK_FAN_SEGRETI, 'fan_unlocked'):
                        st.success("✅ Lista Sbloccata")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

    except Exception as e:
        st.error("Errore nel caricamento.")

# FOOTER ADS (BANNER SEMPRE VISIBILE)
st.write("---")
components.html("""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
