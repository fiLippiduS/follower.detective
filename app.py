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

# --- DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; background-color: #000; color: #f5f5f7; 
    }
    
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    
    .section-card { 
        background: #0a0a0a; padding: 25px; border-radius: 20px; 
        border: 1px solid #1a1a1a; margin-bottom: 20px; 
    }
    
    .premium-lock-card { 
        background: linear-gradient(145deg, #111, #000); 
        border: 1px solid #d4af37; padding: 30px; 
        border-radius: 20px; text-align: center; margin: 10px 0;
    }
    
    .stButton>button { 
        border-radius: 12px !important; font-weight: 800 !important; 
        width: 100% !important; background: #d4af37 !important; 
        color: black !important; border: none !important; padding: 15px;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
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

# --- LOGICA VIDEO AD OVERLAY ---
def video_ad_component(target_link, session_key):
    """Componente personalizzato per gestire il video ad e lo sblocco"""
    components.html(f"""
    <div id="ad-overlay" style="position:fixed; top:0; left:0; width:100%; height:100%; background:black; z-index:9999; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#d4af37; font-family:sans-serif;">
        <h2 style="margin-bottom:20px;">🎬 Analisi Video in Corso...</h2>
        <p style="color:white; opacity:0.8; margin-bottom:30px;">Non chiudere questa finestra per sbloccare i dati</p>
        
        <div id="timer" style="font-size:48px; font-weight:bold; border:4px solid #d4af37; border-radius:50%; width:100px; height:100px; display:flex; align-items:center; justify-content:center; margin-bottom:30px;">30</div>
        
        <div id="reward-btn" style="display:none;">
            <button onclick="window.parent.location.reload();" style="background:#d4af37; color:black; border:none; padding:15px 40px; border-radius:30px; font-weight:bold; font-size:18px; cursor:pointer; box-shadow:0 0 20px #d4af37;">✅ ACCEDI AI DATI</button>
        </div>
    </div>

    <script>
        // Apri lo smart link in una nuova scheda
        window.open('{target_link}', '_blank');

        let timeLeft = 30;
        let timerElement = document.getElementById('timer');
        let rewardBtn = document.getElementById('reward-btn');

        let countdown = setInterval(function() {{
            timeLeft--;
            timerElement.innerText = timeLeft;
            if (timeLeft <= 0) {{
                clearInterval(countdown);
                timerElement.style.display = 'none';
                rewardBtn.style.display = 'block';
                // Invia segnale a Streamlit (opzionale, qui usiamo il reload)
            }}
        }}, 1000);
    </script>
    """, height=600)

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

                # --- TAB 1: UNFOLLOWERS ---
                with t1:
                    if 'unf_unlocked' not in st.session_state: st.session_state.unf_unlocked = False
                    
                    if not st.session_state.unf_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">📉 Lista Unfollowers ({len(non_ricambiano)})</h3>
                                <p>Scegli come sbloccare i nomi di chi ti ha rimosso.</p>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA SUBITO 0,99€</button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📺 GUARDA VIDEO E SBLOCCA (GRATIS)", key="btn_unf"):
                            st.session_state.show_ad_unf = True
                        
                        if st.session_state.get('show_ad_unf'):
                            video_ad_component(LINK_UNFOLLOWERS, "unf_unlocked")
                            # Dopo il reload del componente, sblocchiamo
                            st.session_state.unf_unlocked = True

                    else:
                        st.success("✅ Lista Unfollowers Sbloccata")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True)

                # --- TAB 2: FAN SEGRETI ---
                with t2:
                    if 'fan_unlocked' not in st.session_state: st.session_state.fan_unlocked = False
                    
                    if not st.session_state.fan_unlocked:
                        st.markdown(f"""
                            <div class="premium-lock-card">
                                <h3 style="color:#d4af37;">👑 Fan Segreti ({len(fan)})</h3>
                                <p>Scopri l'identità dei tuoi ammiratori segreti.</p>
                                <a href="https://www.paypal.me/TUO_USER/0.99" target="_blank" style="text-decoration:none;">
                                    <button style="background:#d4af37; color:black; border:none; padding:15px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer; margin-bottom:15px;">🚀 SBLOCCA SUBITO 0,99€</button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📺 GUARDA VIDEO E SBLOCCA (GRATIS)", key="btn_fan"):
                            st.session_state.show_ad_fan = True
                        
                        if st.session_state.get('show_ad_fan'):
                            video_ad_component(LINK_FAN_SEGRETI, "fan_unlocked")
                            st.session_state.fan_unlocked = True

                    else:
                        st.success("✅ Lista Fan Sbloccata")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    st.download_button("📥 GENERA SNAPSHOT .INSTA", json.dumps({"f": list(fols)}), "profilo.insta")

    except Exception: st.error("Errore ZIP.")

# BANNER FISSO FOOTER
st.write("---")
components.html("""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)
st.markdown('</div>', unsafe_allow_html=True)
