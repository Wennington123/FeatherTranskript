import * as FileSystem from 'expo-file-system';
import { initWhisper, initWhisperVad, libVersion } from 'whisper.rn';
import type { WhisperContext, WhisperVadContext } from 'whisper.rn';
import { Platform } from 'react-native';

export type WhisperModelSize = 'tiny' | 'base' | 'small' | 'medium' | 'large-v3';

// Modelos multilíngue do whisper.cpp (HF: ggerganov/whisper.cpp)
const MODEL_URLS: Record<WhisperModelSize, string> = {
  tiny: 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin',
  base: 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin',
  small: 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin',
  medium: 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin',
  'large-v3': 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin',
};

const VAD_URL =
  'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-silero-v6.2.0.bin';

const MODELS_DIR = `${FileSystem.documentDirectory}models/`;

function modelFileName(size: WhisperModelSize): string {
  return `ggml-${size}.bin`;
}

function vadFileName(): string {
  return 'ggml-silero-v6.2.0.bin';
}

async function ensureDir(dir: string) {
  const info = await FileSystem.getInfoAsync(dir);
  if (!info.exists) {
    await FileSystem.makeDirectoryAsync(dir, { intermediates: true });
  }
}

async function downloadFile(url: string, dest: string, onProgress?: (p: number) => void) {
  await ensureDir(MODELS_DIR);
  const downloadResumable = FileSystem.createDownloadResumable(
    url,
    dest,
    {},
    (progress) => {
      if (onProgress && progress.totalBytesExpectedToDownload > 0) {
        onProgress(progress.totalBytesWritten / progress.totalBytesExpectedToDownload);
      }
    },
  );
  const result = await downloadResumable.downloadAsync();
  if (!result || !result.uri) {
    throw new Error('Falha no download do modelo.');
  }
  return result.uri;
}

async function getModelPath(size: WhisperModelSize, onProgress?: (p: number) => void) {
  const local = `${MODELS_DIR}${modelFileName(size)}`;
  const info = await FileSystem.getInfoAsync(local);
  if (info.exists) return local;
  return downloadFile(MODEL_URLS[size], local, onProgress);
}

async function getVadPath(onProgress?: (p: number) => void) {
  const local = `${MODELS_DIR}${vadFileName()}`;
  const info = await FileSystem.getInfoAsync(local);
  if (info.exists) return local;
  return downloadFile(VAD_URL, local, onProgress);
}

export interface LoadedEngine {
  whisper: WhisperContext;
  vad: WhisperVadContext;
}

export const WhisperEngine = {
  libVersion,

  async load(
    size: WhisperModelSize,
    onProgress?: (stage: string, p: number) => void,
  ): Promise<LoadedEngine> {
    onProgress?.('Baixando modelo de IA…', 0);
    const whisperPath = await getModelPath(size, (p) => onProgress?.('Baixando modelo de IA…', p * 0.7));
    onProgress?.('Baixando VAD…', 0.72);
    const vadPath = await getVadPath((p) => onProgress?.('Baixando VAD…', 0.72 + p * 0.18));

    onProgress?.('Carregando modelo na memória…', 0.92);
    const whisper = await initWhisper({ filePath: whisperPath });
    const vad = await initWhisperVad({
      filePath: vadPath,
      useGpu: Platform.OS === 'ios',
      nThreads: 4,
    });
    onProgress?.('Pronto!', 1);
    return { whisper, vad };
  },
};
