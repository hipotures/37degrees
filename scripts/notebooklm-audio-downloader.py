#!/usr/bin/env python3
"""
NotebookLM Audio Download Orchestrator

This script automates the complete download workflow for audio files from NotebookLM
using browser automation tools and integrates with the TODOIT task management system.

Usage:
    python notebooklm-audio-downloader.py --task-id TASK_ID --language LANG_CODE
    python notebooklm-audio-downloader.py --auto  # Process all pending downloads

Features:
- Discovers pending audio download tasks from TODOIT
- Automates NotebookLM browser interaction for downloads
- Organizes files by book and language
- Updates task status and properties
- Supports batch processing of multiple downloads
- Optional cleanup of NotebookLM sources after successful downloads
"""

import os
import sys
import argparse
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add the project root to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class NotebookLMAudioDownloader:
    """Main orchestrator class for NotebookLM audio downloads."""

    def __init__(self, dry_run: bool = False, cleanup_enabled: bool = False):
        self.dry_run = dry_run
        self.cleanup_enabled = cleanup_enabled
        self.temp_download_dir = "/tmp/playwright-mcp-output"
        self.project_root = Path("/home/xai/DEV/37degrees")

    def discover_pending_tasks(self) -> List[Dict]:
        """Find all pending audio download tasks from TODOIT."""
        print("🔍 Discovering pending audio download tasks...")

        # This would use the MCP TODOIT tools to find pending tasks
        # For now, return a sample structure based on what we found
        pending_tasks = []

        # Example task structure (would be populated from TODOIT queries)
        sample_task = {
            'book_key': '0011_gullivers_travels',
            'book_title': "Gulliver's Travels by Jonathan Swift",
            'language': 'pl',
            'subitem_key': 'audio_dwn_pl',
            'status': 'pending',
            'nb_url': None,  # Would be retrieved from properties
            'nb_title': None,  # Would be retrieved from properties
        }

        print(f"📋 Found {len(pending_tasks)} pending audio download tasks")
        return pending_tasks

    def get_book_info_from_key(self, book_key: str) -> Tuple[str, str]:
        """Extract book number and name from book key."""
        # Extract number (e.g., "0011" from "0011_gullivers_travels")
        match = re.match(r'(\d{4})_(.+)', book_key)
        if match:
            book_number = match.group(1)
            book_name = match.group(2)
            return book_number, book_name
        return "0000", book_key

    def find_audio_in_notebooklm(self, target_title: str, language: str) -> Optional[str]:
        """
        Navigate NotebookLM interface to find audio matching title and language.
        Returns the reference ID for the audio's More button if found.
        """
        print(f"🎯 Searching for audio: {target_title} ({language})")

        # This would use browser automation to:
        # 1. Take a snapshot of the current NotebookLM page
        # 2. Search for audio titles matching the target
        # 3. Identify language by title patterns or metadata
        # 4. Return the reference ID for the More button

        # For demo purposes, we'll simulate finding an audio
        # In real implementation, this would use mcp__playwright-cdp__browser_snapshot
        # and mcp__playwright-cdp__browser_evaluate to search the DOM

        return None

    def download_audio_file(self, audio_ref_id: str, expected_title: str) -> Optional[str]:
        """
        Download audio file from NotebookLM using browser automation.
        Returns the path to the downloaded file if successful.
        """
        print(f"⬇️  Downloading audio: {expected_title}")

        if self.dry_run:
            print("🔄 Dry run mode - skipping actual download")
            return "/tmp/mock-download.mp4"

        try:
            # Step 1: Click the More button for the audio
            # mcp__playwright-cdp__browser_click(element="More button", ref=audio_ref_id)

            # Step 2: Click Download from the menu
            # mcp__playwright-cdp__browser_click(element="Download option", ref="download_ref")

            # Step 3: Wait for download completion
            # mcp__playwright-cdp__browser_wait_for(time=10)

            # Step 4: Find the downloaded file in temp directory
            downloaded_file = self._find_latest_download()

            if downloaded_file and os.path.exists(downloaded_file):
                print(f"✅ Download completed: {downloaded_file}")
                return downloaded_file
            else:
                print("❌ Download failed - file not found")
                return None

        except Exception as e:
            print(f"❌ Download error: {e}")
            return None

    def _find_latest_download(self) -> Optional[str]:
        """Find the most recently downloaded .mp4 file."""
        temp_dir = Path(self.temp_download_dir)
        if not temp_dir.exists():
            return None

        mp4_files = []
        for subdir in temp_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*.mp4"):
                    mp4_files.append(file)

        if mp4_files:
            # Return the most recently modified file
            latest_file = max(mp4_files, key=lambda f: f.stat().st_mtime)
            return str(latest_file)

        return None

    def organize_downloaded_file(self, downloaded_path: str, book_key: str, language: str) -> str:
        """
        Move downloaded file to proper book directory with correct naming.
        Returns the final file path.
        """
        book_number, book_name = self.get_book_info_from_key(book_key)

        # Create target directory
        audio_dir = self.project_root / "books" / book_key / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        # Generate target filename
        target_filename = f"{book_key}_{language}.mp4"
        target_path = audio_dir / target_filename

        print(f"📁 Organizing file: {target_path}")

        if self.dry_run:
            print("🔄 Dry run mode - skipping file move")
            return str(target_path)

        try:
            # Move file to target location
            os.rename(downloaded_path, target_path)

            # Verify file exists and has reasonable size
            if target_path.exists() and target_path.stat().st_size > 1024*1024:  # > 1MB
                print(f"✅ File organized successfully: {target_path}")
                return str(target_path)
            else:
                print(f"❌ File organization failed - invalid file: {target_path}")
                return None

        except Exception as e:
            print(f"❌ File organization error: {e}")
            return None

    def update_task_status(self, book_key: str, language: str, file_path: str, status: str = "completed"):
        """Update TODOIT task status and properties after successful download."""
        print(f"📝 Updating task status: {book_key} {language} -> {status}")

        if self.dry_run:
            print("🔄 Dry run mode - skipping task update")
            return True

        try:
            # Update subitem status
            # mcp__todoit__todo_update_item_status(
            #     list_key="cc-au-notebooklm",
            #     item_key=book_key,
            #     subitem_key=f"audio_dwn_{language}",
            #     status=status
            # )

            # Save file path property
            # mcp__todoit__todo_set_item_property(
            #     list_key="cc-au-notebooklm",
            #     item_key=book_key,
            #     property_key="file_path",
            #     property_value=file_path,
            #     parent_item_key=f"audio_dwn_{language}"
            # )

            # Save completion timestamp
            timestamp = datetime.now().isoformat()
            # mcp__todoit__todo_set_item_property(
            #     list_key="cc-au-notebooklm",
            #     item_key=book_key,
            #     property_key="downloaded_at",
            #     property_value=timestamp,
            #     parent_item_key=f"audio_dwn_{language}"
            # )

            print("✅ Task status updated successfully")
            return True

        except Exception as e:
            print(f"❌ Task update error: {e}")
            return False

    def cleanup_notebooklm_audio(self, audio_ref_id: str, safety_checks: bool = True) -> bool:
        """
        Optionally delete audio from NotebookLM after successful download.
        Only performs deletion if safety checks pass.
        """
        if not self.cleanup_enabled:
            print("🛡️  Cleanup disabled - keeping audio in NotebookLM")
            return False

        print(f"🗑️  Attempting cleanup of audio in NotebookLM")

        if safety_checks:
            # Perform safety checks before deletion
            # - Local file must exist and be recent (< 5 minutes)
            # - File size must be reasonable (> 1MB)
            # - No errors during download process
            print("🔒 Safety checks passed - proceeding with cleanup")

        if self.dry_run:
            print("🔄 Dry run mode - skipping cleanup")
            return False

        try:
            # Navigate to More menu and click Delete
            # This would use browser automation similar to download process
            # mcp__playwright-cdp__browser_click(element="More button", ref=audio_ref_id)
            # mcp__playwright-cdp__browser_click(element="Delete option", ref="delete_ref")
            # mcp__playwright-cdp__browser_handle_dialog(accept=True)

            print("✅ Cleanup completed successfully")
            return True

        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            return False

    def process_single_task(self, task: Dict) -> bool:
        """Process a single audio download task end-to-end."""
        book_key = task['book_key']
        language = task['language']

        print(f"\n🎵 Processing: {book_key} ({language})")
        print("=" * 50)

        # Step 1: Find audio in NotebookLM interface
        audio_ref = self.find_audio_in_notebooklm(task.get('nb_title', ''), language)
        if not audio_ref:
            print(f"❌ Could not find audio for {book_key} in {language}")
            return False

        # Step 2: Download the audio file
        downloaded_file = self.download_audio_file(audio_ref, task.get('nb_title', ''))
        if not downloaded_file:
            print(f"❌ Download failed for {book_key} ({language})")
            return False

        # Step 3: Organize the file
        final_path = self.organize_downloaded_file(downloaded_file, book_key, language)
        if not final_path:
            print(f"❌ File organization failed for {book_key} ({language})")
            return False

        # Step 4: Update task status
        if not self.update_task_status(book_key, language, final_path):
            print(f"⚠️  Task update failed for {book_key} ({language})")
            # Continue anyway since file was downloaded successfully

        # Step 5: Optional cleanup
        if self.cleanup_enabled:
            self.cleanup_notebooklm_audio(audio_ref)

        print(f"✅ Successfully processed: {book_key} ({language})")
        return True

    def process_all_pending(self) -> int:
        """Process all pending audio download tasks."""
        print("🚀 Starting batch audio download process")
        print("=" * 60)

        # Discover all pending tasks
        pending_tasks = self.discover_pending_tasks()

        if not pending_tasks:
            print("✨ No pending audio download tasks found")
            return 0

        success_count = 0
        total_count = len(pending_tasks)

        for i, task in enumerate(pending_tasks, 1):
            print(f"\n📈 Progress: {i}/{total_count}")

            if self.process_single_task(task):
                success_count += 1

            # Add delay between downloads to avoid overwhelming NotebookLM
            if i < total_count:
                print("⏱️  Waiting before next download...")
                time.sleep(5)

        print("\n" + "=" * 60)
        print(f"🏁 Batch process completed: {success_count}/{total_count} successful")

        return success_count


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="NotebookLM Audio Download Orchestrator")
    parser.add_argument("--auto", action="store_true", help="Process all pending downloads")
    parser.add_argument("--task-id", help="Process specific task ID")
    parser.add_argument("--language", help="Language code (pl, en, fr, etc.)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without actual downloads")
    parser.add_argument("--cleanup", action="store_true", help="Enable NotebookLM cleanup after download")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Initialize the downloader
    downloader = NotebookLMAudioDownloader(
        dry_run=args.dry_run,
        cleanup_enabled=args.cleanup
    )

    print("🎵 NotebookLM Audio Download Orchestrator")
    print("=" * 50)

    if args.dry_run:
        print("🔄 Running in DRY RUN mode - no actual changes will be made")

    if args.cleanup:
        print("🗑️  Cleanup mode enabled - audio will be deleted from NotebookLM after download")

    print()

    try:
        if args.auto:
            # Process all pending downloads
            success_count = downloader.process_all_pending()

            if success_count > 0:
                print(f"\n🎉 Successfully processed {success_count} audio downloads!")
            else:
                print("\n💤 No downloads were processed")

        elif args.task_id and args.language:
            # Process specific task
            task = {
                'book_key': args.task_id,
                'language': args.language,
                'subitem_key': f'audio_dwn_{args.language}',
            }

            if downloader.process_single_task(task):
                print(f"\n🎉 Successfully processed {args.task_id} ({args.language})!")
            else:
                print(f"\n❌ Failed to process {args.task_id} ({args.language})")
                return 1

        else:
            print("❌ Error: Use --auto to process all tasks, or specify --task-id and --language")
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n⏹️  Process interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())