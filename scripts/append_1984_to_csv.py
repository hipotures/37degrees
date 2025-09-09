#!/usr/bin/env python3
import csv
import json

# Prepare the new row data
new_row = {
    'book_folder_id': '0021_nineteen_eighty_four',
    'title': 'Nineteen Eighty-Four',
    'year': '1949',
    'translations_count': '65',  # From facts document
    'A_kontrowersyjnosc': '5',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '5',
    'E_polski_kontekst': '5',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '4',
    'B_jung_3plus': '1',
    'B_symbolika_relig_mit': '1',
    'B_warstwy_3plus': '1',
    'B_metafory_egzyst': '1',
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'
}

# Append to CSV file
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    # Get the field names from existing file
    with open(csv_path, 'r', encoding='utf-8') as r:
        reader = csv.DictReader(r)
        fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Successfully added row for {new_row['book_folder_id']} to CSV")