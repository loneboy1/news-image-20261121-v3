// THE WORLD LEDGER — Saturday, November 21, 2026.
// Entrypoint for make.fun news-image-20261121 (v3 rebuild from scratch).
//
// The front page is drawn by build/draw_frontpage_v3.py (PIL) and shipped
// as entry.png. This program only validates that image against the
// competition's gate and copies it to the output directory, byte for byte.
// A plain copy is deterministic: both grader runs write identical bytes,
// and the SHA-256 printed here is the fingerprint that proves it.
//
// Usage:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1048576; // 1 MiB
const MAX_DIM = 1024;

function fail(message: string): never {
  throw new Error(`entry rejected: ${message}`);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const src = join(here, "entry.png");
  if (!existsSync(src)) fail("entry.png is missing from the repository root");

  const buf = readFileSync(src);
  if (buf.length === 0) fail("entry.png is empty");
  if (buf.length > MAX_BYTES) {
    fail(`entry.png is ${buf.length} bytes, over the 1 MiB cap`);
  }

  // Identify the format from its first bytes (the file is named entry.png
  // either way): JPEG starts FF D8 FF, PNG starts 89 50 4E 47.
  const isJpeg = buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
  const isPng =
    buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
  if (!isJpeg && !isPng) fail("entry.png is neither a JPEG nor a PNG");

  // Measure the image from its header so a file over 1024x1024 is refused
  // before it is copied. PNG: width/height are the first 8 bytes of IHDR.
  // JPEG: scan segments for a Start-Of-Frame marker (C0-C3, C5-C7, C9-CB,
  // CD-CF) whose payload holds height then width as 16-bit big-endian.
  let width = 0;
  let height = 0;
  if (isPng) {
    width = buf.readUInt32BE(16);
    height = buf.readUInt32BE(20);
  } else {
    let off = 2;
    while (off + 9 <= buf.length) {
      if (buf[off] !== 0xff) fail("entry.png has a corrupt JPEG segment");
      const marker = buf[off + 1];
      if (marker === 0xd8 || marker === 0xd9 || (marker >= 0xd0 && marker <= 0xd7)) {
        off += 2;
        continue;
      }
      const len = buf.readUInt16BE(off + 2);
      if (len < 2 || off + 2 + len > buf.length) fail("entry.png has a corrupt JPEG segment");
      const isSof =
        (marker >= 0xc0 && marker <= 0xc3) ||
        (marker >= 0xc5 && marker <= 0xc7) ||
        (marker >= 0xc9 && marker <= 0xcb) ||
        (marker >= 0xcd && marker <= 0xcf);
      if (isSof) {
        height = buf.readUInt16BE(off + 5);
        width = buf.readUInt16BE(off + 7);
        break;
      }
      off += 2 + len;
    }
    if (width === 0 || height === 0) fail("entry.png has no JPEG frame to measure");
  }
  if (width > MAX_DIM || height > MAX_DIM) {
    fail(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  copyFileSync(src, dest);
  // Prove the copy is byte-identical, not just the same size: hash both
  // files and refuse to report success unless the digests agree.
  const srcHash = createHash("sha256").update(buf).digest("hex");
  const dstHash = createHash("sha256").update(readFileSync(dest)).digest("hex");
  if (srcHash !== dstHash) fail("copied entry.png does not match the source");
  const written = statSync(dest).size;
  if (written !== buf.length) fail("copied entry.png does not match the source");
  console.log(`entry.png: ${width}x${height}, ${buf.length} bytes, sha256 ${srcHash} -> ${dest}`);
}

main();
