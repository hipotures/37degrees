#!/bin/bash

# Script to reset scene_gen and scene_style status to pending for books 0050-0079
# Usage: ./scripts/reset-scene-status-0050-0079.sh

echo "Resetting scene_gen and scene_style status to pending for books 0050-0079..."

# List of books from 0050 to 0079
books=(
    "0050_the_three_musketeers"
    "0051_mobydick"
    "0052_uncle_toms_cabin"
    "0053_the_scarlet_letter"
    "0054_the_catcher_in_the_rye"
    "0055_of_mice_and_men"
    "0056_the_grapes_of_wrath"
    "0057_east_of_eden"
    "0058_for_whom_the_bell_tolls"
    "0059_a_farewell_to_arms"
    "0060_the_sun_also_rises"
    "0061_one_flew_over_the_cuckoos_nest"
    "0062_catch22"
    "0063_slaughterhousefive"
    "0064_the_metamorphosis"
    "0065_the_castle"
    "0066_doctor_zhivago"
    "0067_the_gulag_archipelago"
    "0068_one_day_in_the_life_of_ivan_denisovich"
    "0069_lolita"
    "0070_on_the_road"
    "0071_beloved"
    "0072_the_color_purple"
    "0073_their_eyes_were_watching_god"
    "0074_invisible_man"
    "0075_native_son"
    "0076_things_fall_apart"
    "0077_the_god_of_small_things"
    "0078_midnights_children"
    "0079_the_satanic_verses"
)

# Counter for progress
total=${#books[@]}
current=0

for book in "${books[@]}"; do
    current=$((current + 1))
    echo "[$current/$total] Processing $book..."
    
    # Process all 25 scenes (scene_0001 to scene_0025)
    for scene_num in {1..25}; do
        scene_key=$(printf "scene_%04d" $scene_num)
        echo "  Processing $scene_key..."
        
        # Set scene_gen to pending
        todoit item status \
            --list "$book" \
            --item "$scene_key" \
            --subitem "scene_gen" \
            --status "pending" 2>/dev/null || echo "    Warning: $scene_key/scene_gen not found"
        
        # Set scene_style to pending  
        todoit item status \
            --list "$book" \
            --item "$scene_key" \
            --subitem "scene_style" \
            --status "pending" 2>/dev/null || echo "    Warning: $scene_key/scene_style not found"
    done
    
    echo "  ✓ Completed $book"
    echo
done

echo "✓ All books processed successfully!"
echo "Reset scene_gen and scene_style to pending for $total books (0050-0079)"