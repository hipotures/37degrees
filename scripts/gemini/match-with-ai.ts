#!/usr/bin/env ts-node
/**
 * AI-powered matching: NotebookLM audio titles → book tasks
 *
 * Usage:
 *   npx ts-node scripts/gemini/match-with-ai.ts <tasks.json> <all_audio.json> [--model gemini|claude] [--gemini-model <model_name>] [--gemini-extra-args <args>]
 *
 * Output (JSON to stdout):
 *   {
 *     "success": true,
 *     "matches": [
 *       {
 *         "book_key": "0057_east_of_eden",
 *         "language_code": "pt",
 *         "audio_title": "A Leste do Éden...",
 *         "audio_ref": "audio-5",
 *         "notebook_url": "https://..."
 *       }
 *     ],
 *     "unmatched_tasks": [...],
 *     "model_used": "gemini"
 *   }
 */

import * as fs from 'fs';
import { execSync } from 'child_process';

// ============================================================================
// TYPES
// ============================================================================

interface Task {
  book_key: string;
  language_code: string;
  subitem_key: string;
  notebook_url: string;
}

interface AudioItem {
  title: string;
  ref: string;
  timestamp?: string;
}

interface AudioCollection {
  notebook_url: string;
  audio: AudioItem[];
}

interface Match {
  book_key: string;
  language_code: string;
  audio_title: string;
  audio_ref: string;
  notebook_url: string;
}

interface MatchResult {
  success: boolean;
  matches: Match[];
  unmatched_tasks: Task[];
  model_used?: string;
  error?: string;
}

// ============================================================================
// AI PROVIDERS
// ============================================================================

