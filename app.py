import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- DESIGN SYSTEM MOBILE-OPTIMIZED ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }

    /* Ottimizzazione per Schermi Piccoli */
    @media (max-width: 768px) {
        .hero-card { padding: 20px !important; border-radius: 20px !important; }
        .stMetric { margin-bottom: 10px !important; }
        h1 { font-size: 2.2em !important; }
    }

    .hero-card {
        background: linear-gradient(145deg, #121212, #000000);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        margin-bottom: 20px;
    }

    .premium-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(0,0,0,1) 100%);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid #d4af37;
        text-align: center;
    }

    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 700 !important;
    }

    .instruction-step {
        background: #111;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #222;
        font-size: 0.8em;
    }

    /* Alert Unfollower Mobile */
    .unfollow-alert {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid #e74c3c;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #ff4b4b;
        font-size: 0.9em;
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
        if (clean and len(clean) < 31 and clean not in blacklist and 
            not clean.startswith('http') and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

# --- SIDEBAR (MOBILE DRAWER) ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37; text-align:center;'>ELITE PROTOCOL</h2>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;">
            <div style="background:#d4af37; color:#000; padding:15px; border-radius:12px; text-align:center; font-weight:800;">
                SBLOCCA INSIGHTS PRO
            </div>
        </a>
    """, unsafe_allow_html=True)
    
    st.write("###")
    st.markdown("#### ⏳ STORICO")
    historical_file = st.file_uploader("Carica Snapshot .insta", type="insta")
    
    st.write("---")
    st.markdown("#### GUIDA RAPIDA")
    for s in ["1. Impostazioni IG", "2. Centro Account", "3. Scarica Info", "4. Follower/Seguiti", "5. Formato JSON"]:
        st.markdown(f"<div class='instruction-step'>{s}</div>", unsafe_allow_html=True)

# --- CORPO PRINCIPALE ---
st.markdown("<h1 style='text-align:center; font-weight:800; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.4; letter-spacing:2px; font-size:0.8em; margin-bottom:30px;'>SECURITY PROTOCOL v5.0</p>", unsafe_allow_html=True)

st.markdown('<div class="hero-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica lo ZIP aggiornato", type="zip", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Analisi in corso..."):
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                fols, fings = set(), set()
                for path in z.namelist():
                    p_lower = path.lower()
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f: fols.update(raw_text_extract(f.read()))
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f: fings.update(raw_text_extract(f.read()))

                if fings and fols:
                    non_ricambiano = sorted(list(fings - fols))
                    fan = sorted(list(fols - fings))
                    comuni = fings.intersection(fols)

                    # Alert Storico (Responsive)
                    if historical_file:
                        old_data = json.load(historical_file)
                        old_fols = set(old_data.get("followers", []))
                        persi = sorted(list(old_fols - fols))
                        if persi:
                            st.markdown(f'<div class="unfollow-alert">🚨 {len(persi)} nuovi unfollowers rilevati!<br><small>{", ".join(persi)}</small></div>', unsafe_allow_html=True)
                        else:
                            st.success("Nessun nuovo unfollower.")

                    # Dashboard Metriche (Auto-stacking su mobile)
                    m1, m2 = st.columns(2)
                    m1.metric("Seguiti", len(fings))
                    m2.metric("Followers", len(fols))
                    
                    m3, m4 = st.columns(2)
                    m3.metric("Persi", len(non_ricambiano))
                    m4.metric("Privacy", "A+")

                    st.write("###")
                    
                    t1, t2, t3 = st.tabs(["📉 LISTA", "💎 PRO", "⏱️ SALVA"])

                    with t1:
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Account"]), use_container_width=True, height=300)

                    with t2:
                        st.markdown(f"""
                            <div class="premium-card">
                                <h3 style='color:#d4af37;'>Fan Segreti</h3>
                                <p style='font-size:0.9em; opacity:0.8;'>Sblocca l'identità di {len(fan)} persone che ti seguono.</p>
                                <a href="https://www.paypal.me/TUO_USER/1.29" style='text-decoration:none;'>
                                    <div style="background:#d4af37; color:#000; padding:15px; border-radius:50px; font-weight:bold; margin-top:10px;">SBLOCCA 1,29€</div>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)

                    with t3:
                        st.markdown("#### Crea Snapshot")
                        st.caption("Scarica il file .insta per confrontarlo in futuro.")
                        snapshot_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                        st.download_button("📥 GENERA .INSTA", json.dumps(snapshot_data), f"snap_{datetime.now().strftime('%d_%m')}.insta")

        except Exception:
            st.error("File non valido.")

st.markdown('<p style="text-align:center; opacity:0.1; font-size:0.6em; margin-top:50px;">GOLD ENGINE v5.1</p>', unsafe_allow_html=True)
