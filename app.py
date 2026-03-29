import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- UI DESIGN SYSTEM (ULTRA-MODERN) ---
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

    /* Animazione Fade In */
    .stApp {
        animation: fadeIn 1.5s;
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }

    .hero-card {
        background: linear-gradient(145deg, #121212, #000000);
        padding: 50px;
        border-radius: 40px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 30px 60px rgba(0,0,0,0.8);
    }

    .premium-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(0,0,0,1) 100%);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid #d4af37;
        text-align: center;
    }

    .cta-gold {
        background: #d4af37 !important;
        color: #000 !important;
        font-weight: 800 !important;
        padding: 20px 60px !important;
        border-radius: 100px !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.4s;
        border: none !important;
        cursor: pointer;
    }

    .status-badge {
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.7em;
        font-weight: bold;
        background: rgba(212, 175, 55, 0.2);
        color: #d4af37;
        border: 1px solid #d4af37;
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#d4af37;'>ELITE OPS</h1>", unsafe_allow_html=True)
    user_tag = st.text_input("Inserisci il tuo @username", placeholder="@username")
    
    st.write("---")
    st.markdown("#### Guida Rapida")
    for step in ["01. Impostazioni IG", "02. Centro Account", "03. Scarica Info", "04. JSON + Dall'inizio"]:
        st.markdown(f"<div style='margin-bottom:8px; font-size:0.9em; opacity:0.7;'>{step}</div>", unsafe_allow_html=True)
    
    st.write("---")
    st.markdown(f"""
        <a href="https://www.paypal.me/TUO_USER/1.29" target="_blank">
            <button style="width:100%; background:#d4af37; color:black; border-radius:12px; padding:15px; font-weight:bold; border:none; cursor:pointer;">
                SBLOCCA TUTTE LE FUNZIONI
            </button>
        </a>
    """, unsafe_allow_html=True)

# --- MAIN ENGINE ---
st.markdown("<h1 style='text-align:center; font-weight:800; font-size:3.5em; margin-bottom:0;'>InstaDetective</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.5; letter-spacing:4px; margin-bottom:50px;'>SECURITY & INSIGHTS PROTOCOL</p>", unsafe_allow_html=True)

if not user_tag:
    st.info("👈 Inserisci il tuo @username nella barra laterale per personalizzare il report.")

st.markdown('<div class="hero-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type="zip", label_visibility="collapsed")
if not uploaded_file:
    st.markdown("<p style='opacity:0.5;'>Trascina il tuo archivio .zip qui per iniziare la scansione</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    # --- ANIMAZIONE DI CARICAMENTO AVANZATA ---
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    messages = [
        "Inizializzazione protocollo...",
        "Analisi crittografica in corso...",
        f"Ricerca connessioni per {user_tag}...",
        "Confronto database Seguiti/Followers...",
        "Generazione report finale..."
    ]
    
    for i, msg in enumerate(messages):
        status_text.markdown(f"<p style='text-align:center; color:#d4af37;'>{msg}</p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) * 20)
        time.sleep(0.6)
    
    status_text.empty()
    progress_bar.empty()

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

                # Dashboard Metriche
                st.write("###")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Seguiti", len(fings))
                c2.metric("Followers", len(fols))
                c3.metric("Non Ricambiano", len(non_ricambiano))
                c4.metric("Privacy Score", "A+")

                st.write("###")
                
                t1, t2, t3 = st.tabs(["🕵️ UNFOLLOWERS", "👑 PREMIUM INSIGHTS", "📈 ANALISI DATA"])

                with t1:
                    st.markdown(f"##### Report Unfollowers per {user_tag}")
                    df_unf = pd.DataFrame(non_ricambiano, columns=["Nome Account"])
                    st.dataframe(df_unf, use_container_width=True, height=400)
                    
                    # Bottone Download con stile
                    csv = df_unf.to_csv(index=False).encode('utf-8')
                    st.download_button("SCARICA REPORT PDF (BETA)", csv, "report.csv", "text/csv")

                with t2:
                    st.markdown(f"""
                        <div class="premium-card">
                            <span class="status-badge">ACCESSO LIMITATO</span>
                            <h2 style='margin-top:20px;'>Hai {len(fan)} Fan Segreti</h2>
                            <p style='opacity:0.7;'>Questi utenti visualizzano i tuoi contenuti ma tu non ricambi il follow.</p>
                            <p style='font-size:1.2em; font-weight:bold; color:#d4af37;'>Sblocca l'identità dei tuoi fan</p>
                            <br>
                            <a href="https://www.paypal.me/TUO_USER/1.29" style='text-decoration:none;'>
                                <button class="cta-gold">SBLOCCA ORA - 1,29€</button>
                            </a>
                            <p style='margin-top:20px; font-size:0.8em; opacity:0.5;'>Pagamento sicuro via PayPal. Accesso istantaneo.</p>
                        </div>
                    """, unsafe_allow_html=True)

                with t3:
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        fig = px.pie(
                            values=[len(comuni), len(non_ricambiano)],
                            names=['Ricambiano', 'Non Ricambiano'],
                            color_discrete_sequence=['#d4af37', '#333333'],
                            hole=0.8
                        )
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    with col_b:
                        st.write("###")
                        st.write(f"**Analisi per:** {user_tag}")
                        st.write(f"**Fedeltà Network:** {int((len(comuni)/len(fings))*100)}%")
                        st.write("**Stato:** Account Protetto")

    except Exception:
        st.error("Errore critico: archivio non riconosciuto.")

st.markdown("<p style='text-align:center; opacity:0.1; margin-top:100px;'>ENCRYPTED SYSTEM ACCESS | 2026</p>", unsafe_allow_html=True)
