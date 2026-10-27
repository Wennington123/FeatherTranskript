const fs = require('fs');
const path = require('path');

const modules = [
  {
    dir: '@fugood/react-native-audio-pcm-stream',
    namespace: 'com.imxiqi.rnliveaudiostream',
  },
  {
    dir: 'react-native-fs',
    namespace: 'com.rnfs',
  },
];

for (const { dir, namespace } of modules) {
  const buildGradle = path.join(__dirname, '..', 'node_modules', dir, 'android', 'build.gradle');
  if (!fs.existsSync(buildGradle)) continue;

  const content = fs.readFileSync(buildGradle, 'utf8');
  if (content.includes(`namespace "${namespace}"`)) continue;

  fs.appendFileSync(buildGradle, `\nandroid { namespace "${namespace}" }\n`);
}
