#!/usr/bin/env python3
"""
Script to update scene generators to use proportional distribution instead of fixed 25 scenes
"""
import re
import os
from pathlib import Path

def update_generator_file(filepath):
    """Update a single generator file to use proportional distribution"""

    with open(filepath, 'r') as f:
        content = f.read()

    # Track if file was modified
    original = content

    # Fix duplicated text from bad sed command
    content = re.sub(
        r'Create scene descriptions for podcast illustration generation\. The total number.*?Distribute scenes proportionally ',
        'Create scene descriptions for podcast illustration generation. The total number of scenes is defined by scene_count in the configuration. Distribute scenes proportionally ',
        content,
        flags=re.DOTALL
    )

    # Remove specific scene numbers from section headers
    # Pattern: ### Something (Scenes X-Y) or ### Scenes X-Y: Something
    content = re.sub(r'### (.*?)\s*\(Scenes? \d+-?\d*\)', r'### \1', content)
    content = re.sub(r'### Scenes? \d+-?\d*:\s*(.*)', r'### \1', content)

    # Add percentage indicators to main sections
    # Count how many ### sections exist (excluding those in examples or tools)
    main_sections = re.findall(r'^### [^#].*$', content, re.MULTILINE)
    main_sections = [s for s in main_sections if 'Example' not in s and 'Tool' not in s and 'Technique' not in s]

    if len(main_sections) > 0:
        # Calculate percentage per section
        if len(main_sections) == 3:
            # Three-act structure
            percentages = ['30-35%', '40-45%', '25-30%']
        elif len(main_sections) == 5:
            # Five-act structure
            percentages = ['20%'] * 5
        else:
            # Equal distribution
            pct = 100 // len(main_sections)
            percentages = [f'{pct}%'] * len(main_sections)

        # Add percentages to section headers if not already present
        for i, section in enumerate(main_sections):
            if i < len(percentages) and '% of total scene_count' not in section:
                old_section = section
                # Extract just the title part
                title = section.replace('###', '').strip()
                new_section = f'### {title} ({percentages[i]} of total scene_count)'
                content = content.replace(old_section, new_section)

    # Remove specific scene number references in bullet points
    # Pattern: - **X-Y**: or - **X**:
    content = re.sub(r'^- \*\*\d+-?\d*\*\*:\s*', '- **', content, flags=re.MULTILINE)

    # Replace numbered bullets with descriptive ones
    replacements = [
        (r'- \*\*1-?\d*\*\*:', '- **Opening:'),
        (r'- \*\*\d+-\d+\*\*:.*?[Ee]arly', '- **Early scenes:'),
        (r'- \*\*\d+-\d+\*\*:.*?[Mm]iddle', '- **Middle section:'),
        (r'- \*\*\d+-\d+\*\*:.*?[Ll]ate', '- **Late section:'),
        (r'- \*\*\d+\*\*:.*?[Ff]inal', '- **Closing:'),
        (r'- \*\*\d+\*\*:.*?[Ll]ast', '- **Final moment:'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Update any remaining "25 scenes" references
    content = re.sub(r'\b25 scenes?\b', 'the total scenes', content, flags=re.IGNORECASE)
    content = re.sub(r'through 25 carefully', 'through carefully', content)

    # Only write if changed
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    """Process all generator files"""
    generator_dir = Path('/home/xai/DEV/37degrees/config/prompt/scene-generator')

    # Skip these files as they're already done or special
    skip_files = ['narrative-prompt-generator.md', 'atmospheric-moments-generator.md',
                  'character-perspective-generator.md']

    updated = []
    for filepath in generator_dir.glob('*.md'):
        if filepath.name in skip_files:
            print(f"Skipping {filepath.name} (already updated)")
            continue

        print(f"Processing {filepath.name}...")
        if update_generator_file(filepath):
            updated.append(filepath.name)
            print(f"  ✓ Updated")
        else:
            print(f"  - No changes needed")

    print(f"\nUpdated {len(updated)} files:")
    for name in updated:
        print(f"  - {name}")

if __name__ == '__main__':
    main()