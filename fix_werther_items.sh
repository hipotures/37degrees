#!/bin/bash

# Skrypt do naprawy nazw głównych itemów w TODOIT 0032_sorrows_of_young_werther
# Na podstawie właściwości scene_style_pathfile w subitemach

LIST_KEY="0032_sorrows_of_young_werther"

echo "🔄 KROK 1: Przemianowanie na tymczasowe nazwy"

todoit item rename --list "$LIST_KEY" --item "scene_0025" --new-key "tmp_scene_0001" --force
todoit item rename --list "$LIST_KEY" --item "scene_0002" --new-key "tmp_scene_0002" --force
todoit item rename --list "$LIST_KEY" --item "scene_0003" --new-key "tmp_scene_0003" --force
todoit item rename --list "$LIST_KEY" --item "scene_0004" --new-key "tmp_scene_0004" --force
todoit item rename --list "$LIST_KEY" --item "scene_0005" --new-key "tmp_scene_0005" --force
todoit item rename --list "$LIST_KEY" --item "scene_0006" --new-key "tmp_scene_0006" --force
todoit item rename --list "$LIST_KEY" --item "scene_0007" --new-key "tmp_scene_0007" --force
todoit item rename --list "$LIST_KEY" --item "scene_0008" --new-key "tmp_scene_0008" --force
todoit item rename --list "$LIST_KEY" --item "scene_0009" --new-key "tmp_scene_0009" --force
todoit item rename --list "$LIST_KEY" --item "scene_0010" --new-key "tmp_scene_0010" --force
todoit item rename --list "$LIST_KEY" --item "scene_0011" --new-key "tmp_scene_0011" --force
todoit item rename --list "$LIST_KEY" --item "scene_0012" --new-key "tmp_scene_0012" --force
todoit item rename --list "$LIST_KEY" --item "scene_0013" --new-key "tmp_scene_0013" --force
todoit item rename --list "$LIST_KEY" --item "scene_0014" --new-key "tmp_scene_0014" --force
todoit item rename --list "$LIST_KEY" --item "scene_0015" --new-key "tmp_scene_0015" --force
todoit item rename --list "$LIST_KEY" --item "scene_0016" --new-key "tmp_scene_0016" --force
todoit item rename --list "$LIST_KEY" --item "scene_0017" --new-key "tmp_scene_0017" --force
todoit item rename --list "$LIST_KEY" --item "scene_0018" --new-key "tmp_scene_0018" --force
todoit item rename --list "$LIST_KEY" --item "scene_0019" --new-key "tmp_scene_0019" --force
todoit item rename --list "$LIST_KEY" --item "scene_0020" --new-key "tmp_scene_0020" --force
todoit item rename --list "$LIST_KEY" --item "scene_0021" --new-key "tmp_scene_0021" --force
todoit item rename --list "$LIST_KEY" --item "scene_0022" --new-key "tmp_scene_0022" --force
todoit item rename --list "$LIST_KEY" --item "scene_0023" --new-key "tmp_scene_0023" --force
todoit item rename --list "$LIST_KEY" --item "scene_0024" --new-key "tmp_scene_0024" --force
todoit item rename --list "$LIST_KEY" --item "scene_0025_duplicate" --new-key "tmp_scene_0025" --force

echo "🔄 KROK 2: Przemianowanie na finalne nazwy"

todoit item rename --list "$LIST_KEY" --item "tmp_scene_0001" --new-key "scene_0001" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0002" --new-key "scene_0002" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0003" --new-key "scene_0003" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0004" --new-key "scene_0004" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0005" --new-key "scene_0005" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0006" --new-key "scene_0006" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0007" --new-key "scene_0007" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0008" --new-key "scene_0008" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0009" --new-key "scene_0009" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0010" --new-key "scene_0010" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0011" --new-key "scene_0011" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0012" --new-key "scene_0012" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0013" --new-key "scene_0013" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0014" --new-key "scene_0014" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0015" --new-key "scene_0015" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0016" --new-key "scene_0016" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0017" --new-key "scene_0017" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0018" --new-key "scene_0018" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0019" --new-key "scene_0019" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0020" --new-key "scene_0020" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0021" --new-key "scene_0021" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0022" --new-key "scene_0022" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0023" --new-key "scene_0023" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0024" --new-key "scene_0024" --force
todoit item rename --list "$LIST_KEY" --item "tmp_scene_0025" --new-key "scene_0025" --force

echo "✅ Zakończono przemianowanie itemów"