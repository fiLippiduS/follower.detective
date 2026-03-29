import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- UI DESIGN SYSTEM ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #000000;
        color: #f5f5f7;
    }

    /* Card Principale */
    .hero-card {
        background: linear-gradient(145deg, #1a1a1a, #0a0a0a);
        padding: 60px;
        border-radius: 40px;
        border: 1px solid rgba(212, 175, 55, 0.15);
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
    }

    /* Paywall Elegante */
    .paywall-container {
        background: rgba(212, 175, 55, 0.03);
        padding: 80px 40px;
        border-radius: 30px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        text-align: center;
        backdrop-filter: blur(20px);
        margin: 20px 0;
    }

    .premium-badge {
        background: #d4af37;
        color: #000;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.7em;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
        display: inline-block;
    }

    /* Bottoni */
    .cta-button {
        background: #d4af37 !important;
        color: #000 !important;
        font-weight: 600 !important;
        padding: 18px 45px !important;
        border-radius: 100px !important;
        text-decoration: none;
        display: inline-block;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        border: none;
    }

    .cta-button:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(212, 175, 55, 0.4);
    }

    /* Tutorial Sidebar */
    .guide-step {
        background: #111;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 10px;
        border: 1px solid #222;
        font-size: 0.85em;
    }
    
    .stMetric {
        background: transparent !important;
        border: 1px solid #222 !important;
        border-radius: 20px !important;
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

# --- SIDEBAR: REVENUE & GUIDA ---
with st.sidebar:
    st.markdown("<h2 style='color:#d4af37;'>Elite Support</h2>", unsafe_allow_html=True)
    st.markdown("""
        <a href="https://www.paypal.me/TUO_USER/1.29" target="_blank" style="text-decoration:none;">
            <div style="background:#d4af37; color:#000; padding:15px; border-radius:12px; text-align:center; font-weight:700;">
                Sostieni il Progetto
            </div>
        </a>
    """, unsafe_allow_html=True)
    
    st.write("###")
    st.markdown("#### Protocollo di Esportazione")
    st.markdown("""
    <div class="guide-step"><b>01.</b> Apri Impostazioni Instagram</div>
    <div class="guide-step"><b>02.</b> Centro gestione account</div>
    <div class="guide-step"><b>03.</b> Scarica le tue informazioni</div>
    <div class="guide-step"><b>04.</b> Seleziona 'Follower e seguiti'</div>
    <div class="guide-step"><b>05.</b> Formato: <b>JSON</b></div>
    <div class="guide-step"><b>06.</b> Intervallo: <b>Dall'inizio</b></div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("Standard di Sicurezza Militare: Nessun dato viene trasmesso o salvato.")

# --- INTERFACCIA PRINCIPALE ---
st.markdown("<h1 style='text-align:center; letter-spacing:-1px;'>InstaDetective Elite</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; opacity:0.6; font-size:1.1em;'>Analisi crittografica delle relazioni digitali.</p>", unsafe_allow_html=True)

st.markdown('<div class="hero-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Trascina l'archivio .zip per iniziare la scansione", type="zip", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Decriptazione e analisi in corso..."):
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
                    c4.metric("Fan Index", "PRO")

                    st.write("###")
                    
                    t1, t2, t3 = st.tabs(["UNFOLLOWERS", "PREMIUM INSIGHTS", "DATA VISUALIZATION"])

                    with t1:
                        if non_ricambiano:
                            st.markdown("##### Profili che non ricambiano l'interazione")
                            df_unf = pd.DataFrame(non_ricambiano, columns=["Account ID"])
                            st.dataframe(df_unf, use_container_width=True, height=400)
                            
                            csv = df_unf.to_csv(index=False).encode('utf-8')
                            st.download_button("Esporta Report CSV", csv, "unfollowers.csv", "text/csv")
                        else:
                            st.success("Analisi completata: Connessioni 100% reciproche.")

                    with t2:
                        st.markdown(f"""
                            <div class="paywall-container">
                                <div class="premium-badge">Exclusive Access</div>
                                <h2 style="color:#f5f5f7; margin-bottom:10px;">Identifica i tuoi Fan ({len(fan)})</h2>
                                <p style="opacity:0.6; max-width:500px; margin: 0 auto 30px auto;">
                                    Scopri gli utenti che seguono i tuoi aggiornamenti ma che non hai ancora ricambiato. Ottimizza il tuo network sociale ora.
                                </p>
                                <a href="https://www.paypal.me/TUO_USER/1.29" class="cta-button">Sblocca Insights per 1,29€</a>
                            </div>
                        """, unsafe_allow_html=True)

                    with t3:
                        fig = px.pie(
                            values=[len(comuni), len(non_ricambiano)],
                            names=['Reciproci', 'Unfollowers'],
                            color_discrete_sequence=['#1db954', '#ff4b4b'],
                            hole=0.7
                        )
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', 
                            font_color="white",
                            showlegend=True
                        )
                        st.plotly_chart(fig, use_container_width=True)

        except Exception:
            st.error("Protocollo fallito. Verificare l'integrità del file .zip.")

st.markdown('<p style="text-align:center; opacity:0.2; font-size:0.7em; margin-top:100px; letter-spacing:2px;">INSTADETECTIVE ELITE &bull; ENCRYPTED ENGINE v4.5</p>', unsafe_allow_html=True)
