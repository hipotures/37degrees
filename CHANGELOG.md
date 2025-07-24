# Changelog

All notable changes to the 37degrees project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-24

This major release introduces a plugin architecture for image generators and a centralized configuration system, making the project more extensible and maintainable.

### Added

#### Plugin Architecture for Image Generators
- **Abstract Base Class** (`src/generators/base.py`): All generators now inherit from `BaseImageGenerator`
- **Generator Registry** (`src/generators/registry.py`): Dynamic plugin loading and management
- **Mock Generator** (`src/generators/mock.py`): Testing without GPU or external services
- **Retry Mechanism**: Automatic retry with exponential backoff for transient failures
- **CLI Support**: `--generator` flag to select image generator

#### Centralized Configuration System
- **Main Config File** (`config/settings.yaml`): Single source of truth for all settings
- **Environment Variables**: Support for `.env` files with automatic loading
- **Variable Substitution**: `${VAR}` and `${VAR:-default}` syntax in YAML
- **CLI Overrides**: `--set key=value` to override any setting
- **Custom Configs**: `--config file.yaml` to use alternative configuration

#### AI-Powered Research Integration
- **Research Module** (`src/research/`): Extensible research provider system
- **Perplexity AI Integration**: Real-time web search for book facts
- **Google Search Integration**: Alternative research provider
- **Review Generator**: Automatic `review.md` creation with Polish content
- **CLI Command**: `python main.py research` with provider selection
- **Caching System**: Smart caching of API responses

#### Static HTML Site Generator
- **Site Generator Module** (`src/site_generator/`): Complete static site system
- **Book Pages**: Interactive HTML pages from book.yaml data
- **Collection Pages**: Overview pages for each book collection
- **Main Index**: Beautiful landing page with all collections
- **CLI Command**: `python main.py site` for site generation
- **Responsive Design**: Mobile-friendly with Tailwind CSS

#### Documentation
- `docs/PLUGIN_ARCHITECTURE.md`: Guide for creating custom image generators
- `docs/CONFIGURATION.md`: Complete configuration system documentation
- `docs/RESEARCH_API.md`: Research provider integration guide
- `docs/STATIC_SITE_GENERATOR.md`: Site generation documentation
- `.env.example`: Template for environment variables

### Changed

#### Refactored Modules
- **InvokeAI Generator**: Now inherits from base class, moved to `src/generators/invokeai.py`
- **ComfyUI Generator**: Now inherits from base class, moved to `src/generators/comfyui.py`
- **CLI Module** (`src/cli/ai.py`): Updated to use generator registry
- **Main Entry Point**: Added configuration override support

#### Improved Features
- Better error handling with custom exception types
- Reduced environment variable warnings with `.env` support
- More flexible generator selection and configuration
- Cleaner code organization with plugin structure

### Fixed
- Environment variable warnings now only show for truly missing required variables
- Import paths standardized across the project
- Configuration loading is now more robust

### Technical Details

#### Breaking Changes
- Generator classes must now inherit from `BaseImageGenerator`
- Direct instantiation of generators deprecated in favor of registry
- Some import paths have changed (but CLI interface remains the same)

#### Migration Guide
For users upgrading from v1.x:
1. Copy `.env.example` to `.env` and configure as needed
2. Update any custom scripts to use the new generator registry
3. No changes needed for standard CLI usage

### Future Plans
The refactoring in v2.0.0 lays groundwork for:
- Web-based image generators (ChatGPT, Midjourney via browser automation)
- AI-powered research for book reviews
- Static site generation for all books
- Reference and citation management

## [1.0.0] - 2024-12-XX

### Initial Release
- Basic video generation for TikTok book reviews
- InvokeAI integration for image generation
- Text overlay with multiple rendering methods
- Support for 37 classic books
- CLI interface for all operations