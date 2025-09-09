#!/usr/bin/env python3
import csv

# Data for Narnia book
new_row = {
    'book_folder_id': '0020_narnia',
    'title': 'The Chronicles of Narnia: The Lion, the Witch and the Wardrobe',
    'year': '1950',
    'translations_count': '47',  # 47 languages mentioned
    'A_kontrowersyjnosc': '4',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '4',
    'E_polski_kontekst': '4',
    'F_aktualnosc': '4',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '3',
    'B_jung_3plus': '1',
    'B_symbolika_relig_mit': '1',
    'B_warstwy_3plus': '1',
    'B_metafory_egzyst': '1',
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'
}

# Append to CSV
csv_path = 'config/audio_format_scores.csv'
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    # Get existing headers from file
    with open(csv_path, 'r', encoding='utf-8') as rf:
        reader = csv.DictReader(rf)
        fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Added {new_row['book_folder_id']} to CSV")