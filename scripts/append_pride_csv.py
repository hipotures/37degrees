#!/usr/bin/env python3
import csv

# New row data for Pride and Prejudice
new_row = {
    'book_folder_id': '0026_pride_and_prejudice',
    'title': 'Pride and Prejudice',
    'year': '1813',
    'translations_count': '174',
    'A_kontrowersyjnosc': '4',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '5',
    'E_polski_kontekst': '4',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '5',
    'B_jung_3plus': '1',
    'B_symbolika_relig_mit': '1',
    'B_warstwy_3plus': '1',
    'B_metafory_egzyst': '1',
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'
}

# Define CSV path
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

# Append to CSV
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    # Get existing headers from the file
    with open(csv_path, 'r', encoding='utf-8') as rf:
        reader = csv.DictReader(rf)
        fieldnames = reader.fieldnames
    
    # Write the new row
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)
    
print(f"Successfully added Pride and Prejudice data to {csv_path}")