#!/usr/bin/env python3
"""
Update last3_formats column in audio_format_scores.csv based on audio_format_output.csv
"""

import csv
from pathlib import Path

def main():
    scores_path = Path("config/audio_format_scores.csv")
    output_path = Path("config/audio_format_output.csv")
    
    # Read output formats
    output_formats = {}
    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book_id = row['book_folder_id']
            format_name = row['chosen_format']
            output_formats[book_id] = format_name
    
    # Read scores data
    scores_data = []
    with open(scores_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            scores_data.append(row)
    
    # Build format history for last3_formats
    format_history = []
    for i, row in enumerate(scores_data):
        book_id = row['book_folder_id']
        
        # Get the format from output_formats
        if book_id in output_formats:
            current_format = output_formats[book_id]
            format_history.append(current_format)
            
            # Update last3_formats - take last 3 formats up to this point
            if i >= 2:
                last3 = format_history[-3:]
            elif i >= 1:
                last3 = format_history[-2:]
            elif i >= 0:
                last3 = format_history[-1:]
            else:
                last3 = []
            
            # Format as JSON array string
            row['last3_formats'] = str(last3).replace("'", '"')
        else:
            row['last3_formats'] = '[]'
    
    # Write updated data back
    with open(scores_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scores_data)
    
    print(f"Updated {len(scores_data)} rows in audio_format_scores.csv")
    
    # Show sample of updates
    print("\nSample of updated last3_formats:")
    for i in [0, 10, 20, 30, 35]:
        if i < len(scores_data):
            book = scores_data[i]['book_folder_id']
            last3 = scores_data[i]['last3_formats']
            print(f"  {book}: {last3}")

if __name__ == '__main__':
    main()