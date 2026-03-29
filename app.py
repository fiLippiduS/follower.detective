import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="InstaDetective Elite", page_icon="💎", layout="wide")

# --- CSS PROFESSIONALE & BLOCCO MENU ---
st.markdown("""
    <style>
    /* Nasconde il menu Streamlit e il footer per privacy */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Font e Sfondo */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #050505;
        color: #FFFFFF;
    }

    .main-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        backdrop-filter: blur(20px);
        text-align: center;
    }

    .stMetric {
        background: rgba(212, 175, 55, 0.05) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 20px !important;
        padding: 20px !important;
    }

    /* Pulsanti Eleganti */
    .stButton>button {
        background: linear-gradient(135deg, #d4af37 0%, #aa8928 100%) !important;
        color: black !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 25px !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.3);
    }

    /* Tabs Custom */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px 10px 0 0;
        color: white;
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

# --- SIDEBAR MONETIZZAZIONE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1053/1053210.png", width=100)
    st.title("Premium Support")
    st.write("Sostieni lo sviluppo di tool sicuri e senza tracciamento.")
    st.markdown("""
        <a href="https://www.paypal.me/TUO_USER" target="_blank">
            <button style="width:100%; border-radius:50px; background:#d4af37; border:none; color:black; padding:10px; font-weight:bold; cursor:pointer;">
                ☕ Offrimi un caffè
            </button>
        </a>
    """, unsafe_allow_html=True)
    st.write("---")
    st.caption("Versione Gold v4.5 | 2026")

# --- MAIN PAGE ---
st.title("💎 Analisi Account Elite")
st.markdown("##### Il metodo più sicuro per monitorare le tue connessioni social senza condividere password.")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="zip", help="Trascina qui il file JSON scaricato da Instagram")
    st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Elaborazione dei metadati in corso..."):
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

                    # Statistiche High-Level
                    st.write("###")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non Ricambiano", len(non_ricambiano))
                    c4.metric("Fan", len(fan))

                    st.write("###")
                    
                    tab1, tab2, tab3 = st.tabs(["📉 Analisi Unfollowers", "⭐ Elenco Fan", "📊 Report Grafico"])

                    with tab1:
                        if non_ricambiano:
                            st.write("I seguenti utenti non ricambiano il tuo interesse:")
                            df_unf = pd.DataFrame(non_ricambiano, columns=["Nome Utente"])
                            st.dataframe(df_unf, use_container_width=True, height=400)
                            
                            csv = df_unf.to_csv(index=False).encode('utf-8')
                            st.download_button("Esporta Elenco (.csv)", csv, "unfollowers.csv", "text/csv")
                        else:
                            st.balloons()
                            st.success("Tutte le persone che segui ricambiano il follow.")

                    with tab2:
                        if fan:
                            st.write("Questi utenti ti seguono, ma tu non li hai ancora ricambiati:")
                            st.dataframe(pd.DataFrame(fan, columns=["Nome Utente"]), use_container_width=True, height=400)
                        else:
                            st.write("Non hai fan da mostrare.")

                    with tab3:
                        fig = px.pie(
                            values=[len(comuni), len(non_ricambiano), len(fan)],
                            names=['Reciproco', 'Unfollowers', 'Fan'],
                            color_discrete_sequence=['#2ecc71', '#e74c3c', '#f1c40f'],
                            hole=0.6
                        )
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font_color="white",
                            margin=dict(t=0, b=0, l=0, r=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)

        except Exception:
            st.error("Si è verificato un errore durante l'analisi. Assicurati che il file sia un archivio Instagram valido.")

st.markdown("""
    <div style="text-align:center; padding: 50px; opacity: 0.5; font-size: 0.8em;">
        I dati vengono elaborati esclusivamente nel tuo browser. Nessun profilo o file viene salvato sui nostri sistemi.<br>
        InstaDetective Elite &copy; 2026
    </div>
    """, unsafe_allow_html=True)
