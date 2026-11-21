// news-image-20261120 entrypoint (Node 22, standard library only).
//
// The entry image is rendered, not stored as data: generate_drafts.py —
// the Python (Pillow) broadsheet generator whose final revision produced
// the approved front page — is bundled in this repository, and this
// program builds the entry from it. It copies the generator into a
// scratch directory, runs its `final` stage there, validates the render
// (PNG magic bytes, the 1 MiB gate limit, the approved sha256), and
// writes it to entry.png in the output directory — $MAKEFUN_OUTPUT_DIR
// when set, else /output where that directory exists (the grader's
// container), else ./ beside this file:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// The render is deterministic: every run writes byte-identical output
// (165,561 bytes, sha256
// ffbfc3c317e303131530c0b12ffad19ed8ffd9b7eb66ad3ea4083cd0b1a28162),
// the same entry.png committed beside this file. Requires python3 with
// Pillow on PATH; the build fails loudly if either is missing.

import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const MAX_BYTES = 1_048_576; // 1 MiB gate limit
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
const EXPECTED_SHA256 =
  'ffbfc3c317e303131530c0b12ffad19ed8ffd9b7eb66ad3ea4083cd0b1a28162';

const here = dirname(fileURLToPath(import.meta.url));
const generator = join(here, 'generate_drafts.py');
if (!existsSync(generator)) {
  throw new Error(`generator not found beside main.ts: ${generator}`);
}

const work = mkdtempSync(join(tmpdir(), 'news-image-20261120-'));
try {
  copyFileSync(generator, join(work, 'generate_drafts.py'));

  const run = spawnSync('python3', ['generate_drafts.py', 'final'], {
    cwd: work,
    stdio: 'inherit',
  });
  if (run.error) {
    throw new Error(
      `could not start python3 (is it installed, with Pillow?): ${run.error.message}`,
    );
  }
  if (run.status !== 0) {
    throw new Error(
      `generate_drafts.py final failed (status ${run.status}, signal ${run.signal ?? 'none'})`,
    );
  }

  const rendered = join(work, 'output', 'entry.png');
  if (!existsSync(rendered)) {
    throw new Error(`generator ran but produced no output/entry.png in ${work}`);
  }
  const bytes = readFileSync(rendered);

  if (bytes.length > MAX_BYTES) {
    throw new Error(`entry image is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  if (!PNG_MAGIC.every((b, i) => bytes[i] === b)) {
    throw new Error('rendered image does not start with the PNG magic bytes');
  }
  const sha256 = createHash('sha256').update(bytes).digest('hex');
  if (sha256 !== EXPECTED_SHA256) {
    throw new Error(
      `rendered image sha256 ${sha256} does not match the approved entry ${EXPECTED_SHA256}`,
    );
  }

  const outDir =
    process.env.MAKEFUN_OUTPUT_DIR ?? (existsSync('/output') ? '/output' : here);
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, 'entry.png'), bytes);
} finally {
  rmSync(work, { recursive: true, force: true });
}
