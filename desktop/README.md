# 🪶 FeatherTranskript — Versão Desktop

Esta pasta documenta a **versão desktop** (release nativo para Windows/Linux/macOS) do FeatherTranskript.

> ⚠️ **Nota:** o código-fonte da versão desktop **não está versionado neste repositório**.
> A primeira versão do FeatherTranskript foi distribuída como um executável de desktop (release),
> construída sobre o mesmo motor de transcrição local (Faster-Whisper / Whisper da OpenAI).
> O histórico público do repositório começou a partir da versão web (Streamlit).

## O que a versão desktop faz

- Transcrição de áudio **100% local** (sem envio de dados para a nuvem).
- Suporte aos formatos `MP3`, `OGG`, `AAC`, `WAV` e `FLAC`.
- Interface gráfica nativa para selecionar o arquivo e exportar `.txt` / `.srt`.
- Otimizações de modelo (tiny → large-v3) rodando em CPU via `faster-whisper`.

## Relação com as outras versões

| Pasta            | Plataforma          | Status             | Descrição                                 |
| ---------------- | ------------------- | ------------------ | ----------------------------------------- |
| `desktop/`       | Windows/Linux/macOS | Release (binário)  | App nativo de desktop (código não versionado) |
| `web/`           | Navegador           | Ativo (Streamlit)  | `feathertranskriptweb.streamlit.app`      |
| `mobile/`        | Android (APK)       | Em desenvolvimento | App Expo nativo, on-device, com gravação  |

## Identidade visual

Todas as versões compartilham a identidade do projeto:

- 🪶 **Logo FeatherTranskript**
- 🟢 **GETMEP** (Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa — UPE)
- Cores: verde `#4CAF50`, azul `#2196F3`, teal `#00897B`, coral `#FF7043`
- Seção "Nos faça um Pix" e rodapé GETMEP/UPE

## Como reconstruir a versão desktop

Caso queira versionar o código desktop no futuro, a base é a mesma do `web/app.py`
(modelo `WhisperModel` do `faster-whisper`) envolvida por uma interface nativa
(ex.: `PyQt`/`Tkinter`/Electron). O motor de inferência permanece idêntico.
