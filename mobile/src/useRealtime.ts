import { useRef, useState, useCallback } from 'react';
import RNFS from 'react-native-fs';
import {
  RealtimeTranscriber,
  RingBufferVad,
  VAD_PRESETS,
} from 'whisper.rn/realtime-transcription';
import { AudioPcmStreamAdapter } from 'whisper.rn/realtime-transcription/adapters';
import type { WhisperContext, WhisperVadContext } from 'whisper.rn';

export type LangOption = 'pt' | 'en' | 'auto';

export function useRealtime() {
  const transcriberRef = useRef<RealtimeTranscriber | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [partial, setPartial] = useState('');

  const start = useCallback(
    async (whisper: WhisperContext | null, vad: WhisperVadContext | null, lang: LangOption) => {
      if (!whisper || !vad) {
        setPartial('Modelo não carregado. Aguarde o carregamento e tente novamente.');
        return;
      }
      try {
        const audioStream = new AudioPcmStreamAdapter();
        const ringVad = new RingBufferVad(vad, {
          vadOptions: VAD_PRESETS.default,
          vadPreset: 'default',
        });

        const transcriber = new RealtimeTranscriber(
          { whisperContext: whisper, vadContext: ringVad, audioStream, fs: RNFS },
          {
            audioSliceSec: 30,
            audioMinSec: 0.5,
            maxSlicesInMemory: 1,
            transcribeOptions: { language: lang === 'auto' ? undefined : lang },
          },
          {
            onTranscribe: (event) => {
              const data = (event as any).data;
              if (data?.result) {
                const all = transcriberRef.current?.getTranscriptionResults() || [];
                const full = all
                  .map((r: any) => r.transcribeEvent?.data?.result)
                  .filter(Boolean)
                  .join(' ')
                  .trim();
                setPartial(full || data.result);
              }
            },
            onStatusChange: (active: boolean) => setIsActive(active),
            onError: (err: string) => setPartial(`Erro: ${err}`),
          },
        );
        transcriberRef.current = transcriber;
        setPartial('');
        await transcriber.start();
      } catch (e) {
        console.error('Erro no realtime:', e);
        setPartial('Erro ao iniciar transcrição ao vivo.');
      }
    },
    [],
  );

  const stop = useCallback(async () => {
    try {
      await transcriberRef.current?.stop();
    } catch (e) {
      console.error('Erro ao parar:', e);
    } finally {
      transcriberRef.current?.release();
      transcriberRef.current = null;
      setIsActive(false);
    }
  }, []);

  return { isActive, partial, start, stop, setPartial };
}
