#!/bin/bash

# Script to check PNG image resolutions and validate image completeness
# Phase 1: Check and fix image resolutions by swapping with correct variants
# Phase 2: Check image completeness (25 files per book with correct naming)
# Expected resolution: 1024x1536
#
# Usage:
#   ./check_and_fix_resolutions.sh          # Run both phases
#   ./check_and_fix_resolutions.sh --phase 1   # Run only Phase 1
#   ./check_and_fix_resolutions.sh --phase 2   # Run only Phase 2

# Parse command line arguments
PHASE_TO_RUN="all"
while [[ $# -gt 0 ]]; do
    case $1 in
        --phase)
            PHASE_TO_RUN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--phase 1|2]"
            exit 1
            ;;
    esac
done

# Validate phase parameter
if [[ "$PHASE_TO_RUN" != "all" && "$PHASE_TO_RUN" != "1" && "$PHASE_TO_RUN" != "2" ]]; then
    echo "Error: --phase must be 1, 2, or omitted for all phases"
    echo "Usage: $0 [--phase 1|2]"
    exit 1
fi

EXPECTED_RESOLUTION="1024x1536"
REPORT_FILE="image_resolution_report.txt"
INCORRECT_FILES=()
FIXED_FILES=()
UNFIXABLE_FILES=()
INCOMPLETE_BOOKS=()

echo "=== IMAGE RESOLUTION CHECK & COMPLETENESS REPORT ===" > "$REPORT_FILE"
echo "Expected resolution: $EXPECTED_RESOLUTION" >> "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "Phases to run: $PHASE_TO_RUN" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

if [[ "$PHASE_TO_RUN" == "all" || "$PHASE_TO_RUN" == "1" ]]; then
    echo "🔍 PHASE 1: Checking and fixing image resolutions in books directories..."
else
    echo "⏩ Skipping Phase 1 (only running Phase $PHASE_TO_RUN)"
fi

# Function to safely swap two files (triple rename)
safe_swap_files() {
    local file1="$1"
    local file2="$2"
    local temp_name="${file1}.temp_swap_$(date +%s)"
    
    echo "  🔄 Swapping files:"
    echo "    Original: $(basename "$file1")"
    echo "    Replacement: $(basename "$file2")"
    
    # Triple rename to avoid conflicts
    mv "$file1" "$temp_name"
    mv "$file2" "$file1"
    mv "$temp_name" "$file2"
    
    echo "  ✅ Files swapped successfully"
}

# Function to check resolution of a file
get_resolution() {
    local file="$1"
    if [[ ! -s "$file" ]]; then
        echo ""
        return
    fi
    
    local identify_output=$(identify "$file" 2>/dev/null)
    if [[ $? -ne 0 || -z "$identify_output" ]]; then
        echo ""
        return
    fi
    
    echo "$identify_output" | grep -o '[0-9]\+x[0-9]\+' | head -1
}

# Phase 1: Resolution check and fix
if [[ "$PHASE_TO_RUN" == "all" || "$PHASE_TO_RUN" == "1" ]]; then

