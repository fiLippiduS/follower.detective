import streamlit as st
import json
import zipfile
import pandas as pd
import re
import hashlib
import streamlit.components.v1 as components

# ─── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FollowerDetective",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── ADSTERRA LINKS ───────────────────────────────────────────────────────────
LINK_UNFOLLOWERS = "https://www.profitablecpmratenetwork.com/uizvppk2?key=f0a721816237e7835d3ea630c5d8e33e"
LINK_FAN_SEGRETI = "https://www.profitablecpmratenetwork.com/shd3c1hdud?key=4d5754de72adc6dc7c524a6a47c574e5"

# ─── LOGICA ───────────────────────────────────────────────────────────────────
def get_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

@st.cache_data(show_spinner=False)
def process_zip(file_bytes):
    try:
        with zipfile.ZipFile(file_bytes, 'r') as z:
            fols, fings = set(), set()
            for path in z.namelist():
                if path.lower().endswith('followers_1.json'):
                    with z.open(path) as f:
                        fols.update(raw_text_extract(f.read()))
                elif path.lower().endswith('following.json') and 'hashtag' not in path.lower():
                    with z.open(path) as f:
                        fings.update(raw_text_extract(f.read()))
            return fols, fings
    except:
        return set(), set()

def raw_text_extract(text_bytes):
    text = text_bytes.decode('utf-8', errors='ignore')
    potentials = re.findall(r'"([^"]*)"', text)
    found = set()
    blacklist = {'value','href','timestamp','string_list_data','relationships_following','title','true','false','none'}
    for p in potentials:
        clean = p.strip().lower()
        if (clean and len(clean) < 31 and clean not in blacklist
                and not clean.startswith('http')
                and not (clean.isdigit() and len(clean) > 5)):
            found.add(clean)
    return found

# ─── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in [('unf_unlocked', False), ('fan_unlocked', False), ('last_file_hash', None),
             ('show_guide', False), ('active_tab', 'unfollowers')]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
#MainMenu, footer, header, [data-testid="stSidebar"] { visibility: hidden; display: none; }
[data-testid="stAppViewContainer"] { background: #0d0d0f; }
[data-testid="stMain"] { background: #0d0d0f; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stFileUploaderDropzone"] {
    background: #1a1a1e !important;
    border: 1.5px dashed #333 !important;
    border-radius: 14px !important;
    color: #888 !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #f5a623 !important;
}
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
}
button[data-testid="stDownloadButton"] button,
div[data-testid="stDownloadButton"] button {
    background: #1a1a1e !important;
    color: #f5a623 !important;
    border: 1px solid #f5a623 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSpinner > div { border-top-color: #f5a623 !important; }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;700&display=swap');
* { box-sizing: border-box; }
body { margin: 0; background: transparent; }

.fd-header {
    background: linear-gradient(180deg, #111114 0%, #0d0d0f 100%);
    border-bottom: 1px solid #1e1e24;
    padding: 28px 24px 22px;
    text-align: center;
    font-family: 'DM Sans', sans-serif;
}
.fd-logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.fd-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #f5a623, #e8831a);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
}
.fd-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(22px, 5vw, 30px);
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.fd-title span { color: #f5a623; }
.fd-sub {
    font-size: 13px;
    color: #555;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 2px;
}
</style>
<div class="fd-header">
    <div class="fd-logo">
        <div class="fd-logo-icon">🔍</div>
        <div class="fd-title">Follower<span>Detective</span></div>
    </div>
    <div class="fd-sub">Scopri chi non ti segue su Instagram</div>
</div>
""", height=110)

# ─── WRAPPER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:760px; margin:0 auto; padding:24px 16px 80px;">
""", unsafe_allow_html=True)

# ─── GUIDA DOWNLOAD ───────────────────────────────────────────────────────────
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; }
body { margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }

