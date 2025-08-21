# 37 Degrees - Agent Guidelines

## Build/Lint/Test Commands
- **Install**: `uv pip install -r requirements.txt`
- **Lint**: No formal linter configured (follow PEP 8 manually)
- **Test single script**: `python scripts/test_html_video.py` or `python scripts/test_download.py 0009_fahrenheit_451`
- **Quick test**: `python main.py ai 17 --generator mock` (no GPU/API costs)
- **Full pipeline test**: `python main.py generate 17`

## Code Style Guidelines
- **Python**: 3.12+ with PEP 8, 4-space indentation, docstrings for public functions
- **Imports**: Standard library first, then third-party, then local imports (alphabetized within groups)
- **Types**: Use type hints for function parameters and return values
- **Naming**: `snake_case` for functions/variables/modules, `PascalCase` for classes
- **Error handling**: Use specific exceptions, log errors with context
- **Functions**: Keep small and focused; prefer editing existing modules over creating new ones
- **Documentation**: English only, comprehensive docstrings with Args/Returns sections

## Project Structure
- `src/`: Core Python package with CLI, generators, research, and site generation
- `books/NNNN_slug/`: Per-book assets (zero-padded 4-digit index + short slug)
- `config/`: YAML configs and prompt templates
- `scripts/`: Utility scripts for batch operations and testing
- Entry point: `python main.py` (comprehensive CLI with subcommands)

## Development Workflow
- Use `python main.py ai <book_id> --generator mock` for quick testing
- Verify outputs in `output/` directory before committing
- Never commit secrets, large binaries, or derived media files
- Follow conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`