# Find all PNG files in books/*/images/ directories
while IFS= read -r -d '' png_file; do
    if [[ -f "$png_file" ]]; then
        # Skip files that are variants (have suffix after scene number)
        # Pattern: *_scene_XXXX_Y.png (where Y is variant number or hash)
        if [[ $(basename "$png_file") =~ _scene_[0-9]+_[0-9a-f]+\.png$ ]]; then
            continue
        fi
        
        resolution=$(get_resolution "$png_file")
        
        if [[ -z "$resolution" ]]; then
            echo "✗ UNREADABLE: $png_file - Cannot read file" | tee -a "$REPORT_FILE"
            UNFIXABLE_FILES+=("$png_file")
        elif [[ "$resolution" != "$EXPECTED_RESOLUTION" ]]; then
            echo "✗ INCORRECT: $png_file - Resolution: $resolution" | tee -a "$REPORT_FILE"
            
            # Try to find a variant with correct resolution
            base_name="${png_file%.png}"
            found_replacement=false
            
            echo "  🔍 Looking for variants with correct resolution..."
            
            # Check variants: numeric (_1, _2, _3, etc.) and hash-based
            # First check numeric variants
            for i in {1..10}; do
                variant_file="${base_name}_${i}.png"
                if [[ -f "$variant_file" ]]; then
                    variant_resolution=$(get_resolution "$variant_file")
                    echo "    Checking $(basename "$variant_file"): $variant_resolution"
                    
                    if [[ "$variant_resolution" == "$EXPECTED_RESOLUTION" ]]; then
                        echo "  ✅ Found correct variant: $(basename "$variant_file")"
                        safe_swap_files "$png_file" "$variant_file"
                        FIXED_FILES+=("$png_file")
                        found_replacement=true
                        echo "  🎯 FIXED: $png_file (swapped with variant _${i})" | tee -a "$REPORT_FILE"
                        break
                    fi
                fi
            done
            
            # If no numeric variant found, check hash-based variants
            if [[ "$found_replacement" == false ]]; then
                # Find all files matching base_name_HASH.png pattern
                while IFS= read -r -d '' hash_variant; do
                    if [[ -f "$hash_variant" ]]; then
                        variant_resolution=$(get_resolution "$hash_variant")
                        echo "    Checking $(basename "$hash_variant"): $variant_resolution"
                        
                        if [[ "$variant_resolution" == "$EXPECTED_RESOLUTION" ]]; then
                            echo "  ✅ Found correct hash variant: $(basename "$hash_variant")"
                            safe_swap_files "$png_file" "$hash_variant"
                            FIXED_FILES+=("$png_file")
                            found_replacement=true
                            hash_suffix=$(basename "$hash_variant" | sed "s/$(basename "$base_name")_//; s/\.png$//")
                            echo "  🎯 FIXED: $png_file (swapped with hash variant _${hash_suffix})" | tee -a "$REPORT_FILE"
                            break
                        fi
                    fi
                done < <(find "$(dirname "$png_file")" -name "$(basename "$base_name")_[0-9a-f]*.png" -print0 2>/dev/null)
            fi
            
            if [[ "$found_replacement" == false ]]; then
                echo "  ❌ No suitable replacement found"
                INCORRECT_FILES+=("$png_file")
                echo "  🔧 NEEDS REGENERATION: $png_file" | tee -a "$REPORT_FILE"
            fi
            echo ""
        fi
    fi
done < <(find /home/xai/DEV/37degrees/books -path "*/images/*.png" -name "*scene_*.png" -not -path "*/alt/*" -print0)

echo "" >> "$REPORT_FILE"
echo "=== SUMMARY ===" >> "$REPORT_FILE"
echo "Files automatically fixed: ${#FIXED_FILES[@]}" >> "$REPORT_FILE"
echo "Files still need regeneration: ${#INCORRECT_FILES[@]}" >> "$REPORT_FILE"
echo "Unreadable files: ${#UNFIXABLE_FILES[@]}" >> "$REPORT_FILE"

echo ""
echo "📊 SUMMARY:"
echo "✅ Files automatically fixed: ${#FIXED_FILES[@]}"
echo "🔧 Files still need regeneration: ${#INCORRECT_FILES[@]}"
echo "❌ Unreadable files: ${#UNFIXABLE_FILES[@]}"

