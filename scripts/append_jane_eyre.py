#!/usr/bin/env python3
import csv
import json

# Data for Jane Eyre
new_row = {
    'book_folder_id': '0014_jane_eyre',
    'title': 'Jane Eyre',
    'year': '1847',
    'translations_count': '174',  # From CSV line 15
    'A_kontrowersyjnosc': '4',
    'B_glebia': '5', 
    'C_fenomen': '5',
    'D_rezonans': '4',
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

# Path to CSV file
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

# Read existing headers from the file
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames

# Append the new row
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writerow(new_row)

print("Successfully added Jane Eyre entry to CSV")