import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px

# Configurazione Pagina
st.set_page_config(page_title="InstaDetective Business", page_icon="💰", layout="wide")

# CSS Elite con accenti Oro per la monetizzazione
st.markdown("""
    <style>
    .stApp { background: #0e1117; color: white; }
    .main-box {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #d4af37;
        margin-bottom: 20px;
    }
    .money-box {
        background: linear-gradient(135deg, #d4af37 0%, #f9d976 100%);
        padding: 20px;
        border-radius: 15px;
        color: #1a1a1a;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    .stMetric { border: 1px solid #d4af37 !important; border-radius: 10px !important; }
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
    st.title("💰 Supporta il Progetto")
    st.markdown("""
    <div style="background: #262730; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37;">
    Ti piace questo tool? Aiutaci a mantenerlo attivo e senza pubblicità invasiva!
    </div>
    """, unsafe_allow_html=True)
    
    # Inserisci qui il tuo link PayPal o BuyMeACoffee
    st.markdown("[☕ Offrimi un caffè su PayPal](https://www.paypal.me/TUO_USER)")
    
    st.write("---")
    st.subheader("🛡️ Privacy Garantita")
    st.caption("Nessuna password richiesta. Analizziamo solo i dati ufficiali scaricati da te.")

# --- MAIN UI ---
st.title("💎 InstaDetective Elite Pro")
st.write("Versione 4.0 - Analisi Avanzata & Business")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Trascina qui lo ZIP dei tuoi dati Instagram", type="zip")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("Analisi dei dati in corso..."):
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
                    # LOGICA BUSINESS
                    non_ricambiano = sorted(list(fings - fols)) # Chi seguo ma non mi segue
                    fan = sorted(list(fols - fings))           # Chi mi segue ma non seguo (FAN)
                    comuni = fings.intersection(fols)          # Amicizie reciproche

                    # Metriche
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Seguiti", len(fings))
                    c2.metric("Followers", len(fols))
                    c3.metric("Non Ricambiano", len(non_ricambiano), delta_color="inverse")
                    c4.metric("Tuoi Fan", len(fan))

                    tab1, tab2, tab3 = st.tabs(["📉 Unfollowers", "⭐ Tuoi Fan", "📊 Analisi"])

                    with tab1:
                        st.subheader("Chi non ricambia il tuo follow")
                        if non_ricambiano:
                            st.table(pd.DataFrame(non_ricambiano, columns=["Username"]))
                            st.download_button("📥 Scarica Lista Nera", "\n".join(non_ricambiano), "unfollowers.txt")
                        else: st.success("Grande! Ti seguono tutti.")

                    with tab2:
                        st.subheader("Persone che ti seguono e che tu non segui")
                        if fan:
                            st.table(pd.DataFrame(fan, columns=["Username"]))
                            st.info("Questi sono i tuoi 'Fan'. Potresti voler ricambiare il follow!")
                        else: st.write("Non hai fan non ricambiati al momento.")

                    with tab3:
                        st.subheader("Rapporto Relazioni")
                        fig = px.pie(
                            values=[len(comuni), len(non_ricambiano), len(fan)],
                            names=['Amici Reciproci', 'Non Ricambiano', 'Tuoi Fan'],
                            color_discrete_sequence=['#00d1b2', '#e94560', '#f9d976'],
                            hole=0.5
                        )
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Errore tecnico: {e}")

# Footer Monetizzazione
st.markdown("""
    <div class="money-box">
        🚀 Vuoi funzioni extra? Supporta lo sviluppo con una piccola donazione!
    </div>
    """, unsafe_allow_html=True)
