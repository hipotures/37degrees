/**
 * AFA Prompt Assembler - Combines 17 specialized agents into single research prompt
 *
 * This module reads agent definitions from .claude/agents/ and extracts:
 * - Primary Tasks
 * - Search Focus Areas
 * - Output Requirements
 * - Notes
 *
 * Then assembles them into a cohesive Deep Research prompt for Gemini.
 */

import * as fs from 'fs';
import * as path from 'path';
import { parse as parseYaml } from 'yaml';

// ============================================================================
// TYPES
// ============================================================================

interface AgentSection {
  name: string;
  primaryTasks: string[];
  searchFocus: string[];
  outputRequirements: string[];
  notes: string[];
}

interface BookInfo {
  title: string;
  author: string;
  year?: number;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  projectRoot: '/home/xai/DEV/37degrees',
  agentsDir: '.claude/agents',

  // 8 specialized agents (in order of appearance in prompt)
  specializedAgents: [
    { key: 'culture-impact-researcher', title: 'Culture Impact Research' },
    { key: 'youth-digital-connector', title: 'Youth Digital Connection' },
    { key: 'symbols-meaning-analyst', title: 'Symbols & Meaning Analysis' },
    { key: 'facts-history-specialist', title: 'Facts & History' },
    { key: 'reality-wisdom-checker', title: 'Reality & Wisdom' },
    { key: 'dark-drama-investigator', title: 'Dark Drama Investigation' },
    { key: 'writing-innovation-expert', title: 'Writing Innovation' },
    { key: 'content-warning-assessor', title: 'Content Warning Assessment' }
  ],

  // 9 language contexts (in order of appearance in prompt)
  languageAgents: [
    { key: 'pl', title: 'Polish Context (pl)' },
    { key: 'en', title: 'English Context (en)' },
    { key: 'de', title: 'German Context (de)' },
    { key: 'fr', title: 'French Context (fr)' },
    { key: 'es', title: 'Spanish Context (es)' },
    { key: 'pt', title: 'Portuguese Context (pt)' },
    { key: 'ja', title: 'Japanese Context (ja)' },
    { key: 'ko', title: 'Korean Context (ko)' },
    { key: 'hi', title: 'Hindi Context (hi)' }
  ]
};

// ============================================================================
// CORE FUNCTIONS
// ============================================================================

/**
 * Read book.yaml and extract title/author/year
 */
function readBookInfo(sourceName: string): BookInfo {
  const bookYamlPath = path.join(CONFIG.projectRoot, 'books', sourceName, 'book.yaml');

  if (!fs.existsSync(bookYamlPath)) {
    throw new Error(`book.yaml not found: ${bookYamlPath}`);
  }

  const yamlContent = fs.readFileSync(bookYamlPath, 'utf-8');
  const bookData = parseYaml(yamlContent) as any;

  // Read from book_info section
  const bookInfo = bookData.book_info || bookData;

  const title = bookInfo.title || bookInfo.title_pl || 'Unknown';
  const author = bookInfo.author || 'Unknown';
  const year = bookInfo.year || undefined;

  return { title, author, year };
}

/**
 * Parse agent markdown file and extract sections
 */
function parseAgentFile(filePath: string, displayTitle: string): AgentSection {
  if (!fs.existsSync(filePath)) {
    console.error(`  ⚠ Agent file not found: ${filePath}`);
    return {
      name: displayTitle,
      primaryTasks: [],
      searchFocus: [],
      outputRequirements: [],
      notes: []
    };
  }

  const content = fs.readFileSync(filePath, 'utf-8');

  return {
    name: displayTitle,
    primaryTasks: extractSection(content, '## Primary Tasks'),
    searchFocus: extractSection(content, '## Search Focus Areas'),
    outputRequirements: extractSection(content, '## Output Requirements'),
    notes: extractSection(content, '## Notes')
  };
}

/**
 * Extract section content between headers
 * Returns array of lines (preserving markdown formatting)
 */
