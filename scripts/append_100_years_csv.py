#!/usr/bin/env python3
import csv

# Data for One Hundred Years of Solitude
new_row = {
    'book_folder_id': '0023_one_hundred_years_of_solitude',
    'title': 'One Hundred Years of Solitude',
    'year': '1967',
    'translations_count': '44',
    'A_kontrowersyjnosc': '5',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '5',
    'E_polski_kontekst': '4',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '5',
    'B_jung_3plus': '1',  # Yes - 4 archetypes
    'B_symbolika_relig_mit': '1',  # Yes - biblical and pre-columbian
    'B_warstwy_3plus': '1',  # Yes - multiple interpretation layers
    'B_metafory_egzyst': '1',  # Yes - solitude, cyclical time
    'last3_formats': '["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]'  # Last 3 from CSV
}

# Open CSV and append
csv_path = '/home/xai/DEV/37degrees/config/audio_format_scores.csv'

with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    fieldnames = [
        'book_folder_id', 'title', 'year', 'translations_count',
        'A_kontrowersyjnosc', 'B_glebia', 'C_fenomen', 'D_rezonans',
        'E_polski_kontekst', 'F_aktualnosc', 'G_innowacyjnosc', 
        'H_zlozonosc', 'I_gender',
        'B_jung_3plus', 'B_symbolika_relig_mit', 'B_warstwy_3plus', 'B_metafory_egzyst',
        'last3_formats'
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Added {new_row['title']} to CSV")