if [[ ${#FIXED_FILES[@]} -gt 0 ]]; then
    echo "" >> "$REPORT_FILE"
    echo "=== AUTOMATICALLY FIXED FILES ===" >> "$REPORT_FILE"
    for file in "${FIXED_FILES[@]}"; do
        echo "$file" >> "$REPORT_FILE"
    done
fi

if [[ ${#INCORRECT_FILES[@]} -eq 0 && ${#UNFIXABLE_FILES[@]} -eq 0 ]]; then
    echo ""
    echo "🎉 All resolution issues resolved automatically!"
    echo "📄 Phase 1 report saved to: $REPORT_FILE"
    # Don't exit here - continue to Phase 1 completion
fi

if [[ ${#INCORRECT_FILES[@]} -gt 0 ]]; then
    echo "" >> "$REPORT_FILE"
    echo "=== FILES THAT NEED REGENERATION ===" >> "$REPORT_FILE"
    for file in "${INCORRECT_FILES[@]}"; do
        echo "$file" >> "$REPORT_FILE"
    done

    echo ""
    echo "🔧 Found ${#INCORRECT_FILES[@]} files that still need regeneration."
    echo "📄 Full report saved to: $REPORT_FILE"
    echo ""

    # Ask user if they want to regenerate remaining images
    echo "Do you want to regenerate the remaining ${#INCORRECT_FILES[@]} images?"
    echo "This will set image_gen status to 'pending' in TODOIT for affected scenes."
    echo -n "Continue? (y/N): "
    read -r answer

    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
        echo ""
        echo "🔄 Setting image_gen status to 'pending' for remaining scenes..."
        
        for file in "${INCORRECT_FILES[@]}"; do
            # Extract book folder and scene from filename
            filename=$(basename "$file")
            book_folder=$(echo "$filename" | sed 's/_scene_.*\.png$//')
            scene=$(echo "$filename" | grep -o 'scene_[0-9]\{4\}')
            
            if [[ -n "$book_folder" && -n "$scene" ]]; then
                echo "📝 Processing: $book_folder -> $scene"
                echo "   File: $file"
                
                # Use TODOIT CLI to set both image_gen and image_dwn status to pending
                echo "   Setting image_gen to pending..."
                todoit item status --list "$book_folder" --item "$scene" --subitem "image_gen" --status pending 2>/dev/null
                gen_result=$?
                
                echo "   Setting image_dwn to pending..."
                todoit item status --list "$book_folder" --item "$scene" --subitem "image_dwn" --status pending 2>/dev/null
                dwn_result=$?
                
                if [[ $gen_result -eq 0 && $dwn_result -eq 0 ]]; then
                    echo "   ✅ Both image_gen and image_dwn updated successfully"
                elif [[ $gen_result -eq 0 ]]; then
                    echo "   ⚠️  image_gen updated, but image_dwn failed"
                elif [[ $dwn_result -eq 0 ]]; then
                    echo "   ⚠️  image_dwn updated, but image_gen failed"
                else
                    echo "   ❌ Both updates failed via TODOIT CLI"
                fi
            else
                echo "   ❌ Could not extract book_folder or scene from: $filename"
            fi
            echo ""
        done
        
        echo "✅ Processing complete!"
    else
        echo "❌ Regeneration cancelled."
    fi
fi

# End of Phase 1 - Final Summary
echo ""
echo "📊 PHASE 1 FINAL SUMMARY:"
echo "✅ Files automatically fixed: ${#FIXED_FILES[@]}"
echo "🔧 Files still needing regeneration: ${#INCORRECT_FILES[@]}"
echo "❌ Unreadable files: ${#UNFIXABLE_FILES[@]}"

if [[ ${#FIXED_FILES[@]} -gt 0 || ${#INCORRECT_FILES[@]} -gt 0 || ${#UNFIXABLE_FILES[@]} -gt 0 ]]; then
    echo ""
    echo "📋 DETAILED BREAKDOWN:"
    
    if [[ ${#FIXED_FILES[@]} -gt 0 ]]; then
        echo "   ✅ FIXED (${#FIXED_FILES[@]} files): Resolution issues resolved by swapping with correct variants"
    fi
    
    if [[ ${#INCORRECT_FILES[@]} -gt 0 ]]; then
        echo "   🔧 NEED REGENERATION (${#INCORRECT_FILES[@]} files): No suitable replacement variants found"
    fi
    
    if [[ ${#UNFIXABLE_FILES[@]} -gt 0 ]]; then
        echo "   ❌ UNREADABLE (${#UNFIXABLE_FILES[@]} files): Cannot read image metadata"
    fi
else
    echo ""
    echo "🎉 All images have correct resolution (${EXPECTED_RESOLUTION})!"
fi

echo ""
echo "✅ PHASE 1 COMPLETE!"
echo "📄 Phase 1 report available at: $REPORT_FILE"

fi # End of Phase 1 condition

# Phase 1 to Phase 2 transition (only when running all phases)
if [[ "$PHASE_TO_RUN" == "all" ]]; then
    echo ""
    echo "Do you want to proceed to PHASE 2: Image completeness check?"
    echo "This will check that each book has exactly 25 images with correct naming (NNNN_book_scene_NNNN.png)."
    echo -n "Continue to Phase 2? (y/N): "
    read -r answer_phase2

    if [[ "$answer_phase2" != "y" && "$answer_phase2" != "Y" ]]; then
        echo "❌ Phase 2 cancelled. Script complete."
        echo "📄 Report available at: $REPORT_FILE"
        exit 0
    fi
fi

# Phase 2: Image completeness check
if [[ "$PHASE_TO_RUN" == "all" || "$PHASE_TO_RUN" == "2" ]]; then

echo ""
echo "🔍 PHASE 2: Checking image completeness..."
echo "" >> "$REPORT_FILE"
echo "=== PHASE 2: IMAGE COMPLETENESS CHECK ===" >> "$REPORT_FILE"

# Function to check image completeness for a book
check_book_completeness() {
    local book_dir="$1"
    local book_name=$(basename "$book_dir")
    local images_dir="$book_dir/images"
    
    # Skip if images directory doesn't exist or is empty
    if [[ ! -d "$images_dir" ]] || [[ -z "$(ls -A "$images_dir" 2>/dev/null)" ]]; then
        return 0  # Not an error - book hasn't been generated yet
    fi
    
    # Count main scene files (not variants)
    local main_files=()
    local scene_numbers=()
    
    while IFS= read -r -d '' png_file; do
        local filename=$(basename "$png_file")
        # Check if it matches the exact pattern: NNNN_book_scene_NNNN.png
        if [[ "$filename" =~ ^[0-9][0-9][0-9][0-9]_.*_scene_[0-9][0-9][0-9][0-9]\.png$ ]] && [[ ! "$filename" =~ _scene_[0-9][0-9][0-9][0-9]_[0-9a-f]+\.png$ ]]; then
            main_files+=("$filename")
            # Extract scene number
            local scene_num=$(echo "$filename" | grep -o 'scene_[0-9]\{4\}' | grep -o '[0-9]\{4\}')
            scene_numbers+=("$scene_num")
        fi
    done < <(find "$images_dir" -maxdepth 1 -name "*.png" -print0)
    
    local file_count=${#main_files[@]}
    
    if [[ $file_count -eq 25 ]]; then
        # Check if scene numbers are consecutive from 0001 to 0025
        local sorted_scenes=($(printf '%s\n' "${scene_numbers[@]}" | sort))
        local expected_scenes=()
        for i in {1..25}; do
            expected_scenes+=($(printf "%04d" $i))
        done
        
        local scenes_match=true
        for i in {0..24}; do
            if [[ "${sorted_scenes[$i]}" != "${expected_scenes[$i]}" ]]; then
                scenes_match=false
                break
            fi
        done
        
        if [[ "$scenes_match" == false ]]; then
            echo "$book_name - $file_count (incorrect scene numbering)" | tee -a "$REPORT_FILE"
            INCOMPLETE_BOOKS+=("$book_name")
        fi
        # If everything is correct, don't print anything (as requested)
    else
        echo "$book_name - $file_count" | tee -a "$REPORT_FILE"
        INCOMPLETE_BOOKS+=("$book_name")
    fi
}

# Check all book directories
for book_dir in /home/xai/DEV/37degrees/books/*/; do
    if [[ -d "$book_dir" ]]; then
        check_book_completeness "$book_dir"
    fi
done

echo "" >> "$REPORT_FILE"
echo "=== PHASE 2 SUMMARY ===" >> "$REPORT_FILE"
echo "Books with incomplete/incorrect images: ${#INCOMPLETE_BOOKS[@]}" >> "$REPORT_FILE"

echo ""
echo "📊 PHASE 2 SUMMARY:"
echo "📚 Books with incomplete/incorrect images: ${#INCOMPLETE_BOOKS[@]}"

if [[ ${#INCOMPLETE_BOOKS[@]} -eq 0 ]]; then
    echo ""
    echo "🎉 All books have correct image completeness!"
    echo "📄 Phase 2 report saved to: $REPORT_FILE"
    # Don't exit here - continue to end of Phase 2
fi

if [[ ${#INCOMPLETE_BOOKS[@]} -gt 0 ]]; then
    echo "" >> "$REPORT_FILE"
    echo "=== BOOKS WITH INCOMPLETE/INCORRECT IMAGES ===" >> "$REPORT_FILE"
    for book in "${INCOMPLETE_BOOKS[@]}"; do
        echo "$book" >> "$REPORT_FILE"
    done

    echo ""
    echo "📚 Found ${#INCOMPLETE_BOOKS[@]} books with incomplete/incorrect images."
    echo ""

    # First, prepare a summary of what will be set to pending
    echo ""
    echo "📋 SUMMARY: Missing scenes that will be set to 'pending' status:"
    echo "" >> "$REPORT_FILE"
    echo "=== MISSING SCENES TO BE SET TO PENDING ===" >> "$REPORT_FILE"
    
    # Collect missing scenes info first
    declare -A missing_scenes_summary
    books_with_missing=()
    
    for book_name in "${INCOMPLETE_BOOKS[@]}"; do
        book_dir="/home/xai/DEV/37degrees/books/$book_name"
        images_dir="$book_dir/images"
        missing_count=0
        missing_list=""
        
        if [[ -d "$images_dir" ]]; then
            # Find existing scene numbers
            existing_scenes=()
            while IFS= read -r -d '' png_file; do
                filename=$(basename "$png_file")
                if [[ "$filename" =~ ^[0-9][0-9][0-9][0-9]_.*_scene_[0-9][0-9][0-9][0-9]\.png$ ]] && [[ ! "$filename" =~ _scene_[0-9][0-9][0-9][0-9]_[0-9a-f]+\.png$ ]]; then
                    scene_num=$(echo "$filename" | grep -o 'scene_[0-9]\{4\}' | grep -o '[0-9]\{4\}')
                    existing_scenes+=("$scene_num")
                fi
            done < <(find "$images_dir" -maxdepth 1 -name "*.png" -print0 2>/dev/null)
            
            # Check if directory is truly empty (no PNG files found)
            total_pngs=$(find "$images_dir" -maxdepth 1 -name "*.png" 2>/dev/null | wc -l)
            if [[ $total_pngs -eq 0 ]]; then
                # Directory exists but is empty
                missing_count=25
                missing_list="0001-0025 (all - empty directory)"
            else
                # Check all scenes from 0001 to 0025
                for i in {1..25}; do
                    scene_num=$(printf "%04d" $i)
                    
                    # Check if this scene exists
                    scene_exists=false
                    for existing in "${existing_scenes[@]}"; do
                        if [[ "$existing" == "$scene_num" ]]; then
                            scene_exists=true
                            break
                        fi
                    done
                    
                    if [[ "$scene_exists" == false ]]; then
                        if [[ $missing_count -eq 0 ]]; then
                            missing_list="$scene_num"
                        else
                            missing_list="$missing_list, $scene_num"
                        fi
                        ((missing_count++))
                    fi
                done
            fi
        else
            # Directory doesn't exist - all 25 scenes missing
            missing_count=25
            missing_list="0001-0025 (all - no directory)"
        fi
        
        if [[ $missing_count -gt 0 ]]; then
            echo "📚 $book_name: $missing_count missing scenes ($missing_list)"
            echo "$book_name: $missing_count missing scenes ($missing_list)" >> "$REPORT_FILE"
            missing_scenes_summary["$book_name"]="$missing_list"
            books_with_missing+=("$book_name")
        fi
    done
    
    # Ask user if they want to set missing images to pending status
    if [[ ${#books_with_missing[@]} -eq 0 ]]; then
        echo ""
        echo "🎉 No missing scenes found! All incomplete books have other issues (numbering, etc.)"
        # Don't exit here - continue to end of Phase 2
    else
        echo ""
        echo "Do you want to set these missing images to 'pending' status in TODOIT?"
        echo "This will set image_gen status to 'pending' for the scenes listed above."
        echo -n "Continue? (y/N): "
        read -r answer_pending

        if [[ "$answer_pending" == "y" || "$answer_pending" == "Y" ]]; then
            echo ""
            echo "🔄 Setting missing images to 'pending' status..."
            
            # Determine processing mode
            echo ""
            echo "Choose processing mode:"
            echo "1. Process all books automatically (recommended)"
            echo "2. Ask for confirmation for each book"
            echo -n "Enter choice (1/2): "
            read -r processing_mode
            
            case $processing_mode in
                1)
                    echo ""
                    echo "📋 Processing all books automatically..."
                    auto_mode=true
                    ;;
                2)
                    echo ""
                    echo "📋 Processing books with individual confirmation..."
                    auto_mode=false
                    ;;
                *)
                    echo "Invalid choice. Using automatic mode."
                    auto_mode=true
                    ;;
            esac
            
            for book_name in "${books_with_missing[@]}"; do
                if [[ "$auto_mode" == false ]]; then
                    echo ""
                    echo "📝 Next book: $book_name"
                    echo "Missing scenes: ${missing_scenes_summary[$book_name]}"
                    echo -n "Process this book? (y/N/a=all remaining): "
                    read -r book_answer
                    
                    case $book_answer in
                        [Yy]*)
                            echo "✅ Processing $book_name..."
                            ;;
                        [Aa]*)
                            echo "✅ Processing $book_name and all remaining books..."
                            auto_mode=true
                            ;;
                        *)
                            echo "⏭️  Skipping $book_name"
                            continue
                            ;;
                    esac
                else
                    echo "📝 Processing book: $book_name"
                fi
                
                # Check which scenes are missing and set them to pending
                book_dir="/home/xai/DEV/37degrees/books/$book_name"
                images_dir="$book_dir/images"
                
                if [[ -d "$images_dir" ]]; then
                    # Find existing scene numbers
                    existing_scenes=()
                    while IFS= read -r -d '' png_file; do
                        filename=$(basename "$png_file")
                        if [[ "$filename" =~ ^[0-9][0-9][0-9][0-9]_.*_scene_[0-9][0-9][0-9][0-9]\.png$ ]] && [[ ! "$filename" =~ _scene_[0-9][0-9][0-9][0-9]_[0-9a-f]+\.png$ ]]; then
                            scene_num=$(echo "$filename" | grep -o 'scene_[0-9]\{4\}' | grep -o '[0-9]\{4\}')
                            existing_scenes+=("$scene_num")
                        fi
                    done < <(find "$images_dir" -maxdepth 1 -name "*.png" -print0 2>/dev/null)
                    
                    # Check all scenes from 0001 to 0025
                    for i in {1..25}; do
                        scene_num=$(printf "%04d" $i)
                        scene_key="scene_$scene_num"
                        
                        # Check if this scene exists
                        scene_exists=false
                        for existing in "${existing_scenes[@]}"; do
                            if [[ "$existing" == "$scene_num" ]]; then
                                scene_exists=true
                                break
                            fi
                        done
                        
                        if [[ "$scene_exists" == false ]]; then
                            echo "   Missing: $scene_key - setting to pending..."
                            
                            # Set both image_gen and image_dwn to pending
                            todoit item status --list "$book_name" --item "$scene_key" --subitem "image_gen" --status pending 2>/dev/null
                            gen_result=$?
                            
                            todoit item status --list "$book_name" --item "$scene_key" --subitem "image_dwn" --status pending 2>/dev/null
                            dwn_result=$?
                            
                            if [[ $gen_result -eq 0 && $dwn_result -eq 0 ]]; then
                                echo "   ✅ $scene_key updated successfully"
                            else
                                echo "   ⚠️  $scene_key update failed"
                            fi
                        fi
                    done
                fi
                echo ""
            done
        
            echo "✅ Phase 2 processing complete!"
        else
            echo "❌ Status updates cancelled."
        fi
    fi # End of books_with_missing check
fi # End of INCOMPLETE_BOOKS check

echo ""
echo "📄 Complete report available at: $REPORT_FILE"

fi # End of Phase 2 condition

# Script completion message
echo ""
if [[ "$PHASE_TO_RUN" == "all" ]]; then
    echo "🎉 All phases completed!"
elif [[ "$PHASE_TO_RUN" == "1" ]]; then
    echo "🎉 Phase 1 completed!"
elif [[ "$PHASE_TO_RUN" == "2" ]]; then
    echo "🎉 Phase 2 completed!"
fi
echo "📄 Final report available at: $REPORT_FILE"