#!/bin/bash

# ---
# Skrypt do walidacji plików PNG w katalogach książek
# 
# Sprawdza:
# 1. Liczbę plików PNG (powinna być 25)
# 2. Nazewnictwo plików [BOOK_FOLDER]_scene_NNNN.png
# 3. Duplikaty MD5 między wszystkimi książkami
# 4. Rozmiar plików (odchylenie max 50% od średniej dla danej książki)
#
# Użycie:
#   ./validate-images.sh           - sprawdza wszystkie fazy
#   ./validate-images.sh count     - sprawdza tylko liczbę plików
#   ./validate-images.sh naming    - sprawdza tylko nazewnictwo
#   ./validate-images.sh duplicates - sprawdza tylko duplikaty MD5
#   ./validate-images.sh size      - sprawdza tylko rozmiary plików
# ---

# Katalog główny z książkami
BOOKS_DIR="/home/xai/DEV/37degrees/books"

# Kolory dla outputu
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funkcja do wyświetlania nagłówka fazy
phase_header() {
    echo -e "${BLUE}=================================================${NC}"
    echo -e "${BLUE}FAZA: $1${NC}"
    echo -e "${BLUE}=================================================${NC}"
}

# FAZA 1: Sprawdzanie liczby plików PNG
check_count() {
    phase_header "Sprawdzanie liczby plików PNG"
    
    local errors=0
    
    for book_dir in "$BOOKS_DIR"/*/; do
        if [ -d "$book_dir" ]; then
            book_name=$(basename "$book_dir")
            images_dir="$book_dir/images"
            
            if [ -d "$images_dir" ]; then
                # Liczba plików PNG (bez podkatalogów)
                png_count=$(find "$images_dir" -maxdepth 1 -name "*.png" -type f | wc -l)
                
                if [ "$png_count" -ne 25 ]; then
                    echo -e "${RED}❌ $book_name: $png_count plików (oczekiwano 25)${NC}"
                    ((errors++))
                else
                    echo -e "${GREEN}✅ $book_name: $png_count plików${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️ $book_name: brak katalogu images${NC}"
            fi
        fi
    done
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ FAZA 1: Wszystkie książki mają poprawną liczbę plików (25)${NC}"
    else
        echo -e "${RED}❌ FAZA 1: $errors książek ma niepoprawną liczbę plików${NC}"
    fi
    echo ""
    
    return $errors
}

# FAZA 2: Sprawdzanie nazewnictwa plików
check_naming() {
    phase_header "Sprawdzanie nazewnictwa plików"
    
    local errors=0
    
    for book_dir in "$BOOKS_DIR"/*/; do
        if [ -d "$book_dir" ]; then
            book_name=$(basename "$book_dir")
            images_dir="$book_dir/images"
            
            if [ -d "$images_dir" ]; then
                echo "📂 Sprawdzam $book_name:"
                
                # Sprawdź wszystkie pliki PNG
                find "$images_dir" -maxdepth 1 -name "*.png" -type f | while read -r png_file; do
                    filename=$(basename "$png_file")
                    
                    # Oczekiwany wzorzec: [BOOK_FOLDER]_scene_NNNN.png
                    expected_pattern="^${book_name}_scene_[0-9]{4}\.png$"
                    
                    if ! echo "$filename" | grep -qE "$expected_pattern"; then
                        echo -e "  ${RED}❌ Niepoprawna nazwa: $filename${NC}"
                        ((errors++))
                    fi
                done
                
                # Sprawdź czy są wszystkie sceny od 0001 do 0025
                for i in $(seq -f "%04g" 1 25); do
                    expected_file="${book_name}_scene_${i}.png"
                    if [ ! -f "$images_dir/$expected_file" ]; then
                        echo -e "  ${RED}❌ Brakuje: $expected_file${NC}"
                        ((errors++))
                    fi
                done
                
                if [ $errors -eq 0 ]; then
                    echo -e "  ${GREEN}✅ Wszystkie nazwy poprawne${NC}"
                fi
            fi
        fi
    done
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ FAZA 2: Wszystkie pliki mają poprawne nazwy${NC}"
    else
        echo -e "${RED}❌ FAZA 2: $errors błędów w nazewnictwie${NC}"
    fi
    echo ""
    
    return $errors
}

