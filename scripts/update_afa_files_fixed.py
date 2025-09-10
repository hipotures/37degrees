#!/usr/bin/env python3
"""
Update AFA files with new format distribution from audio_format_output.csv
Fixed version with correct host prompts for each format
"""

import csv
import re
import shutil
from pathlib import Path
from datetime import datetime

# Format prompts based on system_wyboru_formatu_audio.md
# IMPORTANT: Host A = mężczyzna, Host B = kobieta
FORMAT_PROMPTS = {
    1: {  # Przyjacielska wymiana
        "name": "Przyjacielska wymiana",
        "A_name": "Michał",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Michał (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś entuzjastycznym miłośnikiem książek. Dzielisz się osobistymi refleksjami, łączysz wątki z życiem. Mów naturalnie, używaj potocznego języka. 3-4 zdania na wypowiedź."',
        "B_name": "Kasia",
        "B_gender": "kobieta", 
        "B_prompt": 'Host B = Kasia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Jesteś ciekawską przyjaciółką. Zadajesz pytania o emocje, dopytuj \'dlaczego tak cię to dotknęło?\'. Podchwytuj wątki, rozwijaj je. Mów potocznie."',
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
        "B_prompt": 'Host B = Ola (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Reprezentujesz współczesną perspektywę. Łączysz książkę z obecnymi trendami, social media, popkulturą. Używaj współczesnych analogii."',
        "structure_note": "Zderzenie perspektyw czasowych"
    },
    6: {  # Emocja i Analiza
        "name": "Emocja i Analiza",
        "A_name": "Piotr",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Piotr (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Jesteś analitykiem. Rozkładasz strukturę, analizujesz techniki narracyjne, symbolikę. Zachowujesz dystans, używasz precyzyjnych terminów."',
        "B_name": "Ewa",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Ewa (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Reagujesz emocjonalnie na książkę. Mówisz o uczuciach, które wzbudza, identyfikujesz się z bohaterami. Używaj języka uczuć i wrażeń."',
        "structure_note": "Uczucia vs rozum"
    },
    7: {  # Lokalny i Globalny
        "name": "Lokalny i Globalny",
        "A_name": "Robert",
        "A_gender": "mężczyzna",
        "A_prompt": 'Host A = Robert (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.\n"Przedstawiasz perspektywę globalną. Mówisz o światowej recepcji, różnych interpretacjach kulturowych, uniwersalnych tematach."',
        "B_name": "Agnieszka",
        "B_gender": "kobieta",
        "B_prompt": 'Host B = Agnieszka (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Znasz polski kontekst. Opowiadasz o polskich przekładach, recepcji, adaptacjach. Łączysz z polską kulturą i edukacją."',
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
        "B_prompt": 'Host B = Natalia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.\n"Analizujesz książkę z perspektywy kobiecej. Zwracasz uwagę na role płciowe, reprezentację kobiet, relacje między postaciami."',
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
    new_content.append("## METRYKA DZIEŁA")
    if 'book_meta' in sections:
        new_content.append(sections['book_meta'].rstrip())
    else:
        new_content.append("")
        new_content.append("**Tytuł**: ")
        new_content.append("**Autor**: ")
        new_content.append("**Rok wydania**: ")
        new_content.append("**Gatunek**: ")
    new_content.append("")
    
    # Scores
    new_content.append("## PUNKTACJA SZCZEGÓŁOWA")
    if 'scores' in sections:
        new_content.append(sections['scores'].rstrip())
    new_content.append("")
    
    # Format section
    new_content.append("## FORMAT")
    new_content.append("")
    new_content.append(f"- **Główny:** {new_format_name} — format przydzielony według nowej dystrybucji")
    new_content.append(f"- **Alternatywny:** Przyjacielska wymiana (uniwersalny fallback)")
    new_content.append(f"- **Długość:** {duration} min (suma={suma_points})")
    new_content.append(f"- **Uzasadnienie:** Format wybrany na podstawie algorytmu dystrybucji zapewniającego różnorodność i rotację wszystkich 12 formatów.")
    new_content.append("")
    
    # Threads
    new_content.append("## KLUCZOWE WĄTKI Z WIARYGODNOŚCIĄ")
    if 'threads' in sections:
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
    new_content.append("## MAPOWANIE WĄTKÓW NA STRUKTURĘ")
    if 'mapping' in sections:
        new_content.append(sections['mapping'].rstrip())
    else:
        new_content.append("━" * 37)
        new_content.append("")
        new_content.append("**Część 1: Hook** (3 min) — rola: A — wątek: [wstęp]")
        new_content.append("**Część 2: Główny temat** (3 min) — rola: B — wątek: [rozwinięcie]")
        new_content.append("**Część 3: Kontrowersje** (3 min) — rola: A — wątek: [dyskusja]")
        new_content.append("**Część 4: Współczesność** (3 min) — rola: B — wątek: [paralele]")
        new_content.append(f"**Część 5: Podsumowanie** ({duration-12} min) — rola: A+B — wątek: [zakończenie]")
        new_content.append("")
        new_content.append("━" * 37)
    new_content.append("")
    
    # Educational block
    if 'educational' in sections:
        new_content.append("## BLOK EDUKACYJNY (lektura szkolna)")
        new_content.append(sections['educational'].rstrip())
        new_content.append("")
    
    # Metadata
    if 'metadata' in sections:
        new_content.append("## METADANE PRODUKCYJNE")
        new_content.append(sections['metadata'].rstrip())
        new_content.append("")
    else:
        new_content.append("## METADANE PRODUKCYJNE")
        new_content.append("- Tempo: 130 słów/min")
        new_content.append("- Pauzy: [naturalne]")
        new_content.append("- Dżingle: Intro/Przejścia/Outro")
        new_content.append("")
    
    # Footer
    new_content.append("---")
    new_content.append(f"*Dokument zaktualizowany {datetime.now().strftime('%Y-%m-%d')} przez system AFA*")
    new_content.append(f"*Book ID: {book_name} | Format: {new_format_name} | Czas: {duration} min*")
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_content))

def main():
    # Read the CSV with new format assignments
    csv_path = Path("config/audio_format_output.csv")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Found {len(rows)} books to update")
    
    for row in rows:
        book_id = row['book_folder_id']
        format_id = int(row['chosen_format_id'])
        format_name = row['chosen_format']
        duration = int(row['duration_min'])
        suma = int(row['suma_points'])
        
        # Find AFA file
        afa_pattern = f"books/{book_id}/docs/{book_id}-afa.md"
        afa_files = list(Path(".").glob(afa_pattern))
        
        if not afa_files:
            print(f"  ⚠️ No AFA file found for {book_id}")
            continue
        
        afa_file = afa_files[0]
        print(f"📝 Updating: {afa_file}")
        print(f"  New format: {format_name} (ID: {format_id})")
        print(f"  Duration: {duration} min")
        
        update_afa_file(afa_file, format_id, format_name, duration, suma)
        print(f"  ✅ Updated successfully")

if __name__ == "__main__":
    main()