# 🪶 FeatherTranskript — Mobile (Android APK)

App **Expo nativo** que grava áudio e transcreve **100% no dispositivo** (on-device),
usando [`whisper.rn`](https://github.com/mybigday/whisper.rn) (binding do whisper.cpp).
Nenhum dado de áudio sai do aparelho — privacidade total.

## Funcionalidades

- 🎙️ **2 modos de gravação**:
  - **Gravar e transcrever** (não-simultâneo): grava o áudio → para → transcreve o arquivo.
  - **Ao vivo / simultâneo**: transcreve em tempo real enquanto grava (VAD + RealtimeTranscriber).
- 🇧🇷 Otimizado para **PT-BR** (modelos multilíngue do whisper.cpp).
- 📝 Exportação em **`.txt`** e **`.srt`**.
- 🔒 100% local, sem nuvem.

## Stack

- `expo` + `react-native`
- `whisper.rn` — inferência Whisper on-device
- `@fugood/react-native-audio-pcm-stream` — captura PCM ao vivo (modo simultâneo)
- `expo-av` — gravação de arquivo (modo não-simultâneo)
- `react-native-fs` / `expo-file-system` — modelos e arquivos

## Pré-requisitos

- Node.js 18+
- Conta Expo: **wennington123** (expo.dev/accounts/wennington123)
- `npm i -g eas-cli`

## Build do APK (EAS Build — nuvem)

O EAS Build faz o **prebuild** automaticamente (não precisa de Android Studio/Xcode).

```bash
cd mobile
npm install
eas login            # conta wennington123
eas build -p android --profile preview    # gera um .apk (teste/internal)
# ou
eas build -p android --profile production # gera um .aab (loja)
```

Ao terminar, o EAS disponibiliza o link de download do APK.

## Rodar em desenvolvimento (opcional)

```bash
npm install
npx expo prebuild   # gera código nativo (necessário p/ whisper.rn)
npx expo run:android
```

## Modelos

O modelo (`ggml-base.bin`) e o VAD (`ggml-silero-v6.2.0.bin`) são baixados do HuggingFace
no primeiro uso e cacheados em `FileSystem.documentDirectory/models/`.

## Identidade visual

Mantém a identidade do projeto: logo Feather, cores GETMEP (verde/azul), seção Pix e
rodapé GETMEP/UPE.
