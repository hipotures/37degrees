# 37 Degrees - AI-Powered TikTok Video Generator

## Project Overview

This project, "37 Degrees," is a sophisticated Python-based system designed to create engaging TikTok videos about classic literature, targeting Polish youth. It automates the entire content creation pipeline, from research and scriptwriting to AI-powered image generation and final video rendering.

The core of the project is a powerful command-line interface (CLI) application (`main.py`) that orchestrates a complex workflow. This workflow involves several key components:

*   **Book Management:** Each book is represented by a directory (e.g., `books/0017_little_prince/`) containing a central `book.yaml` configuration file. This file defines the book's metadata, themes, and analysis, which drives the content generation process.
*   **AI Agent Research System:** A multi-agent system, defined in `.claude/agents/`, performs in-depth research on each book. These agents have specialized roles (e.g., `facts-hunter`, `culture-impact`, `symbol-analyst`) and work in a coordinated sequence to gather information and populate the `book.yaml` file with their findings.
*   **Scene and Prompt Generation:** Based on the `book.yaml` data, the system generates 25 distinct scenes for each book. These scenes are then used to create detailed prompts for an AI image generator.
*   **AI Image Generation:** The project integrates with AI image generation tools like InvokeAI and ComfyUI to create visually appealing, non-photorealistic illustrations for each scene.
*   **Video Production:** A GPU-accelerated rendering pipeline (using FFmpeg with NVENC) assembles the generated images into a 1080x1920 video. It adds Ken Burns effects, animated text overlays, and transitions to create a polished final product suitable for TikTok.
*   **Static Site Generation:** The system can also generate an interactive HTML site to showcase the books and their generated content.

The project is highly configurable, using YAML files for settings (`config/settings.yaml`), book data, and collections (`collections/*.yaml`).

## Building and Running

The project uses `uv` for package management and Python 3.12+.

**Installation:**

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:user/37degrees.git
    cd 37degrees
    ```
2.  **Set up the environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your API keys
    ```
3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```

**Key Commands (via `main.py`):**

*   **List books and collections:**
    ```bash
    python main.py collections
    python main.py list classics
    ```
*   **Generate AI images:**
    ```bash
    # Use the mock generator for testing without a GPU
    python main.py ai 17 --generator mock

    # Generate for a specific book
    python main.py ai 17

    # Generate for an entire collection
    python main.py ai classics
    ```
*   **Generate video:**
    ```bash
    python main.py video 17
    ```
*   **Run the full pipeline (prompts, AI images, video):**
    ```bash
    python main.py generate 17
    ```
*   **Run the research agent system:**
    ```bash
    # This is a conceptual command from the README
    # /37d-research "The Little Prince"
    ```
*   **Generate the static site:**
    ```bash
    python main.py site
    ```

## Development Conventions

*   **Code Style:** The project follows PEP 8 for Python code. Use `snake_case` for variables and functions, and `PascalCase` for classes.
*   **Modularity:** The codebase is organized into modules within the `src` directory, with a clear separation of concerns (CLI, generators, research, etc.).
*   **Configuration:** Centralized configuration is managed in `config/settings.yaml` and can be overridden by environment variables or command-line flags.
*   **Data-Driven:** The content generation process is heavily data-driven, with `book.yaml` files serving as the single source of truth for each book.
*   **Extensibility:** The project uses a plugin-style architecture (Registry Pattern) for image generators and research providers, making it easy to add new components.
*   **Testing:** The primary method for testing is to use the `--generator mock` flag to run the pipeline without incurring API costs or requiring a GPU.
