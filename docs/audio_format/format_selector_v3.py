#!/usr/bin/env python3
"""
Format Selector v3 - z prawidłową rotacją formatów
Buduje historię inkrementalnie podczas przetwarzania, nie używa starych danych
"""

import csv
import sys
import hashlib
import json
from collections import Counter

FORMATS = [
    "Przyjacielska wymiana",
    "Mistrz i Uczeń",
    "Adwokat i Sceptyk",
    "Reporter i Świadek",
    "Współczesny i Klasyk",
    "Emocja i Analiza",
    "Lokalny i Globalny",
    "Fan i Nowicjusz",
    "Perspektywa Ona/On",
    "Wykład filologiczny",
    "Glosa do przekładów",
    "Komentarz historyczno-literacki",
]

# Default weights for "wynik ważony" per format
WEIGHTS = {
    1: {"A":1.0,"B":1.0,"C":1.2,"D":1.2},  # Przyjacielska
    2: {"B":1.5,"E":1.2,"G":1.3},          # Mistrz/Uczeń
    3: {"A":1.6,"F":1.2,"C":1.1},          # Adwokat/Sceptyk
    4: {"H":1.4,"A":1.2},                  # Reporter/Świadek
    5: {"F":1.5,"D":1.3},                  # Współczesny/Klasyk
    6: {"B":1.5,"G":1.4},                  # Emocja/Analiza
    7: {"E":1.6,"C":1.2},                  # Lokalny/Globalny
    8: {"C":1.5,"D":1.3},                  # Fan/Nowicjusz
    9: {"I":1.6,"H":1.1},                  # Ona/On
    10: {"G":1.4,"B":1.5,"H":1.2},         # Wykład filologiczny
    11: {"E":1.2,"G":1.1},                 # Glosa
    12: {"H":1.4,"B":1.2,"E":1.1},         # Komentarz hist.-lit.
}

def duration(sum_points, H):
    if sum_points >= 38 and H >= 4:
        return 14
    elif sum_points >= 35:
        return 12
    elif sum_points >= 30:
        return 10
    elif sum_points >= 25:
        return 8
    else:
        return 5

def eligible_formats(row):
    A=int(row["A_kontrowersyjnosc"] or 0)
    B=int(row["B_glebia"] or 0)
    C=int(row["C_fenomen"] or 0)
    D=int(row["D_rezonans"] or 0)
    E=int(row["E_polski_kontekst"] or 0)
    F=int(row["F_aktualnosc"] or 0)
    G=int(row["G_innowacyjnosc"] or 0)
    H=int(row["H_zlozonosc"] or 0)
    I=int(row["I_gender"] or 0)
    year = int(row["year"] or 0)
    translations = int(row["translations_count"] or 0)

    elig = set()

    # 1 Przyjacielska wymiana: C ≥ 3 oraz (D ≥ 3 lub suma < 20)
    suma = A+B+C+D+E+F+G+H+I
    if C >= 3 and (D >= 3 or suma < 20):
        elig.add(1)
    # 2 Mistrz i Uczeń: B ≥ 4 oraz E ≥ 3 oraz G ≥ 3
    if B >= 4 and E >= 3 and G >= 3:
        elig.add(2)
    # 3 Adwokat i Sceptyk: A ≥ 4 lub (A ≥ 3 i F < 2)
    if A >= 4 or (A >= 3 and F < 2):
        elig.add(3)
    # 4 Reporter i Świadek: H ≥ 4 oraz A ≥ 3
    if H >= 4 and A >= 3:
        elig.add(4)
    # 5 Współczesny i Klasyk: (F < 2 i C ≥ 4) lub (year < 1980 i D ≥ 3)
    if (F < 2 and C >= 4) or (year < 1980 and D >= 3):
        elig.add(5)
    # 6 Emocja i Analiza: B ≥ 4 oraz G ≥ 3
    if B >= 4 and G >= 3:
        elig.add(6)
    # 7 Lokalny i Globalny: E ≥ 4 oraz C ≥ 3
    if E >= 4 and C >= 3:
        elig.add(7)
    # 8 Fan i Nowicjusz: C ≥ 5 oraz D ≥ 3
    if C >= 5 and D >= 3:
        elig.add(8)
    # 9 Perspektywa Ona/On: I ≥ 4
    if I >= 4:
        elig.add(9)
    # 10 Wykład filologiczny: G ≥ 5 oraz B ≥ 4
    if G >= 5 and B >= 4:
        elig.add(10)
    # 11 Glosa do przekładów: E ≥ 4 oraz translations ≥ 3
    if E >= 4 and translations >= 3:
        elig.add(11)
    # 12 Komentarz historyczno-literacki: H ≥ 4 oraz year < 1950
    if H >= 4 and year < 1950:
        elig.add(12)

    return elig, suma

def weighted_score(fmt, row):
    vals = {
        "A": int(row["A_kontrowersyjnosc"] or 0),
        "B": int(row["B_glebia"] or 0),
        "C": int(row["C_fenomen"] or 0),
        "D": int(row["D_rezonans"] or 0),
        "E": int(row["E_polski_kontekst"] or 0),
        "F": int(row["F_aktualnosc"] or 0),
        "G": int(row["G_innowacyjnosc"] or 0),
        "H": int(row["H_zlozonosc"] or 0),
        "I": int(row["I_gender"] or 0)
    }
    w = WEIGHTS.get(fmt, {})
    score = 0.0
    for k, mult in w.items():
        score += vals[k] * mult
    return round(score, 3)

