#!/usr/bin/env python3
"""
TODOIT Properties to Subtasks Converter
Konwersja systemu properties na hierarchiczne subtaski

Wykorzystuje automatyczną synchronizację statusów (TODOIT v1.20.0+):
- Status głównego taska jest automatycznie kalkulowany na podstawie subtasków
- Nie wymaga ręcznej synchronizacji statusów
- System automatycznie propaguje zmiany w górę hierarchii
"""

import subprocess
import json
import sys
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TodoitConverter:
    """Klasa do konwersji properties na subtaski w TODOIT"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.backup_dir = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.conversion_log = []
        
        # Definicja mapowania subtasków i ich properties
        self.subtask_definitions = [
            {"key": "scene_gen", "desc": "Generowanie sceny", "props": ["generator"]},
            {"key": "scene_style", "desc": "Generowanie sceny ze stylem", "props": ["style"]},
            {"key": "image_gen", "desc": "Generowanie obrazu", "props": ["thread_id"]},
            {"key": "image_dwn", "desc": "Pobranie obrazu", "props": ["path_filename", "image_url"]},
            {"key": "audio_gen", "desc": "Wygenerowanie pliku audio", "props": ["voice_id", "text", "audio_params"]},
            {"key": "audio_dwn", "desc": "Pobranie pliku audio", "props": ["path_filename", "audio_url"]},
            {"key": "video_gen", "desc": "Wygenerowanie finalnego wideo", "props": ["path_filename", "duration", "resolution"]}
        ]
        
    def run_todoit_command(self, command: str, capture_output: bool = True) -> Optional[str]:
        """Wykonaj komendę TODOIT CLI"""
        try:
            logger.debug(f"Executing: {command}")
            
            if self.dry_run and any(cmd in command for cmd in ['add', 'delete', 'set', 'create', 'update']):
                logger.info(f"[DRY-RUN] Would execute: {command}")
                return None
                
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=True
            )
            return result.stdout if capture_output else None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}")
            logger.error(f"Error: {e.stderr}")
            raise
            
    def generate_unique_key(self, length: int = 8) -> str:
        """Generuj unikalny klucz alfanumeryczny"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        
    def get_list_info(self, list_key: str) -> Optional[Dict]:
        """Pobierz informacje o liście"""
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit list show "{list_key}"'
            )
            if output:
                return json.loads(output)
            return None
        except:
            return None
            
    def get_all_lists(self) -> List[str]:
        """Pobierz wszystkie listy książek (katalogi zaczynające się od cyfr)"""
        try:
            output = self.run_todoit_command(
                'TODOIT_OUTPUT_FORMAT=json todoit list all'
            )
            if output:
                data = json.loads(output)
                # Filtruj listy książek (zaczynające się od cyfr)
                book_lists = []
                for item in data.get('data', []):
                    key = item.get('Key', '')
                    if key and key[0].isdigit() and '_' in key:
                        book_lists.append(key)
                return book_lists
            return []
        except:
            return []
            
    def get_list_items(self, list_key: str) -> List[Dict]:
        """Pobierz wszystkie itemy z listy"""
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit list show "{list_key}"'
            )
            if output:
                data = json.loads(output)
                items = []
                # Items are in data['items']['data'], not data['data']
                items_data = data.get('items', {}).get('data', [])
                for item in items_data:
                    # Accept all items with a Key, not just those starting with specific prefixes
                    if item.get('Key'):
                        items.append(item)
                return items
            return []
        except:
            return []
            
    def get_item_properties(self, list_key: str, item_key: str) -> Dict[str, str]:
        """Pobierz wszystkie properties dla danego itemu"""
        properties = {}
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit item property list "{list_key}"'
            )
            if output:
                data = json.loads(output)
                for prop in data.get('data', []):
                    if prop.get('Item Key') == item_key:
                        prop_key = prop.get('Property Key', '')
                        prop_value = prop.get('Value', '')
                        properties[prop_key] = prop_value
            return properties
        except:
            return properties
            
    def backup_list(self, list_key: str):
        """Utwórz backup listy"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        logger.info(f"Creating backup for list: {list_key}")
        
        # Backup list info
        list_info = self.get_list_info(list_key)
        if list_info:
            backup_file = self.backup_dir / f"{list_key}_list.json"
            with open(backup_file, 'w') as f:
                json.dump(list_info, f, indent=2)
                
        # Backup properties
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit item property list "{list_key}"'
            )
            if output:
                backup_file = self.backup_dir / f"{list_key}_properties.json"
                with open(backup_file, 'w') as f:
                    f.write(output)
        except:
            pass
            
    def create_main_task(self, list_key: str) -> str:
        """Utwórz główny task dla listy"""
        task_key = self.generate_unique_key()
        scene_count = len(self.get_list_items(list_key))
        task_content = f"scene:{scene_count} Dane itemów listy będą w properties subtasków"
        
        logger.info(f"Creating main task: {task_key} for list: {list_key}")
        
        self.run_todoit_command(
            f'todoit item add "{list_key}" "{task_key}" "{task_content}"'
        )
        
        # Status głównego taska będzie automatycznie synchronizowany
        # na podstawie statusów subtasków (TODOIT v1.20.0+)
        logger.info(f"  Main task status will be auto-synchronized from subtasks")
        
        return task_key
        
    def migrate_item_to_subtasks(self, original_list_key: str, new_list_key: str, main_task_key: str, item: Dict) -> int:
        """Migruj pojedynczy item na subtaski"""
        item_key = item.get('Key', '')
        item_content = item.get('Task', '')  # Używamy 'Task' zamiast 'Content'
        
        logger.info(f"  Migrating item: {item_key}")
        
        # Pobierz properties itemu z oryginalnej listy
        properties = self.get_item_properties(original_list_key, item_key)
        
        # Mapowanie properties na subtaski
        subtasks_created = 0
        
        for subtask_def in self.subtask_definitions:
            subtask_key = f"{main_task_key}_{subtask_def['key']}"  # Dodaj prefix głównego taska
            subtask_content = f"{subtask_def['desc']} - {item_content}"
            
            # Utwórz subtask w nowej liście
            logger.info(f"    Creating subtask: {subtask_key}")
            self.run_todoit_command(
                f'todoit item add-subtask "{new_list_key}" "{main_task_key}" "{subtask_key}" "{subtask_content}"'
            )
            
            # Przenieś odpowiednie properties do nowej listy
            for prop_key in subtask_def['props']:
                if prop_key in properties:
                    prop_value = properties[prop_key]
                    logger.info(f"      Setting property: {prop_key}={prop_value}")
                    self.run_todoit_command(
                        f'todoit item property set "{new_list_key}" "{subtask_key}" "{prop_key}" "{prop_value}"'
                    )
                    
            # Ustaw status subtaska na podstawie properties
            status = self.determine_subtask_status(subtask_def['key'], properties)
            if status != 'pending':
                self.run_todoit_command(
                    f'todoit item status "{new_list_key}" "{subtask_key}" --status {status}'
                )
                
            subtasks_created += 1
            
        return subtasks_created
        
    def determine_subtask_status(self, subtask_type: str, properties: Dict) -> str:
        """Określ status subtaska na podstawie properties"""
        status_mapping = {
            'scene_gen': 'image_generated',
            'scene_style': 'style_applied',
            'image_gen': 'image_generated',
            'image_dwn': 'image_downloaded',
            'audio_gen': 'audio_generated',
            'audio_dwn': 'audio_downloaded',
            'video_gen': 'video_generated'
        }
        
        prop_key = status_mapping.get(subtask_type)
        if prop_key and prop_key in properties:
            prop_value = properties[prop_key]
            if prop_value == 'completed':
                return 'completed'
            elif prop_value == 'in_progress':
                return 'in_progress'
            elif prop_value == 'failed':
                return 'failed'
                
        return 'pending'
        
    def delete_old_items(self, list_key: str, items_to_delete: List[str]):
        """Usuń stare itemy po migracji"""
        logger.info(f"Deleting {len(items_to_delete)} old items from list: {list_key}")
        
        for item_key in items_to_delete:
            logger.info(f"  Deleting item: {item_key}")
            self.run_todoit_command(
                f'todoit item delete "{list_key}" "{item_key}" --force'
            )
            
    def create_new_list(self, original_list_key: str) -> str:
        """Stwórz nową listę z sufiksem _subtask"""
        new_list_key = f"{original_list_key}_subtask"
        
        # Pobierz info o oryginalnej liście
        original_info = self.get_list_info(original_list_key)
        original_title = original_info.get('list_info', {}).get('title', '') if original_info else ''
        new_title = f"{original_title} (Subtasks)" if original_title else f"{original_list_key} (Subtasks)"
        
        logger.info(f"Creating new list: {new_list_key} with title: {new_title}")
        
        self.run_todoit_command(
            f'todoit list create "{new_list_key}" --title "{new_title}"'
        )
        
        return new_list_key

    def process_list(self, list_key: str) -> Tuple[bool, Dict]:
        """Przetwórz pojedynczą listę"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing list: {list_key}")
        logger.info(f"{'='*60}")
        
        result = {
            'list_key': list_key,
            'new_list_key': None,
            'items_migrated': 0,
            'subtasks_created': 0,
            'items_deleted': 0,
            'errors': []
        }
        
        try:
            # Backup oryginalnej listy
            self.backup_list(list_key)
            
            # Pobierz itemy z oryginalnej listy
            items = self.get_list_items(list_key)
            if not items:
                logger.warning(f"No items found in list: {list_key}")
                return True, result
                
            logger.info(f"Found {len(items)} items to migrate")
            
            # Stwórz nową listę
            new_list_key = self.create_new_list(list_key)
            result['new_list_key'] = new_list_key
            
            # Migruj każdy item jako osobny główny task z subtaskami
            for item in items:
                try:
                    # Utwórz główny task dla tego itemu
                    item_key = item.get('Key', '')
                    item_content = item.get('Task', '')
                    # Przekształć item_0001 na scene_0001
                    if item_key.startswith('item_'):
                        main_task_key = item_key.replace('item_', 'scene_')
                    else:
                        main_task_key = f"scene_{item_key}"
                    
                    logger.info(f"Creating main task for item: {item_key} -> {main_task_key}")
                    self.run_todoit_command(
                        f'todoit item add "{new_list_key}" "{main_task_key}" "{item_content}"'
                    )
                    
                    # Migruj item na subtaski pod tym głównym taskiem
                    subtasks = self.migrate_item_to_subtasks(list_key, new_list_key, main_task_key, item)
                    result['items_migrated'] += 1
                    result['subtasks_created'] += subtasks
                except Exception as e:
                    error_msg = f"Failed to migrate item {item.get('Key')}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                    
            # Nie usuwamy starych itemów - zostawiamy oryginalną listę nietknętą
            logger.info(f"Migration complete. Original list '{list_key}' left intact.")
                
            logger.info(f"\n✅ Successfully processed list: {list_key}")
            logger.info(f"   New list: {new_list_key}")
            logger.info(f"   Items migrated: {result['items_migrated']}")
            logger.info(f"   Subtasks created: {result['subtasks_created']}")
            logger.info(f"   Parent status: Auto-synchronized from subtasks")
            
            return True, result
            
        except Exception as e:
            error_msg = f"Failed to process list {list_key}: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            return False, result
            
    def verify_conversion(self, list_key: str, result: Dict):
        """Weryfikuj poprawność konwersji"""
        logger.info(f"\nVerifying conversion for list: {list_key}")
        
        if not result.get('main_task_key'):
            logger.error("No main task created!")
            return False
            
        # Sprawdź główny task
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit item show "{list_key}" "{result["main_task_key"]}"'
            )
            if output:
                data = json.loads(output)
                main_task_status = data.get('status', 'unknown')
                logger.info(f"✓ Main task exists: {result['main_task_key']}")
                logger.info(f"  Auto-synchronized status: {main_task_status}")
            else:
                logger.error(f"✗ Main task not found: {result['main_task_key']}")
                return False
        except:
            logger.error(f"✗ Failed to verify main task")
            return False
            
        # Sprawdź subtaski
        try:
            output = self.run_todoit_command(
                f'TODOIT_OUTPUT_FORMAT=json todoit item subtasks "{list_key}" "{result["main_task_key"]}"'
            )
            if output:
                data = json.loads(output)
                subtask_count = len(data.get('data', []))
                logger.info(f"✓ Found {subtask_count} subtasks")
                
                if subtask_count != result['subtasks_created']:
                    logger.warning(f"⚠ Expected {result['subtasks_created']} subtasks, found {subtask_count}")
                    
                # Analiza statusów subtasków
                status_counts = {}
                for subtask in data.get('data', []):
                    status = subtask.get('Status', 'pending')
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                logger.info(f"  Subtask status distribution: {status_counts}")
                
                # Weryfikacja automatycznej synchronizacji
                expected_parent_status = self.calculate_expected_parent_status(status_counts)
                logger.info(f"  Expected parent status (based on subtasks): {expected_parent_status}")
                
                # Porównaj z faktycznym statusem głównego taska
                if main_task_status == expected_parent_status:
                    logger.info(f"✓ Status synchronization working correctly!")
                else:
                    logger.warning(f"⚠ Status mismatch: expected {expected_parent_status}, got {main_task_status}")
                    
            else:
                logger.error("✗ No subtasks found")
                return False
        except:
            logger.error("✗ Failed to verify subtasks")
            return False
            
        return True
        
    def calculate_expected_parent_status(self, status_counts: Dict[str, int]) -> str:
        """Oblicz oczekiwany status rodzica na podstawie statusów subtasków (TODOIT v1.20.0 logic)"""
        # Logika z automatycznej synchronizacji TODOIT
        if status_counts.get('failed', 0) > 0 or status_counts.get('❌', 0) > 0:
            return 'failed'
        elif all(status == 'pending' or status == '⏳' for status in status_counts.keys()):
            return 'pending'
        elif all(status == 'completed' or status == '✅' for status in status_counts.keys()):
            return 'completed'
        else:
            return 'in_progress'
        
    def run_conversion(self, list_key: Optional[str] = None):
        """Uruchom proces konwersji"""
        logger.info("Starting TODOIT Properties to Subtasks Conversion")
        logger.info(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        
        if list_key:
            # Konwersja pojedynczej listy
            lists_to_process = [list_key]
        else:
            # Konwersja wszystkich list książek
            lists_to_process = self.get_all_lists()
            
        if not lists_to_process:
            logger.error("No lists found to process")
            return False
            
        logger.info(f"Found {len(lists_to_process)} lists to process")
        
        # Potwierdzenie
        if not self.dry_run:
            print(f"\n⚠️  WARNING: This will modify {len(lists_to_process)} lists!")
            print("Lists to process:", ', '.join(lists_to_process))
            response = input("\nContinue? (y/n): ")
            if response.lower() not in ['y', 'yes']:
                logger.info("Conversion cancelled by user")
                return False
                
        # Przetwarzanie list
        results = []
        successful = 0
        failed = 0
        
        for list_key in lists_to_process:
            success, result = self.process_list(list_key)
            results.append(result)
            
            if success:
                successful += 1
                if not self.dry_run:
                    self.verify_conversion(list_key, result)
            else:
                failed += 1
                
        # Podsumowanie
        logger.info("\n" + "="*60)
        logger.info("CONVERSION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total lists processed: {len(lists_to_process)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        
        total_items = sum(r['items_migrated'] for r in results)
        total_subtasks = sum(r['subtasks_created'] for r in results)
        total_deleted = sum(r['items_deleted'] for r in results)
        
        logger.info(f"Total items migrated: {total_items}")
        logger.info(f"Total subtasks created: {total_subtasks}")
        logger.info(f"Total items deleted: {total_deleted}")
        
        if self.backup_dir.exists():
            logger.info(f"\nBackup saved to: {self.backup_dir}")
            
        # Zapisz raport
        report_file = Path(f"conversion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'mode': 'dry_run' if self.dry_run else 'live',
                'summary': {
                    'total_lists': len(lists_to_process),
                    'successful': successful,
                    'failed': failed,
                    'total_items_migrated': total_items,
                    'total_subtasks_created': total_subtasks,
                    'total_items_deleted': total_deleted
                },
                'results': results
            }, f, indent=2)
            
        logger.info(f"Detailed report saved to: {report_file}")
        
        return failed == 0


def main():
    """Główna funkcja programu"""
    parser = argparse.ArgumentParser(
        description='Convert TODOIT properties to subtasks structure'
    )
    parser.add_argument(
        'list_key',
        nargs='?',
        help='Specific list key to convert (e.g., 0011_gullivers_travels). If not provided, converts all book lists.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate conversion without making changes'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
    converter = TodoitConverter(dry_run=args.dry_run)
    
    try:
        success = converter.run_conversion(args.list_key)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nConversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
