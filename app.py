import streamlit as st
import os
import tempfile
import time
from pathlib import Path
from faster_whisper import WhisperModel
import ffmpeg
import base64

# =================== CONFIGURAÇÕES ===================
st.set_page_config(
    page_title="FeatherTranskript Web",
    page_icon="🪶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =================== FUNÇÃO BASE64 PARA IMAGENS ===================
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Carregar logos em base64
logo_path = Path(__file__).parent / "assets" / "logo.png"
getmep_path = Path(__file__).parent / "assets" / "getmep_logo.png"
pix_qr_path = Path(__file__).parent / "assets" / "pix_qrcode.png"

feather_b64 = img_to_base64(logo_path) if logo_path.exists() else ""
getmep_b64 = img_to_base64(getmep_path) if getmep_path.exists() else ""
pix_qr_b64 = img_to_base64(pix_qr_path) if pix_qr_path.exists() else ""

# =================== CSS CUSTOMIZADO ===================
st.markdown(f"""
<style>
    /* ===== CORES DO GETMEP ===== */
    :root {{
        --getmep-green: #4CAF50;
        --getmep-blue: #2196F3;
        --getmep-dark-blue: #1565C0;
        --getmep-gray: #607D8B;
        --getmep-light: #E8F5E9;
        --feather-teal: #00897B;
        --feather-coral: #FF7043;
        --feather-dark: #263238;
    }}

    /* ===== FUNDO CLARO ===== */
    .main {{
        background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
    }}
    .stApp {{
        background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
    }}

    /* ===== TIPOGRAFIA ===== */
    h1 {{
        color: var(--feather-dark) !important;
        text-align: center;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        margin-bottom: 5px !important;
    }}
    h2, h3 {{
        color: var(--feather-dark) !important;
        font-weight: 600 !important;
    }}
    p, label, .stMarkdown {{
        color: #455A64 !important;
    }}

    /* ===== LOGO FEATHER ===== */
    .feather-logo-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
        padding-top: 10px;
    }}
    .feather-logo {{
        width: 70px;
        height: auto;
        filter: drop-shadow(0 3px 8px rgba(0, 137, 123, 0.25));
        transition: transform 0.3s ease;
    }}
    .feather-logo:hover {{
        transform: scale(1.08);
    }}

    /* ===== BOTÕES ===== */
    .stButton>button {{
        background: linear-gradient(135deg, var(--getmep-green), #66BB6A);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 14px 36px;
        font-weight: 600;
        font-size: 1.05em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        background: linear-gradient(135deg, #43A047, #66BB6A);
    }}
    .stButton>button:disabled {{
        background: #BDBDBD;
        box-shadow: none;
    }}

    /* ===== UPLOAD ===== */
    .stFileUploader {{
        background: white;
        border: 2px dashed var(--getmep-blue);
        border-radius: 16px;
        padding: 25px;
        transition: all 0.3s;
    }}
    .stFileUploader:hover {{
        border-color: var(--getmep-green);
        background: var(--getmep-light);
    }}

    /* ===== PROGRESSO ===== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--getmep-green), var(--getmep-blue));
        border-radius: 10px;
    }}

    /* ===== CAIXAS ===== */
    .success-box {{
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(76, 175, 80, 0.05));
        border: 1px solid var(--getmep-green);
        border-radius: 12px;
        padding: 18px;
        color: #2E7D32;
        font-weight: 500;
    }}
    .info-box {{
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(33, 150, 243, 0.05));
        border: 1px solid var(--getmep-blue);
        border-radius: 12px;
        padding: 18px;
        color: #1565C0;
        font-weight: 500;
    }}

    /* ===== RADIO ===== */
    .stRadio > div {{
        background: white;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%);
        border-right: 1px solid #E0E0E0;
    }}
    [data-testid="stSidebar"] h3 {{
        color: var(--feather-dark) !important;
    }}
    [data-testid="stSidebar"] p {{
        color: #546E7A !important;
    }}

    /* ===== TEXTO RESULTADO ===== */
    .stTextArea textarea {{
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        font-family: 'Segoe UI', sans-serif;
        font-size: 0.95em;
        line-height: 1.7;
        color: #37474F;
    }}

    /* ===== GETMEP RODAPÉ ===== */
    .getmep-footer {{
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 16px;
        padding: 25px 20px;
        margin-top: 40px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}
    .getmep-footer .logos-row {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin-bottom: 18px;
        flex-wrap: wrap;
    }}
    .getmep-footer .logos-row img {{
        max-height: 55px;
        width: auto;
        transition: transform 0.3s;
    }}
    .getmep-footer .logos-row img:hover {{
        transform: scale(1.05);
    }}
    .getmep-footer h4 {{
        color: var(--getmep-green) !important;
        font-size: 1.1em;
        margin-bottom: 8px;
        font-weight: 600;
    }}
    .getmep-footer p {{
        color: #546E7A !important;
        font-size: 0.92em;
        line-height: 1.7;
        margin: 5px 0;
    }}
    .getmep-footer a {{
        color: var(--getmep-blue);
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }}
    .getmep-footer a:hover {{
        color: var(--getmep-dark-blue);
        text-decoration: underline;
    }}
    .getmep-footer .divider {{
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--getmep-green), var(--getmep-blue));
        border-radius: 2px;
        margin: 12px auto;
    }}
    .getmep-footer .version {{
        font-size: 0.8em;
        color: #90A4AE !important;
        margin-top: 12px;
    }}

    /* ===== FOOTER GERAL ===== */
    .footer {{
        text-align: center;
        color: #90A4AE;
        margin-top: 25px;
        font-size: 0.85em;
    }}
    .footer a {{
        color: var(--getmep-gray);
    }}

    /* ===== CARD FORMATOS ===== */
    .format-card {{
        background: white;
        border-radius: 12px;
        padding: 15px;
        min-width: 100px;
        text-align: center;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s;
        color: var(--feather-dark);
        font-weight: 500;
    }}
    .format-card:hover {{
        border-color: var(--getmep-green);
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.15);
    }}

    /* ===== INFO ARQUIVO ===== */
    .file-info {{
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        color: #455A64;
    }}

    /* ===== SEPARADOR ===== */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E0E0E0, transparent);
        margin: 25px 0;
    }}

    /* ===== CAFÉ - COMPRE-NOS UM CAFÉ ===== */
    .coffee-section {{
        background: linear-gradient(135deg, rgba(123, 31, 162, 0.1), rgba(142, 68, 173, 0.1));
        border: 2px solid #7B1FA2;
        border-radius: 16px;
        padding: 28px 24px;
        text-align: center;
        margin: 30px 0;
    }}
    .coffee-section h3 {{
        color: #6A1B9A;
        font-size: 1.35em;
        margin-top: 0;
        margin-bottom: 15px;
        font-weight: 700;
    }}
    .coffee-section p {{
        color: #455A64;
        font-size: 0.95em;
        margin: 8px 0;
    }}
    .coffee-buttons {{
        display: flex;
        justify-content: center;
        gap: 12px;
        flex-wrap: wrap;
        margin: 18px 0;
    }}
    .coffee-btn {{
        background: linear-gradient(135deg, #7B1FA2, #9C27B0);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 11px 22px;
        font-weight: 600;
        font-size: 0.96em;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(123, 31, 162, 0.3);
    }}
    .coffee-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(123, 31, 162, 0.4);
        background: linear-gradient(135deg, #6A1B9A, #7B1FA2);
    }}
    .coffee-qrcode {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid rgba(123, 31, 162, 0.3);
    }}
    .coffee-qrcode img {{
        max-width: 200px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 12px 0;
    }}
    .pix-key {{
        background: white;
        border: 2px solid #7B1FA2;
        border-radius: 8px;
        padding: 12px;
        font-family: monospace;
        font-size: 1.1em;
        color: #6A1B9A;
        font-weight: 600;
        word-break: break-all;
        margin: 12px 0;
    }}
    .coffee-tip {{
        font-size: 0.85em;
        color: #7B1FA2;
        font-style: italic;
        margin-top: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# =================== ESTADO DA SESSÃO ===================
if 'model' not in st.session_state:
    st.session_state.model = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# =================== FUNÇÕES AUXILIARES ===================
@st.cache_resource
def load_model(model_size="base"):
    """Carrega o modelo Whisper otimizado"""
    with st.spinner("🔋 Carregando modelo de IA... (primeira vez pode demorar)"):
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return model

def convert_to_wav(input_path):
    """Converte qualquer formato de áudio para WAV"""
    output_path = input_path.rsplit(".", 1)[0] + "_converted.wav"
    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except Exception as e:
        st.error(f"Erro na conversão: {e}")
        return None

def get_audio_duration(audio_path):
    """Obtém duração do áudio em segundos"""
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        return duration
    except:
        return None

def format_time(seconds):
    """Formata segundos para HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def transcribe_audio(audio_path, model, mode="texto", language="pt", progress_bar=None, status_text=None):
    """
    Transcreve o áudio
    mode: 'texto' = texto corrido, 'tempo' = com timestamps
    """
    segments, info = model.transcribe(
        audio_path,
        language=language,
        task="transcribe",
        vad_filter=True,
        condition_on_previous_text=True,
        word_timestamps=(mode == "tempo")
    )

    full_text = []
    total_segments = list(segments)
    total_count = len(total_segments)

    for i, segment in enumerate(total_segments):
        if mode == "tempo":
            start = format_time(segment.start)
            end = format_time(segment.end)
            text = f"[{start} --> {end}] {segment.text.strip()}"
        else:
            text = segment.text.strip()

        full_text.append(text)

        if progress_bar and total_count > 0:
            progress = (i + 1) / total_count
            progress_bar.progress(min(progress, 0.99))

        if status_text:
            status_text.text(f"🎙️ Processando... segmento {i+1}/{total_count}")

    return "\n".join(full_text), info

def generate_srt(transcription_text):
    """Gera formato SRT a partir da transcrição com timestamps"""
    lines = transcription_text.strip().split("\n")
    srt_entries = []
    counter = 1

    for line in lines:
        if " --> " in line:
            parts = line.split("]", 1)
            time_part = parts[0].replace("[", "").strip()
            text = parts[1].strip() if len(parts) > 1 else ""

            start_end = time_part.split(" --> ")
            if len(start_end) == 2:
                start = start_end[0].strip()
                end = start_end[1].strip()

                def to_srt_time(t):
                    parts = t.split(":")
                    if len(parts) == 2:
                        return f"00:{parts[0]}:{parts[1].replace('.', ',')},000"
                    elif len(parts) == 3:
                        return f"{parts[0]}:{parts[1]}:{parts[2].replace('.', ',')},000"
                    return t

                srt_start = to_srt_time(start)
                srt_end = to_srt_time(end)

                srt_entries.append(f"{counter}\n{srt_start} --> {srt_end}\n{text}\n")
                counter += 1

    return "\n".join(srt_entries)

# =================== INTERFACE ===================
# Logo Feather (pequena, centralizada)
if feather_b64:
    st.markdown(f"""
    <div class="feather-logo-container">
        <img src="data:image/png;base64,{feather_b64}" class="feather-logo" alt="FeatherTranskript">
    </div>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1>FeatherTranskript Web</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#607D8B; font-size:1.1em; margin-top:-5px;'>Transcrição de áudio com IA — Whisper Optimizado</p>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar com configurações
with st.sidebar:
    st.markdown("### ⚙️ Configurações")

    model_size = st.selectbox(
        "Modelo de IA",
        ["tiny", "base", "small", "medium", "large-v3"],
        index=1,
        help="Tiny = mais rápido, menos preciso | Large = mais lento, mais preciso"
    )

    language = st.selectbox(
        "Idioma Principal",
        ["pt", "en", "auto"],
        index=0,
        format_func=lambda x: {"pt": "🇧🇷 Português (PT-BR)", "en": "🇺🇸 Inglês", "auto": "🔍 Auto-detectar"}[x],
        help="PT-BR com reconhecimento automático de termos em inglês"
    )

    st.markdown("---")
    st.markdown("### 📋 Sobre")
    st.info("""
    **FeatherTranskript Web** v1.0

    Baseado no modelo **Whisper** da OpenAI,
    otimizado com **Faster-Whisper**.

    Suporta: MP3, OGG, AAC, WAV, FLAC
    """)

    st.markdown("---")
    st.markdown("<p class='footer'>Feito com ❤️ para pesquisa</p>", unsafe_allow_html=True)

# Área principal
st.markdown("### 📁 Envie seu arquivo de áudio")

uploaded_file = st.file_uploader(
    "Arraste ou clique para selecionar",
    type=["mp3", "ogg", "aac", "wav", "flac"],
    accept_multiple_files=False,
    help="Formatos suportados: MP3, OGG, AAC, WAV, FLAC"
)

# Opções de transcrição
col1, col2 = st.columns(2)
with col1:
    mode = st.radio(
        "📝 Modo de Transcrição",
        ["texto", "tempo"],
        format_func=lambda x: "📝 Texto Corrido" if x == "texto" else "⏱️ Com Timestamps",
        help="Texto corrido = apenas o texto | Com timestamps = marcação de tempo"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-box">
    💡 <b>Dica:</b> Para áudios longos, o modelo <b>base</b> oferece bom equilíbrio entre velocidade e precisão.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Botão de transcrição
if uploaded_file is not None:
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.markdown(f"""
    <div class="file-info">
        📄 <b>Arquivo:</b> {uploaded_file.name}<br>
        📦 <b>Tamanho:</b> {file_size:.2f} MB
    </div>
    """, unsafe_allow_html=True)

    transcribe_btn = st.button("🚀 Iniciar Transcrição", use_container_width=True, disabled=st.session_state.is_processing)

    if transcribe_btn and not st.session_state.is_processing:
        st.session_state.is_processing = True

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, uploaded_file.name)
            with open(input_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            progress_container = st.container()
            with progress_container:
                st.markdown("### ⏳ Processando...")

                progress_bar = st.progress(0)
                status_text = st.empty()

                # Passo 1: Conversão
                status_text.text("🔄 Convertendo áudio para formato otimizado...")
                progress_bar.progress(0.1)

                wav_path = convert_to_wav(input_path)
                if not wav_path:
                    st.error("❌ Falha na conversão do áudio. Verifique se o arquivo não está corrompido.")
                    st.session_state.is_processing = False
                    st.stop()

                duration = get_audio_duration(wav_path)
                if duration:
                    st.markdown(f"⏱️ Duração do áudio: **{format_time(duration)}**")

                progress_bar.progress(0.2)

                # Passo 2: Carregar modelo
                status_text.text("🧠 Carregando modelo de IA...")
                try:
                    model = load_model(model_size)
                except Exception as e:
                    st.error(f"❌ Erro ao carregar modelo: {e}")
                    st.session_state.is_processing = False
                    st.stop()

                progress_bar.progress(0.3)

                # Passo 3: Transcrição
                status_text.text("🎙️ Iniciando transcrição...")
                start_time = time.time()

                try:
                    transcription, info = transcribe_audio(
                        wav_path, 
                        model, 
                        mode=mode, 
                        language=language if language != "auto" else None,
                        progress_bar=progress_bar,
                        status_text=status_text
                    )

                    elapsed = time.time() - start_time
                    progress_bar.progress(1.0)

                    # Resultado
                    st.markdown("---")
                    st.markdown("### ✅ Transcrição Concluída!")

                    st.markdown(f"""
                    <div class="success-box">
                        ⏱️ <b>Tempo total:</b> {format_time(elapsed)}<br>
                        🎯 <b>Idioma detectado:</b> {info.language}<br>
                        📊 <b>Confiança:</b> {info.language_probability:.1%}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 📄 Resultado:")
                    result_text = st.text_area(
                        "Transcrição",
                        value=transcription,
                        height=400,
                        label_visibility="collapsed"
                    )

                    col_d1, col_d2 = st.columns(2)

                    with col_d1:
                        st.download_button(
                            label="💾 Baixar como .txt",
                            data=transcription,
                            file_name=f"transcricao_{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    with col_d2:
                        if mode == "tempo":
                            srt_content = generate_srt(transcription)
                            st.download_button(
                                label="🎬 Baixar como .srt",
                                data=srt_content,
                                file_name=f"transcricao_{uploaded_file.name.rsplit('.', 1)[0]}.srt",
                                mime="text/plain",
                                use_container_width=True
                            )

                    st.balloons()

                except Exception as e:
                    st.error(f"❌ Erro durante transcrição: {e}")

                finally:
                    st.session_state.is_processing = False
                    if os.path.exists(wav_path):
                        os.remove(wav_path)

else:
    # Estado vazio
    st.markdown("""
    <div style="text-align:center; padding:50px 20px;">
        <h2 style="color:#455A64;">👋 Bem-vindo ao FeatherTranskript Web!</h2>
        <p style="font-size:1.15em; color:#607D8B;">Envie um arquivo de áudio acima para começar.</p>
        <br>
        <div style="display:flex; justify-content:center; gap:15px; flex-wrap:wrap;">
            <div class="format-card">🎵 MP3</div>
            <div class="format-card">🎵 OGG</div>
            <div class="format-card">🎵 AAC</div>
            <div class="format-card">🎵 WAV</div>
            <div class="format-card">🎵 FLAC</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =================== SEÇÃO COMPRE-NOS UM CAFÉ ===================
st.markdown("---")

coffee_html = """
<div class="coffee-section">
    <h3>☕ Compre-nos um Café</h3>
    <p>Ajude a manter este projeto em funcionamento com uma contribuição simbólica!</p>
    
    <div class="coffee-buttons">
        <button class="coffee-btn">☕ R$ 5</button>
        <button class="coffee-btn">☕☕ R$ 15</button>
        <button class="coffee-btn">☕☕☕ R$ 20</button>
    </div>

    <div class="coffee-qrcode">
        <p style="font-weight: 600; color: #6A1B9A;">Escaneie o QR Code ou copie a chave PIX:</p>
"""

if pix_qr_b64:
    coffee_html += f'<img src="data:image/png;base64,{pix_qr_b64}" style="max-width: 200px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">'

coffee_html += """
        <div class="pix-key">(74) 98821-7793</div>
        <p class="coffee-tip">💡 Qualquer valor ajuda a manter este projeto vivo!</p>
    </div>
</div>
"""

st.markdown(coffee_html, unsafe_allow_html=True)

# =================== GETMEP / UPE RODAPÉ ===================
st.markdown("---")

if getmep_b64 and feather_b64:
    st.markdown(f"""
    <div class="getmep-footer">
        <div class="logos-row">
            <img src="data:image/png;base64,{feather_b64}" alt="FeatherTranskript" style="max-height:45px;">
            <span style="color:#BDBDBD; font-size:1.5em;">×</span>
            <img src="data:image/png;base64,{getmep_b64}" alt="GETMEP" style="max-height:55px;">
        </div>
        <div class="divider"></div>
        <h4>GETMEP — Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa</h4>
        <p>
            Este aplicativo web é fomentado pelo <strong>GETMEP</strong>,<br>
            vinculado à <strong>Universidade de Pernambuco (UPE)</strong>.
        </p>
        <p>
            🔗 <a href="https://getmep-study.vercel.app/" target="_blank">https://getmep-study.vercel.app/</a><br>
            📧 <a href="mailto:wenningtondiasx25@gmail.com">wenningtondiasx25@gmail.com</a>
        </p>
        <p class="version">
            FeatherTranskript Web v1.0 | Baseado em OpenAI Whisper
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="getmep-footer">
        <h4>GETMEP — Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa</h4>
        <p>
            Este aplicativo web é fomentado pelo <strong>GETMEP</strong>,<br>
            vinculado à <strong>Universidade de Pernambuco (UPE)</strong>.
        </p>
        <p>
            🔗 <a href="https://getmep-study.vercel.app/" target="_blank">https://getmep-study.vercel.app/</a><br>
            📧 <a href="mailto:wenningtondiasx25@gmail.com">wenningtondiasx25@gmail.com</a>
        </p>
        <p class="version">
            FeatherTranskript Web v1.0 | Baseado em OpenAI Whisper
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    🪶 FeatherTranskript Web v1.0 | <a href="https://github.com/seu-usuario/feather-transkript-web" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
