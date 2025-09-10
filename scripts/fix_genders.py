#!/usr/bin/env python3
"""
Fix gender assignments in update_afa_files.py
Host A should be male, Host B should be female
"""

with open('scripts/update_afa_files.py', 'r') as f:
    content = f.read()

# Define correct gender assignments
# Format: (old_A_name, old_A_gender, new_A_name, old_B_name, old_B_gender, new_B_name)
replacements = [
    # Format 1 - already fixed manually
    # Format 2 - already correct (Andrzej/Julia)
    # Format 3
    ('        "A_name": "Marta",\n        "A_gender": "kobieta",', 
     '        "A_name": "Tomasz",\n        "A_gender": "mężczyzna",'),
    ('Host A = Marta (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Tomasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('"Jesteś adwokatką dzieła.',
     '"Jesteś adwokatem dzieła.'),
    ('        "B_name": "Tomasz",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Marta",\n        "B_gender": "kobieta",'),
    ('Host B = Tomasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Marta (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    ('"Jesteś sceptycznym krytykiem.',
     '"Jesteś sceptyczną krytyczką.'),
    
    # Format 4
    ('        "A_name": "Anna",\n        "A_gender": "kobieta",',
     '        "A_name": "Marek",\n        "A_gender": "mężczyzna",'),
    ('Host A = Anna (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Marek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('"Jesteś reporterką relacjonującą',
     '"Jesteś reporterem relacjonującym'),
    ('        "B_name": "Marek",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Anna",\n        "B_gender": "kobieta",'),
    ('Host B = Marek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Anna (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    ('uczestnika, dodajesz detale',
     'uczestniczki, dodajesz detale'),
    ('jakbyś tam był.',
     'jakbyś tam była.'),
    
    # Format 5
    ('        "A_name": "Ola",\n        "A_gender": "kobieta",',
     '        "A_name": "Profesor Jan",\n        "A_gender": "mężczyzna",'),
    ('Host A = Ola (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Profesor Jan (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('        "B_name": "Profesor Jan",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Ola",\n        "B_gender": "kobieta",'),
    ('Host B = Profesor Jan (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Ola (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    # Swap prompts for format 5
    ('"Reprezentujesz współczesną perspektywę. Łączysz książkę z obecnymi trendami, social media, popkulturą. Używaj współczesnych analogii."',
     '"Jesteś klasykiem, znasz kontekst historyczny. Wyjaśniasz oryginalne intencje autora, konwencje epoki. Bronisz wartości ponadczasowych."'),
    
    # Format 6
    ('        "A_name": "Ewa",\n        "A_gender": "kobieta",',
     '        "A_name": "Piotr",\n        "A_gender": "mężczyzna",'),
    ('Host A = Ewa (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Piotr (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('        "B_name": "Piotr",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Ewa",\n        "B_gender": "kobieta",'),
    ('Host B = Piotr (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Ewa (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    # Swap prompts for format 6
    ('"Reagujesz emocjonalnie na książkę. Mówisz o uczuciach, które wzbudza, identyfikujesz się z bohaterami. Używaj języka uczuć i wrażeń."',
     '"Jesteś analitykiem. Rozkładasz strukturę, analizujesz techniki narracyjne, symbolikę. Zachowujesz dystans, używasz precyzyjnych terminów."'),
    
    # Format 7
    ('        "A_name": "Agnieszka",\n        "A_gender": "kobieta",',
     '        "A_name": "Robert",\n        "A_gender": "mężczyzna",'),
    ('Host A = Agnieszka (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Robert (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('        "B_name": "Robert",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Agnieszka",\n        "B_gender": "kobieta",'),
    ('Host B = Robert (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Agnieszka (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    # Swap prompts for format 7
    ('"Znasz polski kontekst. Opowiadasz o polskich przekładach, recepcji, adaptacjach. Łączysz z polską kulturą i edukacją."',
     '"Przedstawiasz perspektywę globalną. Mówisz o światowej recepcji, różnych interpretacjach kulturowych, uniwersalnych tematach."'),
    
    # Format 8
    ('        "A_name": "Magda",\n        "A_gender": "kobieta",',
     '        "A_name": "Bartek",\n        "A_gender": "mężczyzna",'),
    ('Host A = Magda (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Bartek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('"Jesteś superfanką książki.',
     '"Jesteś superfanem książki.'),
    ('        "B_name": "Bartek",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Magda",\n        "B_gender": "kobieta",'),
    ('Host B = Bartek (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Magda (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    
    # Format 9
    ('        "A_name": "Natalia",\n        "A_gender": "kobieta",',
     '        "A_name": "Adam",\n        "A_gender": "mężczyzna",'),
    ('Host A = Natalia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Adam (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('        "B_name": "Adam",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Natalia",\n        "B_gender": "kobieta",'),
    ('Host B = Adam (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Natalia (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    # Swap prompts for format 9
    ('"Analizujesz książkę z perspektywy kobiecej. Zwracasz uwagę na role płciowe, reprezentację kobiet, relacje między postaciami."',
     '"Przedstawiasz męską perspektywę odbioru. Zwracasz uwagę na inne aspekty fabuły, bohaterów, konfliktów."'),
    
    # Format 10 - already correct (Jerzy/Monika)
    
    # Format 11
    ('        "A_name": "Beata",\n        "A_gender": "kobieta",',
     '        "A_name": "Krzysztof",\n        "A_gender": "mężczyzna",'),
    ('Host A = Beata (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Krzysztof (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('"Jesteś tłumaczką.',
     '"Jesteś tłumaczem.'),
    ('        "B_name": "Krzysztof",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Beata",\n        "B_gender": "kobieta",'),
    ('Host B = Krzysztof (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Beata (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    ('"Jesteś czytelnikiem różnych',
     '"Jesteś czytelniczką różnych'),
    
    # Format 12
    ('        "A_name": "Prof. Barbara",\n        "A_gender": "kobieta",',
     '        "A_name": "Prof. Łukasz",\n        "A_gender": "mężczyzna",'),
    ('Host A = Prof. Barbara (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.',
     'Host A = Prof. Łukasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.'),
    ('        "B_name": "Łukasz",\n        "B_gender": "mężczyzna",',
     '        "B_name": "Barbara",\n        "B_gender": "kobieta",'),
    ('Host B = Łukasz (mężczyzna). Mów w pierwszej osobie w rodzaju męskim.',
     'Host B = Barbara (kobieta). Mów w pierwszej osobie w rodzaju żeńskim.'),
    ('"Jesteś ciekawym słuchaczem.',
     '"Jesteś ciekawą słuchaczką.'),
]

# Apply replacements
for old, new in replacements:
    content = content.replace(old, new)

# Write back
with open('scripts/update_afa_files.py', 'w') as f:
    f.write(content)

print("Fixed gender assignments in update_afa_files.py")