#!/usr/bin/env python3
import csv
import json

# Define the CSV path
CSV_PATH = "/home/xai/DEV/37degrees/config/audio_format_scores.csv"

# Get last 3 formats from existing CSV
last3_formats = []
try:
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if rows:
            # Get last 3 formats from recent rows
            for row in rows[-3:]:
                if 'last3_formats' in row and row['last3_formats']:
                    try:
                        formats = json.loads(row['last3_formats'])
                        if formats and isinstance(formats, list):
                            last3_formats = formats
                            break
                    except:
                        pass
except:
    pass

# If we couldn't get formats from CSV, use most recent ones
if not last3_formats:
    last3_formats = ["Przyjacielska wymiana", "Przyjacielska wymiana", "Przyjacielska wymiana"]

# Prepare the new row data
new_row = {
    'book_folder_id': '0037_wuthering_heights',
    'title': 'Wuthering Heights',
    'year': '1847',
    'translations_count': '174',
    'A_kontrowersyjnosc': '5',
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
    'last3_formats': json.dumps(last3_formats)
}

# Read existing headers from CSV
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

# Append the new row to CSV
with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Successfully added Wuthering Heights to {CSV_PATH}")