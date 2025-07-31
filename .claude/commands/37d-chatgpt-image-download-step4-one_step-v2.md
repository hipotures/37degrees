# ChatGPT Image Download - Single Step Process (MCP Version)

**AUTOMATED EXECUTION: Claude MUST execute ALL steps in EXACT ORDER using MCP playwright-headless tools and file operations.**

**PURPOSE**: Download ONE image per execution from ChatGPT conversations for book "[TITLE]" by "[AUTHOR]"

**DYNAMIC PARAMETERS**: 
- `[BOOK_FOLDER]`: Directory name (e.g., "0016_lalka", "0006_don_quixote")
- `[TITLE]`: Book title from user request
- `[AUTHOR]`: Book author from user request
- `[XX]`: Scene number (01-25)

## CRITICAL EXECUTION RULES

1. **NEVER SKIP STEPS** - Each step must be completed before proceeding
2. **VERIFY AFTER EACH ACTION** - Confirm success before moving forward  
3. **STOP ON ERROR** - Do not continue if any step fails
4. **ONE TASK PER EXECUTION** - Process exactly one unrealized task

## EXECUTION PHASES

### Phase 1: RESEARCH & ANALYSIS
**Goal**: Understand current state and what needs to be done
1. Check if TODO list exists
2. Analyze existing files
3. Document findings

### Phase 2: PLANNING  
**Goal**: Determine exact actions needed
4. If no TODO: Plan TODO creation
5. Identify first unrealized task
6. Define success criteria

### Phase 3: EXECUTION
**Goal**: Perform the actual download task
7. Navigate to correct conversation
8. Download image(s)
9. Process and rename files

### Phase 4: VERIFICATION
**Goal**: Ensure task completed successfully
10. Verify files saved correctly
11. Update TODO status
12. Confirm no data loss

## DETAILED STEP-BY-STEP EXECUTION

### STEP 1: Check TODO List Status

**Action**:
```bash
ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
```

**Expected Result**: 
- File exists → Proceed to STEP 3
- File not found → Proceed to STEP 2

**VALIDATION CHECKPOINT**: 
- ✓ Confirmed TODO-DOWNLOAD.md status
- ✓ Path is correct for the book
- ✓ No permission errors

**STOP**: Do not proceed until you have confirmed the TODO list status.

### STEP 2: Create TODO List (IF NEEDED)

**Sub-step 2.1: Navigate to ChatGPT Project**

**Action**:
```javascript
// Rozpocznij od otwarcia strony ChatGPT
mcp__playwright-headless__browser_navigate('https://chatgpt.com/');

// Otwórz sidebar
mcp__playwright-headless__browser_snapshot();
mcp__playwright-headless__browser_click(
  element: "Open sidebar button",
  ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT"
);

// Kliknij na projekt dla książki (użyj nazwy z book.yaml)
mcp__playwright-headless__browser_click(
  element: "[BOOK_FOLDER] project link", 
  ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT"
);
```

**VALIDATION CHECKPOINT**:
- ✓ Correct project opened
- ✓ Can see conversation list
- ✓ Project name matches book title

**CRITICAL ERROR HANDLING - CloudFlare/CAPTCHA Detection**:
If CloudFlare protection page or CAPTCHA appears:
1. **IMMEDIATELY take screenshot** using browser screenshot tool
2. **ABORT the task** - do not attempt to bypass
3. **Report**: "CloudFlare/CAPTCHA detected - task terminated, screenshot saved"
4. **EXIT** without updating TODO status

**Sub-step 2.2: Load ALL Conversations**

**CRITICAL**: The page uses DYNAMIC LOADING - conversations appear as you scroll!
**MUST DO BEFORE CREATING TODO FILE**

