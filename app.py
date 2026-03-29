import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- DESIGN SYSTEM ULTRA-RESPONSIVE ---
st.markdown("""
    <style>
    /* Rimozione elementi di sistema per pulizia totale */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;} /* Eliminiamo la sidebar problematica */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }

    /* Container Principale Adattivo */
    .main-container {
        max-width: 900px;
        margin: auto;
        padding: 20px;
    }

    .hero-card {
        background: linear-gradient(145deg, #121212, #000000);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .premium-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(0,0,0,1) 100%);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #d4af37;
        text-align: center;
        margin: 20px 0;
    }

    .stButton>button {
        width: 100% !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-weight: 800 !important;
        background: #d4af37 !important;
        color: black !important;
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Tab Design Professionale */
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-size: 0.8em;
        font-weight: 600;
        padding: 10px 15px;
    }

    .guide-step {
        background: #111;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #222;
        font-size: 0.85em;
        text-align: left;
    }
    
    .unfollow-alert {
        background: rgba(231, 76, 60, 0.1);
        border: 1px solid #e74c3c;
        padding: 20px;
        border-radius: 15px;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
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

# --- UI START ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; font-weight:800; font-size:2.8em; margin-bottom:5px;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.4; letter-spacing:3px; font-size:0.7em; margin-bottom:30px;'>ELITE SECURITY INTERFACE</p>", unsafe_allow_html=True)

# 1. SEZIONE CARICAMENTO (Sempre visibile)
st.markdown('<div class="hero-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Carica lo ZIP di Instagram", type="zip", label_visibility="collapsed")
if not uploaded_file:
    st.markdown("<p style='opacity:0.5; font-size:0.9em;'>Trascina il file ZIP o caricalo dalla galleria</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 2. SEZIONE ANALISI
if uploaded_file:
    with st.spinner("Analisi crittografica..."):
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

                    # DASHBOARD METRICHE
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Persi", len(non_ricambiano))

                    st.write("###")

                    # NAVIGAZIONE PRINCIPALE (Tabs al posto della Sidebar)
                    t1, t2, t3, t4 = st.tabs(["📉 LISTA", "⏱️ STORICO", "💎 PRO", "📖 GUIDA"])

                    with t1:
                        st.markdown("##### Profili che non ricambiano")
                        st.dataframe(pd.DataFrame(non_ricambiano, columns=["Account"]), use_container_width=True, height=350)

                    with t2:
                        st.markdown("#### Confronto Storico")
                        st.write("Carica uno Snapshot (.insta) per vedere chi ti ha rimosso.")
                        hist_file = st.file_uploader("Upload .insta", type="insta")
                        
                        if hist_file:
                            old_data = json.load(hist_file)
                            old_fols = set(old_data.get("followers", []))
                            persi = sorted(list(old_fols - fols))
                            if persi:
                                st.markdown(f'<div class="unfollow-alert">🚨 {len(persi)} nuovi unfollowers rilevati!<br><small>{", ".join(persi)}</small></div>', unsafe_allow_html=True)
                            else:
                                st.success("Nessun cambiamento rilevato.")
                        
                        st.write("---")
                        st.write("Salva la situazione attuale:")
                        snap_data = {"date": datetime.now().strftime("%Y-%m-%d"), "followers": list(fols)}
                        st.download_button("GENERA SNAPSHOT .INSTA", json.dumps(snap_data), "snapshot.insta")

                    with t3:
                        st.markdown(f"""
                            <div class="premium-card">
                                <h2 style='color:#d4af37;'>Insights Fan Segreti</h2>
                                <p>Individuati {len(fan)} profili che ti seguono senza ricambio.</p>
                                <a href="https://www.paypal.me/TUO_USER/1.29" style='text-decoration:none;'>
                                    <button style="background:#d4af37; color:black; padding:15px; border-radius:50px; font-weight:bold; border:none; cursor:pointer; width:100%;">SBLOCCA ORA 1,29€</button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)

                    with t4:
                        st.markdown("#### Come ottenere i dati")
                        steps = ["1. Impostazioni IG", "2. Centro Account", "3. Scarica le tue informazioni", "4. Seleziona 'Follower e seguiti'", "5. Formato JSON", "6. Intervallo 'Dall'inizio'"]
                        for s in steps:
                            st.markdown(f"<div class='guide-step'>{s}</div>", unsafe_allow_html=True)

        except Exception:
            st.error("Errore nel caricamento dello ZIP.")

else:
    # Se non c'è file, mostriamo la guida e il tasto PayPal subito
    st.info("Carica il file ZIP per visualizzare le statistiche e lo storico.")
    st.markdown("""
        <div style="text-align:center; margin-top:20px;">
            <a href="https://www.paypal.me/TUO_USER/1.29" style='text-decoration:none;'>
                <p style="color:#d4af37; font-weight:bold;">Sostieni il progetto con una donazione</p>
            </a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Fine main-container
st.markdown('<p style="text-align:center; opacity:0.1; font-size:0.6em; margin-top:100px;">GOLD ENGINE v5.2</p>', unsafe_allow_html=True)
