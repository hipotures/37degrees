#!/usr/bin/env python3
"""
Naprawa dystrybucji formatów AFA w 3 warstwach:
1. Definicje → scal formaty, podnieś progi
2. Algorytm → quoty docelowe, cooldown, korekta wag
3. Harmonogram → greedy wg deficytów
"""

import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

# WARSTWA 1: DEFINICJE
# ====================

# Scal "Wykład filologiczny" → "Wykład filologiczny w duecie" (#10)
FORMAT_MAPPING = {
    "Wykład filologiczny": "Wykład filologiczny w duecie",
    "WYKŁAD FILOLOGICZNY": "Wykład filologiczny w duecie",
    "WYKŁAD FILOLOGICZNY W DUECIE": "Wykład filologiczny w duecie",
    "**PRZYJACIELSKA WYMIANA**": "Przyjacielska wymiana",
    "PRZYJACIELSKA WYMIANA": "Przyjacielska wymiana",
    "Mistrz i Uczeń": "Mistrz i Uczeń",
    "MISTRZ I UCZEŃ": "Mistrz i Uczeń"
}

# Formaty z ID (1-12)
FORMATS = [
    "Przyjacielska wymiana",           # 1
    "Mistrz i Uczeń",                  # 2
    "Adwokat i Sceptyk",               # 3
    "Reporter i Świadek",              # 4
    "Współczesny i Klasyk",            # 5
    "Emocja i Analiza",                # 6
    "Lokalny i Globalny",              # 7
    "Fan i Nowicjusz",                 # 8
    "Perspektywa Ona/On",              # 9
    "Wykład filologiczny w duecie",   # 10
    "Glosa do przekładów",             # 11
    "Komentarz historyczno-literacki"  # 12
]

# WARSTWA 2: ALGORYTM
# ===================

# Quoty docelowe (sumują się do 1.0)
TARGET_SHARE = {
    1: 0.11,  # Przyjacielska wymiana
    2: 0.09,  # Mistrz i Uczeń
    3: 0.09,  # Adwokat i Sceptyk
    4: 0.09,  # Reporter i Świadek
    5: 0.09,  # Współczesny i Klasyk
    6: 0.09,  # Emocja i Analiza
    7: 0.09,  # Lokalny i Globalny
    8: 0.06,  # Fan i Nowicjusz
    9: 0.09,  # Perspektywa Ona/On
    10: 0.09, # Wykład filologiczny w duecie
    11: 0.06, # Glosa do przekładów
    12: 0.09  # Komentarz historyczno-literacki
}

WINDOW = 12        # Okno kontroli
COOLDOWN = 2       # Odcinki przerwy
GAMMA = 0.6        # Siła korekty
MAX_PER_FORMAT = 4 # Max w oknie 12
MAX_PRZYJACIELSKA = 3  # Specjalny limit dla #1

def normalize_format(format_name):
    """Normalizuj nazwę formatu."""
    if not format_name:
        return None
    clean = format_name.strip().replace('**', '').strip()
    return FORMAT_MAPPING.get(clean, clean)

def get_format_id(format_name):
    """Zwróć ID formatu (1-12)."""
    normalized = normalize_format(format_name)
    if normalized in FORMATS:
        return FORMATS.index(normalized) + 1
    return None

def recent_stats(history_rows):
    """Oblicz statystyki ostatnich WINDOW odcinków."""
    last = history_rows[-WINDOW:] if len(history_rows) > WINDOW else history_rows
    counts = Counter(last)
    total = max(1, len(last))
    share = {i: (counts.get(i, 0) / total) for i in range(1, 13)}
    return counts, share

