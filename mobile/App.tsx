import 'react-native-gesture-handler';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { HomeScreen } from './src/components/HomeScreen';
import { theme } from './src/theme';

export default function App() {
  return (
    <SafeAreaProvider style={{ flex: 1, backgroundColor: theme.bg }}>
      <StatusBar style="dark" />
      <HomeScreen />
    </SafeAreaProvider>
  );
}
