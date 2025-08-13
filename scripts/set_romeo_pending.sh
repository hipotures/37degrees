#!/bin/bash

# Skrypt do ustawienia wszystkich itemów w 0030_romeo_and_juliet na:
# - status: pending
# - image_generated: completed  
# - image_downloaded: pending

echo "Ustawiam wszystkie itemy w 0030_romeo_and_juliet..."

for i in {1..25}; do
    # Formatuj numer z wiodącymi zerami
    if [ $i -lt 10 ]; then
        item_key="item_000$i"
    else
        item_key="item_00$i"
    fi
    
    echo "Ustawiam $item_key..."
    
    # Ustaw status na pending
    todoit item status 0030_romeo_and_juliet "$item_key" --status completed
    
    # Ustaw properties
    todoit item property set 0030_romeo_and_juliet "$item_key" image_generated completed
    todoit item property set 0030_romeo_and_juliet "$item_key" image_downloaded completed
done

echo "✅ Ukończono ustawianie wszystkich itemów!"

