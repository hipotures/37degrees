import { parse as parseYaml } from 'yaml';
import * as fs from 'fs';

interface AudioItem {
  title: string;
  ref: string;
}

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
  return label
    .replace(/''/g, "'")
    .replace(/\\"/g, '"');
}

function extractAudioItems(rawYaml: string): AudioItem[] {
  const parsed = parseYaml(rawYaml);
  const results: AudioItem[] = [];
  const seenRefs = new Set<string>();

  const GENERIC_WITH_REF_REGEX = /^generic\s+\[ref=([^\]]+)\]$/;
  const BUTTON_WITH_REF_REGEX = /^'?button\s+/;
  const audioButtonRefs = new Set<string>();

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
          const hasAudio = findInTree(value, 'audio_magic_eraser');
          if (hasAudio) {
            const refMatch = key.match(/\[ref=([^\]]+)\]/);
            if (refMatch) {
              audioButtonRefs.add(refMatch[1]);
              console.error(`✓ Audio button found: ${refMatch[1]}`);
            }
          }
        }

        findAudioButtons(value);
      }
    }
  };

  // Second pass: collect generic strings inside audio buttons
  const collectTitles = (node: unknown, insideAudioButton: boolean): void => {
    if (Array.isArray(node)) {
      for (const item of node) {
        collectTitles(item, insideAudioButton);
      }
      return;
    }

    if (node && typeof node === 'object') {
      for (const [key, value] of Object.entries(node as Record<string, unknown>)) {
        const buttonMatch = typeof key === 'string' ? key.match(BUTTON_WITH_REF_REGEX) : null;
        const refMatch = buttonMatch ? key.match(/\[ref=([^\]]+)\]/) : null;
        const isAudioButton = !!(refMatch && audioButtonRefs.has(refMatch[1]));

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

        collectTitles(value, insideAudioButton || isAudioButton);
      }
    }
  };

  findAudioButtons(parsed);
  collectTitles(parsed, false);

  return results;
}

// Test
const snapshotContent = fs.readFileSync('/tmp/snap7', 'utf-8');
const match = snapshotContent.match(/Page Snapshot:\s*```yaml\s*([\s\S]*?)```/);

if (match && match[1]) {
  console.error('\n=== First Pass: Finding audio buttons ===\n');
  const items = extractAudioItems(match[1]);
  console.error('\n=== Second Pass: Collecting titles ===\n');
  console.log(`Found ${items.length} audio items:`);
  items.forEach((item, i) => {
    console.log(`${i+1}. ${item.title} (${item.ref})`);
  });
} else {
  console.error('Could not parse YAML from snapshot');
}
