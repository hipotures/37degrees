#!/bin/bash

set -e

# Script: process_all_media_styles.sh
# Purpose: Apply style changes to ALL 116 media folders using parallel processing
# Usage: ./process_all_media_styles.sh

echo "🚀 Starting batch style processing for all media folders..."

# Define all 116 media folders
MEDIA_FOLDERS=(
    m00001_atomic_bomb m00002_anastasia_assassination m00003_costello_attempt
    m00004_rosenberg_trial_sing_sing m00005_harlem_riots_1943 m00006_waterfront_commission_shape_up
    m00007_kefauver_hearings_50_51 m00008_roswell_incident_1947 m00009_rendlesham_forest_1980
    m00010_belgian_ufo_wave_1989_90 m00011_phoenix_lights_1997 m00012_ohare_airport_ufo_2006
    m00013_uss_nimitz_tic_tac_2004 m00014_betty_barney_hill_1961 m00015_kecksburg_incident_1965
    m00016_dyatlov_pass_1959 m00017_broad_haven_school_1977 m00018_aveley_abduction_1974
    m00019_bonnybridge_hotspot_1977 m00020_solway_spaceman_1964 m00021_glasgow_fireballs_1752
    m00022_liverpool_mile_long_ufo_2007 m00023_conisholme_wind_turbine_2009 m00024_church_stowe_missing_time_1978
    m00025_voynich_manuscript_15th_century m00026_loch_ness_monster_1933 m00027_mary_celeste_1872
    m00028_db_cooper_1971 m00029_zodiac_killer_1968 m00030_market_harborough_airship_1909
    m00031_isle_sheppey_silver_suit_1979 m00032_aldershot_green_men_1983 m00033_clonmacnoise_flying_ship
    m00034_oumuamua_interstellar_2017 m00035_stonehenge_3000bc m00036_atlantis_plato
    m00037_cleopatras_tomb m00038_mh370_disappearance_2014 m00039_hat_man_phenomenon
    m00040_russian_number_stations m00041_grimsby_alien_abduction_2000 m00042_london_n19_orange_lights_2007
    m00043_isle_arran_mushroom_ufo_1985 m00044_greenock_green_ufo_2008 m00045_inverness_orange_lights_2008
    m00046_livingston_cube_uap_2021 m00047_great_emu_war_1932 m00048_war_of_the_bucket_1325
    m00049_window_tax_introduction_1696 m00050_beard_tax_russia_1705 m00051_microwave_oven_invention_1945
    m00052_super_glue_discovery_1942 m00053_teflon_discovery_1938 m00054_gps_satellite_deployment_1973
    m00055_corn_flakes_invention_1894 m00056_post_it_notes_creation_1968 m00057_coca_cola_formula_1885
    m00058_milgram_obedience_experiment_1961 m00059_stanford_prison_experiment_1971 m00060_jane_elliott_eye_color_1968
    m00061_project_mkultra_exposure_1970s m00062_cointelpro_revelation_1971 m00063_tuskegee_syphilis_study_1972
    m00064_cia_heart_attack_gun_1975 m00065_ariane_5_rocket_disaster_1996 m00066_mpemba_effect_discovery_1960s
    m00067_jack_baboon_railway_worker_1881 m00068_michel_lotito_eats_airplane_1978 m00069_longest_eyelash_record_2021
    m00070_immortal_jellyfish_discovery m00071_schrodinger_cat_paradox_1935 m00072_antikythera_mechanism_1901
    m00073_ketchup_fish_sauce_origins_17th m00074_medieval_animal_trials_1386 m00075_credit_card_invention_1949
    m00076_jozef_hofmann_inventions_19th m00077_scarf_camera_record m00078_pistol_shrimp_sonic_weapon
    m00079_twin_paradox_explained_1905 m00080_olbers_paradox_solution_1826 m00081_stanford_marshmallow_test_1960s
    m00082_penicillin_discovery_1928 m00083_dr_martens_boot_origin_1945 m00084_polish_bus_packing_record_2011
    m00085_oymyakon_extreme_cold m00086_bolivian_death_road m00087_satere_mawe_ant_ritual
    m00088_rapatronic_camera_nuclear_1950s m00089_lsd_elephant_experiment_1962 m00090_soviet_two_headed_dog_1954
    m00091_mechanical_monk_automation_1560 m00092_cholut_bridge_volcano_1884 m00093_first_computer_bug_1947
    m00094_greek_bulgarian_dog_war_1925 m00095_anglo_zanzibar_war_1896 m00096_american_pig_war_1859
    m00097_holland_scilly_war_1651 m00098_vasa_warship_sinking_1628 m00099_tacoma_narrows_bridge_1940
    m00100_roy_sullivan_lightning_1942 m00101_evel_knievel_bones_1960s m00102_chimborazo_farthest_point
    m00103_challenger_deep_point_1960 m00104_atacama_desert_drought_1570 m00105_oymyakon_coldest_place_1924
    m00106_mars_climate_orbiter_1999 m00107_french_trains_too_wide_2014 m00108_cell_phones_vs_toilets_2013
    m00109_trees_outnumber_stars_2015 m00110_kellogg_ape_child_experiment_1931 m00111_monster_study_stuttering_1939
    m00112_monte_carlo_consecutive_blacks_1913 m00113_monty_hall_paradox_1975 m00114_placebo_effect_healing
    m00115_nocebo_effect_harm m00116_dunning_kruger_effect_1999
)

