import { useEffect, useState } from 'react';
import { Audio } from 'expo-av';

export function useMicrophonePermission() {
  const [granted, setGranted] = useState<boolean | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { status } = await Audio.getPermissionsAsync();
        setGranted(status === 'granted');
      } catch {
        setGranted(false);
      }
    })();
  }, []);

  const request = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      const ok = status === 'granted';
      setGranted(ok);
      return ok;
    } catch {
      setGranted(false);
      return false;
    }
  };

  return { granted, request };
}