def update_eligibility_rules(scores):
    """Zaktualizowane reguły eligibility z podniesionymi progami."""
    C = scores.get('C_fenomen', 0)
    D = scores.get('D_rezonans', 0)
    
    # Podniesiony próg dla Przyjacielskiej wymiany
    if C >= 4 and D >= 3:
        eligible = {1}  # Format 1: Przyjacielska wymiana
    else:
        eligible = set()
    
    # Pozostałe formaty - rozluźnione kryteria
    A = scores.get('A_kontrowersyjnosc', 0)
    B = scores.get('B_glebia', 0)
    E = scores.get('E_polski_kontekst', 0)
    F = scores.get('F_aktualnosc', 0)
    G = scores.get('G_innowacyjnosc', 0)
    H = scores.get('H_zlozonosc', 0)
    I = scores.get('I_gender', 0)
    
    # Dodaj eligible formaty na podstawie scores
    if B >= 3 and H >= 3:
        eligible.add(2)  # Mistrz i Uczeń
    if A >= 3 or F >= 4:
        eligible.add(3)  # Adwokat i Sceptyk
    if H >= 3:
        eligible.add(4)  # Reporter i Świadek
    if F >= 3 or C >= 3:
        eligible.add(5)  # Współczesny i Klasyk
    if I >= 3 or B >= 3:
        eligible.add(6)  # Emocja i Analiza
    if E >= 3:
        eligible.add(7)  # Lokalny i Globalny
    if D >= 3:
        eligible.add(8)  # Fan i Nowicjusz
    if I >= 3:
        eligible.add(9)  # Perspektywa Ona/On
    if G >= 3 or B >= 3:
        eligible.add(10)  # Wykład filologiczny w duecie
    if scores.get('translations_count', 0) >= 5:
        eligible.add(11)  # Glosa do przekładów
    if scores.get('year', 2000) < 1900:
        eligible.add(12)  # Komentarz historyczno-literacki
    
    # Jeśli nic nie pasuje, dodaj fallbacki
    if not eligible:
        eligible = {1, 2, 10}  # Podstawowe formaty
    
    return eligible

def calculate_duration(format_id, scores):
    """Oblicz długość odcinka na podstawie formatu i scores."""
    H = scores.get('H_zlozonosc', 0)
    G = scores.get('G_innowacyjnosc', 0)
    
    # Format #1 i #8: cap 12 min (chyba że H≥4 → 13 max)
    if format_id in [1, 8]:
        if H >= 4:
            return 13
        else:
            return 12
    
    # Format #10: 14 min tylko gdy G≥5 i H≥4, inaczej 12
    if format_id == 10:
        if G >= 5 and H >= 4:
            return 14
        else:
            return 12
    
    # Format #4: +1 min gdy są 2+ sceny z rekonstrukcją
    if format_id == 4:
        # Tu należałoby sprawdzić liczbę scen, na razie domyślnie
        return 13
    
    # Pozostałe formaty: domyślnie 13-14 min
    suma = sum(scores.get(k, 0) for k in ['A_kontrowersyjnosc', 'B_glebia', 'C_fenomen', 
                                           'D_rezonans', 'E_polski_kontekst', 'F_aktualnosc',
                                           'G_innowacyjnosc', 'H_zlozonosc', 'I_gender'])
    if suma >= 35:
        return 14
    else:
        return 13

def select_format_with_quota(eligible_formats, history, scores, last_formats):
    """Wybierz format z uwzględnieniem quot i cooldownów."""
    counts, share = recent_stats(history)
    
    # Filtruj formaty w cooldownie
    last_used = []
    if last_formats:
        last_used = [get_format_id(f) for f in last_formats.split('|')[-COOLDOWN:] if f]
    
    candidates = [f for f in eligible_formats if f not in last_used]
    if not candidates:
        candidates = list(eligible_formats)
    
    # Sprawdź twarde limity
    filtered = []
    for fmt in candidates:
        if fmt == 1 and counts.get(1, 0) >= MAX_PRZYJACIELSKA:
            continue  # Przyjacielska przekroczyła limit 3/12
        if counts.get(fmt, 0) >= MAX_PER_FORMAT:
            continue  # Format przekroczył limit 4/12
        filtered.append(fmt)
    
    if not filtered:
        filtered = candidates  # Jeśli wszystko zablokowane, weź wszystkie
    
    # Oblicz skorygowane wagi
    weighted_scores = {}
    for fmt in filtered:
        base_score = 10  # Domyślny score jeśli brak danych
        
        # Korekta wag na podstawie deficytu/nadmiaru
        target = TARGET_SHARE[fmt]
        recent = share.get(fmt, 0.0)
        adj = 1 + GAMMA * (target - recent)
        adj = min(1.4, max(0.6, adj))  # Clamp do [0.6, 1.4]
        
        weighted_scores[fmt] = base_score * adj
    
    # Wybierz format o najwyższym skorygowanym score
    if weighted_scores:
        chosen = max(weighted_scores, key=weighted_scores.get)
        return chosen
    
    return 1  # Fallback do Przyjacielskiej wymiany

