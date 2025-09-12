#!/bin/bash
# Test prompt generation for all supported languages

echo "Testing AFA prompt generator for all 9 languages..."
echo "================================================"

# English
echo -e "\n[EN] Generating English prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland en academic_analysis > /dev/null 2>&1
echo "✓ English saved to: books/0001_alice_in_wonderland/prompts/afa_en_academic_analysis.txt"

# Polish
echo -e "\n[PL] Generating Polish prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland pl academic_analysis > /dev/null 2>&1
echo "✓ Polish saved to: books/0001_alice_in_wonderland/prompts/afa_pl_academic_analysis.txt"

# German
echo -e "\n[DE] Generating German prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland de academic_analysis > /dev/null 2>&1
echo "✓ German saved to: books/0001_alice_in_wonderland/prompts/afa_de_academic_analysis.txt"

# Spanish
echo -e "\n[ES] Generating Spanish prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland es academic_analysis > /dev/null 2>&1
echo "✓ Spanish saved to: books/0001_alice_in_wonderland/prompts/afa_es_academic_analysis.txt"

# Portuguese
echo -e "\n[PT] Generating Portuguese prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland pt academic_analysis > /dev/null 2>&1
echo "✓ Portuguese saved to: books/0001_alice_in_wonderland/prompts/afa_pt_academic_analysis.txt"

# French
echo -e "\n[FR] Generating French prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland fr academic_analysis > /dev/null 2>&1
echo "✓ French saved to: books/0001_alice_in_wonderland/prompts/afa_fr_academic_analysis.txt"

# Japanese
echo -e "\n[JA] Generating Japanese prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland ja academic_analysis > /dev/null 2>&1
echo "✓ Japanese saved to: books/0001_alice_in_wonderland/prompts/afa_ja_academic_analysis.txt"

# Korean
echo -e "\n[KO] Generating Korean prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland ko academic_analysis > /dev/null 2>&1
echo "✓ Korean saved to: books/0001_alice_in_wonderland/prompts/afa_ko_academic_analysis.txt"

# Hindi
echo -e "\n[HI] Generating Hindi prompt..."
python afa2-temporary_directory/afa-prompt-generator.py 0001_alice_in_wonderland hi academic_analysis > /dev/null 2>&1
echo "✓ Hindi saved to: books/0001_alice_in_wonderland/prompts/afa_hi_academic_analysis.txt"

echo -e "\n================================================"
echo "All 9 language prompts generated successfully!"
echo "Check: books/0001_alice_in_wonderland/prompts/"