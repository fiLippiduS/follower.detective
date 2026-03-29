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

# --- 🟢 INCOLLA QUI IL TUO DIRECT LINK DI ADSTERRA ---
ADSTERRA_DIRECT_LINK = "https://www.esempio-direct-link.com/tuo-codice-qui" 

# --- DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #000; 
        color: #f5f5f7; 
    }
    
    .main-container { max-width: 800px; margin: auto; padding: 10px; }
    
    .section-card { 
        background: #0a0a0a; 
        padding: 25px; 
        border-radius: 20px; 
        border: 1px solid #1a1a1a; 
        margin-bottom: 20px; 
    }
    
    .premium-choice { 
        background: #111; 
        border: 1px solid #d4af37; 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
    }
    
    .stButton>button { 
        border-radius: 12px !important; 
        font-weight: 800 !important; 
        width: 100% !important; 
        background: #d4af37 !important; 
        color: black !important; 
        border: none !important; 
    }

    .guide-box {
        background: rgba(255,255,255,0.03);
        padding: 20px;
        border-radius: 15px;
        border-left: 4px solid #d4af37;
        font-size: 0.85em;
        margin-bottom: 25px;
    }
    
    .unlock-loading { 
        color: #d4af37; 
        font-weight: 600; 
        text-align: center; 
        margin: 15px 0; 
        font-size: 1.1em; 
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

# HEADER
st.markdown("<h1 style='text-align:center; color:#d4af37; font-weight:800; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; letter-spacing:3px; font-size:0.7em; margin-bottom:40px;'>PREMIUM SECURITY ANALYTICS</p>", unsafe_allow_html=True)

# 1. GUIDA ESPANDIBILE (Sempre visibile per aiuto)
with st.expander("📖 Guida Rapida: Come ottenere i tuoi dati", expanded=False):
    st.markdown("""
    <div class="guide-box">
    <b>01.</b> Apri Instagram > Centro Account.<br>
    <b>02.</b> Scarica informazioni > Seleziona 'Follower e seguiti'.<br>
    <b>03.</b> Formato: <b>JSON</b> | Intervallo: <b>Dall'inizio</b>.<br>
    <b>04.</b> Carica lo ZIP qui sotto appena pronto.
    </div>
    """, unsafe_allow_html=True)

# 2. AREA CARICAMENTO (Dual Upload)
st.markdown('<div class="section-card" style="border: 1px solid rgba(212,175,55,0.2);">', unsafe_allow_html=True)
c_zip, c_hist = st.columns(2)
with c_zip:
    uploaded_file = st.file_uploader("📂 Archivio ZIP", type="zip")
with c_hist:
    historical_file = st.file_uploader("⏳ Snapshot .insta", type="insta")
st.markdown('</div>', unsafe_allow_html=True)

# 3. ANALISI
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

                # --- CONFRONTO STORICO ---
                if historical_file:
                    old_data = json.load(historical_file)
                    old_fols = set(old_data.get("followers", []))
                    persi = sorted(list(old_fols - fols))
                    if persi:
                        st.error(f"🚨 ATTENZIONE: {len(persi)} utenti hanno smesso di seguirti! \n\n {', '.join(persi)}")
                    else:
                        st.success("✅ Nessun nuovo unfollower rilevato dallo storico.")

                # DASHBOARD
                st.write("---")
                m1, m2, m3 = st.columns(3)
                m1.metric("Seguiti", len(fings))
                m2.metric("Followers", len(fols))
                m3.metric("Non Ricambiano", len(non_ricambiano))

                st.write("###")
                t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "👑 FAN (PRO)", "💾 SALVA STORICO"])

                with t1:
                    st.markdown("##### Profili che non ricambiano il follow")
                    st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True, height=300)

                with t2:
                    if 'unlocked' not in st.session_state: st.session_state.unlocked = False

                    if not st.session_state.unlocked:
                        st.markdown(f"### 🔒 Sblocca {len(fan)} Fan Segreti")
                        st.write("Scegli il metodo di accesso:")
                        
                        col_p, col_a = st.columns(2)
                        with col_p:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("💰 **Fast Pass**")
                            st.markdown(f'<a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;"><button style="background:#d4af37; color:black; border:none; padding:12px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">PAGA 1,29€</button></a>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)

                        with col_a:
                            st.markdown('<div class="premium-choice">', unsafe_allow_html=True)
                            st.write("📺 **Ad-Support**")
                            # Link Diretto Adsterra
                            st.markdown(f"""
                                <a href="{ADSTERRA_DIRECT_LINK}" target="_blank" style="text-decoration:none;">
                                    <button style="background:#222; color:#d4af37; border:1px solid #d4af37; padding:12px; width:100%; border-radius:10px; font-weight:bold; cursor:pointer;">
                                        GUARDA PUBBLICITÀ
                                    </button>
                                </a>
                            """, unsafe_allow_html=True)
                            if st.button("SBLOCCA ORA"):
                                st.session_state.loading_fan = True
                            st.markdown('</div>', unsafe_allow_html=True)

                        if 'loading_fan' in st.session_state and st.session_state.loading_fan:
                            st.markdown('<div class="unlock-loading">⚠️ Sblocco in corso... Non chiudere (30s)</div>', unsafe_allow_html=True)
                            bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.3) 
                                bar.progress(i + 1)
                            st.session_state.unlocked = True
                            st.session_state.loading_fan = False
                            st.rerun()
                    else:
                        st.success("✅ Fan Segreti Sbloccati!")
                        st.dataframe(pd.DataFrame(fan, columns=["Username"]), use_container_width=True)

                with t3:
                    st.markdown("##### Crea Snapshot Temporale")
                    st.write("Salva i follower di oggi per confrontarli la prossima settimana.")
                    snap_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                    st.download_button("📥 GENERA FILE .INSTA", json.dumps(snap_data), "mio_profilo.insta")

    except Exception: st.error("Errore nell'analisi del file ZIP.")

# --- FOOTER CON BANNER PUBBLICITARIO FISSO ---
st.write("---")
st.markdown('<p style="text-align:center; opacity:0.3; font-size:0.6em; letter-spacing:2px;">SPONSORED BY ADSTERRA</p>', unsafe_allow_html=True)
components.html(f"""
    <div style="display:flex; justify-content:center;">
        <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
    </div>
""", height=250)

st.markdown('<p style="text-align:center; opacity:0.1; font-size:0.6em;">GOLD ENGINE v9.0 | PRIVACY ENCRYPTED</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
