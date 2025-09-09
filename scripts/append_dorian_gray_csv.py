#!/usr/bin/env python3
import csv

# Data for The Picture of Dorian Gray
new_row = {
    'book_folder_id': '0025_portrait_of_dorian_gray',
    'title': 'The Picture of Dorian Gray',
    'year': '1890',
    'translations_count': '174',  # Many translations worldwide
    'A_kontrowersyjnosc': '5',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '5',
    'E_polski_kontekst': '4',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '5',
    'B_jung_3plus': '1',  # Yes - Puer Aeternus, Shadow, Doppelgänger
    'B_symbolika_relig_mit': '1',  # Yes - Faustian pact, Narcissus
    'B_warstwy_3plus': '1',  # Yes - multiple interpretative layers
    'B_metafory_egzyst': '1',  # Yes - mortality, authenticity
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'
}

# CSV file path
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

# Read existing fieldnames from CSV
with open(csv_path, 'r', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

# Append new row to CSV
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Successfully added {new_row['title']} to CSV")