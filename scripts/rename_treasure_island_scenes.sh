#!/bin/bash

# Script to rename Treasure Island scene images
# Execute this script from the project root directory

cd "books/0036_treasure_island/generated"

# Main sequence of scenes generated at 10:32-10:33 (chronological order)
mv "ChatGPT Image 27 lip 2025, 10_32_10.png" "0036_scene_01.png"
mv "ChatGPT Image 27 lip 2025, 10_32_14.png" "0036_scene_02.png"
mv "ChatGPT Image 27 lip 2025, 10_32_17.png" "0036_scene_03.png"
mv "ChatGPT Image 27 lip 2025, 10_32_21.png" "0036_scene_04.png"
mv "ChatGPT Image 27 lip 2025, 10_32_23.png" "0036_scene_05.png"
mv "ChatGPT Image 27 lip 2025, 10_32_27.png" "0036_scene_06.png"
mv "ChatGPT Image 27 lip 2025, 10_32_30.png" "0036_scene_08.png"  # Scene 07 is handled separately below
mv "ChatGPT Image 27 lip 2025, 10_32_34.png" "0036_scene_09.png"
mv "ChatGPT Image 27 lip 2025, 10_32_37.png" "0036_scene_11.png"  # Scene 10 is handled separately below
mv "ChatGPT Image 27 lip 2025, 10_32_41.png" "0036_scene_12.png"
mv "ChatGPT Image 27 lip 2025, 10_32_44.png" "0036_scene_13.png"
mv "ChatGPT Image 27 lip 2025, 10_32_47.png" "0036_scene_14.png"
mv "ChatGPT Image 27 lip 2025, 10_32_50.png" "0036_scene_16.png"  # Scene 15 is handled separately below
mv "ChatGPT Image 27 lip 2025, 10_32_57.png" "0036_scene_17.png"
mv "ChatGPT Image 27 lip 2025, 10_33_00.png" "0036_scene_18.png"
mv "ChatGPT Image 27 lip 2025, 10_33_02.png" "0036_scene_19.png"
mv "ChatGPT Image 27 lip 2025, 10_33_05.png" "0036_scene_20.png"
mv "ChatGPT Image 27 lip 2025, 10_33_08.png" "0036_scene_21.png"
mv "ChatGPT Image 27 lip 2025, 10_33_11.png" "0036_scene_22.png"
mv "ChatGPT Image 27 lip 2025, 10_33_14.png" "0036_scene_23.png"
mv "ChatGPT Image 27 lip 2025, 10_33_17.png" "0036_scene_24.png"
mv "ChatGPT Image 27 lip 2025, 10_33_19.png" "0036_scene_25.png"

# Specific scenes with explicit scene numbers (generated later)
mv "ChatGPT Image 27 lip 2025, 12_01_22__scene07_gpt4o.png" "0036_scene_07.png"
mv "ChatGPT Image 27 lip 2025, 11_47_27__scene10.png" "0036_scene_10.png"
mv "ChatGPT Image 27 lip 2025, 12_09_41_scena15.png" "0036_scene_15.png"

echo "Scene files renamed successfully!"
echo "Total scenes: 25"
echo "Scenes 1-25 are now properly numbered as 0036_scene_XX.png"