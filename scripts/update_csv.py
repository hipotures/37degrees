#!/usr/bin/env python3
import csv
import json

# Read the last 3 formats from existing CSV
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'
last3_formats = []

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
    # Get last 3 formats used (if they exist)
    for row in rows[-3:]:
        if 'chosen_format' in row and row['chosen_format']:
            last3_formats.append(row['chosen_format'])

# Prepare the new row data
new_row = {
    'book_folder_id': '0013_hobbit',
    'title': 'The Hobbit',
    'year': 1937,
    'translations_count': 60,
    'A_kontrowersyjnosc': 5,
    'B_glebia': 5,
    'C_fenomen': 5,
    'D_rezonans': 5,
    'E_polski_kontekst': 4,
    'F_aktualnosc': 5,
    'G_innowacyjnosc': 5,
    'H_zlozonosc': 5,
    'I_gender': 4,
    'B_jung_3plus': 1,  # Yes, multiple Jung archetypes
    'B_symbolika_relig_mit': 1,  # Yes, religious/mythological symbolism
    'B_warstwy_3plus': 1,  # Yes, 3+ interpretative layers
    'B_metafory_egzyst': 1,  # Yes, existential metaphors
    'last3_formats': json.dumps(last3_formats, ensure_ascii=False)
}

# Write the new row to CSV
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    # Get fieldnames from existing file
    with open(csv_path, 'r', encoding='utf-8') as read_f:
        reader = csv.DictReader(read_f)
        fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Successfully added row for 0013_hobbit with score: 43/45")
print(f"Last 3 formats used: {last3_formats}")