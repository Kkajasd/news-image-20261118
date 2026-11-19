// news-image-20261118 — "The World Today", a newspaper front page
// summing up Wednesday 18 November 2026 in one image.
//
// The entry is the image this repository holds (entry.png, drawn by
// tools/draw_frontpage.py from the day's verified news). This program
// copies it to the output directory, checking first that it is a PNG
// of at most 1 MiB and 1024 by 1024 pixels, so the two graded runs
// write identical bytes.
//
// Run it locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const OUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const SRC = new URL('./entry.png', import.meta.url);

const bytes = readFileSync(SRC);

// A PNG starts with these eight magic bytes.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error('entry.png is not a PNG file');
}
if (bytes.length > 1024 * 1024) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
}
// The IHDR chunk holds the width and height as big-endian uint32s.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024 cap`);
}

mkdirSync(OUT_DIR, { recursive: true });
const DEST = join(OUT_DIR, 'entry.png');
copyFileSync(SRC, DEST);

// Read the copy back and confirm it is the same image, byte for byte.
const written = readFileSync(DEST);
if (!written.equals(bytes)) {
  throw new Error('entry.png did not copy cleanly');
}
console.log(`wrote ${DEST}: ${width}x${height} PNG, ${bytes.length} bytes`);
