#!/usr/bin/env python3
import csv
import json
from collections import Counter

# Przygotowanie danych o historii formatów
existing_rows = []
CSV_PATH = "/home/xai/DEV/37degrees/config/audio_format_scores.csv"

# Odczyt istniejącego CSV dla historii formatów
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_rows.append(row)

# Zbierz wszystkie formaty z kolumny last3_formats
all_formats = []
for row in existing_rows:
    last3_str = row.get('last3_formats', '[]')
    try:
        # Usuń zewnętrzne cudzysłowy jeśli są
        if last3_str.startswith('"') and last3_str.endswith('"'):
            last3_str = last3_str[1:-1]
        # Napraw podwójne cudzysłowy
        last3_str = last3_str.replace('""', '"')
        
        last3_list = json.loads(last3_str) if last3_str and last3_str != '[]' else []
        if isinstance(last3_list, list):
            all_formats.extend(last3_list)
    except:
        pass

# Dodaj formaty z format_history kolumny (książka 73)
for row in existing_rows:
    if row.get('book_folder_id') == '0073_their_eyes_were_watching_god':
        format_history_str = row.get('format_history', '[]')
        try:
            if format_history_str.startswith('"') and format_history_str.endswith('"'):
                format_history_str = format_history_str[1:-1]
            format_history_str = format_history_str.replace('""', '"')
            history_list = json.loads(format_history_str) if format_history_str and format_history_str != '[]' else []
            if isinstance(history_list, list):
                all_formats = history_list  # Use full history from book 73
        except:
            pass
        break

# Ostatnie 3 formaty
last3_formats = all_formats[-3:] if len(all_formats) >= 3 else all_formats

# Statystyki dystrybucji
format_counts = Counter(all_formats) if all_formats else Counter()
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

# Przygotuj nowy wiersz
new_row = {
    'book_folder_id': '0079_the_satanic_verses',
    'title': 'The Satanic Verses',
    'year': '1988',
    'translations_count': '40',  # Estimated based on global reach
    'A_kontrowersyjnosc': '5',
    'B_glebia': '5', 
    'C_fenomen': '5',
    'D_rezonans': '3',
    'E_polski_kontekst': '3',
    'F_aktualnosc': '5',
    'G_innowacyjnosc': '5',
    'H_zlozonosc': '5',
    'I_gender': '5',
    'B_jung_3plus': '1',
    'B_symbolika_relig_mit': '1',
    'B_warstwy_3plus': '1',
    'B_metafory_egzyst': '1',
    'last3_formats': json.dumps(last3_formats),
    'format_history': json.dumps(all_formats)
}

# Dodaj wiersz do CSV
with open(CSV_PATH, 'a', newline='', encoding='utf-8') as f:
    # Get field names from existing file
    with open(CSV_PATH, 'r', encoding='utf-8') as fr:
        reader = csv.DictReader(fr)
        fieldnames = reader.fieldnames
    
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writerow(new_row)

print(f"Added row for 0079_the_satanic_verses with score: 41/45")
print(f"Format history length: {len(all_formats)}")
print(f"Last 3 formats: {last3_formats}")