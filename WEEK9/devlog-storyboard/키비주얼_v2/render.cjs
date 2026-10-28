// Deterministic SVG rasterization using the bundled libvips/librsvg runtime.
const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/yu505/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const scenes = JSON.parse(fs.readFileSync(path.join(__dirname, 'scenes.json'), 'utf8'));
(async () => {
  for (const s of scenes) {
    const input = path.join(__dirname, s.id + '.svg');
    await sharp(input, { density: 72 }).resize(1920, 1080).png().toFile(path.join(__dirname, s.id + '.png'));
  }
  console.log(`Rendered ${scenes.length} PNGs at 1920x1080.`);
})().catch(err => { console.error(err); process.exitCode = 1; });
