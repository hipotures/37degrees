#!/usr/bin/env python3
"""
Update AFA files with new format distribution from audio_format_output.csv
"""

import csv
import re
import shutil
from pathlib import Path
from datetime import datetime

# Format prompts based on system_wyboru_formatu_audio.md
FORMAT_PROMPTS = {
    1: {  # Przyjacielska wymiana
        "name": "Przyjacielska wymiana",
        "A_name": "Michał",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Michał (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś entuzjastycznym miłośnikiem książek. Dzielisz się osobistymi refleksjami, łączysz wątki z życiem. Mów naturalnie, używaj potocznego języka. 3-4 zdania na wypowiedź."',
        "B_name": "Kasia",
        "B_gender": "kobieta", 
        "B_prompt": 'Host B = Kasia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś ciekawską przyjaciółką. Zadajesz pytania o emocje, dopytuj',
        "structure_note": "Swobodna rozmowa przyjaciół"
    },
    2: {  # Mistrz i Uczeń
        "name": "Mistrz i Uczeń",
        "A_name": "Profesor Andrzej",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Profesor Andrzej (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś doświadczonym filologiem. Cel: porządkować pojęcia i budować mosty między dziełami. Używaj porównań, definicji 1-2 zdania. Każdy termin wyjaśnij krótko. Po każdym bloku oddaj głos B: „co w tym niejasne?"."',
        "B_name": "Julia",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Julia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś bystrą studentką. Zadajesz precyzyjne pytania „czy to znaczy, że…?". Prosisz o przykłady z tekstu. Gdy coś niejasne, prosisz o parafrazę. Zwięźle podsumowujesz, zanim oddasz głos A."',
        "structure_note": "Dialog edukacyjny z wyjaśnieniami"
    },
    3: {  # Adwokat i Sceptyk
        "name": "Adwokat i Sceptyk",
        "A_name": "Tomasz",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Tomasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś adwokatem dzieła. Bronisz kontrowersyjnych wątków, znajdujesz uzasadnienia dla trudnych tematów. Używaj argumentów i faktów. Odnosisz się do kontekstu historycznego."',
        "B_name": "Marta",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Marta (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś sceptyczną krytyczką. Kwestionujesz założenia, wskazujesz problemy moralne i anachronizmy. Pytasz „ale czy to nie jest problematyczne?". Dbasz o współczesną wrażliwość."',
        "structure_note": "Debata o kontrowersjach"
    },
    4: {  # Reporter i Świadek
        "name": "Reporter i Świadek",
        "A_name": "Marek",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Marek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś reporterem relacjonującym wydarzenia. Opisujesz sceny, rekonstruujesz fakty, zadajesz pytania świadkowi. Mów dynamicznie, buduj napięcie."',
        "B_name": "Anna",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Anna (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś świadkiem wydarzeń z książki. Opowiadasz z perspektywy uczestniczki, dodajesz detale sensoryczne. Mów emocjonalnie, jakbyś tam była."',
        "structure_note": "Relacja z wydarzeń fabularnych"
    },
    5: {  # Współczesny i Klasyk
        "name": "Współczesny i Klasyk",
        "A_name": "Profesor Jan",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Profesor Jan (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś klasykiem, znasz kontekst historyczny. Wyjaśniasz oryginalne intencje autora, konwencje epoki. Bronisz wartości ponadczasowych."',
        "B_name": "Ola",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Ola (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś klasykiem, znasz kontekst historyczny. Wyjaśniasz oryginalne intencje autora, konwencje epoki. Bronisz wartości ponadczasowych."',
        "structure_note": "Zderzenie perspektyw czasowych"
    },
    6: {  # Emocja i Analiza
        "name": "Emocja i Analiza",
        "A_name": "Piotr",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Piotr (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś analitykiem. Rozkładasz strukturę, analizujesz techniki narracyjne, symbolikę. Zachowujesz dystans, używasz precyzyjnych terminów."',
        "B_name": "Ewa",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Ewa (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś analitykiem. Rozkładasz strukturę, analizujesz techniki narracyjne, symbolikę. Zachowujesz dystans, używasz precyzyjnych terminów."',
        "structure_note": "Uczucia vs rozum"
    },
    7: {  # Lokalny i Globalny
        "name": "Lokalny i Globalny",
        "A_name": "Robert",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Robert (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Przedstawiasz perspektywę globalną. Mówisz o światowej recepcji, różnych interpretacjach kulturowych, uniwersalnych tematach."',
        "B_name": "Agnieszka",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Agnieszka (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Przedstawiasz perspektywę globalną. Mówisz o światowej recepcji, różnych interpretacjach kulturowych, uniwersalnych tematach."',
        "structure_note": "Polski vs światowy kontekst"
    },
    8: {  # Fan i Nowicjusz
        "name": "Fan i Nowicjusz",
        "A_name": "Bartek",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Bartek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś superfanem książki. Z entuzjazmem opowiadasz o ulubionych fragmentach, ciekawostkach, teoriach fanowskich. Zarażasz pasją."',
        "B_name": "Magda",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Magda (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Nie znasz książki. Zadajesz podstawowe pytania, prosisz o wyjaśnienia. Reagujesz zaskoczeniem na zwroty akcji."',
        "structure_note": "Wprowadzenie dla początkujących"
    },
    9: {  # Perspektywa Ona/On
        "name": "Perspektywa Ona/On",
        "A_name": "Adam",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Adam (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Przedstawiasz męską perspektywę odbioru. Zwracasz uwagę na inne aspekty fabuły, bohaterów, konfliktów."',
        "B_name": "Natalia",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Natalia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Przedstawiasz męską perspektywę odbioru. Zwracasz uwagę na inne aspekty fabuły, bohaterów, konfliktów."',
        "structure_note": "Różnice w odbiorze płciowym"
    },
    10: {  # Wykład filologiczny w duecie
        "name": "Wykład filologiczny w duecie",
        "A_name": "Profesor Jerzy",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Profesor Jerzy (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś specjalistą od poetyki i edytorstwa. Definiujesz terminy, wskazujesz warianty tekstu, cytujesz edycje krytyczne. 4-6 zdań, precyzyjnie. Kończ pytaniem do B o klarowność."',
        "B_name": "Dr Monika",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Dr Monika (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś filolożką-moderatorką. Tłumaczysz trudne pojęcia, prosisz o przykłady, pilnujesz tempa dla laika. Podsumowujesz punktami."',
        "structure_note": "Akademicka analiza dzieła"
    },
    11: {  # Glosa do przekładów
        "name": "Glosa do przekładów",
        "A_name": "Krzysztof",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Krzysztof (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś tłumaczem. Porównujesz różne przekłady, wyjaśniasz wybory translatorskie, pokazujesz jak zmienia się sens."',
        "B_name": "Beata",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Beata (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś czytelniczką różnych wersji. Pytasz o różnice, dopytuj o niuanse. Dziwisz się rozbieżnościom."',
        "structure_note": "Analiza przekładów"
    },
    12: {  # Komentarz historyczno-literacki
        "name": "Komentarz historyczno-literacki",
        "A_name": "Prof. Łukasz",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Prof. Łukasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś historykiem literatury. Osadzasz dzieło w kontekście epoki, wyjaśniasz konwencje, obyczaje, realia historyczne."',
        "B_name": "Barbara",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Barbara (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś ciekawą słuchaczką. Dopytuj o kontekst, zaskakujące fakty historyczne, związki z innymi dziełami epoki."',
        "structure_note": "Kontekst historyczny i literacki"
    }
}

def backup_file(filepath):
    """Create backup of file before modification"""
    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
    shutil.copy2(filepath, backup_path)
    return backup_path

def extract_sections(content):
    """Extract existing sections from AFA file"""
    sections = {}
    
    # Extract scores (A-I)
    scores_match = re.search(r'## PUNKTACJA SZCZEGÓŁOWA\n(.*?)## FORMAT', content, re.DOTALL)
    if scores_match:
        sections['scores'] = scores_match.group(1)
    
    # Extract threads
    threads_match = re.search(r'## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ\n(.*?)## PROMPTY A/B|## MAPOWANIE', content, re.DOTALL)
    if threads_match:
        sections['threads'] = threads_match.group(1)
    
    # Extract mapping
    mapping_match = re.search(r'## MAPOWANIE WĄTKÓW NA STRUKTURĘ\n(.*?)## BLOK EDUKACYJNY|## METADANE|$', content, re.DOTALL)
    if mapping_match:
        sections['mapping'] = mapping_match.group(1)
    
    # Extract educational block if exists
    edu_match = re.search(r'## BLOK EDUKACYJNY.*?\n(.*?)## (METADANE|PORÓWNANIE|$)', content, re.DOTALL)
    if edu_match:
        sections['educational'] = edu_match.group(1)
    
    # Extract metadata
    meta_match = re.search(r'## METADANE PRODUKCYJNE\n(.*?)(?:---|\*Dokument|$)', content, re.DOTALL)
    if meta_match:
        sections['metadata'] = meta_match.group(1)
    
    # Extract book metadata
    meta_match = re.search(r'## METRYKA DZIEŁA\n(.*?)## PUNKTACJA', content, re.DOTALL)
    if meta_match:
        sections['book_meta'] = meta_match.group(1)
    
    return sections

def update_afa_file(filepath, new_format_id, new_format_name, duration, suma_points):
    """Update single AFA file with new format"""
    
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original
    backup_path = backup_file(filepath)
    print(f"  Backup created: {backup_path}")
    
    # Extract existing sections
    sections = extract_sections(content)
    
    # Get format prompts
    format_data = FORMAT_PROMPTS[new_format_id]
    
    # Build new content
    new_content = []
    
    # Header
    book_name = filepath.parent.parent.name
    title = book_name.split('_', 1)[1].replace('_', ' ').title()
    new_content.append(f"# ANALIZA FORMATU AUDIO — {title.upper()}")
    new_content.append("=" * 32)
    new_content.append("")
    
    # Book metadata
    if 'book_meta' in sections and sections['book_meta']:
        new_content.append("## METRYKA DZIEŁA")
        new_content.append(sections['book_meta'].rstrip())
        new_content.append("")
    
    # Scores
    if 'scores' in sections and sections['scores']:
        new_content.append("## PUNKTACJA SZCZEGÓŁOWA")
        new_content.append(sections['scores'].rstrip())
        new_content.append("")
    
    # Format section
    new_content.append("## FORMAT")
    new_content.append("")
    new_content.append(f"- **Główny:** {format_data['name']} — format przydzielony według nowej dystrybucji")
    new_content.append(f"- **Alternatywny:** Przyjacielska wymiana (uniwersalny fallback)")
    new_content.append(f"- **Długość:** {duration} min (suma={suma_points})")
    new_content.append(f"- **Uzasadnienie:** Format wybrany na podstawie algorytmu dystrybucji zapewniającego różnorodność i rotację wszystkich 12 formatów.")
    new_content.append("")
    
    # Threads
    if 'threads' in sections and sections['threads']:
        new_content.append("## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ")
        new_content.append(sections['threads'].rstrip())
        new_content.append("")
    
    # Prompts A/B
    new_content.append("## PROMPTY A/B DLA FORMATU")
    new_content.append("")
    new_content.append(f"### Prowadzący A — {format_data['A_name']} ({format_data['A_gender'].capitalize()})")
    new_content.append(format_data['A_prompt'])
    new_content.append("")
    new_content.append(f"### Prowadzący B — {format_data['B_name']} ({format_data['B_gender'].capitalize()})")
    new_content.append(format_data['B_prompt'])
    new_content.append("")
    
    # Mapping
    if 'mapping' in sections and sections['mapping']:
        new_content.append("## MAPOWANIE WĄTKÓW NA STRUKTURĘ")
        new_content.append(sections['mapping'].rstrip())
        new_content.append("")
    else:
        # Generate default mapping
        new_content.append("## MAPOWANIE WĄTKÓW NA STRUKTURĘ")
        new_content.append("━" * 40)
        new_content.append(f"**Część 1: Wprowadzenie** (3 min)")
        new_content.append(f"— rola: A wprowadza — {format_data['structure_note']}")
        new_content.append("")
        new_content.append(f"**Część 2: Rozwinięcie** (4 min)")
        new_content.append(f"— rola: dialog A/B — analiza głównych wątków")
        new_content.append("")
        new_content.append(f"**Część 3: Kulminacja** (4 min)")
        new_content.append(f"— rola: B dopytuje — najważniejsze odkrycia")
        new_content.append("")
        new_content.append(f"**Część 4: Podsumowanie** ({duration-11} min)")
        new_content.append(f"— rola: A podsumowuje — wnioski i refleksje")
        new_content.append("━" * 40)
        new_content.append("")
    
    # Educational block
    if 'educational' in sections and sections['educational']:
        new_content.append("## BLOK EDUKACYJNY (lektura szkolna)")
        new_content.append(sections['educational'].rstrip())
        new_content.append("")
    
    # Metadata
    if 'metadata' in sections and sections['metadata']:
        new_content.append("## METADANE PRODUKCYJNE")
        new_content.append(sections['metadata'].rstrip())
        new_content.append("")
    else:
        new_content.append("## METADANE PRODUKCYJNE")
        new_content.append("")
        new_content.append(f"- **Tempo:** 130-140 słów/min")
        new_content.append(f"- **Pauzy:** [PAUSE_2S] po wprowadzeniu, [PAUSE_1S] przy zmianach wątku")
        new_content.append(f"- **Dżingle:** Intro delikatne, Przejścia subtelne, Outro refleksyjne")
        new_content.append(f"- **Ton:** Dostosowany do formatu {format_data['name']}")
        new_content.append(f"- **Balans:** 50% {format_data['A_name']}, 50% {format_data['B_name']}")
        new_content.append("")
    
    # Footer
    new_content.append("---")
    new_content.append(f"*Dokument zaktualizowany {datetime.now().strftime('%Y-%m-%d')} przez system AFA*")
    new_content.append(f"*Book ID: {book_name} | Format: {format_data['name']} | Czas: {duration} min*")
    
    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_content))
    
    return True

def main():
    """Main function to update all AFA files"""
    
    # Read new distribution
    output_path = Path("config/audio_format_output.csv")
    format_assignments = {}
    
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book_id = row['book_folder_id']
            format_assignments[book_id] = {
                'format': row['chosen_format'],
                'format_id': int(row['chosen_format_id']),
                'duration': int(row['duration_min']),
                'suma': int(row['suma_points'])
            }
    
    # Find and update AFA files
    books_dir = Path("books")
    updated_count = 0
    errors = []
    
    for book_id, assignment in format_assignments.items():
        # Skip duplicates in CSV (e.g., multiple entries for same book)
        afa_pattern = f"{book_id}/docs/{book_id}-afa.md"
        afa_paths = list(books_dir.glob(afa_pattern))
        
        if not afa_paths:
            print(f"❌ AFA file not found: {afa_pattern}")
            errors.append(f"Missing: {book_id}")
            continue
        
        afa_path = afa_paths[0]
        print(f"\n📝 Updating: {afa_path}")
        print(f"  New format: {assignment['format']} (ID: {assignment['format_id']})")
        print(f"  Duration: {assignment['duration']} min")
        
        try:
            success = update_afa_file(
                afa_path,
                assignment['format_id'],
                assignment['format'],
                assignment['duration'],
                assignment['suma']
            )
            if success:
                updated_count += 1
                print(f"  ✅ Updated successfully")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors.append(f"Error in {book_id}: {e}")
    
    # Final report
    print("\n" + "=" * 60)
    print("📊 UPDATE SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully updated: {updated_count} files")
    print(f"❌ Errors: {len(errors)}")
    
    if errors:
        print("\n⚠️ ERRORS:")
        for error in errors:
            print(f"  - {error}")
    
    # Show format distribution
    format_counts = {}
    for assignment in format_assignments.values():
        fmt = assignment['format']
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    
    print("\n📈 FORMAT DISTRIBUTION:")
    for fmt_id in range(1, 13):
        fmt_name = FORMAT_PROMPTS[fmt_id]['name']
        count = format_counts.get(fmt_name, 0)
        percent = (count / len(format_assignments)) * 100 if format_assignments else 0
        print(f"  {fmt_id:2}. {fmt_name:35} {count:2} ({percent:5.1f}%)")

if __name__ == '__main__':
    main()