**Action**:
```javascript
// PROVEN METHOD: Multi-scroll technique dla mobile devices
mcp__playwright-headless__browser_evaluate(() => {
  // Kombinacja 4 metod scrollowania - gwarantuje sukces na mobile
  window.scrollTo(0, 5000);
  document.documentElement.scrollTop = 5000;
  document.body.scrollTop = 5000;
  
  const listContainer = document.querySelector('main');
  if (listContainer) {
    listContainer.scrollTop = 5000;
  }
  
  return 'Multi-scroll completed';
});

// Sprawdź czy załadowały się wszystkie konwersacje
mcp__playwright-headless__browser_snapshot();
```

**Success Criteria**:
- Found conversation with "scene_01" (indicates end of list)
- All scene numbers from 01 to 25 are visible
- Conversations loaded via lazy loading

**CRITICAL**: NIE TWÓRZ TODO FILE dopóki nie zobaczysz scene_01 w snapshot!
**STOP**: Jeśli nie widzisz scene_01, powtórz scrollowanie - TODO będzie niepełne!

**Sub-step 2.3: Create TODO File (ONLY AFTER COMPLETE SCROLL)**

**Action**:
1. Create new file: `/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md`
2. Add EACH CONVERSATION as a separate line (not scene numbers!)
3. Use EXACT chat titles from ChatGPT (not generic descriptions)
4. **CRITICAL**: Maintain EXACT SAME ORDER as chats appear in ChatGPT sidebar!
5. Each chat may contain multiple generated images to download

**CRITICAL**: 
- Lista zawiera NAZWY CHATÓW, nie sceny! W chacie może być wiele obrazów.
- **KOLEJNOŚĆ MUSI BYĆ IDENTYCZNA** z ChatGPT sidebar - niektóre chaty mają identyczne nazwy!
- Bez zachowania kolejności nie da się jednoznacznie zidentyfikować chatu do pobrania.

**Format Requirements**:
```
[ ] [Exact conversation title from ChatGPT - as displayed in sidebar]
```

**Example (CORRECT - Real chat names from ChatGPT sidebar)**:
```
[ ] Generowanie obrazu z jsona - Wygeneruj obraz opisany załączonym jsonem
[ ] Generowanie obrazu JSON - Wygeneruj obraz opisany załączonym jsonem  
[ ] New chat
[ ] Create image from JSON scene_25 - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.
[ ] Wygeneruj obraz z tym samym promptem, zmien tylko rozdzielczosc na 1024 × 1792 px
[ ] Brak wygenerowanego obrazu obraz sie nie wygenerował
[ ] Create image from JSON scene_24 - create an image based on the scene, style, and visual specifications described in the attached JSON. The JSON is a blueprint, not the content.
```

**Example (WRONG - Do NOT use generic descriptions)**:
```
[ ] Check and download from scene_25 conversation
[ ] Download image for scene 24
[ ] Scene 23 processing
```

**VALIDATION CHECKPOINT**:
- ✓ File created successfully
- ✓ Contains ALL conversations from project (verify by scrolling count)
- ✓ Each line has `[ ]` prefix  
- ✓ Using REAL chat titles from ChatGPT sidebar, not scene numbers
- ✓ **MAINTAINS EXACT ORDER** from ChatGPT sidebar (top to bottom)
- ✓ Includes all chat types (original prompts, retries, resolution changes, etc.)
- ✓ Order preserved for duplicate chat names identification

### STEP 3: Find First Unrealized Task

**Action**:
```bash
grep -n "^\[ \]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md | head -1
```

**Expected Result**:
- Line number and task description
- Example: `3:[ ] New chat` or `2:[ ] Generowanie obrazu z jsona - Wygeneruj...`

**CRITICAL**: 
- Pierwszy nieukończony task może być DOWOLNY chat (nie tylko scene-based)
- Kolejność w TODO odpowiada kolejności w ChatGPT sidebar
- Dzięki temu identyczne nazwy chatów są jednoznacznie identyfikowalne przez pozycję