function extractSection(content: string, header: string): string[] {
  // Match section from header to next ## or end of file
  const headerEscaped = header.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`${headerEscaped}\\s*\\n([\\s\\S]*?)(?=\\n## |$)`, 'i');
  const match = content.match(regex);

  if (!match) return [];

  // Split by newlines, trim, filter empty lines and lines with variables
  return match[1]
    .split('\n')
    .map(line => line.trimEnd())
    .filter(line => line.length > 0)
    .filter(line => !line.includes('$CLAUDE_PROJECT_DIR'))
    .filter(line => !line.includes('[BOOK_FOLDER]'));
}

/**
 * Format agent section as markdown
 */
function formatSection(section: AgentSection): string {
  let output = `### ${section.name}\n\n`;

  if (section.primaryTasks.length > 0) {
    output += `**Primary Tasks:**\n`;
    output += section.primaryTasks.join('\n') + '\n\n';
  }

  if (section.searchFocus.length > 0) {
    output += `**Search Focus Areas:**\n`;
    output += section.searchFocus.join('\n') + '\n\n';
  }

  if (section.outputRequirements.length > 0) {
    output += `**Output Requirements:**\n`;
    output += section.outputRequirements.join('\n') + '\n\n';
  }

  if (section.notes.length > 0) {
    output += `**Notes:**\n`;
    output += section.notes.join('\n') + '\n\n';
  }

  return output;
}

/**
 * Build complete AFA prompt from all sections
 */
function buildPrompt(
  bookInfo: BookInfo,
  specializedSections: AgentSection[],
  languageSections: AgentSection[]
): string {
  let prompt = `# Deep Research - Comprehensive Book Analysis\n\n`;

  // Book Information
  prompt += `## Book Information\n`;
  prompt += `title: ${bookInfo.title}\n`;
  prompt += `author: ${bookInfo.author}\n`;
  prompt += `year: ${bookInfo.year || 'Unknown'}\n\n`;

  // Specialized Topics
  prompt += `## Research Agents - Specialized Topics\n\n`;
  for (const section of specializedSections) {
    prompt += formatSection(section);
  }

  // Language Contexts
  prompt += `## Research Agents - Language Contexts\n\n`;
  for (const section of languageSections) {
    prompt += formatSection(section);
  }

  // Final Instructions
  prompt += `## Final Instructions\n`;
  prompt += `Generate comprehensive research covering all above areas.\n`;
  prompt += `Focus on factual, specific, verifiable information.\n`;
  prompt += `Each language context should have unique insights for that culture.\n`;

  return prompt;
}

/**
 * Main function: Assemble AFA prompt for a book
 */
export async function assembleAFAPrompt(sourceName: string, bookInfo?: BookInfo): Promise<string> {
  console.error('  → Parsing specialized agents...');

  // Parse specialized agents
  const specializedSections: AgentSection[] = CONFIG.specializedAgents.map(agent => {
    const agentPath = path.join(
      CONFIG.projectRoot,
      CONFIG.agentsDir,
      `37d-au-${agent.key}.md`
    );
    return parseAgentFile(agentPath, agent.title);
  });

  console.error('  → Parsing language agents...');

  // Parse language agents
  const languageSections: AgentSection[] = CONFIG.languageAgents.map(agent => {
    const agentPath = path.join(
      CONFIG.projectRoot,
      CONFIG.agentsDir,
      `37d-au-local-${agent.key}-context-specialist.md`
    );
    return parseAgentFile(agentPath, agent.title);
  });

  // Read book info if not provided
  if (!bookInfo) {
    bookInfo = readBookInfo(sourceName);
  }

  // Build final prompt
  const prompt = buildPrompt(bookInfo, specializedSections, languageSections);

  return prompt;
}

// ============================================================================
// CLI INTERFACE (for standalone testing)
// ============================================================================

if (require.main === module) {
  const sourceName = process.argv[2];

  if (!sourceName) {
    console.error('Usage: npx ts-node assemble-afa-prompt.ts <sourceName>');
    console.error('Example: npx ts-node assemble-afa-prompt.ts 0055_of_mice_and_men');
    process.exit(1);
  }

  assembleAFAPrompt(sourceName)
    .then(prompt => {
      console.log(prompt);
      console.error(`\n✓ Generated prompt: ${prompt.length} characters`);
    })
    .catch(error => {
      console.error(`✗ Error: ${error.message}`);
      process.exit(1);
    });
}
