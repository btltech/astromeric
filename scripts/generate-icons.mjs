/**
 * Generate PWA icons from the favicon SVG
 * Run: node scripts/generate-icons.mjs
 */
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SIZES = [72, 96, 128, 144, 152, 192, 384, 512];
const SVG_PATH = path.join(__dirname, '../public/favicon.svg');
const OUTPUT_DIR = path.join(__dirname, '../public/icons');

async function generateIcons() {
  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Read the SVG file
  const svgBuffer = fs.readFileSync(SVG_PATH);

  console.log('Generating PWA icons...');

  for (const size of SIZES) {
    const outputPath = path.join(OUTPUT_DIR, `icon-${size}x${size}.png`);

    await sharp(svgBuffer).resize(size, size).png().toFile(outputPath);

    console.log(`  ✓ Generated ${size}x${size}`);
  }

  // Also generate special icons for shortcuts
  const shortcutIcons = ['daily', 'compatibility'];
  for (const name of shortcutIcons) {
    const outputPath = path.join(OUTPUT_DIR, `${name}-96x96.png`);

    await sharp(svgBuffer).resize(96, 96).png().toFile(outputPath);

    console.log(`  ✓ Generated ${name}-96x96`);
  }

  console.log('\n✅ All icons generated successfully!');
}

generateIcons().catch(console.error);
