#!/bin/bash

# Batch setup TODOIT structures for multiple books
# Calls setup-todoit-structure.sh for each book folder
# Usage: ./scripts/batch-setup-todoit.sh

echo "📋 BATCH SETUP TODOIT STRUCTURES"
echo "================================="
echo ""

# List of books to process (add/remove as needed)
BOOKS=(
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
    "0080_a_passage_to_india"
    "0081_the_jungle_book"
    "0082_heart_of_darkness"
    "0083_lord_of_the_flies"
    "0084_a_clockwork_orange"
    "0085_the_handmaids_tale"
    "0086_frankenstein"
    "0087_dracula"
    "0088_the_strange_case_of_dr_jekyll_and_mr_hyde"
    "0089_twenty_thousand_leagues_under_the_sea"
    "0090_around_the_world_in_eighty_days"
    "0091_journey_to_the_center_of_the_earth"
    "0092_the_time_machine"
    "0093_the_war_of_the_worlds"
    "0094_the_invisible_man"
    "0095_foundation"
    "0096_i_robot"
    "0097_neuromancer"
    "0098_the_man_in_the_high_castle"
    "0099_do_androids_dream_of_electric_sheep"
    "0100_the_left_hand_of_darkness"
    "0101_the_epic_of_gilgamesh"
    "0102_the_divine_comedy"
    "0103_one_thousand_and_one_nights"
    "0104_the_canterbury_tales"
    "0105_a_christmas_carol"
    "0106_the_tale_of_genji"
    "0107_journey_to_the_west"
    "0108_candide"
    "0109_faust"
    "0110_oedipus_rex"
    "0111_a_dolls_house"
    "0112_ulysses"
    "0113_all_quiet_on_the_western_front"
    "0114_the_diary_of_anne_frank"
    "0115_mahabharata"
    "0116_ramayana"
    "0117_aeneid"
    "0118_the_republic"
    "0119_the_art_of_war"
    "0120_the_prince"
    "0121_essays"
    "0122_leviathan"
    "0123_the_social_contract"
    "0124_the_wealth_of_nations"
    "0125_a_vindication_of_the_rights_of_woman"
    "0126_the_communist_manifesto"
    "0127_on_liberty"
    "0128_thus_spoke_zarathustra"
    "0129_the_second_sex"
    "0130_the_wretched_of_the_earth"
    "0131_on_the_origin_of_species"
    "0132_the_interpretation_of_dreams"
    "0133_silent_spring"
    "0134_père_goriot"
    "0135_adventures_of_huckleberry_finn"
    "0136_in_search_of_lost_time"
    "0137_mrs_dalloway"
    "0138_the_waste_land"
    "0139_the_sound_and_the_fury"
    "0140_the_stranger"
    "0141_waiting_for_godot"
    "0142_the_real_story_of_ahq"
    "0143_gitanjali"
    "0144_ficciones"
    "0145_the_cairo_trilogy"
    "0146_season_of_migration_to_the_north"
    "0147_the_house_of_the_spirits"
    "0148_red_sorghum"
    "0149_the_oresteia"
    "0150_tartuffe"
    "0151_death_of_a_salesman"
    "0152_a_streetcar_named_desire"
    "0153_long_days_journey_into_night"
    "0154_mother_courage_and_her_children"
)

TOTAL=${#BOOKS[@]}
SUCCESS_COUNT=0
ERROR_COUNT=0

echo "📚 Processing $TOTAL books..."
echo ""

for i in "${!BOOKS[@]}"; do
    BOOK="${BOOKS[$i]}"
    CURRENT=$((i + 1))
    
    echo "[$CURRENT/$TOTAL] 🚀 Setting up: $BOOK"
    
    # Call setup-todoit-structure.sh for this book
    if ./scripts/setup-todoit-structure.sh "$BOOK"; then
        echo "  ✅ Success: $BOOK"
        ((SUCCESS_COUNT++))
    else
        echo "  ❌ Error: $BOOK"
        ((ERROR_COUNT++))
    fi
    
    echo ""
done

echo "========================================="
echo "📊 BATCH SETUP COMPLETE!"
echo ""
echo "📚 Total books: $TOTAL"
echo "✅ Successful: $SUCCESS_COUNT"
echo "❌ Errors: $ERROR_COUNT"
echo ""

if [ $ERROR_COUNT -gt 0 ]; then
    echo "⚠️  Some books failed - check output above"
    exit 1
else
    echo "🎉 All books processed successfully!"
fi
