# AFA Format Selection Guidelines (GPT Edition)

Purpose: Provide precise, evidence-driven rules for selecting ONE of 8 dialogue formats per book, aligned with the DEPTH×HEAT framework and available research in books/*/docs/findings. This complements, not replaces, docs/AFA_FORMAT_SELECTION_GUIDELINES.md by adding actionable signals, anti-signals, thresholds, and balancers based on current usage statistics.

Scope: For the AFA selector agent and contributors. English-only documentation.

---

## Context And Goals

- Current usage (36 books):
  - Overused: `academic_analysis` (25%)
  - Underused: `exploratory_dialogue` (0%), `narrative_reconstruction` (0%)
  - Goal: Maintain fit-first selection while gently correcting bias toward more accessible formats when appropriate.
- Inputs available to the selector:
  - Book metadata in `book.yaml` (title, author, year, genre)
  - Research files in `docs/findings` (e.g., `au-research_*`, `review.txt`)
  - Eight behavioral scores → composites: DEPTH, HEAT
  - Format usage statistics
- Audience: Polish youth on TikTok (clarity, energy, authenticity). Avoid forcing academic tone where it doesn’t fit.

---

## How To Decide (Summary)

1) Hard constraints first (NEVER rules) → 2) Fit by genre + scores → 3) Evidence threshold → 4) Distribution balancer → 5) Final sanity check.

- Hard constraints (never violate):
  - Never use `academic_analysis` for children’s literature, gothic romance, pure adventure, or when `structural_complexity < 4`.
  - Never use `critical_debate` without real controversy and multiple credible perspectives in findings.
  - Never use `temporal_context` for fantasy without clear historical allegory, “timeless” philosophical treatises, or contemporary-only works.
  - Never use `cultural_dimension` without genuine cross-cultural reception data.

- Evidence threshold (avoid hallucinations): Only select a format if the required research support exists (see each format’s “Minimum evidence”). If the minimum is not met, pick a safer alternative with lower evidence requirements (often `exploratory_dialogue`).

- Distribution balancer (tie-break only): If top two candidates are within a small margin (see “Decision Mechanics”), prefer the underused one that still satisfies all constraints and evidence thresholds.

---

## Mapping DEPTH×HEAT → Likely Formats

- High DEPTH, High HEAT: `academic_analysis`, `critical_debate`, `social_perspective`
- High DEPTH, Medium/Low HEAT: `academic_analysis`, `temporal_context`
- Medium DEPTH, High HEAT: `social_perspective`, `critical_debate`, `emotional_perspective`
- Medium DEPTH, Medium HEAT: `temporal_context`, `cultural_dimension`, `emotional_perspective`
- Low DEPTH, High HEAT: `exploratory_dialogue`, `narrative_reconstruction`, `social_perspective`
- Low/Medium DEPTH, Low HEAT: `exploratory_dialogue`, `temporal_context` (if period matters)

This is indicative only; format-specific signals below control the final choice.

---

## Format Playbooks: Reasons For/Against + Evidence

Each section includes exactly 5 “Use When” and 5 “Avoid When” bullets, plus best-fit signals, anti-signals, and minimum evidence.

### 1) academic_analysis
Host roles: Professor/expert + Student/assistant

- Best-fit signals:
  - `philosophical_depth ≥ 7`, `structural_complexity ≥ 6`, strong symbolism in findings
  - Canonical academic treatment; extensive scholarship referenced in findings
  - Clear theoretical frameworks cited (e.g., structuralism, psychoanalysis)
- Anti-signals:
  - `structural_complexity < 4` or “children”/“YA adventure” genres
  - Gothics where emotion is primary; light, fast-paced adventure

- Use When (5):
  - Philosophical core demands expert scaffolding and theory grounding
  - Complex structure needs methodical unpacking for comprehension
  - University-canon works with established scholarly discourse
  - Dense symbolic networks or mythic frameworks require explication
  - Historical/linguistic expertise is essential to decode meaning

- Avoid When (5):
  - Children’s or YA adventure where academic tone reduces accessibility
  - Emotion-first gothics/romances where distance kills impact
  - Action-forward classics where momentum matters more than theory
  - Contemporary mass-audience narratives with plain style/goals
  - Findings lack scholarly depth to sustain professor-level talk

- Minimum evidence: 2+ research files supporting theory/symbolism (e.g., `symbols_meanings`, `writing_innovation`) and at least 1 example in findings of academic framing.

- Examples from repo: `Thus Spoke Zarathustra`, `The Republic`, `The Waste Land`.

### 2) critical_debate
Host roles: Two critics with opposing stances

- Best-fit signals:
  - `controversy ≥ 7` with multiple independent issues in findings
  - Documented divergent critical receptions or moral ambiguities
  - Substantive “for” and “against” evidence, not mere hot takes
- Anti-signals:
  - Broad critical consensus; purely technical or craft-only discussion

- Use When (5):
  - Real, multi-faceted controversies exist (bans, scandals, ethics)
  - Competing interpretations both defensible from findings
  - Polarized reception across time, culture, or ideology
  - Ethical dilemmas without clean resolutions invite argument
  - Social media or press debates are well-evidenced in findings

- Avoid When (5):
  - Consensus interpretation; no substantive dispute in findings
  - Simple narratives lacking debate-worthy tension
  - Sparse or one-sided research material (can’t stage both sides)
  - Children’s books without credible controversy context
  - Topics better explained than argued (technique > ideology)

- Minimum evidence: 2+ independent controversy strands in `dark_drama` or `youth_digital`, plus at least 1 counterposition source.

- Examples from repo: `Harry Potter 1` (if controversy is foregrounded), `1984` (also fits social_perspective).

### 3) temporal_context
Host roles: Historian + Contemporary observer

- Best-fit signals:
  - Clear period anchoring; evolution of reception across eras
  - Links from original context to modern parallels present in findings
- Anti-signals:
  - Fantasy worlds without historical allegory; timeless treatises

- Use When (5):
  - Historical fiction or epics need era decoding for modern ears
  - The work defined its zeitgeist or captured a pivotal moment
  - Themes’ resonance changes across periods (documented in findings)
  - Findings have strong period-specific data and comparisons
  - Understanding depends on original norms/practices/ideologies

- Avoid When (5):
  - “Timeless” abstractions with little period dependence
  - Secondary-world fantasy without real-historical mapping
  - Limited historical context in findings
  - Present-day relevance dwarfs origin-era analysis
  - Hyper-abstract/philosophical focus with minimal context needs

- Minimum evidence: 1+ file with concrete period facts (`facts_history`) and 1+ file connecting past→present (`reality_wisdom` or `review.txt`).

- Examples from repo: `Narnia 1` (chosen), `Oresteia`, `Oedipus Rex`, `Odyssey`.

### 4) cultural_dimension
Host roles: Local culture specialist + Global observer

- Best-fit signals:
  - `cultural_phenomenon ≥ 7`, multiple adaptations/translations
  - Marked differences in reception across languages/cultures in findings
- Anti-signals:
  - Mono-cultural relevance; universal themes without localization effects

- Use When (5):
  - Cross-cultural divergence in readings or adaptations is documented
  - The book bridges cultures or catalyzes cultural exchange
  - Findings include meaningful localization notes (en/pl/de/…)
  - Translation controversies/choices materially affect meaning
  - Minority or indigenous perspectives are central to reception

- Avoid When (5):
  - Single-culture impact; no notable international footprint
  - Purely universal themes overshadow cultural specifics
  - Findings lack multi-language reception data
  - Narrow Western-canon focus without comparative context
  - Psychological micro-focus supersedes cultural framing

- Minimum evidence: 2+ localized context files with distinct takeaways, or clear adaptation/translation evidence in `culture_impact`.

- Examples from repo: `Master and Margarita` (global reception), `The Waste Land` (translation and reception variations), `The Count of Monte Cristo`.

### 5) social_perspective
Host roles: Social historian + Contemporary critic

- Best-fit signals:
  - High `social_roles` and `relevance`; strong systemic themes
  - Institutional critique (state, class, gender) evident in findings
- Anti-signals:
  - Intimate/psychological focus with minimal systemic context

- Use When (5):
  - Social justice, oppression, or class conflict are central
  - The book materially influenced or reflects social movements
  - Findings document systemic analysis (power, institutions)
  - Gender/class/race dynamics are salient and evidenced
  - Present-day policy or activism parallels exist in findings

- Avoid When (5):
  - Purely personal journeys with limited social backdrop
  - Escapist fantasy/adventure without commentary
  - Great historical distance with no modern lens in findings
  - Works prized mainly for aesthetic experiment
  - Thin social-impact evidence in findings

- Minimum evidence: 1+ `facts_history` or `local_context` file articulating social systems, plus 1+ `reality_wisdom` or `youth_digital` link to present.

- Examples from repo: `Master and Margarita` (chosen), `1984`, `The Gulag Archipelago`, `Mother Courage`.

### 6) emotional_perspective
Host roles: Therapist/psychologist + Personal experiencer

- Best-fit signals:
  - Emotion-led narratives; trauma, grief, coming-of-age in findings
  - Gothic romance or intense affective arcs
- Anti-signals:
  - Intellectual puzzles, satire-first, or technique-dominant works

- Use When (5):
  - Psychological depth drives meaning and reception
  - Powerful affective experiences define the work’s legacy
  - Grief/loss or healing journeys are central and evidenced
  - Coming-of-age arcs foreground emotional development
  - Findings include mental-health or therapeutic frameworks

- Avoid When (5):
  - Idea-first, puzzle-first books where feeling is secondary
  - Systemic/political commentary overwhelms the personal
  - Action/adventure pace likely conflicts with reflective tone
  - Satirical/ironic stance undermines sincerity
  - Findings lack credible psychology/emotion evidence

- Minimum evidence: 1+ file with explicit emotional/psychological analysis (`reality_wisdom`, `review.txt`), and at least 2 strong universal themes tied to feelings.

- Examples from repo: `Wuthering Heights` (recommended), `A Farewell to Arms`.

### 7) exploratory_dialogue
Host roles: Enthusiastic explorer + Curious newcomer

- Best-fit signals:
  - Accessible entry points; world-building or discovery is appealing
  - Lower DEPTH or limited research corpus, but strong interest hooks
- Anti-signals:
  - Requires heavy scholarly apparatus to avoid misinterpretation

- Use When (5):
  - Mystery, exploration, or journey frames the experience
  - Rich world-building invites guided discovery
  - Complex works need on-ramp without theory-heavy talk
  - Findings surface many “aha” facts, easter eggs, or references
  - We lack deep materials, but can safely explore without invention

- Avoid When (5):
  - Straightforward stories with no discovery dimension
  - Academic comprehension is prerequisite for accuracy
  - Emotion-first works where analytical curiosity dampens feeling
  - Findings too thin to sustain meaningful discoveries
  - Didactic texts with single clear message

- Minimum evidence: 3+ universal themes that are safe-to-explore facts/observations; any presence in `culture_impact` or `facts_history` strengthens selection.

- Examples from repo: `Odyssey`, `Gulliver’s Travels`, children’s adventure classics (also viable for Narnia/Hobbit-type works).

### 8) narrative_reconstruction
Host roles: Investigator + Witness reconstructing events

- Best-fit signals:
  - `structural_complexity ≥ 6`, non-linear or multi-perspective
  - Unreliable narration or puzzle-like plotting in findings
- Anti-signals:
  - Linear plots; idea-first expository works; non-fictional facts fixed

- Use When (5):
  - Fragmented timelines or frames need reassembly for clarity
  - Unreliable narrators force the listener to adjudicate truth
  - Multi-POV conflicts benefit from “case file” reconstruction
  - Meta-fiction invites attention to how the story is built
  - Children’s adventures/mysteries thrive on detective framing

- Avoid When (5):
  - Simple linear plots with no ambiguity
  - Philosophy/abstraction outweighs narrative mechanics
  - Emotion-first immersion would be reduced by forensic tone
  - Low plot complexity; few moving parts
  - Historical/factual works with settled chronology

- Minimum evidence: Explicit structural notes in `writing_innovation` or `review.txt` (structure section), plus 2+ universal themes referencing plot mechanics.

- Examples from repo: `Slaughterhouse-Five`-type structures; children’s mystery sequences; could fit `Harry Potter 1` as detective framing when controversy is not primary.

---

## Decision Mechanics (Practical Rules)

1) Compute a per-format suitability score using signals (positive) and anti-signals (negative):
   - Example mapping from scores → signals:
     - `philosophical_depth ≥ 7` → +2 to `academic_analysis`
     - `structural_complexity ≥ 7` → +2 to `narrative_reconstruction`; `< 4` → −3 to `academic_analysis`
     - `controversy ≥ 7` → +2 to `critical_debate`
     - `cultural_phenomenon ≥ 7` + ≥2 localized files → +2 to `cultural_dimension`
     - `social_roles ≥ 7` and `relevance ≥ 7` → +2 to `social_perspective`
     - `contemporary_reception ≥ 7` → +1 to `critical_debate` or `social_perspective` (depending on findings)
     - “children”/“YA adventure” in genre → +2 to `exploratory_dialogue` or `narrative_reconstruction`; −3 to `academic_analysis`

2) Evidence thresholds: If a format doesn’t meet its “Minimum evidence,” zero out its score (cannot be selected).

3) Distribution balancer (applies only when fit is close):
   - If top two scores differ by ≤ 1.0, prefer the underused format.
   - Apply a soft penalty of −0.5 to `academic_analysis` if ≥ 20% usage and the close alternative fully fits.
   - Never override hard constraints or evidence thresholds.

4) Final sanity check (same as AI prompt’s “Final Validation”):
   - Honors book’s essential character? Supported by findings? Engaging for youth? Avoids academic trap? Defensible to experts?

5) Output JSON:
```json
{
  "selected_format": "format_name",
  "confidence": 0.82,
  "reasoning": {
    "primary_factor": "Main driver of choice",
    "genre_fit": "Genre-to-format rationale",
    "material_support": "Which findings back this",
    "audience_appeal": "TikTok-friendly angle",
    "alternatives_considered": ["alt1", "alt2"],
    "why_not_alternatives": "Short, evidence-based"
  },
  "risks": "Potential pitfalls",
  "special_instructions": "Prompt hints for hosts"
}
```

---

## Examples From This Repository (Fit-First, Not Exhaustive)

- Wuthering Heights → `emotional_perspective` (gothic passion, trauma; avoid academic tone).
- The Chronicles of Narnia 1 → `temporal_context` or `exploratory_dialogue` (portal fantasy + 1950s context; repo chose temporal_context).
- Harry Potter 1 → `narrative_reconstruction` (detective framing for school-year plot) or `critical_debate` when controversies dominate (repo chose debate).
- Master and Margarita → `social_perspective` (oppression, power, dual timelines; repo chose social_perspective).
- The Waste Land / The Republic / Zarathustra → `academic_analysis` (dense theory/structure; ensure accessibility via student role).
- The Gulag Archipelago → `social_perspective` (systemic critique; content warnings needed).
- Odyssey / Gulliver’s Travels → `exploratory_dialogue` (journeys, discovery, world-building).

---

## What’s Good In The Existing Guidelines, And What This Adds

Strong in current doc:
- Clear 5×5 “use/avoid” lists per format.
- Practical red flags and youth-audience reminders.

Additions in this GPT Edition:
- DEPTH×HEAT mapping and concrete score-to-signal rules.
- Explicit minimum-evidence thresholds per format to prevent hallucinations.
- Tie-break distribution balancer to reduce `academic_analysis` bias.
- Safer defaults when materials are thin (`exploratory_dialogue`).
- Repository-grounded examples to anchor intuition.

Suggested tweaks if you revise the original (do not edit automatically):
- Add explicit “Minimum evidence” lines per format.
- Include score-trigger examples (e.g., “structural_complexity ≥ 7 → narrative_reconstruction”).
- Document the tie-break balancer to increase variety responsibly.
- Append a short “host tone” reminder per format for youth engagement.

---

## Quick Checklist Before Finalizing A Choice

- Genre sanity: Does the format match the work’s core mode?
- Scores sanity: Do key scores support this format’s signals?
- Evidence: Do findings meet the format’s minimum evidence?
- Youth appeal: Is this engaging, not just correct?
- Balance: Is there a near-tie where underused format should be preferred?
- Guardrails: Are any NEVER rules violated? If yes, stop and pick again.
- Risk note: List one risk and how to mitigate in prompts.

---

## Host Role Reminders (Concise)

- academic_analysis: Professor explains; student clarifies and grounds examples.
- critical_debate: Advocate vs skeptic; ensure respectful, evidence-backed clash.
- temporal_context: Past expert + present reader; always connect eras.
- cultural_dimension: Local specialist + global observer; emphasize contrasts.
- social_perspective: Historian + contemporary critic; system lenses, then today.
- emotional_perspective: Feelings-first + technique interpreter; keep it human.
- exploratory_dialogue: Enthusiast + newcomer; share safe discoveries, avoid over-claiming.
- narrative_reconstruction: Investigator + witness; reconstruct clearly, avoid spoilers if required.

---

This document is designed to be drop-in usable by an AI selector and by humans auditing choices. It encodes fit-first rigor, anti-hallucination guardrails, and gentle diversity pressure to correct current usage imbalance without compromising accuracy or audience fit.

