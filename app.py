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

# --- INIZIALIZZAZIONE STATI ---
if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False
if 'show_ad_unf' not in st.session_state: st.session_state.show_ad_unf = False
if 'show_ad_fan' not in st.session_state: st.session_state.show_ad_fan = False

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
with c1: uploaded_file = st.file_uploader("📂 Carica ZIP", type="zip")
with c2: historical_file = st.file_uploader("⏳ Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # Gestione Overlay Pubblicitario (Senza Reload)
    if st.session_state.show_ad_unf or st.session_state.show_ad_fan:
        target_link = LINK_UNFOLLOWERS if st.session_state.show_ad_unf else LINK_FAN_SEGRETI
        
        # UI Overlay Temporaneo
        st.markdown(f"""
            <div style="position:fixed; top:0; left:0; width:100%; height:100%; background:black; z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#d4af37;">
                <h2>🎬 Analisi in corso...</h2>
                <p style="color:white;">La tua lista si sbloccherà tra 30 secondi</p>
            </div>
            <script>window.open('{target_link}', '_blank');</script>
        """, unsafe_allow_html=True)
        
        bar = st.progress(0)
        for i in range(100):
            time.sleep(0.3) # 30 secondi
            bar.progress(i + 1)
        
        # Sblocco automatico dello stato
        if st.session_state.show_ad_unf: st.session_state.unf_unlocked = True
        if st.session_state.show_ad_fan: st.session_state.fan_unlocked = True
        
        st.session_state.show_ad_unf = False
        st.session_state.show_ad_fan = False
        st.rerun()

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

                st.write("###")
                t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SNAPSHOT"])

                with t1:
                    if not st.session_state.unf_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">📉 Lista Unfollowers ({len(non_ricambiano)})</h3>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA SUBITO 0,99€</button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📺 GUARDA VIDEO E SBLOCCA (GRATIS)", key="btn_unf"):
                            st.session_state.show_ad_unf = True
                            st.rerun()
                    else:
                        st.success("✅ Lista Unfollowers Sbloccata")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                with t2:
                    if not st.session_state.fan_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">👑 Fan Segreti ({len(fan)})</h3>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA SUBITO 0,99€</button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📺 GUARDA VIDEO E SBLOCCA (GRATIS)", key="btn_fan"):
                            st.session_state.show_ad_fan = True
                            st.rerun()
                    else:
                        st.success("✅ Lista Fan Sbloccata")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    st.download_button("📥 GENERA SNAPSHOT", json.dumps({"f": list(fols)}), "profilo.insta")

    except Exception: st.error("Errore ZIP.")

# BANNER FISSO FOOTER
st.write("---")
components.html("""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
