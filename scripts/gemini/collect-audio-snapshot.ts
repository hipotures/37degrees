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
import { parse as parseYaml } from 'yaml';

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

const YAML_BLOCK_REGEX = /Page Snapshot:\s*```yaml\s*([\s\S]*?)```/;
const PAGE_URL_REGEX = /Page URL:\s*(\S+)/;
const GENERIC_WITH_REF_REGEX = /^generic \[ref=([^\]]+)\]$/;

function cleanLabelText(label: string): string {
  const markers = [
    ' Deep dive',
    ' Interactive mode',
    ' Q&A',
    ' Playlist',
    ' Play More',
    ' Play'
  ];

  let cleaned = label;

  for (const marker of markers) {
    const index = cleaned.indexOf(marker);
    if (index !== -1) {
      cleaned = cleaned.slice(0, index);
    }
  }

  return cleaned.trim();
}

function normalizeLabel(label: string): string {
  // YAML single-quote escaping uses double apostrophes.
  // JSON escaped quotes also need to be unescaped.
  return label
    .replace(/''/g, "'")      // YAML: '' → '
    .replace(/\\"/g, '"');    // JSON: \" → "
}

function extractAudioItemsFromSnapshot(rawYaml: string): AudioItem[] {
  const parsed = parseYaml(rawYaml);
  const results: AudioItem[] = [];
  const seenRefs = new Set<string>();

  // Regex to match button elements with audio
  const BUTTON_WITH_REF_REGEX = /^'?button\s+/;

  // Track which refs belong to audio buttons
  const audioButtonRefs = new Set<string>();

  // First pass: find all button refs that contain audio_magic_eraser
  const findAudioButtons = (node: unknown): void => {
    if (Array.isArray(node)) {
      for (const item of node) {
        findAudioButtons(item);
      }
      return;
    }

    if (node && typeof node === 'object') {
      for (const [key, value] of Object.entries(node as Record<string, unknown>)) {
        const buttonMatch = typeof key === 'string' ? key.match(BUTTON_WITH_REF_REGEX) : null;

        if (buttonMatch) {
          // Check if this button contains audio_magic_eraser
          const hasAudio = findInTree(value, 'audio_magic_eraser');
          if (hasAudio) {
            // Extract ref from button
            const refMatch = key.match(/\[ref=([^\]]+)\]/);
            if (refMatch) {
              audioButtonRefs.add(refMatch[1]);
            }
          }
        }

        findAudioButtons(value);
      }
    }
  };

  // Helper to search for text in tree
  const findInTree = (node: unknown, search: string): boolean => {
    if (typeof node === 'string') {
      return node.includes(search);
    }
    if (Array.isArray(node)) {
      return node.some(item => findInTree(item, search));
    }
    if (node && typeof node === 'object') {
      return Object.entries(node as Record<string, unknown>).some(([key, value]) => {
        return key.includes(search) || findInTree(value, search);
      });
    }
    return false;
  };

  // Second pass: collect generic strings that are inside audio buttons
  const collectTitles = (node: unknown, insideAudioButton: boolean): void => {
    if (Array.isArray(node)) {
      for (const item of node) {
        collectTitles(item, insideAudioButton);
      }
      return;
    }

    if (node && typeof node === 'object') {
      for (const [key, value] of Object.entries(node as Record<string, unknown>)) {
        // Check if we're entering an audio button
        const buttonMatch = typeof key === 'string' ? key.match(BUTTON_WITH_REF_REGEX) : null;
        const refMatch = buttonMatch ? key.match(/\[ref=([^\]]+)\]/) : null;
        const isAudioButton = !!(refMatch && audioButtonRefs.has(refMatch[1]));

        // Check if this is a generic [ref=...] with string value
        const genericMatch = typeof key === 'string' ? key.match(GENERIC_WITH_REF_REGEX) : null;

        if (genericMatch && typeof value === 'string' && (insideAudioButton || isAudioButton)) {
          const [, ref] = genericMatch;
          const titleText = value.trim();

          // Filter: not metadata (source/ago), has minimum length
          const isNotMetadata = !titleText.includes('source') && !titleText.includes('ago');
          const hasMinLength = titleText.length > 30; // Audio deepdive titles are long

          if (isNotMetadata && hasMinLength && !seenRefs.has(ref)) {
            seenRefs.add(ref);
            const normalizedTitle = normalizeLabel(titleText);
            results.push({ title: normalizedTitle, ref });
          }
        }

        // Recurse deeper (inside audio button if we found one)
        collectTitles(value, insideAudioButton || !!isAudioButton);
      }
    }
  };

  findAudioButtons(parsed);
  collectTitles(parsed, false);

  return results;
}

function parseNotebookUrl(snapshotOutput: string): string {
  const urlMatch = snapshotOutput.match(PAGE_URL_REGEX);
  if (urlMatch && urlMatch[1]) {
    return urlMatch[1];
  }
  return 'https://notebooklm.google.com';
}

function parseSnapshotOutput(snapshotOutput: string): SnapshotResult {
  const match = snapshotOutput.match(YAML_BLOCK_REGEX);

  if (!match || !match[1]) {
    throw new Error('Unable to locate YAML page snapshot block');
  }

  const audioItems = extractAudioItemsFromSnapshot(match[1]);
  const notebookUrl = parseNotebookUrl(snapshotOutput);

  return {
    notebook_url: notebookUrl,
    audio: audioItems
  };
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

    const parsedResult = parseSnapshotOutput(snapshotOutput);

    console.error(`  ✓ Found ${parsedResult.audio.length} audio items`);

    // ========================================================================
    // PHASE 3: Format output
    // ========================================================================

    console.error('[3/3] Formatting output...');

    const result: SnapshotResult = parsedResult;

    console.error(`  ✓ Formatted ${parsedResult.audio.length} items`);

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

export {
  collectAudioSnapshot,
  AudioItem,
  SnapshotResult,
  parseSnapshotOutput
};