**VALIDATION CHECKPOINT**:
- ✓ Found at least one uncompleted task
- ✓ Task line starts with `[ ]`
- ✓ Noted line number for later update
- ✓ Line number corresponds to chat position in sidebar

**STOP**: If no tasks found (all completed), report completion and exit.

### STEP 4: Navigate to Specific Conversation

**Sub-step 4.1: Open Conversation**

**CRITICAL**: Use POSITION in sidebar, not just chat name (for identical names)!

**Action**:
```javascript
// Znajdź konwersację na podstawie POZYCJI w sidebar (line number z TODO)
// Example: jeśli TODO line 3 = chat na 3. pozycji w sidebar
mcp__playwright-headless__browser_snapshot();

// Kliknij na N-ty chat w liście (gdzie N = line number z TODO)
// UWAGA: Używaj pozycji, nie nazwy - nazwy mogą się powtarzać!
mcp__playwright-headless__browser_click(
  element: "Conversation at position [N] in sidebar list",  
  ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT"
);

// Poczekaj na załadowanie konwersacji
mcp__playwright-headless__browser_wait_for(time: 3);
mcp__playwright-headless__browser_snapshot();
```

**VALIDATION CHECKPOINT**:
- ✓ Opened conversation at correct position (line N from TODO)
- ✓ Conversation title matches TODO task (może być identyczna z innymi)
- ✓ Can see attached JSON files
- ✓ Images are visible in conversation
- ✓ Position in sidebar corresponds to TODO line number

**Sub-step 4.2: Verify Conversation Content**

**CRITICAL**: Check conversation for generated images! (JSON files optional - some chats may not have them)

**Action**:
```javascript
// Sprawdź zawartość konwersacji - załączone JSONy (jeśli są) i wygenerowane obrazy
mcp__playwright-headless__browser_evaluate(() => {
  // Znajdź załączone pliki JSON (mogą nie istnieć w niektórych chatach)
  const fileElements = document.querySelectorAll('[data-testid*="file"], .file-name, .attachment');
  const files = [];
  fileElements.forEach(el => {
    const text = el.textContent || el.innerText || '';
    if (text.includes('.json')) {
      files.push(text.trim());
    }
  });
  
  // Policz obrazy do pobrania - TO JEST KLUCZOWE
  const images = document.querySelectorAll('img[alt="Generated image"]');
  
  return {
    jsonFiles: files,
    imageCount: images.length,
    hasImages: images.length > 0,
    chatType: files.length > 0 ? 'scene-based' : 'generic'
  };
});
```

**Success Criteria**:
- Found at least 1 generated image to download (REQUIRED)
- JSON files may or may not be present (depends on chat type)
- Conversation matches TODO task description

**ERROR HANDLING**: If no JSON found, this may be wrong chat or technical error - STOP and report issue.

### STEP 5: Download Image(s)

**Sub-step 5.1: Locate and Count Images**

**CRITICAL**: W chacie może być wiele obrazów - pobierz WSZYSTKIE!

**Action**:
```javascript
// Znajdź wszystkie obrazy do pobrania w tej konwersacji
mcp__playwright-headless__browser_evaluate(() => {
  const images = document.querySelectorAll('img[alt="Generated image"]');
  return {
    imageCount: images.length,
    imagesFound: images.length > 0,
    note: 'Chat może zawierać wiele obrazów - pobierz wszystkie'
  };
});
```

**IMPORTANT**: Jeśli w chacie jest więcej niż 1 obraz, pobierz kolejno WSZYSTKIE obrazy!

**Sub-step 5.2: Download All Images in Chat**

**PROCESS**: For each image found in conversation (may be multiple!)

