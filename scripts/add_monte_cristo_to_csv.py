#!/usr/bin/env python3
import csv
import json
import os

# Prepare the full format history from existing CSV
csv_path = "/home/xai/DEV/37degrees/config/audio_format_scores.csv"
all_formats = []
last3_formats = []

# Read existing CSV to get format history
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract format from last3_formats column (it's a JSON string)
            if 'last3_formats' in row and row['last3_formats']:
                try:
                    formats_list = json.loads(row['last3_formats'])
                    if formats_list:
                        # Take the last format from each row (most recent)
                        if isinstance(formats_list, list) and len(formats_list) > 0:
                            all_formats.append(formats_list[-1] if formats_list else "")
                except:
                    pass

# Get last 3 formats for the new entry
last3_formats = all_formats[-3:] if len(all_formats) >= 3 else all_formats

# Calculate distribution stats
from collections import Counter
format_counts = Counter(all_formats)
total_books = len(all_formats)

all_possible_formats = [
    "Przyjacielska wymiana", "Mistrz i Uczeń", "Adwokat i Sceptyk",
    "Reporter i Świadek", "Współczesny i Klasyk", "Emocja i Analiza",
    "Lokalny i Globalny", "Fan i Nowicjusz", "Perspektywa Ona/On",
    "Wykład filologiczny w duecie", "Glosa do przekładów",
    "Komentarz historyczno-literacki"
]

unused_formats = [f for f in all_possible_formats if format_counts.get(f, 0) == 0]
underused_formats = [f for f in all_possible_formats 
                     if 0 < format_counts.get(f, 0) < total_books * 0.05]

distribution_stats = {
    'total': total_books,
    'counts': dict(format_counts),
    'unused': unused_formats,
    'underused': underused_formats
}

# Prepare new row data
new_row = {
    'book_folder_id': '0049_the_count_of_monte_cristo',
    'title': 'The Count of Monte Cristo',
    'year': '1844',
    'translations_count': '174',  # Based on research showing 174 translations
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
    'last3_formats': json.dumps(last3_formats),
}

# Check if header exists
has_header = False
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if 'book_folder_id' in first_line:
            has_header = True

# Append to CSV
with open(csv_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=new_row.keys())
    if not has_header:
        writer.writeheader()
    writer.writerow(new_row)

print(f"Added The Count of Monte Cristo to CSV")
print(f"Total books in history: {total_books + 1}")
print(f"Last 3 formats: {last3_formats}")
print(f"Unused formats: {unused_formats}")