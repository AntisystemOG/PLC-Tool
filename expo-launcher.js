// Launcher script for preview_start — calls Expo CLI's Node.js entry
// directly (no npx/shell) so this process stays alive for the tool to track.
const { spawnSync } = require('child_process');
const path = require('path');

const projectDir = path.join(__dirname, 'thompson-family-chore-app');
const expoCli = path.join(projectDir, 'node_modules', 'expo', 'bin', 'cli');
const extraArgs = process.argv.slice(2); // e.g. ['--web', '--port', '8083']

process.chdir(projectDir);

spawnSync(process.execPath, [expoCli, 'start', ...extraArgs], {
  stdio: 'inherit',
  shell: false,
  cwd: projectDir,
  env: { ...process.env, CI: '1' },
});
