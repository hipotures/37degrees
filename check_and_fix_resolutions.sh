#!/bin/bash

# Script to check PNG image resolutions and fix them by swapping with correct variants
# Expected resolution: 1024x1536

EXPECTED_RESOLUTION="1024x1536"
REPORT_FILE="image_resolution_report.txt"
INCORRECT_FILES=()
FIXED_FILES=()
UNFIXABLE_FILES=()

echo "=== IMAGE RESOLUTION CHECK & FIX REPORT ===" > "$REPORT_FILE"
echo "Expected resolution: $EXPECTED_RESOLUTION" >> "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Checking and fixing image resolutions in books directories..."

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

# Find all PNG files in books/*/images/ directories
while IFS= read -r -d '' png_file; do
    if [[ -f "$png_file" ]]; then
        # Skip files that are variants (have suffix after scene number)
        # Pattern: *_scene_XXXX_Y.png (where Y is variant number)
        if [[ $(basename "$png_file") =~ _scene_[0-9]+_[0-9]+\.png$ ]]; then
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
            
            # Check variants _1, _2, _3, etc.
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
                else
                    # No more variants to check
                    break
                fi
            done
            
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
    echo "🎉 All issues resolved automatically!"
    echo "📄 Report saved to: $REPORT_FILE"
    exit 0
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

echo ""
echo "📄 Report available at: $REPORT_FILE"