**Action for EACH image**:
```javascript  
// LOOP: Dla każdego obrazu w konwersacji
// 1. Znajdź pierwszy niepobrany obraz
mcp__playwright-headless__browser_snapshot();

// 2. Kliknij przycisk "Download this image" dla tego obrazu
mcp__playwright-headless__browser_click(
  element: "Download this image button [first/second/third image]",
  ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT"
);

// 3. Poczekaj na zakończenie pobierania
mcp__playwright-headless__browser_wait_for(time: 5);

// 4. Sprawdź czy plik został pobrany
// 5. Jeśli jest więcej obrazów, powtórz dla następnego
```

**VALIDATION CHECKPOINT**:
- ✓ Download button clicked for current image
- ✓ No error messages appeared  
- ✓ File appears in /tmp/playwright-mcp-files/
- ✓ Process repeated for ALL images in chat

**Alternative Method** (if download button fails):
```javascript
// Użyj right-click jako fallback
mcp__playwright-headless__browser_click(
  element: "Generated image [specify which one]",
  ref: "UŻYJ_RZECZYWISTEGO_REF_Z_SNAPSHOT", 
  button: "right"
);
// Następnie kliknij "Save image as..."
```

### STEP 6: File Management and Naming

**Sub-step 6.1: Locate All Downloaded Files**

**CRITICAL**: May have multiple files from one chat!

**Action**:
```bash
# Znajdź wszystkie nowo pobrane pliki (ostatnie N plików według czasu)
ls -la -t /tmp/playwright-mcp-files/ChatGPT-Image*.png | head -[N]
# gdzie N = liczba obrazów pobranych z aktualnego chatu
```

**Expected**: Multiple files like:
- `ChatGPT-Image-Jul-31-2025-02-16-38-PM.png` (newest)
- `ChatGPT-Image-Jul-31-2025-02-15-22-PM.png` 
- `ChatGPT-Image-Jul-31-2025-02-14-15-PM.png` (oldest from this chat)

**Sub-step 6.2: Determine File Naming Strategy**

**CRITICAL**: Extract scene number or use generic naming depending on chat type!

**Action**:
```javascript
// Strategy 1: Spróbuj wyciągnąć numer sceny z pliku JSON
// Strategy 2: Jeśli brak JSON, użyj generycznego nazewnictwa
mcp__playwright-headless__browser_evaluate(() => {
  const fileElements = document.querySelectorAll('[data-testid*="file"], .file-name, .attachment');
  let sceneNumber = null;
  let namingStrategy = 'generic';
  
  // Sprawdź czy jest plik JSON ze sceną
  fileElements.forEach(el => {
    const text = el.textContent || el.innerText || '';
    const match = text.match(/scene_(\d+)\.json/);
    if (match) {
      sceneNumber = match[1]; // "12" from "scene_12.json"
      namingStrategy = 'scene-based';
    }
  });
  
  // Jeśli brak JSON, spróbuj wyciągnąć z tytułu chatu
  if (!sceneNumber) {
    const titleMatch = window.location.href.match(/scene_(\d+)/);
    if (titleMatch) {
      sceneNumber = titleMatch[1];
      namingStrategy = 'scene-from-title';
    }
  }
  
  return {
    sceneNumber: sceneNumber,
    strategy: namingStrategy,
    hasJSON: fileElements.length > 0
  };
});
```

**Sub-step 6.3: Check for Existing Files and Plan Naming**

**CRITICAL**: Never overwrite existing files! Use appropriate naming strategy.

**Action**:
```bash
# STRATEGY A: Scene-based naming (jeśli mamy scene number)
if [ "$SCENE_NUMBER" != "null" ]; then
  ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_scene_[XX]*
  NAMING_TYPE="scene"
else
  # STRATEGY B: Generic naming (dla polskich chatów, "New chat", etc.)
  ls -la /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[book_number]_generic_*
  NAMING_TYPE="generic"
fi
```

**Naming Decision Trees**:

**A) Scene-based naming** (gdy mamy scene_XX.json lub scene_XX w tytule):
- No existing files → Use: `[book_number]_scene_[XX].png` (first image)
- File exists → Use: `[book_number]_scene_[XX]_a.png` (second image)  
- Multiple exist → Use next letter: `[book_number]_scene_[XX]_b.png`, `_c.png`, etc.

**B) Generic naming** (polskie chaty, "New chat", inne):
- No existing files → Use: `[book_number]_generic_001.png` (first generic image)
- Files exist → Use: `[book_number]_generic_002.png`, `_003.png`, etc.

**Examples**:

**Scene-based chat** (scene_12.json, 3 images):
- `0016_scene_12.png` (first image)
- `0016_scene_12_a.png` (second image)
- `0016_scene_12_b.png` (third image)

**Generic chat** ("Generowanie obrazu z jsona", 2 images):
- `0016_generic_001.png` (first generic image)
- `0016_generic_002.png` (second generic image)

**Sub-step 6.4: Move and Rename All Images**

**PROCESS**: For each downloaded image from this chat - use appropriate naming strategy!

**Action**:
```bash
# Pobierz wyniki z Step 6.2 (naming strategy decision)
SCENE_NUMBER="[XX_OR_NULL]"  # From JavaScript evaluation
NAMING_STRATEGY="[scene-based|generic]"  # From JavaScript evaluation
BOOK_NUMBER="[book_number]"  # From book folder name
TARGET_DIR="/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated"

# Pobierz listę pobranych plików (najnowsze pierwsze)
DOWNLOADED_FILES=($(ls -t /tmp/playwright-mcp-files/ChatGPT-Image*.png | head -[N]))

# STRATEGY A: Scene-based naming
if [ "$NAMING_STRATEGY" = "scene-based" ] || [ "$NAMING_STRATEGY" = "scene-from-title" ]; then
  for i in "${!DOWNLOADED_FILES[@]}"; do
    SOURCE_FILE="${DOWNLOADED_FILES[$i]}"
    
    if [ $i -eq 0 ]; then
      # Pierwszy plik - bazowa nazwa sceny
      TARGET_NAME="${BOOK_NUMBER}_scene_${SCENE_NUMBER}.png"
    else
      # Kolejne pliki - dodaj suffix literowy
      SUFFIX=$(printf \\$(printf '%03o' $((97+$i-1))))  # a, b, c, d...
      TARGET_NAME="${BOOK_NUMBER}_scene_${SCENE_NUMBER}_${SUFFIX}.png"
    fi
    
    # Sprawdź czy plik już istnieje, jeśli tak - pomiń
    if [ -f "$TARGET_DIR/$TARGET_NAME" ]; then
      echo "File $TARGET_NAME already exists - skipping"
      continue
    fi
    
    # Przenieś plik
    mv "$SOURCE_FILE" "$TARGET_DIR/$TARGET_NAME"
    echo "Moved to: $TARGET_NAME"
  done

# STRATEGY B: Generic naming (polskie chaty, "New chat", etc.)
else
  # Znajdź najwyższy numer generic file
  LAST_GENERIC=$(ls "$TARGET_DIR/${BOOK_NUMBER}_generic_"*.png 2>/dev/null | \
                 sed 's/.*_generic_\([0-9]*\)\.png/\1/' | \
                 sort -n | tail -1)
  NEXT_NUM=$((${LAST_GENERIC:-0} + 1))
  
  for i in "${!DOWNLOADED_FILES[@]}"; do
    SOURCE_FILE="${DOWNLOADED_FILES[$i]}"
    CURRENT_NUM=$((NEXT_NUM + i))
    TARGET_NAME="${BOOK_NUMBER}_generic_$(printf '%03d' $CURRENT_NUM).png"
    
    # Sprawdź czy plik już istnieje, jeśli tak - użyj następnego numeru
    while [ -f "$TARGET_DIR/$TARGET_NAME" ]; do
      CURRENT_NUM=$((CURRENT_NUM + 1))
      TARGET_NAME="${BOOK_NUMBER}_generic_$(printf '%03d' $CURRENT_NUM).png"
    done
    
    # Przenieś plik
    mv "$SOURCE_FILE" "$TARGET_DIR/$TARGET_NAME"
    echo "Moved to: $TARGET_NAME"
  done
fi
```

**Example Results**:

**Scene-based chat** (scene_12.json, 3 images):
- `ChatGPT-Image-14-47-01.png` → `0016_scene_12.png`
- `ChatGPT-Image-14-46-55.png` → `0016_scene_12_a.png` 
- `ChatGPT-Image-14-46-42.png` → `0016_scene_12_b.png`

**Generic chat** ("Generowanie obrazu z jsona", 2 images):
- `ChatGPT-Image-15-22-10.png` → `0016_generic_001.png`
- `ChatGPT-Image-15-22-05.png` → `0016_generic_002.png`

**VALIDATION CHECKPOINT**:
- ✓ File moved successfully
- ✓ No existing files overwritten
- ✓ Correct naming convention used
- ✓ File permissions are readable

### STEP 7: Update TODO Status

**Sub-step 7.1: Mark Task Complete**

**CRITICAL**: Mark task as completed AFTER successful file move!

**Action**:
```bash
# Znajdź exact task line to update (N to numer linii z STEP 3)
# Example: jeśli STEP 3 zwrócił "5:[ ] Create image from JSON scene_25..."
# to N=5

# Oznacz zadanie jako ukończone
sed -i 'Ns/^\[ \]/[x]/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

# Sprawdź czy aktualizacja się powiodła
grep -n "scene_[XX]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
```

**Example**:
```bash
# Jeśli scene_25 była w linii 5:
sed -i '5s/^\[ \]/[x]/' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

# Verification:
grep -n "scene_25" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md
# Should show: 5:[x] Create image from JSON scene_25...
```

**VALIDATION CHECKPOINT**:
- ✓ TODO file updated successfully
- ✓ Only one line changed from [ ] to [x]
- ✓ Task now shows `[x]` prefix
- ✓ Other tasks unchanged

## FINAL VERIFICATION

### STEP 8: Complete Execution Verification

**Action**:
```bash
# Sprawdź czy plik istnieje i jest prawidłowy
file /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/[final_name].png

# Sprawdź aktualizację TODO
grep -n "^\[x\].*scene_[XX]" /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md

# Raport postępu
echo "Completed: $(grep -c '^\[x\]' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md)"
echo "Remaining: $(grep -c '^\[ \]' /home/xai/DEV/37degrees/books/[BOOK_FOLDER]/generated/TODO-DOWNLOAD.md)"
```

**SUCCESS CRITERIA**:
- ✓ Image file exists and is valid PNG
- ✓ TODO shows task as completed `[x]`
- ✓ No existing files were overwritten
- ✓ Proper naming convention followed

### STEP 9: Close Browser Session

**CRITICAL**: Always close browser to prevent conflicts with subsequent executions

**Action**:
```javascript
// Zamknij przeglądarkę na końcu procesu
mcp__playwright-headless__browser_close();
```

**VALIDATION CHECKPOINT**:
- ✓ Browser session terminated cleanly
- ✓ No hanging processes remain
- ✓ Next execution can start fresh browser instance

## MCP TECHNICAL NOTES

### Critical MCP Usage Guidelines

1. **Browser Navigation**:
   ```javascript
   mcp__playwright-headless__browser_navigate('https://chatgpt.com/');
   ```

2. **Element Interaction**:
   ```javascript
   // ZAWSZE użyj browser_snapshot() przed interakcją
   mcp__playwright-headless__browser_snapshot();
   mcp__playwright-headless__browser_click(
     element: "human-readable description",
     ref: "REAL_REF_FROM_SNAPSHOT"
   );
   ```

3. **Dynamic Refs**:
   - NIGDY nie używaj hardcoded refs jak "#prompt-textarea"
   - ZAWSZE bierz ref z aktualnego browser_snapshot()
   - Element refs są dynamiczne w React applications

4. **Mobile Scrolling**:
   ```javascript
   // Proven method for ChatGPT mobile lazy loading
   mcp__playwright-headless__browser_evaluate(() => {
     window.scrollTo(0, 5000);
     document.documentElement.scrollTop = 5000;
     document.body.scrollTop = 5000;
     const main = document.querySelector('main');
     if (main) main.scrollTop = 5000;
     return 'Multi-scroll completed';
   });
   ```

5. **Wait Strategies**:
   ```javascript
   // Dla elementów dynamicznych
   mcp__playwright-headless__browser_wait_for(time: 3);
   
   // Dla tekstu
   mcp__playwright-headless__browser_wait_for(text: "Download");
   ```

### Error Recovery Procedures

**ERROR: Ref not found**
- **RECOVERY**: Take new browser_snapshot() and find current ref
- **PREVENTION**: Never hardcode refs, always use snapshot results

**ERROR: Download button not visible**
- **RECOVERY**: Scroll to image, take new snapshot, try again
- **FALLBACK**: Use right-click context menu method

**ERROR: File not downloaded**
- **RECOVERY**: Check /tmp/playwright-mcp-files/ directory
- **ALTERNATIVE**: Try alternative download method or manual save

**ERROR: Scrolling doesn't load conversations**
- **RECOVERY**: Try multi-scroll method multiple times
- **MANUAL**: Request manual scroll from user if automation fails

### Performance Notes

- ChatGPT mobile uses lazy loading - scrolling triggers content load
- Image downloads save to `/tmp/playwright-mcp-files/` with timestamped names
- Browser state persists between MCP calls in same session
- Downloads directory is automatically created by MCP Playwright

## EXECUTION SUMMARY

### Complete MCP Process Flow
```
START
  ├─→ mcp__playwright-headless__browser_navigate(ChatGPT)
  ├─→ Check TODO exists?
  │     ├─ NO → Create TODO (scroll + snapshot + file creation)
  │     └─ YES → Continue
  ├─→ Find first [ ] task (grep)
  ├─→ Navigate to conversation (click + wait)
  ├─→ Download image (click download button)
  ├─→ Move file (bash mv command)
  ├─→ Update TODO (sed command)
  ├─→ Verify success (file + grep validation)
  └─→ mcp__playwright-headless__browser_close()
END
```

### Key Principles
1. **MCP ONLY** - Use mcp__playwright-headless__ prefix for all browser actions
2. **SNAPSHOT FIRST** - Always take browser_snapshot() before element interaction
3. **REAL REFS** - Never use fake refs, always extract from snapshot
4. **MULTI-SCROLL** - Use proven 4-method scroll technique for lazy loading
5. **FILE VALIDATION** - Always verify downloaded files exist and are valid

## CRITICAL REMINDERS

⚠️ **ALWAYS USE MCP PLAYWRIGHT-HEADLESS TOOLS**
⚠️ **NEVER USE RAW PLAYWRIGHT API CALLS**  
⚠️ **TAKE BROWSER_SNAPSHOT() BEFORE EVERY CLICK**
⚠️ **USE REAL REFS FROM SNAPSHOTS, NOT HARDCODED**
⚠️ **SCROLL FIRST, THEN CREATE TODO** - TODO musi zawierać wszystkie sceny 01-25
⚠️ **MULTI-SCROLL METHOD FOR COMPLETE CONVERSATION LOADING**
⚠️ **MARK TODO AS [x] AFTER SUCCESSFUL FILE MOVE**
⚠️ **VERIFY DOWNLOADED FILES IN /tmp/playwright-mcp-files/**
⚠️ **PROCESS ONLY ONE TASK PER EXECUTION**
⚠️ **ALWAYS CLOSE BROWSER AT END** - Zapobiega konfliktom z kolejnymi uruchomieniami