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

# --- INCOLLA QUI IL TUO DIRECT LINK DI ADSTERRA ---
ADSTERRA_DIRECT_LINK = "https://www.esempio-direct-link.com/codice" 

# --- DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; }
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    .section-card { background: #0a0a0a; padding: 25px; border-radius: 20px; border: 1px solid #1a1a1a; margin-bottom: 20px; }
    .premium-choice { background: #111; border: 1px solid #d4af37; padding: 20px; border-radius: 15px; text-align: center; }
    .stButton>button { border-radius: 12px !important; font-weight: 800 !important; width: 100% !important; background: #d4af37 !important; color: black !important; border: none !important; }
    .unlock-loading { color: #d4af37; font-weight: 600; text-align: center; margin: 15px 0; font-size: 1.1em; }
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
st.markdown("<h1 style='text-align:center; color:#d4af37; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; font-size:0.7em; margin-bottom:30px;'>ELITE SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# AREA CARICAMENTO
st.markdown('<div class="section-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1: uploaded_file = st.file_uploader("📂 Carica ZIP", type="zip")
with col2: historical_file = st.file_uploader("⏳ Carica Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as z:
            fols, fings = set(), set()
            for path in z.namelist():
                p_l = path.lower()
                if p_l.endswith('followers_1.json'):
                    with z.open(path) as f: fols.update(raw_text_extract(f.read()))
                elif p_l.endswith('following.json') and 'hashtag' not in p_l:
                    with z.open(path) as f: fings.update(raw_text_extract(f.read()))

            if fings and fols:
                non_ricambiano = sorted(list(fings - fols))
                fan = sorted(list(fols - fings))

                # Dashboard Metriche
                st.write("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("Seguiti", len(fings))
                m2.metric("Followers", len(fols))
                m3.metric("Persi", len(non_ricambiano))

                st.write("###")
                t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SNAPSHOT"])

                with t1:
                    st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                with t2:
                    if 'unlocked' not in st.session_state: st.session_state.unlocked = False

                    if not st.session_state.unlocked:
                        st.markdown(f"### 🔒 Lista Fan Segreti ({len(fan)})")
                        st.write("Scegli come visualizzare i profili che ti seguono:")
                        
                        cp, ca = st.columns(2)
                        with cp:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("💰 **Premium**")
                            st.markdown(f'<a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;"><button style="background:#d4af37; color:black; border:none; padding:12px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">PAGA 1,29€</button></a>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        with ca:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("📺 **Gratis**")
                            # IL TRUCCO: Un link che sembra un bottone per aprire la pubblicità
                            st.markdown(f"""
                                <a href="{ADSTERRA_DIRECT_LINK}" target="_blank" style="text-decoration:none;">
                                    <button onclick="window.location.reload();" style="background:#222; color:#d4af37; border:1px solid #d4af37; padding:12px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">
                                        GUARDA PUBBLICITÀ
                                    </button>
                                </a>
                            """, unsafe_allow_html=True)
                            if st.button("HO CLICCATO, SBLOCCA"):
                                st.session_state.waiting = True
                            st.markdown('</div>', unsafe_allow_html=True)

                        if 'waiting' in st.session_state and st.session_state.waiting:
                            st.markdown('<div class="unlock-loading">⚠️ Verifica visione in corso... Resta sulla pagina (30s)</div>', unsafe_allow_html=True)
                            bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.3) # 30 secondi totali
                                bar.progress(i + 1)
                            st.session_state.unlocked = True
                            st.session_state.waiting = False
                            st.rerun()
                    else:
                        st.success("✅ Accesso Fan Sbloccato")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    snap_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                    st.download_button("📥 GENERA SNAPSHOT .INSTA", json.dumps(snap_data), "profilo.insta")

    except Exception: st.error("Errore ZIP.")

# FOOTER ADS (BANNER FISSO)
st.write("---")
components.html(f"""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
