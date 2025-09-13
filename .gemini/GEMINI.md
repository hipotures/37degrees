# Procedure for 37d-a5au-cc-research.md and its Agents

This document outlines the step-by-step procedure for executing the `37d-a5au-cc-research.md` script and its associated sub-agents. This procedure was developed through iterative interaction with the user to ensure correct and thorough execution.

## Main Script: 37d-a5au-cc-research.md

The main script orchestrates the research process in three phases:

### FAZA 1: Inicjalizacja i pobranie zadania (Initialization and Task Retrieval)
1.  **Retrieve Next Pending Task**: Use `default_api.todo_get_next_pending(list_key="cc-au-research")` to get the next book to process.
2.  **Extract BOOK_FOLDER**: The `item_key` from the retrieved task is used as the `BOOK_FOLDER` variable (e.g., `0018_lord_of_the_rings`, `0019_master_and_margarita`).

### FAZA 2: Uruchomienie Research (Research Execution)
This phase involves executing pairs of specialized research agents sequentially. For each agent, the following sub-procedure is followed:

**Sub-Agent Execution Procedure:**
1.  **Read Agent File**: Read the content of the sub-agent's `.md` file (e.g., `37d-au-culture-impact-researcher.md`) to understand its specific tasks and requirements.
2.  **Read book.yaml**: Read the `book.yaml` file for the current `BOOK_FOLDER` to get book details (e.g., `default_api.read_file(absolute_path="/home/xai/DEV/37degrees/books/[BOOK_FOLDER]/book.yaml")`).
3.  **Document Check**: Check if the agent's output file already exists and is complete.
    *   **File Path**: `$CLAUDE_PROJECT_DIR/books/[BOOK_FOLDER]/docs/findings/au-*.md`
    *   **Action**: Use `default_api.read_file()` to attempt to read the file.
    *   **Decision Logic**:
        *   If the file exists and appears complete (based on previous successful runs or manual inspection if needed), **terminate the current sub-agent's execution** and proceed to the next sub-agent in the main script's sequence.
        *   If the file does not exist or is incomplete, proceed with the research tasks for the current sub-agent.
4.  **Create TODO List (if needed)**: If the output file does not exist or is incomplete, create a new TODO list specifically for this sub-agent's primary tasks.
    *   **Tool**: `default_api.todo_create_list(list_key="[agent_name]-research", title="[Book Title] [Agent Name] Research Tasks")`
5.  **Add Tasks to TODO List**: Add all "Primary Tasks" listed in the sub-agent's `.md` file to the newly created TODO list.
    *   **Tool**: `default_api.todo_quick_add(items=[...], list_key="[agent_name]-research")`
6.  **Execute Tasks from TODO List**: Iterate through the tasks on the sub-agent's TODO list. For each task:
    a.  **Get Next Pending Item**: Use `default_api.todo_get_next_pending(list_key="[agent_name]-research")`.
    b.  **Perform Web Search**: Use `default_api.google_web_search(query="[task_title]")` to gather information.
    c.  **Synthesize Information**: Process the search results and extract relevant facts.
    d.  **Update Output File**: Read the current content of the agent's output file, append/update with the new synthesized information, and write it back.
        *   **Tool**: `default_api.read_file()` followed by `default_api.write_file()`.
    e.  **Mark Task Completed**: Use `default_api.todo_update_item_status(item_key="[item_key]", list_key="[agent_name]-research", status="completed")`.
7.  **Repeat** steps 6a-6e until all tasks for the sub-agent are completed.

**Order of Agent Execution (from 37d-a5au-cc-research.md):**
*   `au-culture-impact-researcher` and `au-dark-drama-investigator` (executed sequentially)
*   `au-facts-history-specialist` and `au-local-pl-context-specialist` (executed sequentially)
*   `au-reality-wisdom-checker` and `au-symbols-meaning-analyst` (executed sequentially)
*   `au-writing-innovation-expert` and `au-youth-digital-connector` (executed sequentially)
*   `au-local-en-context-specialist` and `au-local-de-context-specialist` (executed sequentially)
*   `au-local-es-context-specialist` and `au-local-pt-context-specialist` (executed sequentially)
*   `au-local-fr-context-specialist` and `au-local-ja-context-specialist` (executed sequentially)
*   `au-local-ko-context-specialist` and `au-local-hi-context-specialist` (executed sequentially)
*   `au-content-warning-assessor` (executed after all parallel agents are done)

### FAZA 3: Finalizacja (Finalization)
1.  **Mark Main Task Completed**: Once all sub-agents for the `BOOK_FOLDER` have completed their research (or their existing output has been confirmed), mark the main task in the `cc-au-research` list as "completed".
    *   **Tool**: `default_api.todo_update_item_status(list_key="cc-au-research", item_key="[BOOK_FOLDER]", status="completed")`

## Key Tools Used:
*   `default_api.list_directory` (for initial file checks, though `glob` is preferred for patterns)
*   `default_api.read_file` (to read agent files, book.yaml, and existing research files)
*   `default_api.write_file` (to create and update research files)
*   `default_api.glob` (to find agent files and check for existing research files)
*   `default_api.google_web_search` (for performing research queries)
*   `default_api.todo_create_list` (to create new TODO lists for sub-agent tasks)
*   `default_api.todo_quick_add` (to add multiple tasks to a TODO list)
*   `default_api.todo_get_next_pending` (to retrieve the next task from a TODO list)
*   `default_api.todo_update_item_status` (to mark tasks as completed)