# FAZA 3: Sprawdzanie duplikatów MD5
check_duplicates() {
    phase_header "Sprawdzanie duplikatów MD5"
    
    local temp_file="/tmp/md5_check_$$"
    local errors=0
    
    echo "🔍 Obliczam MD5 dla wszystkich plików PNG..."
    
    # Zbierz MD5 wszystkich plików PNG
    for book_dir in "$BOOKS_DIR"/*/; do
        if [ -d "$book_dir" ]; then
            book_name=$(basename "$book_dir")
            images_dir="$book_dir/images"
            
            if [ -d "$images_dir" ]; then
                find "$images_dir" -maxdepth 1 -name "*.png" -type f -exec md5sum {} \; | \
                sed "s|$images_dir/||" | \
                awk -v book="$book_name" '{print $1 " " book "/" $2}'
            fi
        fi
    done > "$temp_file"
    
    echo "📊 Szukam duplikatów..."
    
    # Znajdź duplikaty MD5
    duplicates=$(awk '{print $1}' "$temp_file" | sort | uniq -d)
    
    if [ -n "$duplicates" ]; then
        echo -e "${RED}❌ Znaleziono duplikaty MD5:${NC}"
        
        while read -r md5_hash; do
            if [ -n "$md5_hash" ]; then
                echo -e "${YELLOW}🔍 MD5: $md5_hash${NC}"
                grep "^$md5_hash " "$temp_file" | while read -r line; do
                    file_path=$(echo "$line" | cut -d' ' -f2-)
                    echo -e "  ${RED}📁 $file_path${NC}"
                done
                ((errors++))
                echo ""
            fi
        done <<< "$duplicates"
    else
        echo -e "${GREEN}✅ Brak duplikatów MD5${NC}"
    fi
    
    # Cleanup
    rm -f "$temp_file"
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ FAZA 3: Brak duplikatów${NC}"
    else
        echo -e "${RED}❌ FAZA 3: Znaleziono $errors grup duplikatów${NC}"
    fi
    echo ""
    
    return $errors
}

# FAZA 4: Sprawdzanie rozmiarów plików
check_size() {
    phase_header "Sprawdzanie rozmiarów plików"
    
    local errors=0
    
    for book_dir in "$BOOKS_DIR"/*/; do
        if [ -d "$book_dir" ]; then
            book_name=$(basename "$book_dir")
            images_dir="$book_dir/images"
            
            if [ -d "$images_dir" ]; then
                echo "📂 Sprawdzam rozmiary dla $book_name:"
                
                # Zbierz rozmiary wszystkich plików PNG
                local sizes=()
                while IFS= read -r -d '' file; do
                    size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
                    sizes+=("$size")
                done < <(find "$images_dir" -maxdepth 1 -name "*.png" -type f -print0)
                
                if [ ${#sizes[@]} -eq 0 ]; then
                    echo -e "  ${YELLOW}⚠️ Brak plików PNG${NC}"
                    continue
                fi
                
                # Oblicz średnią
                local total=0
                for size in "${sizes[@]}"; do
                    ((total += size))
                done
                local average=$((total / ${#sizes[@]}))
                
                # Oblicz progi (±50%)
                local min_size=$((average * 50 / 100))
                local max_size=$((average * 150 / 100))
                
                echo -e "  📏 Średni rozmiar: $(numfmt --to=iec $average)"
                echo -e "  📐 Zakres dopuszczalny: $(numfmt --to=iec $min_size) - $(numfmt --to=iec $max_size)"
                
                # Sprawdź każdy plik
                local book_errors=0
                find "$images_dir" -maxdepth 1 -name "*.png" -type f | while read -r png_file; do
                    filename=$(basename "$png_file")
                    size=$(stat -f%z "$png_file" 2>/dev/null || stat -c%s "$png_file" 2>/dev/null)
                    
                    if [ "$size" -lt "$min_size" ] || [ "$size" -gt "$max_size" ]; then
                        echo -e "  ${RED}❌ $filename: $(numfmt --to=iec $size) (odchylenie > 50%)${NC}"
                        ((book_errors++))
                    fi
                done
                
                if [ $book_errors -eq 0 ]; then
                    echo -e "  ${GREEN}✅ Wszystkie rozmiary w normie${NC}"
                else
                    ((errors += book_errors))
                fi
                echo ""
            fi
        fi
    done
    
    echo ""
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ FAZA 4: Wszystkie rozmiary plików w normie${NC}"
    else
        echo -e "${RED}❌ FAZA 4: $errors plików ma niepoprawny rozmiar${NC}"
    fi
    echo ""
    
    return $errors
}

# Funkcja główna
main() {
    local phase="$1"
    local total_errors=0
    
    echo -e "${BLUE}🔍 WALIDACJA PLIKÓW PNG - $(date)${NC}"
    echo ""
    
    case "$phase" in
        "count")
            check_count
            total_errors=$?
            ;;
        "naming")
            check_naming
            total_errors=$?
            ;;
        "duplicates")
            check_duplicates
            total_errors=$?
            ;;
        "size")
            check_size
            total_errors=$?
            ;;
        *)
            echo -e "${BLUE}Uruchamiam wszystkie fazy walidacji...${NC}"
            echo ""
            
            check_count
            ((total_errors += $?))
            
            check_naming
            ((total_errors += $?))
            
            check_duplicates
            ((total_errors += $?))
            
            check_size
            ((total_errors += $?))
            ;;
    esac
    
    echo -e "${BLUE}=================================================${NC}"
    if [ $total_errors -eq 0 ]; then
        echo -e "${GREEN}🎉 WALIDACJA ZAKOŃCZONA POMYŚLNIE${NC}"
    else
        echo -e "${RED}❌ WALIDACJA ZAKOŃCZONA Z BŁĘDAMI: $total_errors${NC}"
    fi
    echo -e "${BLUE}=================================================${NC}"
    
    return $total_errors
}

# Sprawdź czy skrypt jest wywołany bezpośrednio
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi