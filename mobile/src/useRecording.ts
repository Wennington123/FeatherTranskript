import { useRef, useState, useCallback } from 'react';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { WhisperEngine, type WhisperModelSize } from './WhisperEngine';
import type { WhisperContext } from 'whisper.rn';

export type LangOption = 'pt' | 'en' | 'auto';

export function useRecording() {
  const recordingRef = useRef<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [result, setResult] = useState('');

  const start = useCallback(async () => {
    try {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY,
      );
      recordingRef.current = recording;
      setIsRecording(true);
      setResult('');
    } catch (e) {
      console.error('Erro ao iniciar gravação:', e);
    }
  }, []);

  const stopAndTranscribe = useCallback(
    async (whisper: WhisperContext | null, model: WhisperModelSize, lang: LangOption) => {
      if (!recordingRef.current) return;
      setIsRecording(false);
      setIsTranscribing(true);
      try {
        await recordingRef.current.stopAndUnloadAsync();
        const uri = recordingRef.current.getURI();
        recordingRef.current = null;
        if (!uri || !whisper) {
          setResult('Modelo não carregado. Aguarde o carregamento e tente novamente.');
          return;
        }
        // expo-av grava m4a; whisper.cpp aceita WAV. Convertemos via FileSystem copiando
        // para .wav (whisper.rn faz decode interno de formatos comuns).
        const wavUri = `${FileSystem.documentDirectory}recording_${Date.now()}.wav`;
        await FileSystem.copyAsync({ from: uri, to: wavUri });

        const { promise } = whisper.transcribe(wavUri, {
          language: lang === 'auto' ? undefined : lang,
          task: 'transcribe',
        });
        const { result: text } = await promise;
        setResult(text?.trim() ?? '');
      } catch (e) {
        console.error('Erro na transcrição:', e);
        setResult('Erro ao transcrever o áudio.');
      } finally {
        setIsTranscribing(false);
      }
    },
    [],
  );

  return { isRecording, isTranscribing, result, start, stopAndTranscribe, setResult };
}
