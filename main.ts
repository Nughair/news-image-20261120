// news-image-20261120 entrypoint (Node 22, standard library only).
//
// The entry image is finished and final: it is stored in this repository as
// entry.png.b64, the base64 encoding of the approved PNG. This program
// decodes that asset, validates it (PNG magic bytes, the 1 MiB gate limit),
// and writes the exact bytes to entry.png in the output directory —
// $MAKEFUN_OUTPUT_DIR, or /output inside the grader's container:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// Decoding is deterministic: every run writes byte-identical output
// (sha256 ffbfc3c317e303131530c0b12ffad19ed8ffd9b7eb66ad3ea4083cd0b1a28162).

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const MAX_BYTES = 1_048_576; // 1 MiB gate limit
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const asset = readFileSync(new URL('./entry.png.b64', import.meta.url), 'utf8');
const bytes = Buffer.from(asset.replace(/\s+/g, ''), 'base64');

if (bytes.length > MAX_BYTES) {
  throw new Error(`entry image is ${bytes.length} bytes, over the 1 MiB limit`);
}
if (!PNG_MAGIC.every((b, i) => bytes[i] === b)) {
  throw new Error('entry image does not start with the PNG magic bytes');
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'entry.png'), bytes);
