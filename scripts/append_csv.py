#!/usr/bin/env python3
import csv
import sys

# Data for the new row
new_row = {
    'book_folder_id': '0009_fahrenheit_451',
    'title': 'Fahrenheit 451',
    'year': 1953,
    'translations_count': 58,
    'A_kontrowersyjnosc': 4,
    'B_glebia': 5,
    'C_fenomen': 5,
    'D_rezonans': 5,
    'E_polski_kontekst': 3,
    'F_aktualnosc': 5,
    'G_innowacyjnosc': 5,
    'H_zlozonosc': 4,
    'I_gender': 3,
    'B_jung_3plus': 1,
    'B_symbolika_relig_mit': 1,
    'B_warstwy_3plus': 1,
    'B_metafory_egzyst': 1,
    'last3_formats': '["Mistrz i Uczeń", "Wykład filologiczny", "Lokalny i Globalny"]'
}

# Path to CSV file
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

# Read existing headers
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

# Append the new row
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Successfully added row for {new_row['book_folder_id']} to CSV")