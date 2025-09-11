import csv, sys, hashlib

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
    "Wykład filologiczny w duecie",
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
    try:
        A=int(row["A_kontrowersyjnosc"] or 0)
        B=int(row["B_glebia"] or 0)
        C=int(row["C_fenomen"] or 0)
        D=int(row["D_rezonans"] or 0)
        E=int(row["E_polski_kontekst"] or 0)
        F=int(row["F_aktualnosc"] or 0)
        G=int(row["G_innowacyjnosc"] or 0)
        H=int(row["H_zlozonosc"] or 0)
        I=int(row["I_gender"] or 0)
        
        year=int(row["year"] or 0)
        translations=int(row["translations_count"] or 0)
        
        print(f"DEBUG: Processing {row.get('book_folder_id', 'UNKNOWN')}: A={A},B={B},C={C},D={D},E={E},F={F},G={G},H={H},I={I}")
        
        suma = A+B+C+D+E+F+G+H+I
        elig = set()
        
        # Rules
        if A >= 3 and F >= 4:
            elig.add(3)  # Adwokat/Sceptyk
        if H >= 4 and A >= 3:
            elig.add(4)  # Reporter/Świadek
        if F >= 4 and D >= 3:
            elig.add(5)  # Współczesny/Klasyk
        if B >= 4 and G >= 4:
            elig.add(6)  # Emocja/Analiza
        if E >= 4 and C >= 3:
            elig.add(7)  # Lokalny/Globalny
        if C >= 5 and D >= 3:
            elig.add(8)  # Fan/Nowicjusz
        if I >= 4:
            elig.add(9)  # Perspektywa Ona/On
        if G >= 5 and B >= 4:
            elig.add(10)  # Wykład filologiczny
        if E >= 4 and translations >= 3:
            elig.add(11)  # Glosa
        if H >= 4 and year < 1950:
            elig.add(12)  # Komentarz
            
        # Always eligible
        elig.add(1)  # Przyjacielska wymiana
        elig.add(2)  # Mistrz i Uczeń
        
        print(f"DEBUG: Eligible formats: {elig}")
        return elig, suma
        
    except Exception as e:
        print(f"ERROR in eligible_formats: {e}")
        print(f"Row data: {row}")
        return set([1]), 0

def weighted_score(fmt, row):
    try:
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
    except Exception as e:
        print(f"ERROR in weighted_score: {e}")
        return 0.0

def tie_break(title, elig, weighted, last3_str):
    try:
        if not elig:
            return None, None
        
        # Find top by weighted score
        scores = [(weighted[f], f) for f in elig]
        max_score = max(scores)[0]
        top = [f for s, f in scores if s == max_score]
        
        if len(top) == 1:
            return top[0], None
            
        # deterministic by hash(title)
        h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
        chosen = top[h % len(top)]
        
        # alt = best different from chosen (if any)
        alt = None
        for f in top:
            if f != chosen:
                alt = f
                break
                
        return chosen, alt
        
    except Exception as e:
        print(f"ERROR in tie_break: {e}")
        return 1, None  # fallback

def main(inp, outp):
    with open(inp, newline="", encoding="utf-8") as f, open(outp, "w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        
        print(f"DEBUG: Fieldnames from input: {r.fieldnames}")
        
        fieldnames = list(r.fieldnames) + ["SUMA_points","duration_min","chosen_format","alt_format","chosen_reason"] + \
                     [f"eligible_{i:02d}" for i in range(1,13)] + [f"weighted_{i:02d}" for i in range(1,13)]
        
        print(f"DEBUG: Output fieldnames: {fieldnames}")
        
        w = csv.DictWriter(g, fieldnames=fieldnames)
        w.writeheader()
        
        for row_num, row in enumerate(r):
            print(f"DEBUG: Processing row {row_num}: {row.get('book_folder_id', 'UNKNOWN')}")
            
            # Check for None values in keys
            for key, value in row.items():
                if key is None:
                    print(f"ERROR: Found None key in row {row_num}: {value}")
                    
            try:
                elig, suma = eligible_formats(row)
                weighted = {i: weighted_score(i, row) for i in range(1,13)}
                last3 = row.get("last3_formats","")
                chosen, alt = (None, None)
                if elig:
                    chosen, alt = tie_break(row.get("title",""), elig, weighted, last3)
                dur = duration(suma, int(row.get("H_zlozonosc") or 0))
                
                # enrich row - clear any None keys first
                new_row = {k: v for k, v in row.items() if k is not None}
                
                new_row["SUMA_points"] = suma
                new_row["duration_min"] = dur
                new_row["chosen_format"] = FORMATS[chosen-1] if chosen else ""
                new_row["alt_format"] = FORMATS[alt-1] if alt else ""
                new_row["chosen_reason"] = f"Eligible={sorted(list(elig))}; max_weighted={max(weighted.values()) if elig else 0}"
                
                for i in range(1,13):
                    new_row[f"eligible_{i:02d}"] = 1 if i in elig else 0
                    new_row[f"weighted_{i:02d}"] = weighted[i]
                
                print(f"DEBUG: Final row keys: {list(new_row.keys())}")
                
                w.writerow(new_row)
                print(f"DEBUG: Successfully wrote row {row_num}")
                
            except Exception as e:
                print(f"ERROR processing row {row_num}: {e}")
                print(f"Row data: {row}")
                raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_selector_debug.py input.csv output.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])