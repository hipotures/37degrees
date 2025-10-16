#!/usr/bin/env ts-node
/**
 * Collect audio titles from mcptools browser_snapshot
 *
 * Usage:
 *   npx ts-node scripts/gemini/collect-audio-snapshot.ts <workDir> <browserEndpoint>
 *
 * Output (JSON to stdout):
 *   {
 *     "notebook_url": "https://...",
 *     "audio": [
 *       {"title": "Clean Title", "ref": "e3969"}
 *     ]
 *   }
 */

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// TYPES
// ============================================================================

interface AudioItem {
  title: string;
  ref: string;
}

interface SnapshotResult {
  notebook_url: string;
  audio: AudioItem[];
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function extractAudioFromSnapshot(snapshotText: string): AudioItem[] {
  const audioItems: AudioItem[] = [];

  // Pattern: [ref=XXXX]: "Clean Title"
  // Extract everything between [ref= and ]: " to the closing quote
  const regex = /\[ref=([^\]]+)\]:\s*"([^"]+)"/g;

  let match;
  while ((match = regex.exec(snapshotText)) !== null) {
    const ref = match[1];
    const title = match[2];

    audioItems.push({
      ref,
      title
    });
  }

  return audioItems;
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function collectAudioSnapshot(workDir: string, browserEndpoint: string): Promise<SnapshotResult> {
  console.error('[1/3] Calling mcptools browser_snapshot...');

  try {
    const snapshotOutput = execSync(`~/go/bin/mcptools call browser_snapshot ${browserEndpoint}`, {
      encoding: 'utf-8',
      shell: '/bin/bash',
      timeout: 30000
    });

    console.error('  ✓ Snapshot received');

    // ========================================================================
    // PHASE 2: Extract audio items
    // ========================================================================

    console.error('[2/3] Extracting audio items from snapshot...');

    const audioItems = extractAudioFromSnapshot(snapshotOutput);

    console.error(`  ✓ Found ${audioItems.length} audio items`);

    // ========================================================================
    // PHASE 3: Format output
    // ========================================================================

    console.error('[3/3] Formatting output...');

    const result: SnapshotResult = {
      notebook_url: 'https://notebooklm.google.com',  // Placeholder, will be matched later
      audio: audioItems
    };

    console.error(`  ✓ Formatted ${audioItems.length} items`);

    return result;

  } catch (error: any) {
    throw new Error(`Failed to collect audio snapshot: ${error.message}`);
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: npx ts-node scripts/gemini/collect-audio-snapshot.ts <workDir> <browserEndpoint>');
    console.error('Example: npx ts-node scripts/gemini/collect-audio-snapshot.ts /tmp/audio-batch-XYZ http://127.0.0.1:8931/sse');
    process.exit(1);
  }

  const workDir = args[0];
  const browserEndpoint = args[1];

  console.error(`\n=== Audio Snapshot Collection (mcptools) ===`);
  console.error(`Work Dir: ${workDir}`);
  console.error(`Browser Endpoint: ${browserEndpoint}`);
  console.error('');

  try {
    const result = await collectAudioSnapshot(workDir, browserEndpoint);

    // Save to file
    const outputFilename = `snapshot-studio.json`;
    const outputPath = path.join(workDir, outputFilename);

    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2), 'utf-8');

    console.error(`  → Snapshot saved: ${outputPath}`);
    console.error('');

    // Output path for batch-download-all.sh
    console.log(outputPath);
    process.exit(0);

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { collectAudioSnapshot, AudioItem, SnapshotResult };
