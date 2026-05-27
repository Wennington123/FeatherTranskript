# 🪶 FeatherTranskript Web

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Whisper](https://img.shields.io/badge/Faster--Whisper-OpenAI-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma aplicação web ágil e intuitiva para **transcrição de áudio com Inteligência Artificial**. Baseada no poderoso modelo **Whisper** da OpenAI, mas impulsionada pelo **Faster-Whisper** para garantir máxima velocidade e eficiência sem perder a precisão.

---

## ✨ Principais Funcionalidades

* 🎙️ **Transcrição Automática:** Conversão de fala para texto utilizando IA de ponta.
* 🇧🇷 **Otimização para o Português:** Alta precisão no idioma, com reconhecimento inteligente de termos estrangeiros embutidos na fala.
* 📁 **Suporte Multiformato:** Aceita arquivos em `MP3`, `OGG`, `AAC`, `WAV` e `FLAC`.
* 📝 **Modos de Visualização:** Escolha entre **Texto Corrido** (ideal para leitura/resumos) ou **Com Timestamps** (ideal para decupagem).
* ⏱️ **Feedback em Tempo Real:** Barra de progresso com estimativa de tempo durante o processamento.
* 💾 **Exportação Prática:** Download imediato dos resultados em formato `.TXT` ou arquivo de legenda `.SRT`.

---

## 🔄 Como o FeatherTranskript Funciona?

O fluxo abaixo ilustra a jornada do seu arquivo, desde o upload até a exportação do texto final:

```mermaid
graph TD
    subgraph UI ["🖥️ Interface do Usuário (Streamlit)"]
        A[📁 Upload de Áudio]
        B[⚙️ Configuração <br> Mode e Modelo]
        F[✅ Transcrição Concluída]
        G([💾 Baixar TXT])
        H([🎬 Baixar SRT])
        I([📋 Copiar Área de Transferência])
    end

    subgraph Core ["⚙️ Motor de Processamento (Backend)"]
        C[🔄 Conversão & Otimização <br> FFmpeg]
        D[(🧠 Carregamento do Modelo IA <br> Faster-Whisper)]
        E[🎙️ Inferência & Geração de Texto]
    end

    A -->|Envia Arquivo| C
    B -.->|Define Parâmetros| D
    C -->|Áudio Processado| E
    D -->|Motor de IA| E
    E -->|Devolve Resultado| F
    
    F --> G
    F --> H
    F --> I

    classDef ui fill:#0e1117,stroke:#ff4b4b,stroke-width:2px,color:#fff;
    classDef core fill:#1e1e1e,stroke:#4CAF50,stroke-width:2px,color:#fff;
    class UI ui;
    class Core core;
