#!/usr/bin/env python3
import csv

with open('config/audio_format_output.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['book_folder_id'] == '0020_narnia':
            print(f"Chosen format: {row['chosen_format']}")
            print(f"Alternative format: {row['alt_format']}")
            print(f"Duration: {row['duration_min']} min")
            print(f"Total points: {row['SUMA_points']}")
            print(f"Reason: {row['chosen_reason']}")
            break