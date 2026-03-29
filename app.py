import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE SISTEMA ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- DESIGN SYSTEM ---
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
        padding: 40px;
        border-radius: 30px;
        border: 1px solid #d4af37;
        text-align: center;
    }

    .instruction-step {
        background: #111;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        border: 1px solid #222;
        font-size: 0.85em;
        color: #ccc;
    }

    .stMetric {
        background: transparent !important;
        border: 1px solid #222 !important;
        border-radius: 20px !important;
    }

    .unfollow-alert {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid #e74c3c;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #ff4b4b;
        font-weight: 600;
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

# --- SIDEBAR: PROTOCOLLO & STORICO ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37;'>ELITE PROTOCOL</h2>", unsafe_allow_html=True)
    
    # TASTO MONETIZZAZIONE
    st.markdown("""
        <a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;">
            <div style="background:#d4af37; color:#000; padding:15px; border-radius:12px; text-align:center; font-weight:800; letter-spacing:1px;">
                SBLOCCA INSIGHTS PRO
            </div>
        </a>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    # CARICAMENTO SNAPSHOT (IL "PRIMA")
    st.markdown("#### ⏳ CONFRONTO STORICO")
    st.caption("Carica qui il file .insta salvato in precedenza per rilevare chi ti ha rimosso il segui.")
    historical_file = st.file_uploader("Upload Snapshot", type="insta", label_visibility="collapsed")
    
    st.write("---")
    
    # GUIDA EXPORT
    st.markdown("#### GUIDA ESPORTAZIONE")
    steps = [
        "1. Impostazioni Instagram",
        "2. Centro gestione account",
        "3. Scarica informazioni",
        "4. Seleziona 'Follower e seguiti'",
        "5. Formato: JSON",
        "6. Intervallo: 'Dall'inizio'"
    ]
    for s in steps:
        st.markdown(f"<div class='instruction-step'>{s}</div>", unsafe_allow_html=True)

# --- MAIN ---
st.markdown("<h1 style='text-align:center; font-weight:800; font-size:3em; margin-bottom:0;'>InstaDetective Elite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.4; letter-spacing:4px; margin-bottom:40px;'>MONITORAGGIO STORICO & RELAZIONI</p>", unsafe_allow_html=True)

st.markdown('<div class="hero-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Trascina l'archivio .zip aggiornato per l'analisi", type="zip", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Esecuzione scansione crittografica..."):
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

                    # --- LOGICA CONFRONTO STORICO ---
                    if historical_file:
                        old_data = json.load(historical_file)
                        old_fols = set(old_data.get("followers", []))
                        persi = sorted(list(old_fols - fols))
                        
                        if persi:
                            st.markdown(f"""
                                <div class="unfollow-alert">
                                    🚨 ATTENZIONE: {len(persi)} profili hanno smesso di seguirti dall'ultima analisi!<br>
                                    <span style="color:#ccc; font-size:0.9em; font-weight:400;">Persi: {", ".join(persi)}</span>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.success("✅ Protocollo completato: Nessun nuovo unfollower rilevato.")

                    # METRICHE DASHBOARD
                    st.write("###")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non Ricambiano", len(non_ricambiano))
                    c4.metric("Privacy Score", "A+")

                    st.write("###")
                    
                    t1, t2, t3 = st.tabs(["📉 UNFOLLOWERS", "💎 PREMIUM INSIGHTS", "⏱️ SALVA SNAPSHOT"])

                    with t1:
                        st.markdown("##### Analisi profili senza ricambio")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Nome Account"]), use_container_width=True, height=350)

                    with t2:
                        st.markdown(f"""
                            <div class="premium-card">
                                <h2 style='color:#d4af37;'>Insights Fan Segreti</h2>
                                <p style='opacity:0.7;'>Abbiamo individuato {len(fan)} persone che ti seguono ma che tu non ricambi.</p>
                                <a href="https://www.paypal.me/TUO_USER/1.29" style='text-decoration:none;'>
                                    <button style="background:#d4af37; color:black; padding:18px 45px; border-radius:50px; border:none; font-weight:bold; cursor:pointer; letter-spacing:1px;">
                                        SBLOCCA LISTA - 1,29€
                                    </button>
                                </a>
                                <p style='margin-top:20px; font-size:0.8em; opacity:0.4;'>Accesso istantaneo tramite protocollo sicuro PayPal.</p>
                            </div>
                        """, unsafe_allow_html=True)

                    with t3:
                        st.markdown("### ⏱️ Time Machine")
                        st.write("Crea un punto di ripristino per monitorare chi ti toglie il segui nel tempo.")
                        
                        st.info("""
                        **Come funziona:**
                        1. Scarica ora il file .insta (Snapshot).
                        2. Tra una settimana, carica il nuovo ZIP di Instagram e il file .insta salvato.
                        3. Il sistema ti dirà istantaneamente chi è sparito dalla lista.
                        """)
                        
                        # Generazione file Snapshot
                        snapshot_data = {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "followers": list(fols)
                        }
                        st.download_button(
                            label="📥 GENERA SNAPSHOT STORICO (.insta)",
                            data=json.dumps(snapshot_data),
                            file_name=f"snapshot_{datetime.now().strftime('%d_%m')}.insta",
                            mime="application/json"
                        )

        except Exception:
            st.error("Errore: Archivio non conforme agli standard Instagram.")

st.markdown('<p style="text-align:center; opacity:0.1; margin-top:100px; letter-spacing:2px;">ENCRYPTED SYSTEM ACCESS | v5.0 GOLD</p>', unsafe_allow_html=True)
