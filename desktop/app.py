"""FeatherTranskript Desktop — transcrição de áudio com IA 100% local."""

import queue
import sys
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import transcriber

APP_VERSION = "1.1.0"
LANGUAGES = [
    ("pt", "Português (PT-BR)"),
    ("en", "Inglês"),
    (None, "Auto-detectar"),
]
AUDIO_FILETYPES = [
    ("Arquivos de áudio", "*.mp3 *.ogg *.aac *.wav *.flac *.m4a"),
    ("Todos os arquivos", "*.*"),
]

BG_COLOR = "#f8fafc"
DARK_COLOR = "#263238"
TEXT_COLOR = "#455A64"
GREEN = "#4CAF50"
BLUE = "#2196F3"
TEAL = "#00897B"


def assets_dir():
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "assets"
    return Path(__file__).resolve().parent / "assets"


class FeatherTranskriptApp:
    def __init__(self, root):
        self.root = root
        self.queue = queue.Queue()
        self.worker = None
        self.segments = None
        self.transcription_info = None
        self.audio_path = None
        self.last_progress_step = -1

        root.title(f"FeatherTranskript v{APP_VERSION}")
        root.configure(bg=BG_COLOR)
        root.minsize(760, 660)

        self._load_logos()
        self._build_menu()
        self._build_header()
        self._build_controls()
        self._build_progress()
        self._build_result()
        self._build_footer()
        root.geometry("+80+60")
        root.after(100, self._poll_queue)

    def _load_logos(self):
        assets = assets_dir()
        self.feather_img = None
        self.getmep_img = None
        self.pix_img = None
        try:
            self.feather_img = tk.PhotoImage(file=assets / "feathertlogo.png")
            k = max(1, self.feather_img.height() // 64)
            if k > 1:
                self.feather_img = self.feather_img.subsample(k)
            self.root.iconphoto(True, self.feather_img)
        except tk.TclError:
            pass
        try:
            self.getmep_img = tk.PhotoImage(file=assets / "getmeplogo.png")
            k = max(1, self.getmep_img.height() // 56)
            if k > 1:
                self.getmep_img = self.getmep_img.subsample(k)
        except tk.TclError:
            pass
        try:
            self.pix_img = tk.PhotoImage(file=assets / "pix_qrcode.png")
        except tk.TclError:
            pass

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Sobre o FeatherTranskript", command=self._show_about)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        self.root.config(menu=menubar)

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_COLOR)
        header.pack(fill="x", padx=24, pady=(18, 6))
        if self.feather_img:
            tk.Label(header, image=self.feather_img, bg=BG_COLOR).pack()
        tk.Label(
            header,
            text="FeatherTranskript",
            font=("Segoe UI", 20, "bold"),
            fg=DARK_COLOR,
            bg=BG_COLOR,
        ).pack(pady=(4, 0))
        tk.Label(
            header,
            text="Transcrição de áudio com IA — Whisper otimizado, 100% local",
            font=("Segoe UI", 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
        ).pack()

    def _build_controls(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="x", padx=24, pady=12)

        file_frame = tk.Frame(frame, bg=BG_COLOR)
        file_frame.pack(fill="x")
        tk.Button(
            file_frame,
            text="📁 Selecionar áudio",
            command=self._select_audio,
            bg=BLUE,
            fg="white",
            activebackground="#1565C0",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=8,
            cursor="hand2",
        ).pack(side="left")
        self.file_label = tk.Label(
            file_frame,
            text="Nenhum arquivo selecionado",
            font=("Segoe UI", 10),
            fg=TEXT_COLOR,
            bg=BG_COLOR,
            anchor="w",
        )
        self.file_label.pack(side="left", fill="x", expand=True, padx=12)

        options = tk.Frame(frame, bg=BG_COLOR)
        options.pack(fill="x", pady=(14, 0))

        tk.Label(options, text="Modelo de IA", font=("Segoe UI", 9, "bold"), fg=DARK_COLOR, bg=BG_COLOR).grid(
            row=0, column=0, sticky="w"
        )
        self.model_var = tk.StringVar(value="base")
        model_box = ttk.Combobox(options, textvariable=self.model_var, values=transcriber.MODEL_SIZES, state="readonly", width=12)
        model_box.grid(row=1, column=0, sticky="we", padx=(0, 16))

        tk.Label(options, text="Idioma", font=("Segoe UI", 9, "bold"), fg=DARK_COLOR, bg=BG_COLOR).grid(row=0, column=1, sticky="w")
        self.language_var = tk.StringVar(value=LANGUAGES[0][1])
        language_box = ttk.Combobox(
            options,
            textvariable=self.language_var,
            values=[label for _, label in LANGUAGES],
            state="readonly",
            width=20,
        )
        language_box.grid(row=1, column=1, sticky="we")

        options.columnconfigure(0, weight=1)
        options.columnconfigure(1, weight=1)

        self.mode_var = tk.StringVar(value="texto")
        modes = tk.Frame(frame, bg=BG_COLOR)
        modes.pack(fill="x", pady=(14, 0))
        tk.Label(modes, text="Modo de transcrição", font=("Segoe UI", 9, "bold"), fg=DARK_COLOR, bg=BG_COLOR).pack(anchor="w")
        radios = tk.Frame(modes, bg=BG_COLOR)
        radios.pack(anchor="w")
        tk.Radiobutton(
            radios,
            text="Texto corrido",
            variable=self.mode_var,
            value="texto",
            command=self._render_result,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            activebackground=BG_COLOR,
            selectcolor=BG_COLOR,
        ).pack(side="left")
        tk.Radiobutton(
            radios,
            text="Com timestamps",
            variable=self.mode_var,
            value="tempo",
            command=self._render_result,
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            activebackground=BG_COLOR,
            selectcolor=BG_COLOR,
        ).pack(side="left", padx=(20, 0))

        self.transcribe_btn = tk.Button(
            frame,
            text="🚀 Iniciar Transcrição",
            command=self._start_transcription,
            bg=GREEN,
            fg="white",
            activebackground="#43A047",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 12, "bold"),
            pady=10,
            cursor="hand2",
        )
        self.transcribe_btn.pack(fill="x", pady=(16, 0))

    def _build_progress(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="x", padx=24, pady=(10, 0))
        self.progress = ttk.Progressbar(frame, mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        self.status_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.status_var, font=("Segoe UI", 9), fg=TEXT_COLOR, bg=BG_COLOR).pack(anchor="w", pady=(4, 0))

    def _build_result(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="both", expand=True, padx=24, pady=12)
        self.result_text = tk.Text(
            frame,
            wrap="word",
            relief="flat",
            font=("Segoe UI", 10),
            fg="#37474F",
            bg="white",
            state="disabled",
        )
        scrollbar = ttk.Scrollbar(frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_text.pack(side="left", fill="both", expand=True)

        buttons = tk.Frame(self.root, bg=BG_COLOR)
        buttons.pack(fill="x", padx=24, pady=(0, 12))
        self.save_txt_btn = tk.Button(
            buttons,
            text="💾 Salvar como .txt",
            command=self._save_txt,
            state="disabled",
            bg="#BDBDBD",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=8,
        )
        self.save_txt_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.save_srt_btn = tk.Button(
            buttons,
            text="🎬 Salvar como .srt",
            command=self._save_srt,
            state="disabled",
            bg="#BDBDBD",
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=8,
        )
        self.save_srt_btn.pack(side="left", fill="x", expand=True)

    def _build_footer(self):
        tk.Label(
            self.root,
            text="GETMEP — Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa · Universidade de Pernambuco (UPE)",
            font=("Segoe UI", 8),
            fg="#90A4AE",
            bg=BG_COLOR,
        ).pack(side="bottom", fill="x", pady=(0, 8))

    def _select_audio(self):
        path = filedialog.askopenfilename(title="Selecionar áudio", filetypes=AUDIO_FILETYPES)
        if not path:
            return
        self.audio_path = Path(path)
        size_mb = self.audio_path.stat().st_size / (1024 * 1024)
        self.file_label.config(text=f"{self.audio_path.name}  ·  {size_mb:.2f} MB")

    def _selected_language(self):
        label = self.language_var.get()
        for code, name in LANGUAGES:
            if name == label:
                return code
        return None

    def _start_transcription(self):
        if self.worker is not None:
            return
        if self.audio_path is None:
            messagebox.showwarning("FeatherTranskript", "Selecione um arquivo de áudio primeiro.")
            return

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")
        self.save_txt_btn.config(state="disabled", bg="#BDBDBD")
        self.save_srt_btn.config(state="disabled", bg="#BDBDBD")
        self.segments = None
        self.transcription_info = None
        self.progress["value"] = 0
        self.last_progress_step = -1
        self.status_var.set("Carregando modelo de IA…")
        self.transcribe_btn.config(state="disabled", bg="#BDBDBD")

        self.worker = threading.Thread(target=self._run_transcription, daemon=True)
        self.worker.start()

    def _run_transcription(self):
        try:
            model_size = self.model_var.get()
            language = self._selected_language()
            start_time = time.time()

            def progress_cb(fraction):
                step = int(fraction * 100)
                if step != self.last_progress_step:
                    self.last_progress_step = step
                    self.queue.put(("progress", fraction))

            result = transcriber.transcribe(self.audio_path, model_size, language, progress_cb)
            elapsed = time.time() - start_time

            if self.mode_var.get() == "tempo":
                text = transcriber.to_timestamped(result.segments)
            else:
                text = transcriber.to_plain_text(result.segments)

            self.queue.put(("done", (result, text, elapsed)))
        except Exception as exc:
            self.queue.put(("error", str(exc)))

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.queue.get_nowait()
                if kind == "progress":
                    self.progress["value"] = payload * 100
                elif kind == "done":
                    self._on_done(*payload)
                elif kind == "error":
                    self._on_error(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)

    def _on_done(self, result, text, elapsed):
        self.worker = None
        self.segments = result.segments
        self.transcription_info = result
        self.transcribe_btn.config(state="normal", bg=GREEN)
        self.progress["value"] = 100
        self.status_var.set(
            f"✅ Concluído em {transcriber.format_time(elapsed)} · "
            f"idioma: {result.language} ({result.language_probability:.0%})"
        )
        self.result_text.config(state="normal")
        self.result_text.insert("1.0", text)
        self.result_text.config(state="disabled")
        self.save_txt_btn.config(state="normal", bg=TEAL)
        self.save_srt_btn.config(state="normal", bg=TEAL)

    def _on_error(self, message):
        self.worker = None
        self.transcribe_btn.config(state="normal", bg=GREEN)
        self.status_var.set("❌ Erro durante a transcrição")
        messagebox.showerror("FeatherTranskript", f"Erro durante a transcrição:\n{message}")

    def _render_result(self):
        if self.segments is None:
            return
        if self.mode_var.get() == "tempo":
            text = transcriber.to_timestamped(self.segments)
        else:
            text = transcriber.to_plain_text(self.segments)
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.config(state="disabled")

    def _save_default_name(self, extension):
        stem = self.audio_path.stem if self.audio_path else "transcricao"
        return f"transcricao_{stem}{extension}"

    def _save_txt(self):
        if self.segments is None:
            return
        path = filedialog.asksaveasfilename(
            title="Salvar transcrição",
            defaultextension=".txt",
            initialfile=self._save_default_name(".txt"),
            filetypes=[("Texto", "*.txt")],
        )
        if not path:
            return
        text = self.result_text.get("1.0", "end-1c")
        Path(path).write_text(text, encoding="utf-8")
        self.status_var.set(f"💾 Salvo em {path}")

    def _save_srt(self):
        if self.segments is None:
            return
        path = filedialog.asksaveasfilename(
            title="Salvar legenda",
            defaultextension=".srt",
            initialfile=self._save_default_name(".srt"),
            filetypes=[("Legenda SubRip", "*.srt")],
        )
        if not path:
            return
        Path(path).write_text(transcriber.generate_srt(self.segments), encoding="utf-8")
        self.status_var.set(f"💾 Salvo em {path}")

    def _show_about(self):
        about = tk.Toplevel(self.root)
        about.title("Sobre o FeatherTranskript")
        about.configure(bg="white")
        about.resizable(False, False)
        about.transient(self.root)

        tk.Label(about, image=self.feather_img, bg="white").pack(pady=(18, 4))
        tk.Label(about, text=f"FeatherTranskript Desktop v{APP_VERSION}", font=("Segoe UI", 12, "bold"), fg=DARK_COLOR, bg="white").pack()
        tk.Label(
            about,
            text="Transcrição de áudio com IA local (OpenAI Whisper / faster-whisper).\nNenhum áudio sai do seu computador.",
            font=("Segoe UI", 9),
            fg=TEXT_COLOR,
            bg="white",
            justify="center",
        ).pack(padx=24, pady=6)

        if self.getmep_img and self.feather_img:
            logos = tk.Frame(about, bg="white")
            logos.pack(pady=6)
            tk.Label(logos, image=self.feather_img, bg="white").pack(side="left", padx=8)
            tk.Label(logos, text="×", font=("Segoe UI", 14), fg="#BDBDBD", bg="white").pack(side="left")
            tk.Label(logos, image=self.getmep_img, bg="white").pack(side="left", padx=8)

        tk.Label(
            about,
            text="Fomentado pelo GETMEP — Grupo de Estudos Teórico-Metodológicos\nem Educação e Pesquisa, vinculado à Universidade de Pernambuco (UPE).",
            font=("Segoe UI", 9),
            fg=TEXT_COLOR,
            bg="white",
            justify="center",
        ).pack(padx=24, pady=4)
        tk.Label(
            about,
            text="getmep-study.vercel.app  ·  wenningtondiasx25@gmail.com",
            font=("Segoe UI", 9, "underline"),
            fg=BLUE,
            bg="white",
        ).pack(pady=2)

        if self.pix_img:
            pix = tk.Frame(about, bg="white", highlightbackground=TEAL, highlightthickness=2)
            pix.pack(padx=24, pady=12, fill="x")
            tk.Label(pix, text="💛 Nos faça um Pix!", font=("Segoe UI", 10, "bold"), fg="#00695C", bg="white").pack(pady=(10, 4))
            tk.Label(pix, image=self.pix_img, bg="white").pack()
            tk.Label(pix, text="Escaneie com o app do seu banco", font=("Segoe UI", 9), fg="#004D40", bg="white").pack(pady=4)
            tk.Button(
                pix,
                text="☕ Apoiar no Ko-fi",
                command=lambda: webbrowser.open("https://ko-fi.com/wenningtondaquino"),
                bg=TEAL,
                fg="white",
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                padx=12,
                pady=4,
                cursor="hand2",
            ).pack(pady=(2, 10))
            tk.Label(pix, text="Qualquer valor é bem-vindo!", font=("Segoe UI", 8, "italic"), fg="#00695C", bg="white").pack(pady=(0, 10))

        tk.Button(about, text="Fechar", command=about.destroy, bg=GREEN, fg="white", relief="flat", font=("Segoe UI", 10, "bold"), padx=20, pady=6, cursor="hand2").pack(pady=(0, 16))
        about.wait_visibility()
        about.grab_set()


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    FeatherTranskriptApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
