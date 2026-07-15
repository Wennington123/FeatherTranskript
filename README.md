# 🪶 FeatherTranskript

Aplicativo de **transcrição de áudio com IA** baseado no modelo **Whisper** da OpenAI,
otimizado com **Faster-Whisper** / **whisper.cpp**. Disponível em três frentes:

| Pasta        | Plataforma           | Descrição                                                    |
| ------------ | -------------------- | ------------------------------------------------------------ |
| [`web/`](./web)       | Navegador (Streamlit)    | App web hospedado em `feathertranskriptweb.streamlit.app`   |
| [`mobile/`](./mobile) | Android (APK)            | App **Expo nativo**, 100% on-device, com gravação e transcrição |
| [`desktop/`](./desktop) | Windows/Linux/macOS   | Versão desktop (release) — documentada em `desktop/README.md` |

## ✨ Funcionalidades

- 🎙️ **Transcrição Automática** com IA de ponta.
- 🇧🇷 **Otimização para o Português** (PT-BR), com reconhecimento de termos em inglês.
- 📁 **Multiformato**: `MP3`, `OGG`, `AAC`, `WAV`, `FLAC`.
- 📝 **Texto corrido** ou **com timestamps** (`.srt`).
- 💾 **Exportação** em `.txt` / `.srt`.
- 🔒 **Privacidade** (a versão mobile roda 100% no dispositivo, sem nuvem).

## 📱 Versão Mobile (APK)

A pasta [`mobile/`](./mobile) contém um app **Expo nativo** que:

- Grava áudio pelo microfone e transcreve **localmente** (modelo `whisper.cpp`).
- Oferece **2 modos**:
  - **Não-simultâneo**: grava o áudio → para → transcreve o arquivo.
  - **Simultâneo**: transcreve **ao vivo** enquanto grava (VAD + realtime).
- Gera `.txt` / `.srt` exportáveis.

Veja [`mobile/README.md`](./mobile/README.md) para instruções de build do APK
(`eas build -p android`).

## 🔗 Identidade

Fomentado pelo **GETMEP** (Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa),
vinculado à **Universidade de Pernambuco (UPE)**.

- 🌐 https://getmep-study.vercel.app/
- 📧 wenningtondiasx25@gmail.com
