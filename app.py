import streamlit as st
import json
import zipfile
import pandas as pd

# 1. Configurazione della pagina
st.set_page_config(page_title="InstaChecker Pro", page_icon="🕵️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button { background-color: #E1306C; color: white; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🕵️ InstaChecker Pro")
st.info("Trascina qui il file .zip che hai scaricato da Instagram.")

# Sidebar estetica
with st.sidebar:
    st.header("Configurazione")
    st.text_input("Username Instagram")
    st.text_input("Password", type="password")
    st.caption("I dati sono protetti e non vengono salvati.")

uploaded_file = st.file_uploader("Carica lo ZIP di Instagram", type="zip")

def extract_names(data):
    """Estrae i nomi dai diversi formati JSON di Instagram"""
    names = set()
    if isinstance(data, list):
        for item in data:
            if 'string_list_data' in item and item['string_list_data']:
                val = item['string_list_data'][0].get('value')
                if val: names.add(val.lower().strip())
    elif isinstance(data, dict):
        # Prova percorso Following standard
        entries = data.get('relationships_following', [])
        for item in entries:
            val = item.get('title') or (item.get('string_list_data', [{}])[0].get('value') if item.get('string_list_data') else None)
            if val: names.add(val.lower().strip())
    return names

if uploaded_file:
    with st.spinner('Scansione profonda dello ZIP in corso...'):
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                all_followers = set()
                all_following = set()
                file_list = z.namelist()
                
                # Messaggi di log interni per debug
                found_fo = False
                found_fi = False

                for path in file_list:
                    # Cerchiamo i file ignorando le cartelle (prendiamo solo il nome finale)
                    filename = path.split('/')[-1].lower()
                    
                    if filename.endswith('.json'):
                        if 'follower' in filename:
                            with z.open(path) as f:
                                all_followers.update(extract_names(json.load(f)))
                                found_fo = True
                        elif 'following' in filename:
                            with z.open(path) as f:
                                all_following.update(extract_names(json.load(f)))
                                found_fi = True
                
                if not found_fi or not found_fo:
                    st.error("⚠️ Attenzione: Non ho trovato i file corretti nello ZIP.")
                    st.write("Assicurati di aver selezionato il formato **JSON** (non HTML) quando hai richiesto i dati a Instagram.")
                    st.write(f"File analizzati nello ZIP: {len(file_list)}")
                else:
                    unfollowers = sorted(list(all_following - all_followers))
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Seguiti", len(all_following))
                    col2.metric("Follower", len(all_followers))
                    col3.metric("Non ricambiano", len(unfollowers))
                    
                    if unfollowers:
                        st.subheader("📜 Chi non ti segue più")
                        df = pd.DataFrame(unfollowers, columns=["Username"])
                        df['Profilo'] = df['Username'].apply(lambda x: f"https://www.instagram.com/{x}")
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Scarica Report CSV", csv, "unfollowers.csv", "text/csv")
                    else:
                        st.balloons()
                        st.success("Tutti ricambiano il follow!")
                        
        except Exception as e:
            st.error(f"Errore: {e}")
