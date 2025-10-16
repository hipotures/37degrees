#!/usr/bin/env ts-node
/**
 * Quick helper to validate snapshot parsing logic.
 *
 * Usage:
 *   npx ts-node scripts/gemini/test-collect-audio-parser.ts /tmp/snap3
 */

import * as fs from 'fs';
import { parseSnapshotOutput } from './collect-audio-snapshot';

function main(): void {
  const filePath = process.argv[2];

  if (!filePath) {
    console.error('Usage: npx ts-node scripts/gemini/test-collect-audio-parser.ts <snapshot-file>');
    process.exit(1);
  }

  const snapshotText = fs.readFileSync(filePath, 'utf-8');
  const result = parseSnapshotOutput(snapshotText);

  console.log(`Notebook URL: ${result.notebook_url}`);
  console.log(`Audio items: ${result.audio.length}`);

  result.audio.forEach((item, index) => {
    console.log(`[${index + 1}] ${item.ref} :: ${item.title}`);
  });
}

main();
