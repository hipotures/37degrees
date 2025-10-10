#!/usr/bin/env ts-node
/**
 * AI-powered matching: Downloaded files → book tasks (by timestamp)
 *
 * Usage:
 *   npx ts-node scripts/gemini/match-files-ai.ts <downloads.json> <matching.json> [--model gemini|claude]
 *
 * Output (JSON to stdout):
 *   {
 *     "success": true,
 *     "mappings": [
 *       {
 *         "source_file": "/tmp/.../NotebookLM_audio_123.mp4",
 *         "book_key": "0057_east_of_eden",
 *         "language_code": "pt",
 *         "target_path": "books/0057_east_of_eden/audio/0057_east_of_eden_pt.mp4"
 *       }
 *     ],
 *     "model_used": "gemini"
 *   }
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// ============================================================================
// TYPES
// ============================================================================

interface DownloadRecord {
  success: boolean;
  book_key: string;
  language_code: string;
  file_path?: string;
  timestamp_before?: number;
  timestamp_after?: number;
  error?: string;
}

interface Match {
  book_key: string;
  language_code: string;
  audio_title: string;
  audio_ref: string;
  notebook_url: string;
}

interface FileMapping {
  source_file: string;
  book_key: string;
  language_code: string;
  target_path: string;
}

interface MappingResult {
  success: boolean;
  mappings: FileMapping[];
  model_used?: string;
  error?: string;
}

// ============================================================================
// AI PROVIDERS (same as match-with-ai.ts)
// ============================================================================

async function callGemini(prompt: string, retries: number = 1): Promise<string> {
  console.error('  → Calling Gemini API...');

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const result = execSync(`gemini "${prompt.replace(/"/g, '\\"')}"`, {
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024,
        timeout: 60000
      });

      return result.trim();

    } catch (error: any) {
      console.error(`  ⚠ Gemini attempt ${attempt}/${retries} failed: ${error.message}`);

      if (attempt < retries) {
        console.error('  ⏳ Retrying after 3s...');
        await new Promise(resolve => setTimeout(resolve, 3000));
      } else {
        throw new Error(`Gemini failed after ${retries} attempts: ${error.message}`);
      }
    }
  }

  throw new Error('Gemini: All attempts exhausted');
}

async function callClaude(prompt: string, retries: number = 1): Promise<string> {
  console.error('  → Calling Claude API...');

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const result = execSync(`claude "${prompt.replace(/"/g, '\\"')}"`, {
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024,
        timeout: 60000
      });

      return result.trim();

    } catch (error: any) {
      console.error(`  ⚠ Claude attempt ${attempt}/${retries} failed: ${error.message}`);

      if (attempt < retries) {
        console.error('  ⏳ Retrying after 3s...');
        await new Promise(resolve => setTimeout(resolve, 3000));
      } else {
        throw new Error(`Claude failed after ${retries} attempts: ${error.message}`);
      }
    }
  }

  throw new Error('Claude: All attempts exhausted');
}

async function callAI(prompt: string, primaryModel: 'gemini' | 'claude' = 'gemini'): Promise<{ response: string, model: string }> {
  const fallbackModel = primaryModel === 'gemini' ? 'claude' : 'gemini';

  try {
    const response = primaryModel === 'gemini'
      ? await callGemini(prompt, 1)
      : await callClaude(prompt, 1);

    return { response, model: primaryModel };

  } catch (primaryError: any) {
    console.error(`  ✗ Primary model (${primaryModel}) failed: ${primaryError.message}`);
    console.error(`  → Falling back to ${fallbackModel}...`);

    try {
      const response = fallbackModel === 'gemini'
        ? await callGemini(prompt, 1)
        : await callClaude(prompt, 1);

      return { response, model: fallbackModel };

    } catch (fallbackError: any) {
      throw new Error(`Both models failed. ${primaryModel}: ${primaryError.message}, ${fallbackModel}: ${fallbackError.message}`);
    }
  }
}

// ============================================================================
// MATCHING LOGIC
// ============================================================================

function buildFileMappingPrompt(downloads: DownloadRecord[], matches: Match[]): string {
  // Add download order to records
  const downloadsWithOrder = downloads
    .filter(d => d.success && d.file_path)
    .map((d, index) => ({
      ...d,
      download_order: index + 1,
      filename: path.basename(d.file_path!)
    }));

  const matchesWithOrder = matches.map((m, index) => ({
    ...m,
    expected_order: index + 1
  }));

  return `You are an expert at matching downloaded files with expected tasks.

TASK: Match downloaded audio files with book tasks using timestamp proximity and download order.

RULES:
1. Files are downloaded in the same order as tasks (download_order ≈ expected_order)
2. Match by timestamp proximity (file downloaded ~same time as task)
3. Files can be .mp4 or .m4a extensions
4. Each file should match exactly ONE task
5. Return ONLY valid JSON array, no additional text

DOWNLOADED FILES (with timestamps):
${JSON.stringify(downloadsWithOrder, null, 2)}

EXPECTED TASKS (with order):
${JSON.stringify(matchesWithOrder, null, 2)}

REQUIRED OUTPUT FORMAT:
Return ONLY a JSON array with minimal mapping info:
- source_file: full path from downloads
- book_key: from tasks
- language_code: from tasks

Example:
[
  {"source_file": "/tmp/playwright-mcp-output/NotebookLM_audio_123.mp4", "book_key": "0057_east_of_eden", "language_code": "pt"}
]

Return [] if no matches. NO additional text.`;
}

function parseAIResponse(response: string): FileMapping[] {
  let jsonText = response.trim();

  // Remove markdown code blocks if present
  if (jsonText.startsWith('```json')) {
    jsonText = jsonText.replace(/^```json\n/, '').replace(/\n```$/, '');
  } else if (jsonText.startsWith('```')) {
    jsonText = jsonText.replace(/^```\n/, '').replace(/\n```$/, '');
  }

  try {
    const mappings = JSON.parse(jsonText);

    if (!Array.isArray(mappings)) {
      throw new Error('AI response is not an array');
    }

    // Validate structure (minimal fields)
    for (const mapping of mappings) {
      if (!mapping.source_file || !mapping.book_key || !mapping.language_code) {
        throw new Error(`Invalid mapping structure: ${JSON.stringify(mapping)}`);
      }
    }

    return mappings;

  } catch (error: any) {
    throw new Error(`Failed to parse AI response as JSON: ${error.message}\nResponse: ${jsonText.substring(0, 500)}`);
  }
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function matchFilesWithAI(
  downloadsPath: string,
  matchingPath: string,
  primaryModel: 'gemini' | 'claude' = 'gemini'
): Promise<MappingResult> {
  try {
    console.error('[1/4] Loading input data...');

    // Load downloads
    const downloads: DownloadRecord[] = JSON.parse(fs.readFileSync(downloadsPath, 'utf-8'));
    const successfulDownloads = downloads.filter(d => d.success && d.file_path);

    console.error(`  → Downloads: ${successfulDownloads.length} successful (${downloads.length} total)`);

    // Load matches
    const matchingData = JSON.parse(fs.readFileSync(matchingPath, 'utf-8'));
    const matches: Match[] = matchingData.matches || matchingData;

    console.error(`  → Expected matches: ${matches.length}`);

    if (successfulDownloads.length === 0) {
      throw new Error('No successful downloads to match');
    }

    if (matches.length === 0) {
      throw new Error('No matches to map files to');
    }

    // ========================================================================
    // PHASE 2: Build prompt
    // ========================================================================

    console.error('[2/4] Building AI prompt...');

    const prompt = buildFileMappingPrompt(downloads, matches);
    console.error(`  → Prompt size: ${prompt.length} chars`);

    // Save prompt to file (for debugging/review)
    const promptPath = downloadsPath.replace(/downloads\.json$/, 'prompt-phase3.txt');
    fs.writeFileSync(promptPath, prompt, 'utf-8');
    console.error(`  → Prompt saved: ${promptPath}`);

    // ========================================================================
    // PHASE 3: Call AI
    // ========================================================================

    console.error('[3/4] Calling AI...');

    const { response, model } = await callAI(prompt, primaryModel);

    console.error(`  ✓ Response received from ${model}`);
    console.error(`  → Response size: ${response.length} chars`);

    // ========================================================================
    // PHASE 4: Parse response
    // ========================================================================

    console.error('[4/4] Parsing response...');

    const rawMappings = parseAIResponse(response);

    console.error(`  ✓ Found ${rawMappings.length} file mappings`);

    // Enrich mappings with target_path
    const enrichedMappings = rawMappings.map(mapping => {
      const ext = path.extname(mapping.source_file);
      const targetPath = `books/${mapping.book_key}/audio/${mapping.book_key}_${mapping.language_code}${ext}`;

      return {
        ...mapping,
        target_path: targetPath
      };
    });

    return {
      success: true,
      mappings: enrichedMappings,
      model_used: model
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    return {
      success: false,
      mappings: [],
      error: error.message
    };
  }
}

// ============================================================================
// CLI ENTRY POINT
// ============================================================================

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: npx ts-node scripts/gemini/match-files-ai.ts <downloads.json> <matching.json> [--model gemini|claude]');
    console.error('Example: npx ts-node scripts/gemini/match-files-ai.ts /tmp/downloads.json /tmp/matching.json');
    console.error('Example: npx ts-node scripts/gemini/match-files-ai.ts /tmp/downloads.json /tmp/matching.json --model claude');
    process.exit(1);
  }

  const downloadsPath = args[0];
  const matchingPath = args[1];

  let primaryModel: 'gemini' | 'claude' = 'gemini';
  const modelFlagIndex = args.indexOf('--model');
  if (modelFlagIndex !== -1 && args[modelFlagIndex + 1]) {
    const modelArg = args[modelFlagIndex + 1];
    if (modelArg === 'claude' || modelArg === 'gemini') {
      primaryModel = modelArg;
    }
  }

  console.error(`\n=== AI Matching: Files → Tasks ===`);
  console.error(`Downloads: ${downloadsPath}`);
  console.error(`Matches: ${matchingPath}`);
  console.error(`Primary model: ${primaryModel}`);
  console.error('');

  const result = await matchFilesWithAI(downloadsPath, matchingPath, primaryModel);

  // Output JSON to stdout
  console.log(JSON.stringify(result, null, 2));

  process.exit(result.success ? 0 : 1);
}

if (require.main === module) {
  main().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { matchFilesWithAI, FileMapping, MappingResult };