def main():
    """Główna funkcja naprawiająca dystrybucję."""
    
    # Ścieżki plików
    csv_path = Path("config/audio_format_scores.csv")
    output_path = Path("config/audio_format_output.csv")
    history_path = Path("output/schedule_history.csv")
    
    # Wczytaj dane
    books = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            books.append(row)
    
    # Wczytaj historię jeśli istnieje
    history = []
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                fmt_id = row.get('chosen_format_id')
                if fmt_id and fmt_id.isdigit():
                    history.append(int(fmt_id))
    
    # WARSTWA 3: HARMONOGRAM
    # =======================
    
    # Przetwórz książki i przypisz formaty
    results = []
    for book in books:
        # Zbierz scores
        scores = {
            'A_kontrowersyjnosc': int(book.get('A_kontrowersyjnosc', 0)),
            'B_glebia': int(book.get('B_glebia', 0)),
            'C_fenomen': int(book.get('C_fenomen', 0)),
            'D_rezonans': int(book.get('D_rezonans', 0)),
            'E_polski_kontekst': int(book.get('E_polski_kontekst', 0)),
            'F_aktualnosc': int(book.get('F_aktualnosc', 0)),
            'G_innowacyjnosc': int(book.get('G_innowacyjnosc', 0)),
            'H_zlozonosc': int(book.get('H_zlozonosc', 0)),
            'I_gender': int(book.get('I_gender', 0)),
            'translations_count': int(book.get('translations_count', 0) or 0),
            'year': int(book.get('year', 2000) or 2000)
        }
        
        # Określ eligible formaty
        eligible = update_eligibility_rules(scores)
        
        # Pobierz ostatnie użyte formaty
        last_formats = book.get('last3_formats', '')
        
        # Wybierz format z uwzględnieniem quot
        chosen_id = select_format_with_quota(eligible, history, scores, last_formats)
        chosen_format = FORMATS[chosen_id - 1]
        
        # Oblicz długość
        duration = calculate_duration(chosen_id, scores)
        
        # Dodaj do historii
        history.append(chosen_id)
        
        # Zapisz wynik
        result = {
            'book_folder_id': book['book_folder_id'],
            'title': book['title'],
            'chosen_format': chosen_format,
            'chosen_format_id': chosen_id,
            'duration_min': duration,
            'suma_points': sum(scores[k] for k in scores if k.startswith(('A_', 'B_', 'C_', 'D_', 'E_', 'F_', 'G_', 'H_', 'I_')))
        }
        results.append(result)
        
        print(f"{book['book_folder_id']}: {chosen_format} ({duration} min)")
    
    # Zapisz wyniki
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['book_folder_id', 'title', 'chosen_format', 'chosen_format_id', 'duration_min', 'suma_points']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Zapisz historię
    with open(history_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['book_folder_id', 'chosen_format_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, book in enumerate(books):
            if i < len(results):
                writer.writerow({
                    'book_folder_id': book['book_folder_id'],
                    'chosen_format_id': results[i]['chosen_format_id']
                })
    
    # Raport końcowy
    format_counts = Counter(r['chosen_format'] for r in results)
    print("\n📊 DYSTRYBUCJA PO NAPRAWIE:")
    for fmt in FORMATS:
        count = format_counts.get(fmt, 0)
        percent = (count / len(results)) * 100 if results else 0
        target_percent = TARGET_SHARE[FORMATS.index(fmt) + 1] * 100
        print(f"{fmt}: {count} ({percent:.1f}%) [cel: {target_percent:.0f}%]")

if __name__ == '__main__':
    main()