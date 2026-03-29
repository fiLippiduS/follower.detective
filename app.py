import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- CSS AVANZATO: PAYWALL & TUTORIAL ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #050505;
        color: #FFFFFF;
    }

    .main-card {
        background: rgba(255, 255, 255, 0.02);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(212, 175, 55, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }

    /* Paywall Style */
    .locked-section {
        background: rgba(255, 255, 255, 0.05);
        padding: 50px;
        border-radius: 20px;
        border: 2px dashed rgba(212, 175, 55, 0.5);
        text-align: center;
        backdrop-filter: blur(10px);
    }

    .unlock-btn {
        background: #d4af37 !important;
        color: black !important;
        font-weight: bold;
        padding: 15px 30px;
        border-radius: 50px;
        text-decoration: none;
        display: inline-block;
        margin-top: 20px;
        transition: 0.3s;
    }

    .tutorial-box {
        background: rgba(212, 175, 55, 0.05);
        padding: 15px;
        border-radius: 15px;
        font-size: 0.85em;
        line-height: 1.4;
        border-left: 3px solid #d4af37;
    }
    
    .stMetric {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 15px !important;
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

# --- SIDEBAR & TUTORIAL ---
with st.sidebar:
    st.title("💎 Premium Area")
    st.markdown("""
        <a href="https://www.paypal.me/TUO_USER/1.29" target="_blank">
            <button style="width:100%; border-radius:50px; background:#d4af37; border:none; color:black; padding:12px; font-weight:bold; cursor:pointer; margin-bottom:10px;">
                ☕ Offrimi un caffè
            </button>
        </a>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("📖 Come ottenere i dati")
    st.markdown("""
    <div class="tutorial-box">
    1️⃣ Apri <b>Instagram</b> > Impostazioni.<br>
    2️⃣ <b>Centro gestione account</b> > Le tue informazioni.<br>
    3️⃣ <b>Scarica informazioni</b> > Scarica o trasferisci.<br>
    4️⃣ Seleziona <b>Solo alcuni tipi</b> > 'Follower e seguiti'.<br>
    5️⃣ <b>Importante:</b> Formato <b>JSON</b> e Intervallo <b>'Dall'inizio'</b>.<br>
    6️⃣ Attendi l'email di Instagram e carica lo ZIP qui.
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("Privacy: I dati non lasciano mai il tuo browser.")

# --- MAIN ---
st.title("Analisi Connessioni Elite")
st.markdown("Monitora chi non ricambia il tuo follow in totale sicurezza.")

st.markdown('<div class="main-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type="zip")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Analisi dei metadati..."):
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

                    st.write("###")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Unfollowers", len(non_ricambiano))
                    c4.metric("Fan", "🔒 Locked")

                    tab1, tab2, tab3 = st.tabs(["📉 Unfollowers", "⭐ Area Fan (Pro)", "📊 Statistiche"])

                    with tab1:
                        if non_ricambiano:
                            st.write("Questi profili non ricambiano il tuo follow:")
                            st.dataframe(pd.DataFrame(non_ricambiano, columns=["Username"]), use_container_width=True, height=350)
                        else:
                            st.success("Tutti ricambiano il tuo follow!")

                    with tab2:
                        # SEZIONE BLOCCATA (PAYWALL)
                        st.markdown(f"""
                            <div class="locked-section">
                                <h2 style="color:#d4af37;">🔓 Sblocca la Sezione Fan</h2>
                                <p>Scopri chi ti segue ma non è ancora ricambiato da te ({len(fan)} profili individuati).</p>
                                <p style="font-size:0.9em; opacity:0.7;">Ottieni l'accesso completo a questa funzione premium.</p>
                                <a href="https://www.paypal.me/TUO_USER/1.29" class="unlock-btn">Sblocca ora a 1,29€</a>
                            </div>
                        """, unsafe_allow_html=True)

                    with tab3:
                        fig = px.pie(
                            values=[len(comuni), len(non_ricambiano)],
                            names=['Reciproci', 'Unfollowers'],
                            color_discrete_sequence=['#2ecc71', '#e74c3c'],
                            hole=0.6
                        )
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(t=0, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)

        except Exception:
            st.error("Errore nel caricamento. Verifica che il file ZIP sia corretto.")

st.markdown('<p style="text-align:center; opacity:0.3; font-size:0.7em; margin-top:50px;">InstaDetective Elite &copy; 2026</p>', unsafe_allow_html=True)
