import streamlit as st
import json
import zipfile
import pandas as pd
import re
import plotly.express as px

# Configurazione Pagina
st.set_page_config(page_title="InstaDetective Pro", page_icon="💎", layout="wide")

# CSS Avanzato per un look Cyberpunk/Elite
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1a1a2e 0%, #16213e 100%);
        color: #e94560;
    }
    .main-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(233, 69, 96, 0.3);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    .stMetric {
        background: rgba(233, 69, 96, 0.1);
        border-radius: 10px;
        padding: 15px !important;
        border: 1px solid rgba(233, 69, 96, 0.2);
    }
    h1, h2, h3 { color: #e94560 !important; font-family: 'Segoe UI', sans-serif; }
    .stButton>button {
        background-color: #e94560 !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
    }
    /* Tabella */
    div[data-testid="stTable"] {
        background-color: rgba(255,255,255,0.05);
        border-radius: 10px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def raw_text_extract(file_content):
    """Estrattore infallibile basato su testo grezzo (Regex)"""
    text = file_content.decode('utf-8', errors='ignore')
    potentials = re.findall(r'"([^"]*)"', text)
    found = set()
    blacklist = {
        'value', 'href', 'timestamp', 'string_list_data', 
        'relationships_following', 'title', 'true', 'false', 'none'
    }
    for p in potentials:
        clean = p.strip().lower()
        if (clean and len(clean) < 31 and clean not in blacklist and 
            not clean.startswith('http') and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

# --- SIDEBAR: ISTRUZIONI ---
with st.sidebar:
    st.title("🛡️ Guida Rapida")
    st.info("""
    **Come ottenere i dati:**
    1. Su Instagram: *Centro gestione account*
    2. *Le tue informazioni* -> *Scarica informazioni*
    3. Seleziona **SOLO** 'Follower e seguiti'
    4. Formato: **JSON**
    5. Intervallo: **Dall'inizio**
    """)
    st.write("---")
    st.write("🔒 **Privacy:** I tuoi file vengono elaborati solo in memoria e non salvati.")

# --- MAIN UI ---
st.title("💎 InstaDetective Elite Edition")
st.subheader("Analisi crittografica delle relazioni social")

st.markdown('<div class="main-box">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Trascina qui lo ZIP di Instagram", type="zip")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    with st.spinner("🕵️‍♂️ Analisi profonda in corso..."):
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                fols, fings = set(), set()
                
                for path in z.namelist():
                    p_lower = path.lower()
                    if p_lower.endswith('followers_1.json'):
                        with z.open(path) as f:
                            fols.update(raw_text_extract(f.read()))
                    elif p_lower.endswith('following.json') and 'hashtag' not in p_lower:
                        with z.open(path) as f:
                            fings.update(raw_text_extract(f.read()))

                if fings and fols:
                    # Calcoli
                    non_ricambiano = sorted(list(fings - fols))
                    comuni = fings.intersection(fols)
                    
                    # Layout a colonne per metriche
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Seguiti Totali", len(fings))
                    m2.metric("Followers Totali", len(fols))
                    m3.metric("Non Ricambiano", len(non_ricambiano), delta=f"-{len(non_ricambiano)}", delta_color="inverse")

                    st.write("---")

                    # Grafico e Tabella
                    col_left, col_right = st.columns([1, 1])

                    with col_left:
                        st.subheader("📊 Statistiche Follow")
                        data_chart = pd.DataFrame({
                            "Categoria": ["Ti Seguono", "Non Ricambiano"],
                            "Valore": [len(comuni), len(non_ricambiano)]
                        })
                        fig = px.pie(data_chart, values='Valore', names='Categoria', 
                                    color_discrete_sequence=['#00d1b2', '#e94560'],
                                    hole=0.4)
                        fig.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig, use_container_width=True)

                    with col_right:
                        st.subheader("📋 Lista Nera (Unfollowers)")
                        if non_ricambiano:
                            df_unf = pd.DataFrame(non_ricambiano, columns=["Username Instagram"])
                            st.dataframe(df_unf, height=300, use_container_width=True)
                            
                            # Download Button
                            txt_data = "\n".join(non_ricambiano)
                            st.download_button(
                                label="📥 Scarica Lista Unfollowers",
                                data=txt_data,
                                file_name="unfollowers_report.txt",
                                mime="text/plain"
                            )
                        else:
                            st.balloons()
                            st.success("Complimenti! Tutti ricambiano il tuo follow.")

                else:
                    st.error("⚠️ Errore: File validi non trovati.")
                    st.write(f"Debug: {len(fols)} followers / {len(fings)} seguiti.")

        except Exception as e:
            st.error(f"Errore tecnico: {e}")

st.markdown('---')
st.caption("InstaDetective Elite v3.0 | Progettato per la massima precisione.")
