"""Motor de transcrição do FeatherTranskript Desktop (faster-whisper, CPU)."""

import time
from dataclasses import dataclass

from faster_whisper import WhisperModel

MODEL_SIZES = ["tiny", "base", "small", "medium", "large-v3"]

_models = {}


@dataclass
class TranscriptionResult:
    segments: list
    language: str
    language_probability: float
    duration: float


def load_model(model_size):
    if model_size not in _models:
        _models[model_size] = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _models[model_size]


def transcribe(path, model_size="base", language=None, progress_cb=None):
    """Transcreve um arquivo de áudio e retorna TranscriptionResult.

    language=None deixa o Whisper detectar o idioma.
    progress_cb recebe frações entre 0.0 e 1.0 conforme os segmentos avançam.
    """
    model = load_model(model_size)
    segments_iter, info = model.transcribe(
        str(path),
        language=language,
        task="transcribe",
        vad_filter=True,
        condition_on_previous_text=True,
    )

    duration = info.duration or 0.0
    segments = []
    for segment in segments_iter:
        segments.append(segment)
        if progress_cb and duration > 0:
            progress_cb(min(segment.end / duration, 1.0))
    if progress_cb:
        progress_cb(1.0)

    return TranscriptionResult(
        segments=segments,
        language=info.language,
        language_probability=info.language_probability,
        duration=duration,
    )


def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def to_plain_text(segments):
    return "\n".join(segment.text.strip() for segment in segments)


def to_timestamped(segments):
    lines = []
    for segment in segments:
        start = format_time(segment.start)
        end = format_time(segment.end)
        lines.append(f"[{start} --> {end}] {segment.text.strip()}")
    return "\n".join(lines)


def _srt_time(seconds):
    millis = int(round(seconds * 1000))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(segments):
    entries = []
    for counter, segment in enumerate(segments, 1):
        entries.append(
            f"{counter}\n{_srt_time(segment.start)} --> {_srt_time(segment.end)}\n"
            f"{segment.text.strip()}\n"
        )
    return "\n".join(entries)
