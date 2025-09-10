#!/usr/bin/env python3
import csv
import json
from pathlib import Path

# Paths
CSV_PATH = Path("/home/xai/DEV/37degrees/config/audio_format_scores.csv")

# Read existing CSV to get format history
format_history = []
if CSV_PATH.exists():
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            chosen = row.get('chosen_format', '')
            if chosen:
                format_history.append(chosen)

# Get last 3 formats for compatibility
last3_formats = format_history[-3:] if len(format_history) >= 3 else format_history

# Prepare distribution stats
from collections import Counter
format_counts = Counter(format_history) if format_history else Counter()
total_books = len(format_history)

all_possible_formats = [
    "Przyjacielska wymiana", "Mistrz i Uczeń", "Adwokat i Sceptyk",
    "Reporter i Świadek", "Współczesny i Klasyk", "Emocja i Analiza",
    "Lokalny i Globalny", "Fan i Nowicjusz", "Perspektywa Ona/On",
    "Wykład filologiczny w duecie", "Glosa do przekładów",
    "Komentarz historyczno-literacki"
]

unused_formats = [f for f in all_possible_formats if format_counts.get(f, 0) == 0]
underused_formats = [f for f in all_possible_formats 
                     if 0 < format_counts.get(f, 0) < total_books * 0.05] if total_books > 0 else []

distribution_stats = {
    'total': total_books,
    'counts': dict(format_counts),
    'unused': unused_formats,
    'underused': underused_formats
}

# New row data for King Lear
new_row = {
    'book_folder_id': '0042_king_lear',
    'title': 'King Lear',
    'year': '1606',
    'translations_count': '100',  # Over 100 languages per research
    'A_kontrowersyjnosc': '5',
    'B_glebia': '5',
    'C_fenomen': '5',
    'D_rezonans': '5',
    'E_polski_kontekst': '5',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '5',
    'B_jung_3plus': '1',
    'B_symbolika_relig_mit': '1',
    'B_warstwy_3plus': '1',
    'B_metafory_egzyst': '1',
    'last3_formats': json.dumps(last3_formats),
    'format_history': json.dumps(format_history),
    'distribution_stats': json.dumps(distribution_stats)
}

# Read existing CSV to check if header exists
has_header = False
if CSV_PATH.exists():
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if first_line and 'book_folder_id' in first_line:
            has_header = True

# Append the new row
with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
    fieldnames = list(new_row.keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    
    # Write header if file is empty or doesn't have one
    if not has_header:
        writer.writeheader()
    
    writer.writerow(new_row)

print(f"Added King Lear to {CSV_PATH}")