async function callGemini(
  prompt: string, 
  geminiModel: string, 
  geminiExtraArgs: string, 
  retries: number = 1
): Promise<string> {
  console.error('  → Calling Gemini API...');
  console.error(`    Model: ${geminiModel}`);

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      // Pass prompt via stdin to avoid CLI argument length limits
      const command = `gemini --model "${geminiModel}" ${geminiExtraArgs}`;
      const result = execSync(command, {
        input: prompt,
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024,  // 10MB buffer
        timeout: 60000  // 60s timeout
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
      // Using claude CLI
      const result = execSync(`claude "${prompt.replace(/"/g, '\\"')}"`, {
        encoding: 'utf-8',
        maxBuffer: 10 * 1024 * 1024,  // 10MB buffer
        timeout: 60000  // 60s timeout
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

async function callAI(
  prompt: string, 
  primaryModel: 'gemini' | 'claude' = 'gemini',
  geminiModel: string,
  geminiExtraArgs: string
): Promise<{ response: string, model: string }> {
  const fallbackModel = primaryModel === 'gemini' ? 'claude' : 'gemini';

  try {
    // Try primary model with 1 retry
    const response = primaryModel === 'gemini'
      ? await callGemini(prompt, geminiModel, geminiExtraArgs, 1)
      : await callClaude(prompt, 1);

    return { response, model: primaryModel };

  } catch (primaryError: any) {
    console.error(`  ✗ Primary model (${primaryModel}) failed: ${primaryError.message}`);
    console.error(`  → Falling back to ${fallbackModel}...`);

    try {
      // Fallback to secondary model with 1 retry
      const response = fallbackModel === 'gemini'
        ? await callGemini(prompt, geminiModel, geminiExtraArgs, 1)
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

function buildMatchingPrompt(tasks: Task[], allAudio: AudioCollection[]): string {
  // Only send minimal fields to AI (book_key + language_code)
  const minimalTasks = tasks.map(t => ({
    book_key: t.book_key,
    language_code: t.language_code
  }));

  // Only send minimal audio fields (title + ref)
  const minimalAudio = allAudio.map(collection => ({
    audio: collection.audio.map(a => ({
      title: a.title,
      ref: a.ref
    }))
  }));

  return `You are an expert at matching book titles across different languages.

TASK: Match book download tasks with audio files from NotebookLM.

RULES:
1. Each task represents a book + language that needs audio download
2. Match tasks to audio by book title + language
3. Audio titles are in the target language (e.g., "A Leste do Éden" for Portuguese)
4. Book keys are in English (e.g., "0057_east_of_eden")
5. One task can match audio from ANY notebook
6. Return ONLY valid JSON array, no additional text

TASKS (need download):
${JSON.stringify(minimalTasks, null, 2)}

AVAILABLE AUDIO (all notebooks):
${JSON.stringify(minimalAudio, null, 2)}

REQUIRED OUTPUT FORMAT:
Return ONLY a JSON array with minimal info needed for matching:
- book_key: from tasks
- language_code: from tasks
- audio_title: from audio (for verification)

Example:
[
  {"book_key": "0057_east_of_eden", "language_code": "pt", "audio_title": "A Leste do Éden..."}
]

Return [] if no matches. NO additional text or explanation.`;
}

function parseAIResponse(response: string): Match[] {
  // Try to extract JSON from response
  // AI might wrap JSON in markdown code blocks
  let jsonText = response.trim();

  // Remove markdown code blocks if present
  if (jsonText.startsWith('```json')) {
    jsonText = jsonText.replace(/^```json\n/, '').replace(/\n```$/, '');
  } else if (jsonText.startsWith('```')) {
    jsonText = jsonText.replace(/^```\n/, '').replace(/\n```$/, '');
  }

  // Parse JSON
  try {
    const matches = JSON.parse(jsonText);

    if (!Array.isArray(matches)) {
      throw new Error('AI response is not an array');
    }

    // Validate structure (minimal fields)
    for (const match of matches) {
      if (!match.book_key || !match.language_code || !match.audio_title) {
        throw new Error(`Invalid match structure: ${JSON.stringify(match)}`);
      }
    }

    return matches;

  } catch (error: any) {
    throw new Error(`Failed to parse AI response as JSON: ${error.message}\nResponse: ${jsonText.substring(0, 500)}`);
  }
}

// ============================================================================
// MAIN FUNCTION
// ============================================================================

async function matchWithAI(
  tasksPath: string,
  allAudioPath: string,
  primaryModel: 'gemini' | 'claude' = 'gemini',
  geminiModel: string,
  geminiExtraArgs: string
): Promise<MatchResult> {
  try {
    console.error('[1/4] Loading input data...');

    // Load tasks
    const tasksData = JSON.parse(fs.readFileSync(tasksPath, 'utf-8'));
    const tasks: Task[] = tasksData.data || tasksData.tasks || tasksData;

    console.error(`  → Tasks: ${tasks.length}`);

    // Load all audio collections
    const allAudioData = JSON.parse(fs.readFileSync(allAudioPath, 'utf-8'));
    const allAudio: AudioCollection[] = Array.isArray(allAudioData) ? allAudioData : [allAudioData];

    const totalAudio = allAudio.reduce((sum, collection) => sum + collection.audio.length, 0);
    console.error(`  → Audio items: ${totalAudio} (from ${allAudio.length} notebooks)`);

    // ========================================================================
    // PHASE 2: Build prompt
    // ========================================================================

    console.error('[2/4] Building AI prompt...');

    const prompt = buildMatchingPrompt(tasks, allAudio);
    console.error(`  → Prompt size: ${prompt.length} chars`);

    // Save prompt to file (for debugging/review)
    const promptPath = tasksPath.replace(/tasks\.json$/, 'prompt-phase1.txt');
    fs.writeFileSync(promptPath, prompt, 'utf-8');
    console.error(`  → Prompt saved: ${promptPath}`);

    // ========================================================================
    // PHASE 3: Call AI
    // ========================================================================

    console.error('[3/4] Calling AI...');

    const { response, model } = await callAI(prompt, primaryModel, geminiModel, geminiExtraArgs);

    console.error(`  ✓ Response received from ${model}`);
    console.error(`  → Response size: ${response.length} chars`);

    // ========================================================================
    // PHASE 4: Parse response
    // ========================================================================

    console.error('[4/4] Parsing response...');

    const rawMatches = parseAIResponse(response);

    console.error(`  ✓ Found ${rawMatches.length} matches`);

    // Enrich matches with notebook_url from tasks
    const taskMap = new Map(tasks.map(t => [`${t.book_key}_${t.language_code}`, t]));

    const enrichedMatches = rawMatches.map(match => {
      const taskKey = `${match.book_key}_${match.language_code}`;
      const task = taskMap.get(taskKey);

      return {
        ...match,
        audio_ref: 'matched',  // Placeholder, not used in download
        notebook_url: task?.notebook_url || ''
      };
    });

    // Find unmatched tasks
    const matchedBookKeys = new Set(rawMatches.map(m => `${m.book_key}_${m.language_code}`));
    const unmatchedTasks = tasks.filter(t => !matchedBookKeys.has(`${t.book_key}_${t.language_code}`));

    if (unmatchedTasks.length > 0) {
      console.error(`  ⚠ Unmatched tasks: ${unmatchedTasks.length}`);
    }

    return {
      success: true,
      matches: enrichedMatches,
      unmatched_tasks: unmatchedTasks,
      model_used: model
    };

  } catch (error: any) {
    console.error(`✗ Error: ${error.message}`);

    return {
      success: false,
      matches: [],
      unmatched_tasks: [],
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
    console.error('Usage: npx ts-node scripts/gemini/match-with-ai.ts <tasks.json> <all_audio.json> [--model gemini|claude] [--gemini-model <model_name>] [--gemini-extra-args <args>]');
    console.error('Example: npx ts-node scripts/gemini/match-with-ai.ts /tmp/tasks.json /tmp/all_audio.json --gemini-model gemini-2.5-flash');
    process.exit(1);
  }

  const tasksPath = args[0];
  const allAudioPath = args[1];

  const argValue = (argName: string, defaultValue: string): string => {
    const index = args.indexOf(argName);
    return index !== -1 && args[index + 1] ? args[index + 1] : defaultValue;
  };

  const primaryModel = argValue('--model', 'gemini') as 'gemini' | 'claude';
  const geminiModel = argValue('--gemini-model', 'gemini-2.5-flash');
  const geminiExtraArgs = argValue('--gemini-extra-args', '--yolo --allowed-tools playwright-cdp,todoit');

  console.error(`\n=== AI Matching: Audio Titles → Tasks ===`);
  console.error(`Tasks: ${tasksPath}`);
  console.error(`Audio: ${allAudioPath}`);
  console.error(`Primary model: ${primaryModel}`);
  if (primaryModel === 'gemini') {
    console.error(`Gemini Model: ${geminiModel}`);
  }
  console.error('');

  const result = await matchWithAI(tasksPath, allAudioPath, primaryModel, geminiModel, geminiExtraArgs);

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

export { matchWithAI, Match, MatchResult };
