
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

def tie_break(title, elig, weighted, last3):
    # cooldown preference
    cooldown = set([x.strip() for x in last3.split("|") if x.strip()])
    # prefer formats not used in last 3
    candidates = [f for f in elig if FORMATS[f-1] not in cooldown]
    if not candidates:
        candidates = list(elig)
    # choose max weighted
    max_w = max(weighted[f] for f in candidates)
    top = [f for f in candidates if weighted[f] == max_w]
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

def main(inp, outp):
    with open(inp, newline="", encoding="utf-8") as f, open(outp, "w", newline="", encoding="utf-8") as g:
        r = csv.DictReader(f)
        fieldnames = r.fieldnames + ["SUMA_points","duration_min","chosen_format","alt_format","chosen_reason"] + \
                     [f"eligible_{i:02d}" for i in range(1,13)] + [f"weighted_{i:02d}" for i in range(1,13)]
        w = csv.DictWriter(g, fieldnames=fieldnames)
        w.writeheader()
        for row in r:
            elig, suma = eligible_formats(row)
            weighted = {i: weighted_score(i, row) for i in range(1,13)}
            last3 = row.get("last3_formats","")
            chosen, alt = (None, None)
            if elig:
                chosen, alt = tie_break(row.get("title",""), elig, weighted, last3)
            dur = duration(suma, int(row.get("H_zlozonosc") or 0))
            # enrich row
            row["SUMA_points"] = suma
            row["duration_min"] = dur
            row["chosen_format"] = FORMATS[chosen-1] if chosen else ""
            row["alt_format"] = FORMATS[alt-1] if alt else ""
            row["chosen_reason"] = f"Eligible={sorted(list(elig))}; max_weighted={max(weighted.values()) if elig else 0}"
            for i in range(1,13):
                row[f"eligible_{i:02d}"] = 1 if i in elig else 0
                row[f"weighted_{i:02d}"] = weighted[i]
            w.writerow(row)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_selector.py input.csv output.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
