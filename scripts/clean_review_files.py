#!/usr/bin/env python3
"""
Clean review.txt files from exported format.

This script removes formatting artifacts from review.txt files while preserving
all original content. Uses safety markers to verify content integrity.
"""

import argparse
import glob
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class ReviewFileCleaner:
    """Clean review.txt files with safety verification."""

    def __init__(self, dry_run: bool = False, backup: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.backup = backup
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")

    def extract_safety_markers(self, content: str) -> List[str]:
        """Extract 5 sample sentences from different positions in the content."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        if len(lines) < 5:
            return lines  # If file is too short, use all lines

        # Extract sentences from strategic positions
        positions = [
            min(19, len(lines) - 1),  # Around line 20
            min(99, len(lines) - 1),  # Around line 100
            min(199, len(lines) - 1), # Around line 200
            min(299, len(lines) - 1), # Around line 300
            len(lines) - 1            # Last line
        ]

        markers = []
        for pos in positions:
            if pos < len(lines):
                line = lines[pos]
                # Extract first sentence (up to first period, or whole line if no period)
                sentence = line.split('.')[0].strip()
                if sentence:
                    markers.append(sentence)

        # Remove duplicates while preserving order
        unique_markers = []
        for marker in markers:
            if marker not in unique_markers:
                unique_markers.append(marker)

        return unique_markers[:5]  # Ensure we have at most 5 markers

    def verify_safety_markers(self, original_content: str, cleaned_content: str) -> Tuple[bool, List[str]]:
        """Verify that all safety markers exist in cleaned content."""
        markers = self.extract_safety_markers(original_content)
        missing_markers = []

        for marker in markers:
            if marker not in cleaned_content:
                missing_markers.append(marker)

        return len(missing_markers) == 0, missing_markers

    def fix_encoding(self, content: str) -> str:
        """Fix corrupted Polish characters from encoding issues."""
        try:
            # Try to fix UTF-8 bytes interpreted as Latin-1
            content_bytes = content.encode('latin1')
            fixed_content = content_bytes.decode('utf-8')
            self.log("Fixed UTF-8 encoding issues")
            return fixed_content
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If that fails, return original content
            return content

    def clean_content(self, content: str) -> str:
        """Clean the content by removing formatting artifacts."""

        # 0. Fix encoding issues first
        original_content = content
        content = self.fix_encoding(content)
        if content != original_content:
            self.log("Fixed character encoding")

        # 1. Remove BOM character
        if content.startswith('\ufeff'):
            content = content[1:]
            self.log("Removed BOM character")

        # 2. Remove line number prefixes (format: "number→")
        content = re.sub(r'^\s*\d+→', '', content, flags=re.MULTILINE)
        self.log("Removed line number prefixes")

        # 3. Replace tabs with 4 spaces
        tab_count = content.count('\t')
        if tab_count > 0:
            content = content.replace('\t', '    ')
            self.log(f"Replaced {tab_count} tabs with spaces")

        # 4. Remove trailing whitespace and normalize excessive leading spaces
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]

        # Fix excessive leading spaces (more than 8 spaces gets reduced to 4)
        excessive_spaces_fixed = 0
        normalized_lines = []
        for line in lines:
            if line.startswith(' ' * 20):  # Lines with 20+ leading spaces
                # Reduce to 4 spaces max
                stripped = line.lstrip(' ')
                normalized_lines.append('    ' + stripped)
                excessive_spaces_fixed += 1
            else:
                normalized_lines.append(line)

        content = '\n'.join(normalized_lines)
        if excessive_spaces_fixed > 0:
            self.log(f"Fixed {excessive_spaces_fixed} lines with excessive leading spaces")
        else:
            self.log("Removed trailing whitespace")

        # 5. Collapse multiple consecutive newlines to maximum 2
        original_newlines = len(re.findall(r'\n{3,}', content))
        content = re.sub(r'\n{3,}', '\n\n', content)
        if original_newlines > 0:
            self.log(f"Collapsed {original_newlines} excessive newline sequences")

        # 6. Ensure file ends with single newline
        content = content.rstrip() + '\n'

        return content

    def process_file(self, file_path: Path) -> bool:
        """Process a single review.txt file."""
        self.log(f"Processing: {file_path}")

        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Extract safety markers before cleaning
            safety_markers = self.extract_safety_markers(original_content)
            self.log(f"Extracted {len(safety_markers)} safety markers")

            # Clean content
            cleaned_content = self.clean_content(original_content)

            # Verify safety markers
            markers_safe, missing_markers = self.verify_safety_markers(original_content, cleaned_content)

            if not markers_safe:
                self.log(f"SAFETY CHECK FAILED: Missing markers: {missing_markers}", "ERROR")
                return False

            self.log("Safety markers verified - all content preserved")

            # Show stats
            original_lines = len(original_content.split('\n'))
            cleaned_lines = len(cleaned_content.split('\n'))
            self.log(f"Lines: {original_lines} → {cleaned_lines}")

            if self.dry_run:
                self.log("DRY RUN: Would save cleaned content", "DRYRUN")
                return True

            # Backup original file if requested
            if self.backup:
                backup_path = file_path.with_suffix('.txt.backup')
                backup_path.write_text(original_content, encoding='utf-8')
                self.log(f"Created backup: {backup_path}")

            # Write cleaned content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            self.log(f"Successfully cleaned: {file_path}")
            return True

        except Exception as e:
            self.log(f"ERROR processing {file_path}: {e}", "ERROR")
            return False

    def process_files(self, file_paths: List[Path]) -> Tuple[int, int]:
        """Process multiple files and return success/failure counts."""
        success_count = 0
        failure_count = 0

        for file_path in file_paths:
            if self.process_file(file_path):
                success_count += 1
            else:
                failure_count += 1

        return success_count, failure_count


def main():
    parser = argparse.ArgumentParser(description='Clean review.txt files from exported format')
    parser.add_argument('files', nargs='*', help='Specific files to process (default: all books/*/docs/review.txt)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without modifying files')
    parser.add_argument('--backup', action='store_true', help='Create backup files (.txt.backup)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Determine files to process
    if args.files:
        file_paths = [Path(f) for f in args.files if Path(f).exists()]
        if not file_paths:
            print("Error: No valid files specified")
            sys.exit(1)
    else:
        # Find all review.txt files
        pattern = "books/*/docs/review.txt"
        file_paths = [Path(p) for p in glob.glob(pattern)]
        if not file_paths:
            print(f"Error: No files found matching pattern: {pattern}")
            sys.exit(1)

    print(f"Found {len(file_paths)} file(s) to process")

    # Create cleaner instance
    cleaner = ReviewFileCleaner(
        dry_run=args.dry_run,
        backup=args.backup,
        verbose=args.verbose
    )

    # Process files
    success_count, failure_count = cleaner.process_files(file_paths)

    # Summary
    print(f"\nProcessing complete:")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {failure_count}")

    if args.dry_run:
        print("  (DRY RUN - no files were modified)")

    if failure_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()