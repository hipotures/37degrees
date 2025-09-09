#!/usr/bin/env python3
import csv
import json

def clean_scores_csv():
    """Clean the audio_format_scores.csv file"""
    input_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'
    output_path = '/home/xai/DEV/37degrees/config/audio_format_scores_clean.csv'
    
    # Define the correct headers for scores CSV
    headers = [
        'book_folder_id', 'title', 'year', 'translations_count',
        'A_kontrowersyjnosc', 'B_glebia', 'C_fenomen', 'D_rezonans', 
        'E_polski_kontekst', 'F_aktualnosc', 'G_innowacyjnosc', 
        'H_zlozonosc', 'I_gender',
        'B_jung_3plus', 'B_symbolika_relig_mit', 'B_warstwy_3plus', 'B_metafory_egzyst',
        'last3_formats'
    ]
    
    seen_books = set()
    clean_rows = []
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book_id = row.get('book_folder_id', '')
            
            # Skip empty rows or duplicates
            if not book_id or book_id in seen_books:
                continue
            
            seen_books.add(book_id)
            
            # Clean up the last3_formats field
            last3_formats = row.get('last3_formats', '[]')
            
            # Fix escaped quotes and malformed JSON
            if last3_formats:
                # Remove escape sequences
                last3_formats = last3_formats.replace('\\"', '"')
                # Remove any surrounding quotes if they exist
                if last3_formats.startswith('"[') and last3_formats.endswith(']"'):
                    last3_formats = last3_formats[1:-1]
                # Fix broken JSON arrays
                if last3_formats.startswith('[\\'):
                    last3_formats = '[]'
                
                # Validate JSON
                try:
                    json.loads(last3_formats)
                except:
                    # If invalid, reset to empty array
                    last3_formats = '[]'
            
            # Create clean row with only the necessary fields
            clean_row = {}
            for header in headers:
                if header == 'last3_formats':
                    clean_row[header] = last3_formats
                else:
                    clean_row[header] = row.get(header, '')
            
            clean_rows.append(clean_row)
    
    # Write clean CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(clean_rows)
    
    print(f"Cleaned scores CSV: {len(clean_rows)} unique books")
    return output_path

def clean_output_csv():
    """Clean the audio_format_output.csv file - will be regenerated"""
    output_path = '/home/xai/DEV/37degrees/config/audio_format_output_clean.csv'
    
    # Just create empty file with headers - will be populated by format_selector.py
    headers = [
        'book_folder_id', 'title', 'year', 'translations_count',
        'A_kontrowersyjnosc', 'B_glebia', 'C_fenomen', 'D_rezonans', 
        'E_polski_kontekst', 'F_aktualnosc', 'G_innowacyjnosc', 
        'H_zlozonosc', 'I_gender',
        'B_jung_3plus', 'B_symbolika_relig_mit', 'B_warstwy_3plus', 'B_metafory_egzyst',
        'last3_formats', 'SUMA_points', 'duration_min',
        'eligible_01', 'eligible_02', 'eligible_03', 'eligible_04', 'eligible_05', 
        'eligible_06', 'eligible_07', 'eligible_08', 'eligible_09', 'eligible_10', 
        'eligible_11', 'eligible_12',
        'weighted_01', 'weighted_02', 'weighted_03', 'weighted_04', 'weighted_05',
        'weighted_06', 'weighted_07', 'weighted_08', 'weighted_09', 'weighted_10',
        'weighted_11', 'weighted_12',
        'chosen_format', 'alt_format', 'chosen_reason'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
    
    print(f"Created empty output CSV with headers")
    return output_path

if __name__ == "__main__":
    # Clean both CSV files
    scores_path = clean_scores_csv()
    output_path = clean_output_csv()
    
    print(f"\nCleaned files created:")
    print(f"  - {scores_path}")
    print(f"  - {output_path}")
    print("\nNow run format_selector.py with the clean files")