TOTAL_FOLDERS=${#MEDIA_FOLDERS[@]}
PARALLEL_JOBS=8
SUCCESS_COUNT=0
FAILURE_COUNT=0

echo "📊 Total folders to process: $TOTAL_FOLDERS"
echo "⚡ Parallel jobs: $PARALLEL_JOBS"
echo ""

# Create temporary directory for progress tracking
TEMP_DIR=$(mktemp -d)
SUCCESS_FILE="$TEMP_DIR/success.log"
FAILURE_FILE="$TEMP_DIR/failure.log"
touch "$SUCCESS_FILE" "$FAILURE_FILE"

# Function to process a single media folder
process_media_folder() {
    local media_folder="$1"
    local job_id="$2"

    echo "🔄 [Job $job_id] Processing $media_folder..."

    # Check if media.yaml exists
    if [[ ! -f "media/$media_folder/media.yaml" ]]; then
        echo "❌ [Job $job_id] Skipping $media_folder - no media.yaml found"
        echo "$media_folder - no media.yaml" >> "$FAILURE_FILE"
        return 1
    fi

    # Process the folder using the existing script
    if ./scripts/internal/37d-m2-02.sh "$media_folder" 2>/dev/null; then
        echo "✅ [Job $job_id] Successfully processed $media_folder"
        echo "$media_folder" >> "$SUCCESS_FILE"
        return 0
    else
        echo "❌ [Job $job_id] Failed to process $media_folder"
        echo "$media_folder - style processing failed" >> "$FAILURE_FILE"
        return 1
    fi
}

export -f process_media_folder
export TEMP_DIR SUCCESS_FILE FAILURE_FILE

# Process folders in parallel batches
echo "🚀 Starting parallel processing..."
echo ""

# Use xargs to limit parallel jobs
printf "%s\n" "${MEDIA_FOLDERS[@]}" | \
    nl -nln | \
    xargs -n1 -P"$PARALLEL_JOBS" -I{} bash -c 'process_media_folder $(echo "{}" | cut -f2) $(echo "{}" | cut -f1)'

# Calculate results
SUCCESS_COUNT=$(wc -l < "$SUCCESS_FILE")
FAILURE_COUNT=$(wc -l < "$FAILURE_FILE")

echo ""
echo "📈 PROCESSING COMPLETE!"
echo "=================================="
echo "✅ Successfully processed: $SUCCESS_COUNT folders"
echo "❌ Failed: $FAILURE_COUNT folders"
echo "📊 Total processed: $((SUCCESS_COUNT + FAILURE_COUNT))/$TOTAL_FOLDERS folders"

if [[ $FAILURE_COUNT -gt 0 ]]; then
    echo ""
    echo "❌ Failed folders:"
    cat "$FAILURE_FILE"
fi

echo ""
echo "💾 Processing logs saved in: $TEMP_DIR"
echo "   - Success log: $SUCCESS_FILE"
echo "   - Failure log: $FAILURE_FILE"

# Cleanup function (commented out to preserve logs)
# rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Batch style processing completed!"