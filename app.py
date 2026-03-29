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

# --- STATO DELL'APP ---
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
    .premium-lock-card { background: linear-gradient(145deg, #111, #000); border: 1px solid #d4af37; padding: 30px; border-radius: 20px; text-align: center; margin: 10px 0; }
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; background: #d4af37 !important; color: black !important; border: none !important; padding: 15px; }
    .loading-text { color: #d4af37; font-weight: bold; text-align: center; font-size: 1.2em; margin-bottom: 10px; }
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

# --- UI START ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#d4af37; font-weight:800; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:40px;'>ELITE SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1: uploaded_file = st.file_uploader("📂 Carica lo ZIP di Instagram", type="zip")
with c2: historical_file = st.file_uploader("⏳ Carica Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        # Analisi dei file ZIP
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

                st.write("---")
                t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SNAPSHOT"])

                # --- TAB 1: UNFOLLOWERS ---
                with t1:
                    if not st.session_state.unf_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">📉 Lista Unfollowers ({len(non_ricambiano)})</h3>
                                <p>Sblocca la lista dei profili che non ti ricambiano.</p>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA ORA 0,99€</button>
                                </a>
                                <p style="font-size:0.8em; opacity:0.5;">oppure</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("📺 GUARDA PUBBLICITÀ E SBLOCCA GRATIS", key="btn_unf"):
                            # Apre lo smart link in una nuova scheda
                            components.html(f"<script>window.open('{LINK_UNFOLLOWERS}', '_blank');</script>", height=0)
                            
                            # Countdown visivo
                            st.markdown('<p class="loading-text">Sblocco in corso... Attendi 30 secondi</p>', unsafe_allow_html=True)
                            bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.3)
                                bar.progress(i + 1)
                            
                            st.session_state.unf_unlocked = True
                            st.rerun()
                    else:
                        st.success("✅ Accesso Unfollowers Sbloccato")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                # --- TAB 2: FAN SEGRETI ---
                with t2:
                    if not st.session_state.fan_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">👑 Fan Segreti ({len(fan)})</h3>
                                <p>Scopri chi ti segue segretamente.</p>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA ORA 0,99€</button>
                                </a>
                                <p style="font-size:0.8em; opacity:0.5;">oppure</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("📺 GUARDA PUBBLICITÀ E SBLOCCA GRATIS", key="btn_fan"):
                            components.html(f"<script>window.open('{LINK_FAN_SEGRETI}', '_blank');</script>", height=0)
                            
                            st.markdown('<p class="loading-text">Analisi in corso... Attendi 30 secondi</p>', unsafe_allow_html=True)
                            bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.3)
                                bar.progress(i + 1)
                            
                            st.session_state.fan_unlocked = True
                            st.rerun()
                    else:
                        st.success("✅ Accesso Fan Sbloccato")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    st.download_button("📥 GENERA SNAPSHOT .INSTA", json.dumps({"f": list(fols)}), "mio_profilo.insta")

    except Exception as e:
        st.error(f"Errore: {e}")

# BANNER FISSO FOOTER
st.write("---")
components.html("""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