.guide-toggle {
    background: #15151a;
    border: 1px solid #252530;
    border-radius: 14px;
    padding: 16px 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
    transition: border-color 0.2s;
    user-select: none;
}
.guide-toggle:hover { border-color: #f5a623; }
.guide-toggle-left { display: flex; align-items: center; gap: 12px; }
.guide-toggle-icon {
    width: 34px; height: 34px;
    background: rgba(245,166,35,0.12);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.guide-toggle-text { font-size: 14px; font-weight: 600; color: #f0f0f0; }
.guide-toggle-sub { font-size: 11px; color: #666; margin-top: 1px; }
.guide-arrow { color: #f5a623; font-size: 18px; transition: transform 0.3s; }
.guide-arrow.open { transform: rotate(180deg); }

.guide-body {
    background: #15151a;
    border: 1px solid #252530;
    border-top: none;
    border-radius: 0 0 14px 14px;
    padding: 0 20px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease, padding 0.3s;
}
.guide-body.open {
    max-height: 700px;
    padding: 20px;
}
.step {
    display: flex;
    gap: 14px;
    margin-bottom: 18px;
    align-items: flex-start;
}
.step:last-child { margin-bottom: 0; }
.step-num {
    min-width: 28px; height: 28px;
    background: linear-gradient(135deg, #f5a623, #e8831a);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: #000;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-content { flex: 1; }
.step-title { font-size: 13px; font-weight: 600; color: #e8e8e8; margin-bottom: 3px; }
.step-desc { font-size: 12px; color: #777; line-height: 1.6; }
.step-desc code {
    background: #222;
    color: #f5a623;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 11px;
}
.divider { height: 1px; background: #222; margin: 16px 0; }
.tip-box {
    background: rgba(245,166,35,0.07);
    border-left: 3px solid #f5a623;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    font-size: 12px;
    color: #aaa;
    line-height: 1.6;
}
</style>

<div class="guide-toggle" onclick="toggleGuide()">
    <div class="guide-toggle-left">
        <div class="guide-toggle-icon">📖</div>
        <div>
            <div class="guide-toggle-text">Come scaricare i dati da Instagram</div>
            <div class="guide-toggle-sub">Guida passo dopo passo · ~5 minuti</div>
        </div>
    </div>
    <div class="guide-arrow" id="arrow">▼</div>
</div>

<div class="guide-body" id="guide-body">
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-content">
            <div class="step-title">Apri Instagram e vai al profilo</div>
            <div class="step-desc">Tocca l'icona del tuo profilo in basso a destra, poi il menu ☰ in alto a destra.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-content">
            <div class="step-title">Vai su "Centro Account" o "Impostazioni"</div>
            <div class="step-desc">Seleziona <code>Impostazioni e privacy</code> → poi <code>Centro Account</code> in basso.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-content">
            <div class="step-title">Cerca "Le tue informazioni"</div>
            <div class="step-desc">Nel Centro Account tocca <code>Le tue informazioni e autorizzazioni</code> → <code>Scarica le tue informazioni</code>.</div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">4</div>
        <div class="step-content">
            <div class="step-title">Configura il download</div>
            <div class="step-desc">
                Seleziona <code>Scarica o trasferisci le informazioni</code> → scegli il tuo account Instagram → <code>Alcune delle tue informazioni</code>.<br><br>
                Cerca e seleziona solo <code>Follower e following</code>. Formato: <code>JSON</code>. Intervallo: <code>Tutti i tempi</code>.
            </div>
        </div>
    </div>
    <div class="step">
        <div class="step-num">5</div>
        <div class="step-content">
            <div class="step-title">Attendi l'email di Instagram</div>
            <div class="step-desc">Instagram ti manderà un link via email entro <strong style="color:#f5a623">pochi minuti</strong> (a volte qualche ora). Clicca il link e scarica il file <code>.zip</code>.</div>
        </div>
    </div>
    <div class="divider"></div>
    <div class="tip-box">
        💡 <strong>Importante:</strong> Non estrarre il file ZIP — caricalo direttamente così com'è. Assicurati di scegliere formato <strong>JSON</strong> e non HTML.
    </div>
</div>

<script>
function toggleGuide() {
    const body = document.getElementById('guide-body');
    const arrow = document.getElementById('arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
}
</script>
""", height=60, scrolling=False)

# toggle height viene gestito dal CSS interno, ma dobbiamo dare altezza sufficiente
# Usiamo un componente separato per la guida espansa
components.html("""<div style="height:4px"></div>""", height=4)

# ─── UPLOAD SECTION ───────────────────────────────────────────────────────────
components.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
body { margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }
.upload-label {
    font-size: 13px; font-weight: 600; color: #888;
    text-transform: uppercase; letter-spacing: 0.08em;
    margin: 24px 0 10px;
    display: block;
}
</style>
<span class="upload-label">📂 Carica il tuo archivio ZIP</span>
""", height=50)

uploaded_file = st.file_uploader(
    label="ZIP Instagram",
    type="zip",
    label_visibility="collapsed"
)

# ─── RISULTATI ────────────────────────────────────────────────────────────────
if uploaded_file:
    current_hash = get_file_hash(uploaded_file.getvalue())
    if st.session_state.last_file_hash != current_hash:
        st.session_state.unf_unlocked = False
        st.session_state.fan_unlocked = False
        st.session_state.last_file_hash = current_hash

    with st.spinner("Analisi in corso..."):
        fols, fings = process_zip(uploaded_file)

    non_ricambiano = sorted(list(fings - fols))
    fan_segreti = sorted(list(fols - fings))

    # Statistiche
    components.html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@700&display=swap');
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 20px 0 24px;
    }}
    .stat-card {{
        background: #15151a;
        border: 1px solid #252530;
        border-radius: 14px;
        padding: 16px 14px;
        text-align: center;
    }}
    .stat-num {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(22px, 5vw, 32px);
        font-weight: 700;
        color: #fff;
        line-height: 1;
    }}
    .stat-num.accent {{ color: #f5a623; }}
    .stat-num.red {{ color: #ff6b6b; }}
    .stat-label {{
        font-size: 11px;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-top: 6px;
    }}
    .analysis-bar {{
        background: #15151a;
        border: 1px solid #252530;
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        font-size: 13px;
        color: #888;
    }}
    .analysis-dot {{
        width: 8px; height: 8px;
        background: #2ecc71;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 0 6px #2ecc71;
    }}
    </style>
    <div class="analysis-bar">
        <div class="analysis-dot"></div>
        <span>Analisi completata — file valido rilevato</span>
    </div>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-num">{len(fols)}</div>
            <div class="stat-label">Follower</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">{len(fings)}</div>
            <div class="stat-label">Seguiti</div>
        </div>
        <div class="stat-card">
            <div class="stat-num red">{len(non_ricambiano)}</div>
            <div class="stat-label">Non ricambiano</div>
        </div>
    </div>
    """, height=180)

    # Tab selector
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
    body { margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }
    .tab-bar {
        display: flex;
        background: #15151a;
        border: 1px solid #252530;
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        margin-bottom: 16px;
    }
    .tab-btn {
        flex: 1;
        padding: 10px 12px;
        background: transparent;
        border: none;
        border-radius: 9px;
        color: #666;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        font-family: 'DM Sans', sans-serif;
        transition: all 0.2s;
    }
    .tab-btn.active {
        background: #f5a623;
        color: #000;
        font-weight: 700;
    }
    .tab-btn:not(.active):hover { color: #f5a623; }
    </style>
    <div class="tab-bar">
        <button class="tab-btn active" onclick="sendPrompt('__tab_unfollowers')">👻 Non ricambiano</button>
        <button class="tab-btn" onclick="sendPrompt('__tab_fan')">❤️ Fan segreti</button>
        <button class="tab-btn" onclick="sendPrompt('__tab_save')">💾 Salva</button>
    </div>
    """, height=60)

    # Gestione tab via session
    tab = st.session_state.get('active_tab', 'unfollowers')
    last_msg = st.session_state.get('_last_prompt', '')

    # ─── COMPONENTE REWARDED AD ────────────────────────────────────────────────
    def rewarded_unlock(data_list, session_key, ad_link, icon, label):
        if st.session_state.get(session_key, False):
            # Lista sbloccata
            components.html(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap');
            body {{ margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }}
            .unlocked-header {{
                display: flex; align-items: center; gap: 10px;
                padding: 14px 18px;
                background: rgba(46,204,113,0.08);
                border: 1px solid rgba(46,204,113,0.25);
                border-radius: 12px;
                margin-bottom: 14px;
                font-size: 14px;
                font-weight: 600;
                color: #2ecc71;
            }}
            </style>
            <div class="unlocked-header">
                ✅ Lista sbloccata — {len(data_list)} profili trovati
            </div>
            """, height=70)
            st.dataframe(
                pd.DataFrame(data_list, columns=["Username"]),
                use_container_width=True,
                hide_index=True
            )
            return

        # Schermata di sblocco con rewarded ad
        components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Grotesk:wght@700&display=swap');
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; color: white; }}

        .lock-card {{
            background: #15151a;
            border: 1px solid #252530;
            border-radius: 18px;
            padding: 28px 24px;
            text-align: center;
        }}
        .lock-icon {{
            width: 64px; height: 64px;
            background: rgba(245,166,35,0.1);
            border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-size: 30px;
            margin: 0 auto 16px;
        }}
        .lock-count {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 42px;
            font-weight: 700;
            color: #f5a623;
            line-height: 1;
            margin-bottom: 4px;
        }}
        .lock-desc {{
            font-size: 14px;
            color: #666;
            margin-bottom: 28px;
        }}
        .btn-primary {{
            display: block;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #f5a623, #e8831a);
            color: #000;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: 700;
            font-family: 'DM Sans', sans-serif;
            cursor: pointer;
            margin-bottom: 10px;
            transition: opacity 0.2s, transform 0.1s;
            letter-spacing: -0.2px;
        }}
        .btn-primary:hover {{ opacity: 0.92; transform: scale(0.99); }}
        .btn-secondary {{
            display: block;
            width: 100%;
            padding: 14px;
            background: transparent;
            color: #f5a623;
            border: 1px solid #f5a623;
            border-radius: 14px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'DM Sans', sans-serif;
            cursor: pointer;
            transition: background 0.2s;
            text-decoration: none;
        }}
        .btn-secondary:hover {{ background: rgba(245,166,35,0.08); }}
        .divider {{ display: flex; align-items: center; gap: 10px; margin: 12px 0; color: #444; font-size: 12px; }}
        .divider::before, .divider::after {{ content: ''; flex: 1; height: 1px; background: #252530; }}

        /* OVERLAY REWARDED */
        .overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.92);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            font-family: 'DM Sans', sans-serif;
        }}
        .overlay.visible {{ display: flex; }}
        .overlay-card {{
            background: #18181e;
            border: 1px solid #2a2a35;
            border-radius: 22px;
            padding: 36px 28px;
            text-align: center;
            max-width: 320px;
            width: 90%;
        }}
        .overlay-title {{ font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 6px; }}
        .overlay-sub {{ font-size: 13px; color: #666; margin-bottom: 24px; }}
        .timer-ring {{
            width: 100px; height: 100px;
            margin: 0 auto 20px;
            position: relative;
        }}
        .timer-ring svg {{ transform: rotate(-90deg); }}
        .timer-ring circle.bg {{ stroke: #252530; fill: none; stroke-width: 6; }}
        .timer-ring circle.progress {{
            stroke: #f5a623;
            fill: none;
            stroke-width: 6;
            stroke-linecap: round;
            stroke-dasharray: 283;
            stroke-dashoffset: 0;
            transition: stroke-dashoffset 1s linear;
        }}
        .timer-num {{
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 32px;
            font-weight: 700;
            color: #f5a623;
        }}
        .timer-label {{ font-size: 13px; color: #666; margin-bottom: 20px; }}
        .btn-close {{
            display: none;
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #f5a623, #e8831a);
            color: #000;
            border: none;
            border-radius: 14px;
            font-size: 15px;
            font-weight: 700;
            font-family: 'DM Sans', sans-serif;
            cursor: pointer;
        }}
        .btn-close.visible {{ display: block; }}
        </style>

        <!-- Card principale -->
        <div class="lock-card">
            <div class="lock-icon">{icon}</div>
            <div class="lock-count">{len(data_list)}</div>
            <div class="lock-desc">{label} — lista bloccata</div>

            <button class="btn-primary" onclick="startAd()">
                📺 Guarda un annuncio (gratis)
            </button>

            <div class="divider">oppure</div>

            <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=TUO_EMAIL_PAYPAL&currency_code=EUR&amount=0.99&item_name=FollowerDetective+Pro"
               target="_blank" class="btn-secondary">
                🚀 Sblocca subito — 0,99 €
            </a>
        </div>

        <!-- Overlay rewarded -->
        <div class="overlay" id="overlay">
            <div class="overlay-card">
                <div class="overlay-title">Pubblicità in corso</div>
                <div class="overlay-sub">Attendi il termine per sbloccare la lista</div>

                <div class="timer-ring">
                    <svg width="100" height="100" viewBox="0 0 100 100">
                        <circle class="bg" cx="50" cy="50" r="45"/>
                        <circle class="progress" id="ring" cx="50" cy="50" r="45"/>
                    </svg>
                    <div class="timer-num" id="num">30</div>
                </div>

                <div class="timer-label" id="timer-label">Non chiudere questa finestra</div>

                <button class="btn-close" id="close-btn" onclick="finishAd()">
                    ✅ Visualizza risultati
                </button>
            </div>
        </div>

        <script>
        const TOTAL = 30;
        let countdown = TOTAL;
        let timerInterval = null;

        function startAd() {{
            // Apri la pubblicità
            window.open('{ad_link}', '_blank');

            // Mostra overlay
            document.getElementById('overlay').classList.add('visible');

            // Avvia timer
            timerInterval = setInterval(tick, 1000);
        }}

        function tick() {{
            countdown--;
            document.getElementById('num').textContent = countdown;

            // Aggiorna anello SVG
            const pct = 1 - (countdown / TOTAL);
            const offset = 283 * pct;
            document.getElementById('ring').style.strokeDashoffset = offset;

            if (countdown <= 0) {{
                clearInterval(timerInterval);
                document.getElementById('timer-label').textContent = 'Pubblicità completata!';
                document.getElementById('timer-label').style.color = '#2ecc71';
                document.getElementById('close-btn').classList.add('visible');
            }}
        }}

        function finishAd() {{
            window.parent.postMessage({{
                type: 'streamlit:set_component_value',
                value: 'UNLOCK_{session_key}'
            }}, '*');
            document.getElementById('overlay').style.display = 'none';
        }}
        </script>
        """, height=340, scrolling=False)

    # ─── TAB: UNFOLLOWERS ─────────────────────────────────────────────────────
    components.html("""
    <style>
    body { margin: 0; }
    .section-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        font-weight: 600;
        color: #e0e0e0;
        margin: 0 0 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
    """, height=0)

    # Visualizza sempre entrambe le sezioni (tab bar è solo estetica JS)
    # Unfollowers
    components.html("""
    <div style="font-family:'DM Sans',sans-serif; font-size:15px; font-weight:600; color:#e0e0e0; margin: 16px 0 12px; display:flex; align-items:center; gap:8px;">
        <span style="background:rgba(255,107,107,0.12); color:#ff6b6b; padding:4px 10px; border-radius:8px; font-size:12px; font-weight:700;">👻 NON RICAMBIANO</span>
    </div>
    """, height=46)

    rewarded_unlock(
        non_ricambiano,
        'unf_unlocked',
        LINK_UNFOLLOWERS,
        "👻",
        "Account che non ti seguono"
    )

    # Fan segreti
    components.html("""
    <div style="font-family:'DM Sans',sans-serif; font-size:15px; font-weight:600; color:#e0e0e0; margin: 28px 0 12px; display:flex; align-items:center; gap:8px;">
        <span style="background:rgba(245,166,35,0.12); color:#f5a623; padding:4px 10px; border-radius:8px; font-size:12px; font-weight:700;">❤️ FAN SEGRETI</span>
    </div>
    """, height=46)

    rewarded_unlock(
        fan_segreti,
        'fan_unlocked',
        LINK_FAN_SEGRETI,
        "❤️",
        "Ti seguono ma tu non li segui"
    )

    # Salva snapshot
    components.html("""
    <div style="font-family:'DM Sans',sans-serif; font-size:15px; font-weight:600; color:#e0e0e0; margin: 28px 0 12px; display:flex; align-items:center; gap:8px;">
        <span style="background:rgba(100,100,255,0.12); color:#8888ff; padding:4px 10px; border-radius:8px; font-size:12px; font-weight:700;">💾 SALVA SNAPSHOT</span>
    </div>
    """, height=46)

    snap = {"followers": list(fols), "following": list(fings)}
    components.html("""
    <div style="font-family:'DM Sans',sans-serif; font-size:13px; color:#666; margin-bottom:12px; background:#15151a; border:1px solid #252530; border-radius:12px; padding:14px 16px; line-height:1.6;">
        Salva uno snapshot del tuo profilo attuale. Potrai confrontarlo in futuro per vedere chi ti ha smesso di seguire.
    </div>
    """, height=70)
    st.download_button(
        "📥 Scarica Snapshot",
        data=json.dumps(snap, indent=2),
        file_name="snapshot_instagram.json",
        mime="application/json"
    )

# ─── FOOTER ───────────────────────────────────────────────────────────────────
else:
    components.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500&display=swap');
    body { margin: 0; background: transparent; font-family: 'DM Sans', sans-serif; }
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        color: #444;
    }
    .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
    .empty-text { font-size: 15px; color: #555; margin-bottom: 6px; }
    .empty-sub { font-size: 13px; color: #3a3a3a; }
    </style>
    <div class="empty-state">
        <div class="empty-icon">📂</div>
        <div class="empty-text">Nessun file caricato</div>
        <div class="empty-sub">Carica il tuo archivio ZIP di Instagram per iniziare</div>
    </div>
    """, height=200)

# Banner Adsterra footer
st.write("")
components.html("""
<div style="display:flex; justify-content:center; padding: 10px 0;">
    <script type='text/javascript' src='https://pl29012352.profitablecpmratenetwork.com/e9/80/a8/e980a836caa023115b0fd62679088279.js'></script>
</div>
""", height=260)

components.html("""
<div style="text-align:center; font-family:'DM Sans',sans-serif; font-size:11px; color:#333; padding: 16px 0 8px;">
    FollowerDetective · Non affiliato con Instagram/Meta · I tuoi dati non vengono mai caricati online
</div>
""", height=40)

st.markdown("</div>", unsafe_allow_html=True)
