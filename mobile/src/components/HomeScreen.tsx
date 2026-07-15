import React, { useEffect, useRef, useState } from 'react';
import {
  ScrollView, View, Text, TouchableOpacity, TextInput, ActivityIndicator,
  StyleSheet, Alert, Image,
} from 'react-native';
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { WhisperEngine, type WhisperModelSize, type LoadedEngine } from '../WhisperEngine';
import { useMicrophonePermission } from '../Permissions';
import { useRecording, type LangOption } from '../useRecording';
import { useRealtime } from '../useRealtime';
import { theme } from '../theme';

type Mode = 'sequential' | 'realtime';
const feather = Image.resolveAssetSource(require('../../assets/feathertlogo.png')).uri;
const getmep = Image.resolveAssetSource(require('../../assets/getmeplogo.png')).uri;
const pixQr = Image.resolveAssetSource(require('../../assets/pix_qrcode.png')).uri;

const MODELS: WhisperModelSize[] = ['tiny', 'base', 'small', 'medium', 'large-v3'];

export function HomeScreen() {
  const { granted, request } = useMicrophonePermission();
  const [mode, setMode] = useState<Mode>('sequential');
  const [model, setModel] = useState<WhisperModelSize>('base');
  const [lang, setLang] = useState<LangOption>('pt');
  const [engine, setEngine] = useState<LoadedEngine | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadMsg, setLoadMsg] = useState('');

  const rec = useRecording();
  const rt = useRealtime();
  const engineRef = useRef<LoadedEngine | null>(null);

  useEffect(() => {
    engineRef.current = engine;
  }, [engine]);

  const loadEngine = async () => {
    if (loading) return;
    setLoading(true);
    setLoadMsg('Iniciando…');
    try {
      const eng = await WhisperEngine.load(model, (stage, p) => {
        setLoadMsg(`${stage} ${Math.round(p * 100)}%`);
      });
      engineRef.current = eng;
      setEngine(eng);
    } catch (e) {
      Alert.alert('Erro', 'Não foi possível carregar o modelo. Verifique a conexão.');
    } finally {
      setLoading(false);
    }
  };

  const ensureReady = async () => {
    if (granted !== true) {
      const ok = await request();
      if (!ok) { Alert.alert('Permissão', 'É necessário permitir o microfone.'); return false; }
    }
    if (!engineRef.current) {
      Alert.alert('Modelo', 'Aguarde o carregamento do modelo de IA.');
      return false;
    }
    return true;
  };

  const onToggleRecord = async () => {
    if (!(await ensureReady())) return;
    const e = engineRef.current!;
    if (mode === 'sequential') {
      if (rec.isRecording) {
        await rec.stopAndTranscribe(e.whisper, model, lang);
      } else {
        await rec.start();
      }
    } else {
      if (rt.isActive) {
        await rt.stop();
      } else {
        await rt.start(e.whisper, e.vad, lang);
      }
    }
  };

  const resultText = mode === 'sequential' ? rec.result : rt.partial;
  const busy = loading || rec.isTranscribing;

  const exportFile = async (ext: 'txt' | 'srt') => {
    if (!resultText) return;
    const content = ext === 'txt' ? resultText : toSrt(resultText);
    const path = `${FileSystem.documentDirectory}transcricao_${Date.now()}.${ext}`;
    await FileSystem.writeAsStringAsync(path, content);
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(path);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.logoWrap}>
        <Image source={{ uri: feather }} style={styles.logo} />
      </View>
      <Text style={styles.title}>FeatherTranskript</Text>
      <Text style={styles.subtitle}>Transcrição de áudio com IA — 100% no seu dispositivo</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Modo de gravação</Text>
        <View style={styles.row}>
          <ModeButton label="🎙️ Gravar e transcrever" active={mode === 'sequential'}
            onPress={() => setMode('sequential')} />
          <ModeButton label="⏱️ Ao vivo (simultâneo)" active={mode === 'realtime'}
            onPress={() => setMode('realtime')} />
        </View>

        <Text style={styles.label}>Modelo de IA</Text>
        <View style={styles.chips}>
          {MODELS.map((m) => (
            <Chip key={m} label={m} active={model === m} onPress={() => setModel(m)} disabled={loading} />
          ))}
        </View>

        <Text style={styles.label}>Idioma</Text>
        <View style={styles.chips}>
          <Chip label="🇧🇷 PT-BR" active={lang === 'pt'} onPress={() => setLang('pt')} />
          <Chip label="🇺🇸 Inglês" active={lang === 'en'} onPress={() => setLang('en')} />
          <Chip label="🔍 Auto" active={lang === 'auto'} onPress={() => setLang('auto')} />
        </View>

        {!engine && (
          <TouchableOpacity style={[styles.btn, styles.btnPrimary]} onPress={loadEngine} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>🔋 Carregar modelo de IA</Text>}
          </TouchableOpacity>
        )}
        {loading && <Text style={styles.loadMsg}>{loadMsg}</Text>}
      </View>

      <TouchableOpacity style={[styles.btn, (busy || (mode === 'sequential' ? rec.isRecording : rt.isActive)) ? styles.btnDanger : styles.btnRecord]}
        onPress={onToggleRecord} disabled={busy}>
        {busy ? <ActivityIndicator color="#fff" />
          : <Text style={styles.btnText}>
            {mode === 'sequential'
              ? (rec.isRecording ? '⏹️ Parar e transcrever' : '🎙️ Iniciar gravação')
              : (rt.isActive ? '⏹️ Parar' : '🚀 Iniciar ao vivo')}
          </Text>}
      </TouchableOpacity>

      {resultText ? (
        <View style={styles.resultCard}>
          <Text style={styles.label}>📄 Transcrição</Text>
          <TextInput style={styles.resultText} value={resultText} multiline editable onChangeText={(t) => (mode === 'sequential' ? rec.setResult(t) : rt.setPartial(t))} />
          <View style={styles.row}>
            <TouchableOpacity style={[styles.btn, styles.btnSmall, styles.btnPrimary]} onPress={() => exportFile('txt')}>
              <Text style={styles.btnText}>💾 .txt</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.btn, styles.btnSmall, styles.btnPrimary]} onPress={() => exportFile('srt')}>
              <Text style={styles.btnText}>🎬 .srt</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : null}

      {/* Seção Pix */}
      <View style={styles.pixCard}>
        <Text style={styles.pixTitle}>💛 Nos faça um Pix!</Text>
        <Text style={styles.pixText}>Seu apoio mantém este projeto no ar e ajuda a desenvolver novas funcionalidades.</Text>
        <Image source={{ uri: pixQr }} style={styles.pixQr} />
        <View style={styles.pixKey}><Text selectable style={styles.pixKeyText}>(74) 98821-7793</Text></View>
        <Text style={styles.pixTip}>💡 Qualquer valor é bem-vindo! Obrigado por ajudar.</Text>
      </View>

      {/* Rodapé GETMEP / UPE */}
      <View style={styles.footer}>
        <View style={styles.logosRow}>
          <Image source={{ uri: feather }} style={styles.footerLogo} />
          <Text style={styles.times}>×</Text>
          <Image source={{ uri: getmep }} style={styles.footerLogoGetmep} />
        </View>
        <View style={styles.divider} />
        <Text style={styles.footerTitle}>GETMEP — Grupo de Estudos Teórico-Metodológicos em Educação e Pesquisa</Text>
        <Text style={styles.footerText}>Fomentado pelo GETMEP, vinculado à Universidade de Pernambuco (UPE).</Text>
        <Text style={styles.footerText}>🌐 getmep-study.vercel.app</Text>
        <Text style={styles.footerText}>📧 wenningtondiasx25@gmail.com</Text>
        <Text style={styles.version}>FeatherTranskript v1.0 | OpenAI Whisper (on-device)</Text>
      </View>
    </ScrollView>
  );
}

