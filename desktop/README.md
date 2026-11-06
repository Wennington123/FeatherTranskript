# 🪶 FeatherTranskript — Versão Desktop

Aplicativo **nativo de desktop** (Windows/Linux) para transcrição de áudio com IA,
**100% local** — nenhum áudio sai do computador. O código-fonte é versionado nesta
pasta e os binários são buildados automaticamente pelo GitHub Actions.

🌐 **Site do projeto:** https://wennington123.github.io/FeatherTranskript/
(licença, política de privacidade, termos de uso e links de download)

## Funcionalidades

- 🎙️ Transcrição local com **faster-whisper** (CPU, `int8`), modelos `tiny` → `large-v3`
- 🇧🇷 Otimizado para **PT-BR**, com reconhecimento de termos em inglês
- 📁 Formatos: `MP3`, `OGG`, `AAC`, `WAV`, `FLAC`, `M4A`
- 📝 Texto corrido ou com **timestamps**
- 💾 Exportação em `.txt` / `.srt`
- 🔒 Nenhum áudio sai do dispositivo (o modelo de IA roda na CPU)

## Downloads (GitHub Releases)

| Artefato | Plataforma | Como usar |
| --- | --- | --- |
| `FeatherTranskript-vX-windows.exe` | Windows 10+ | Baixe o arquivo e dê dois cliques (não precisa instalar nada) |
| `FeatherTranskript-vX-linux.tar.gz` | Linux (glibc ≥ 2.35: Ubuntu 22.04+, Debian 12+, Fedora 38+…) | `tar -xzf FeatherTranskript-vX-linux.tar.gz && ./FeatherTranskript/FeatherTranskript` |

Versão Android (APK): veja as releases `apk-v*` do repositório — também listada no site.

> 💡 **Primeiro uso:** o modelo de IA escolhido é baixado da internet
> (≈75 MB para `tiny` até ≈3 GB para `large-v3`) e fica em cache em
> `~/.cache/huggingface` (Windows: `%USERPROFILE%\.cache\huggingface`).
> Depois disso, tudo funciona offline.

## Rodar localmente (desenvolvimento)

```bash
cd desktop
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Requisitos: Python 3.10+ com Tkinter (no Linux, instale o pacote `tk` da sua distro).

## Build manual

```bash
pip install -r requirements.txt pyinstaller
# No Windows, gere também o ícone do executável antes:
#   pip install pillow
#   python -c "from PIL import Image; Image.open('assets/feathertlogo.png').save('build/icon.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
pyinstaller feathertranskript.spec --noconfirm
```

- Windows: gera `dist/FeatherTranskript.exe` (onefile, com splash de carregamento)
- Linux: gera `dist/FeatherTranskript/` (onedir)

## CI (GitHub Actions)

O workflow [`.github/workflows/build-desktop.yml`](../.github/workflows/build-desktop.yml):

- Dispara via `workflow_dispatch` (com input de versão) ou push de tag `desktop-v*`
- **windows-latest**: Python 3.11 + PyInstaller onefile com splash → `FeatherTranskript-vX-windows.exe`
- **ubuntu-22.04**: PyInstaller onedir → `FeatherTranskript-vX-linux.tar.gz`
  (runner 22.04 de propósito: glibc 2.35 garante compatibilidade com distros mais antigas)
- Publica ambos os artefatos em **GitHub Releases**, com link para o site do projeto

Para publicar uma release: `git tag desktop-v1.1.0 && git push origin desktop-v1.1.0`,
ou rode o workflow manualmente em *Actions → Build Desktop → Run workflow*.

## Relação com as outras versões

| Pasta | Plataforma | Status | Descrição |
| --- | --- | --- | --- |
| `desktop/` | Windows/Linux | **Ativo** | App nativo, código versionado, releases via CI |
| `mobile/` | Android (APK) | Em desenvolvimento | App Expo nativo, on-device, com gravação |
| `docs/` | GitHub Pages | Ativo | Site institucional com licença, privacidade e downloads |

## Identidade visual

- 🪶 **Logo FeatherTranskript**
- 🟢 **GETMEP** (Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa — UPE)
- Cores: verde `#4CAF50`, azul `#2196F3`, teal `#00897B`, coral `#FF7043`
- Seção "Nos faça um Pix" no menu **Ajuda → Sobre** e rodapé GETMEP/UPE
