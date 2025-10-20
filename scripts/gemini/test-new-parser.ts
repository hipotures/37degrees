#!/usr/bin/env ts-node
import * as fs from 'fs';
import { parse as parseYaml } from 'yaml';

const GENERIC_WITH_REF_REGEX = /^generic \[ref=([^\]]+)\]$/;
const YAML_BLOCK_REGEX = /Page Snapshot:\s*```yaml\s*([\s\S]*?)```/;

function normalizeLabel(label: string): string {
  return label.replace(/''/g, "'");
}

interface AudioItem {
  title: string;
  ref: string;
}

function extractAudioItemsFromSnapshot(rawYaml: string): AudioItem[] {
  const parsed = parseYaml(rawYaml);
  const results: AudioItem[] = [];
  const seenRefs = new Set<string>();

  const visit = (node: unknown): void => {
    if (Array.isArray(node)) {
      for (const item of node) {
        visit(item);
      }
      return;
    }

    if (node && typeof node === 'object') {
      // Check keys for generic pattern, take value as title
      for (const [key, value] of Object.entries(node as Record<string, unknown>)) {
        const genericMatch = key.match(GENERIC_WITH_REF_REGEX);
        if (genericMatch && typeof value === 'string') {
          const [, ref] = genericMatch;
          const normalizedTitle = normalizeLabel(value);

          if (normalizedTitle && !seenRefs.has(ref)) {
            seenRefs.add(ref);
            results.push({ title: normalizedTitle, ref });
          }
        }

        visit(value);
      }
    }
  };

  visit(parsed);
  return results;
}

const snapshotContent = fs.readFileSync('/tmp/snap5', 'utf-8');
const match = snapshotContent.match(YAML_BLOCK_REGEX);

if (!match || !match[1]) {
  console.error('No YAML block found');
  process.exit(1);
}

const audioItems = extractAudioItemsFromSnapshot(match[1]);
const lolitaItems = audioItems.filter(item => item.title.includes('Lolita'));

console.log('Total audio items found:', audioItems.length);
console.log('Lolita items:', JSON.stringify(lolitaItems, null, 2));

// Debug: print first few items from parsed YAML with types
const parsed = parseYaml(match[1]);
let itemCount = 0;
const visit2 = (node: unknown): void => {
  if (itemCount < 10) {
    if (typeof node === 'string') {
      console.log(`[${itemCount}] String: "${node.substring(0, 80)}"`);
      itemCount++;
    } else if (typeof node === 'object' && node !== null && !Array.isArray(node)) {
      const keys = Object.keys(node as Record<string, unknown>).slice(0, 2).join(', ');
      console.log(`[${itemCount}] Object: {${keys}}`);
      itemCount++;
    }
  }
  if (Array.isArray(node)) {
    for (const item of node) visit2(item);
  } else if (node && typeof node === 'object') {
    for (const value of Object.values(node as Record<string, unknown>)) {
      visit2(value);
    }
  }
};
visit2(parsed);