def choose_format_with_rotation(title, elig, weighted, current_history):
    """
    Wybierz format z wymuszeniem rotacji.
    Używa AKTUALNEJ historii budowanej podczas przetwarzania.
    """
    # Get last 3 formats from current history
    last3 = current_history[-3:] if len(current_history) >= 3 else current_history
    blocked_formats = set(last3)
    
    # Filter eligible formats - remove blocked ones
    candidates = [f for f in elig if FORMATS[f-1] not in blocked_formats]
    
    # If no candidates after blocking, find least recently used
    if not candidates:
        # Count usage in entire history
        usage_counts = Counter(current_history)
        
        # Sort eligible by usage count (ascending) and recency
        def sort_key(fmt_idx):
            fmt_name = FORMATS[fmt_idx-1]
            count = usage_counts.get(fmt_name, 0)
            # Find last occurrence
            try:
                last_idx = len(current_history) - 1 - current_history[::-1].index(fmt_name)
            except ValueError:
                last_idx = -1
            return (count, last_idx)  # Prefer less used, then less recent
        
        candidates = sorted(elig, key=sort_key)
        if candidates:
            # Take top 3 least used
            candidates = candidates[:3]
    
    # If still no candidates, use all eligible
    if not candidates:
        candidates = list(elig)
    
    # If STILL no candidates (no eligible formats), force pick from all
    if not candidates:
        # This shouldn't happen, but as ultimate fallback
        candidates = list(range(1, 13))
        # Remove blocked if possible
        candidates = [f for f in candidates if FORMATS[f-1] not in blocked_formats] or candidates
    
    # Among candidates, prioritize never used formats
    never_used = [f for f in candidates if FORMATS[f-1] not in current_history]
    if never_used:
        # Choose from never used based on weighted score
        max_score = max(weighted[f] for f in never_used)
        top_scored = [f for f in never_used if weighted[f] == max_score]
    else:
        # Choose from candidates based on weighted score
        max_score = max(weighted[f] for f in candidates)
        top_scored = [f for f in candidates if weighted[f] == max_score]
    
    # Deterministic selection if multiple with same score
    if len(top_scored) == 1:
        chosen = top_scored[0]
    else:
        h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
        chosen = top_scored[h % len(top_scored)]
    
    # Find alternative
    alt = None
    for f in sorted(candidates, key=lambda x: weighted[x], reverse=True):
        if f != chosen:
            alt = f
            break
    
    return chosen, alt

def main(inp, outp):
    with open(inp, newline="", encoding="utf-8") as f, open(outp, "w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames + ["SUMA_points","duration_min","chosen_format","alt_format","chosen_reason"] + \
                     [f"eligible_{i:02d}" for i in range(1,13)] + [f"weighted_{i:02d}" for i in range(1,13)]
        w = csv.DictWriter(g, fieldnames=fieldnames)
        w.writeheader()
        
        # Build history incrementally as we process
        current_history = []
        
        for row_num, row in enumerate(r, 1):
            elig, suma = eligible_formats(row)
            weighted = {i: weighted_score(i, row) for i in range(1,13)}
            
            chosen, alt = (None, None)
            if elig:
                # Use current history (not old data from CSV)
                chosen, alt = choose_format_with_rotation(
                    row.get("title", ""),
                    elig,
                    weighted,
                    current_history
                )
            
            # Add chosen format to history
            if chosen:
                chosen_name = FORMATS[chosen-1]
                current_history.append(chosen_name)
            
            dur = duration(suma, int(row.get("H_zlozonosc") or 0))
            
            # Update row with new data
            row["SUMA_points"] = suma
            row["duration_min"] = dur
            row["chosen_format"] = FORMATS[chosen-1] if chosen else ""
            row["alt_format"] = FORMATS[alt-1] if alt else ""
            
            # Update last3_formats with current history
            row["last3_formats"] = json.dumps(current_history[-3:] if len(current_history) >= 3 else current_history)
            row["format_history"] = json.dumps(current_history)
            
            # Better reason
            last3 = current_history[-3:] if len(current_history) >= 3 else current_history
            row["chosen_reason"] = f"Eligible={sorted(list(elig))}; Blocked={last3}; History_len={len(current_history)}"
            
            for i in range(1,13):
                row[f"eligible_{i:02d}"] = 1 if i in elig else 0
                row[f"weighted_{i:02d}"] = weighted[i]
            
            w.writerow(row)
    
    # Print distribution summary
    print("\n" + "="*60)
    print("FINAL DISTRIBUTION SUMMARY:")
    print("="*60)
    
    usage_counts = Counter(current_history)
    total = len(current_history)
    
    for fmt in FORMATS:
        count = usage_counts.get(fmt, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 2)
        print(f"{fmt:35} {count:3} ({pct:5.1f}%) {bar}")
    
    never_used = [fmt for fmt in FORMATS if fmt not in usage_counts]
    if never_used:
        print(f"\nNEVER USED: {never_used}")
    else:
        print("\n✅ ALL FORMATS WERE USED!")
    
    print(f"\nTotal books processed: {total}")
    print(f"Unique formats used: {len(usage_counts)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_selector_v3.py input.csv output.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])