function toSrt(text: string): string {
  const lines = text.split('\n').filter(Boolean);
  return lines.map((l, i) => `${i + 1}\n00:00:0${i} --> 00:00:0${i + 1}\n${l}\n`).join('\n');
}

function ModeButton({ label, active, onPress }: { label: string; active: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity style={[styles.modeBtn, active && styles.modeBtnActive]} onPress={onPress}>
      <Text style={[styles.modeBtnText, active && styles.modeBtnTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

function Chip({ label, active, onPress, disabled }: { label: string; active: boolean; onPress: () => void; disabled?: boolean }) {
  return (
    <TouchableOpacity style={[styles.chip, active && styles.chipActive]} onPress={onPress} disabled={disabled}>
      <Text style={[styles.chipText, active && styles.chipTextActive]}>{label}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.bg },
  content: { padding: 18, paddingBottom: 40 },
  logoWrap: { alignItems: 'center', marginTop: 8 },
  logo: { width: 70, height: 70, resizeMode: 'contain' },
  title: { fontSize: 26, fontWeight: '700', textAlign: 'center', color: theme.featherDark, marginTop: 6 },
  subtitle: { textAlign: 'center', color: theme.getmepGray, fontSize: 14, marginBottom: 14 },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#E0E0E0', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 8 },
  label: { fontSize: 14, fontWeight: '600', color: theme.featherDark, marginTop: 12, marginBottom: 6 },
  row: { flexDirection: 'row', gap: 10 },
  modeBtn: { flex: 1, padding: 12, borderRadius: 12, borderWidth: 1, borderColor: '#E0E0E0', backgroundColor: '#f5f5f5', alignItems: 'center' },
  modeBtnActive: { backgroundColor: theme.getmepLight, borderColor: theme.getmepGreen },
  modeBtnText: { color: theme.text, fontWeight: '500', fontSize: 13 },
  modeBtnTextActive: { color: theme.getmepGreenDark, fontWeight: '700' },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { paddingVertical: 8, paddingHorizontal: 14, borderRadius: 20, borderWidth: 1, borderColor: '#E0E0E0', backgroundColor: '#f5f5f5' },
  chipActive: { backgroundColor: theme.getmepGreen, borderColor: theme.getmepGreen },
  chipText: { color: theme.text, fontSize: 13 },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  btn: { borderRadius: 30, paddingVertical: 14, alignItems: 'center', justifyContent: 'center', marginTop: 14 },
  btnPrimary: { backgroundColor: theme.getmepGreen },
  btnRecord: { backgroundColor: theme.featherTeal },
  btnDanger: { backgroundColor: theme.featherCoral },
  btnSmall: { flex: 1, paddingVertical: 10, marginTop: 0 },
  btnText: { color: '#fff', fontWeight: '600', fontSize: 16 },
  loadMsg: { textAlign: 'center', color: theme.getmepBlue, marginTop: 8, fontSize: 13 },
  resultCard: { backgroundColor: '#fff', borderRadius: 16, padding: 16, marginTop: 16, borderWidth: 1, borderColor: theme.getmepGreen },
  resultText: { backgroundColor: '#fafafa', borderRadius: 12, borderWidth: 1, borderColor: '#E0E0E0', padding: 12, minHeight: 160, textAlignVertical: 'top', fontSize: 15, lineHeight: 24, color: '#37474F' },
  pixCard: { backgroundColor: 'rgba(0,150,136,0.06)', borderWidth: 2, borderColor: theme.pix, borderRadius: 16, padding: 24, marginTop: 24, alignItems: 'center' },
  pixTitle: { color: theme.pixDark, fontSize: 20, fontWeight: '700', marginBottom: 8 },
  pixText: { color: theme.text, fontSize: 14, textAlign: 'center' },
  pixQr: { width: 180, height: 180, borderRadius: 8, marginTop: 14 },
  pixKey: { backgroundColor: '#fff', borderWidth: 2, borderColor: theme.pix, borderRadius: 8, padding: 12, marginTop: 12 },
  pixKeyText: { fontFamily: 'monospace', fontSize: 16, color: '#004D40', fontWeight: '600' },
  pixTip: { color: theme.pixDark, fontStyle: 'italic', fontSize: 12, marginTop: 10 },
  footer: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#E0E0E0', borderRadius: 16, padding: 22, marginTop: 24, alignItems: 'center' },
  logosRow: { flexDirection: 'row', alignItems: 'center', gap: 24 },
  footerLogo: { height: 45, width: 45, resizeMode: 'contain' },
  footerLogoGetmep: { height: 55, width: 120, resizeMode: 'contain' },
  times: { color: '#BDBDBD', fontSize: 22 },
  divider: { width: 60, height: 3, backgroundColor: theme.getmepGreen, borderRadius: 2, marginVertical: 12 },
  footerTitle: { color: theme.getmepGreen, fontWeight: '600', fontSize: 15, textAlign: 'center' },
  footerText: { color: theme.getmepGray, fontSize: 13, marginTop: 4 },
  version: { color: '#90A4AE', fontSize: 12, marginTop: 12 },
});
