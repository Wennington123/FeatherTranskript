# 🪶 FeatherTranskript

Aplicativo de **transcrição de áudio com IA** baseado no modelo **Whisper** da OpenAI,
otimizado com **Faster-Whisper**. Tudo roda **100% no dispositivo** — nenhum áudio
sai do seu computador ou celular. Disponível em duas frentes:

| Pasta        | Plataforma           | Descrição                                                    |
| ------------ | -------------------- | ------------------------------------------------------------ |
| [`desktop/`](./desktop) | Windows / Linux        | App nativo 100% local — releases `.exe` / `.tar.gz` via GitHub Actions |
| [`mobile/`](./mobile) | Android (APK)            | App **Expo nativo**, 100% on-device, com gravação e transcrição |

> 🌐 **Site do projeto (GitHub Pages):** https://wennington123.github.io/FeatherTranskript/
> — licença (MIT), política de privacidade, termos de uso, downloads e seção de apoio.

## ⬇️ Downloads

| Versão | Plataforma | Onde baixar |
| --- | --- | --- |
| Desktop | Windows 10+ | [`FeatherTranskript-vX-windows.exe`](https://github.com/Wennington123/FeatherTranskript/releases/latest) — arquivo único, dê dois cliques |
| Desktop | Linux (glibc ≥ 2.35) | [`FeatherTranskript-vX-linux.tar.gz`](https://github.com/Wennington123/FeatherTranskript/releases/latest) — extraia e rode `./FeatherTranskript/FeatherTranskript` |
| Mobile | Android 7.0+ | APK assinado nas [releases `apk-v*`](https://github.com/Wennington123/FeatherTranskript/releases) |

> 💡 **Primeiro uso:** o modelo de IA é baixado da internet (≈75 MB a ≈3 GB,
> conforme o modelo escolhido) e fica em cache. Depois disso, tudo funciona offline.

## ✨ Funcionalidades

- 🎙️ **Transcrição Automática** com IA de ponta (faster-whisper, CPU).
- 🇧🇷 **Otimização para o Português** (PT-BR), com reconhecimento de termos em inglês.
- 📁 **Multiformato**: `MP3`, `OGG`, `AAC`, `WAV`, `FLAC`, `M4A`.
- 📝 **Texto corrido** ou **com timestamps** (`.srt`).
- 💾 **Exportação** em `.txt` / `.srt`.
- 🔒 **Privacidade**: versões desktop e mobile rodam 100% no dispositivo, sem nuvem.

## 🖥️ Versão Desktop (Windows / Linux)

Código-fonte na pasta [`desktop/`](./desktop): interface gráfica Tkinter + engine
faster-whisper (`tiny` → `large-v3`, CPU `int8`). Binários buildados automaticamente
pelo workflow [`.github/workflows/build-desktop.yml`](./.github/workflows/build-desktop.yml)
a cada tag `desktop-v*` (ou manualmente, via *Run workflow*), publicados direto nas releases.

Detalhes, build manual e desenvolvimento: [`desktop/README.md`](./desktop/README.md).

## 📱 Versão Mobile (APK)

A pasta [`mobile/`](./mobile) contém um app **Expo nativo** que:

- Grava áudio pelo microfone e transcreve **localmente** (modelo `whisper.cpp`).
- Oferece **2 modos**:
  - **Não-simultâneo**: grava o áudio → para → transcreve o arquivo.
  - **Simultâneo**: transcreve **ao vivo** enquanto grava (VAD + realtime).
- Gera `.txt` / `.srt` exportáveis.

Veja [`mobile/README.md`](./mobile/README.md) para instruções de build do APK
(`eas build -p android`).

## 📄 Licença

Distribuído sob a [Licença MIT](./LICENSE) — texto completo também no
[site do projeto](https://wennington123.github.io/FeatherTranskript/licenca.html),
junto com a política de privacidade e os termos de uso.

## 💛 Apoie o projeto

O FeatherTranskript é gratuito e de código aberto:

- ☕ **Ko-fi**: https://ko-fi.com/wenningtondaquino
- 💙 **Pix**: QR Code e copia-e-cola na [seção de apoio do site](https://wennington123.github.io/FeatherTranskript/#apoiar)

## 🔗 Identidade

Fomentado pelo **GETMEP** (Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa),
vinculado à **Universidade de Pernambuco (UPE)**.

- 🌐 https://getmep-study.vercel.app/
- 📧 wenningtondiasx25@gmail.com
