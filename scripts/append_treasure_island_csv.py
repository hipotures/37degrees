#!/usr/bin/env python3
import csv
import json

# Data for Treasure Island
new_row = {
    'book_folder_id': '0036_treasure_island',
    'title': 'Treasure Island',
    'year': 1883,
    'translations_count': 174,  # Standard high number for classics
    'A_kontrowersyjnosc': 4,
    'B_glebia': 5,
    'C_fenomen': 5,
    'D_rezonans': 4,
    'E_polski_kontekst': 3,
    'F_aktualnosc': 4,
    'G_innowacyjnosc': 5,
    'H_zlozonosc': 4,
    'I_gender': 3,
    'B_jung_3plus': 1,
    'B_symbolika_relig_mit': 1,
    'B_warstwy_3plus': 1,
    'B_metafory_egzyst': 1,
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'
}

# Append to CSV
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    # Get fieldnames from the first row
    with open(csv_path, 'r', encoding='utf-8') as rf:
        reader = csv.DictReader(rf)
        fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Added Treasure Island row to {csv_path}")