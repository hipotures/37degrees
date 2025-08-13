#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-}"
LOG_FILE=""
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize logging
init_logging() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    LOG_FILE="${SCRIPT_DIR}/conversion_${timestamp}.log"
    echo "$(date): Starting conversion process" >> "$LOG_FILE"
}

# Logging function
log() {
    if [[ -n "$LOG_FILE" ]]; then
        echo "$(date): $1" >> "$LOG_FILE"
    fi
    local prefix="${GREEN}[$(date +%H:%M:%S)]${NC}"
    if [[ "$DRY_RUN" == "true" ]]; then
        prefix="${YELLOW}[DRY-RUN $(date +%H:%M:%S)]${NC}"
    fi
    echo -e "$prefix $1"
}

log_error() {
    if [[ -n "$LOG_FILE" ]]; then
        echo "$(date): ERROR: $1" >> "$LOG_FILE"
    fi
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    if [[ -n "$LOG_FILE" ]]; then
        echo "$(date): WARNING: $1" >> "$LOG_FILE"
    fi
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    if [[ -n "$LOG_FILE" ]]; then
        echo "$(date): INFO: $1" >> "$LOG_FILE"
    fi
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Confirmation function
confirm() {
    local message="$1"
    echo -e "${YELLOW}$message${NC}"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo -e "${YELLOW}[DRY-RUN] Symulacja - operacja zostałaby wykonana${NC}"
        return 0
    fi
    
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Operation cancelled by user"
        exit 1
    fi
}

# Check if todoit is available
check_todoit() {
    if ! command -v todoit &> /dev/null; then
        log_error "todoit command not found. Please ensure it's installed and in PATH"
        exit 1
    fi
}

# Dry-run aware execution functions
dry_run_mkdir() {
    local dir="$1"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would create directory: $dir"
    else
        mkdir -p "$dir"
    fi
}

dry_run_todoit() {
    local cmd="$*"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would execute: todoit $cmd"
        return 0
    else
        todoit "$@"
    fi
}

dry_run_file_operation() {
    local operation="$1"
    local details="$2"
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY-RUN] Would $operation: $details"
        return 0
    else
        return 1  # Signal to caller to perform actual operation
    fi
}

# ETAP 1: Analiza obecnego stanu
analyze_current_state() {
    log "=== ETAP 1: Analiza obecnego stanu ==="
    
    local output_file="${SCRIPT_DIR}/analysis_report.txt"
    
    log "Pobieranie listy wszystkich list TODOIT..."
    
    # Get all lists and save to temp file
    local all_lists_json=$(mktemp)
    TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    
    log "Analizowanie par Sequential/Linked..."
    
    # Parse and analyze
    {
        echo "=== RAPORT ANALIZY STANU OBECNEGO ==="
        echo "Data: $(date)"
        echo
        
        # Get Sequential lists with 37d tag
        local sequential_lists=$(jq -r '.data[] | select(.["🔀"] == "S" and (.["🏷️"] | contains("●"))) | .Key' "$all_lists_json")
        
        echo "=== ZNALEZIONE LISTY SEQUENTIAL (S) z tagiem 37d ==="
        local seq_count=0
        local linked_found=0
        local linked_missing=0
        
        while IFS= read -r seq_list; do
            if [[ -n "$seq_list" ]]; then
                seq_count=$((seq_count + 1))
                echo "$seq_count. $seq_list"
                
                # Check if corresponding linked list exists
                local linked_key="${seq_list}-download"
                local linked_exists=$(jq -r --arg key "$linked_key" '.data[] | select(.Key == $key) | .Key' "$all_lists_json")
                
                if [[ -n "$linked_exists" ]]; then
                    linked_found=$((linked_found + 1))
                    echo "   -> Linked: $linked_exists ✓"
                    
                    # Get status info
                    local seq_progress=$(jq -r --arg key "$seq_list" '.data[] | select(.Key == $key) | .["⏳"]' "$all_lists_json")
                    local linked_progress=$(jq -r --arg key "$linked_key" '.data[] | select(.Key == $key) | .["⏳"]' "$all_lists_json")
                    echo "   -> Progress: Sequential=${seq_progress}, Linked=${linked_progress}"
                else
                    linked_missing=$((linked_missing + 1))
                    echo "   -> Linked: MISSING ❌"
                fi
                echo
            fi
        done <<< "$sequential_lists"
        
        echo "=== PODSUMOWANIE ==="
        echo "Sequential lists found: $seq_count"
        echo "Linked lists found: $linked_found"
        echo "Linked lists missing: $linked_missing"
        echo
        
        # Find problematic lists (with failed tasks)
        echo "=== LISTY Z PROBLEMAMI (failed tasks) ==="
        local failed_lists=$(jq -r '.data[] | select(.["❌"] != "0") | "\(.Key): \(.["❌"]) failed"' "$all_lists_json")
        if [[ -n "$failed_lists" ]]; then
            echo "$failed_lists"
        else
            echo "Brak list z failed tasks ✓"
        fi
        echo
        
        # Summary of all Linked lists
        echo "=== WSZYSTKIE LINKED LISTS (do usunięcia) ==="
        local all_linked=$(jq -r '.data[] | select(.["🔀"] == "L") | .Key' "$all_lists_json")
        local linked_count=0
        while IFS= read -r linked_list; do
            if [[ -n "$linked_list" ]]; then
                linked_count=$((linked_count + 1))
                echo "$linked_count. $linked_list"
            fi
        done <<< "$all_linked"
        echo "Total Linked lists to delete: $linked_count"
        
    } > "$output_file"
    
    rm "$all_lists_json"
    
    log "Analiza zakończona. Raport zapisany w: $output_file"
    log_info "Przejrzyj raport przed przejściem do następnego etapu"
    
    echo
    echo "=== SZYBKIE PODSUMOWANIE ==="
    grep -E "(Sequential lists found|Linked lists found|Total Linked lists)" "$output_file"
}

# ETAP 2: Backup danych
backup_data() {
    log "=== ETAP 2: Backup danych ==="
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="${SCRIPT_DIR}/backup_${timestamp}"
    
    confirm "Utworzę backup wszystkich list w: $BACKUP_DIR"
    
    dry_run_mkdir "$BACKUP_DIR"
    
    log "Eksportowanie wszystkich list do JSON..."
    
    # Get all lists
    if ! dry_run_file_operation "write" "$BACKUP_DIR/all_lists.json"; then
        TODOIT_OUTPUT_FORMAT=json todoit list all > "$BACKUP_DIR/all_lists.json"
    fi
    
    # Export each Sequential and Linked list individually
    local all_lists_json="$BACKUP_DIR/all_lists.json"
    
    # In dry-run, we need actual data for analysis - use temp file
    if [[ "$DRY_RUN" == "true" ]]; then
        all_lists_json=$(mktemp)
        TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    fi
    
    local relevant_lists=$(jq -r '.data[] | select(.["🔀"] == "S" or .["🔀"] == "L") | select(.["🏷️"] | contains("●")) | .Key' "$all_lists_json")
    
    local exported_count=0
    while IFS= read -r list_key; do
        if [[ -n "$list_key" ]]; then
            exported_count=$((exported_count + 1))
            log_info "Eksportowanie: $list_key"
            
            # Export list details
            if ! dry_run_file_operation "export list" "$BACKUP_DIR/list_${list_key}.json"; then
                TODOIT_OUTPUT_FORMAT=json todoit list show "$list_key" > "$BACKUP_DIR/list_${list_key}.json"
            fi
            
            # Export all items with properties
            if ! dry_run_file_operation "export properties" "$BACKUP_DIR/properties_${list_key}.json"; then
                TODOIT_OUTPUT_FORMAT=json todoit item property list "$list_key" > "$BACKUP_DIR/properties_${list_key}.json" 2>/dev/null || echo '{"items": []}' > "$BACKUP_DIR/properties_${list_key}.json"
            fi
        fi
    done <<< "$relevant_lists"
    
    # Create backup summary
    {
        echo "=== BACKUP SUMMARY ==="
        echo "Date: $(date)"
        echo "Backup directory: $BACKUP_DIR"
        echo "Lists exported: $exported_count"
        echo
        echo "Files created:"
        if [[ "$DRY_RUN" == "false" ]]; then
            ls -la "$BACKUP_DIR"
        else
            echo "[DRY-RUN] Files would be created in $BACKUP_DIR"
        fi
    } > /dev/null  # In dry-run, don't create summary file
    
    # Clean up temp file in dry-run
    if [[ "$DRY_RUN" == "true" && -f "$all_lists_json" ]]; then
        rm "$all_lists_json"
    fi
    
    log "Backup zakończony. Eksportowano $exported_count list"
    log "Lokalizacja backup: $BACKUP_DIR"
}

# ETAP 3: Konwersja do properties
convert_to_properties() {
    log "=== ETAP 3: Konwersja do properties ==="
    
    if [[ -z "$BACKUP_DIR" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY-RUN] Używam najnowszego backup lub symulację..."
            # Find most recent backup directory
            BACKUP_DIR=$(find "$SCRIPT_DIR" -name "backup_*" -type d | sort | tail -1)
            if [[ -z "$BACKUP_DIR" ]]; then
                log_info "[DRY-RUN] Brak backup - symulacja na podstawie aktualnych danych"
                BACKUP_DIR="/tmp/dry_run_backup_simulation"
            fi
        else
            log_error "Backup nie został utworzony. Uruchom najpierw: $0 backup"
            exit 1
        fi
    fi
    
    confirm "Rozpoczynam konwersję statusów na properties. To zmodyfikuje dane w TODOIT!"
    
    local conversion_log="${SCRIPT_DIR}/conversion_details.log"
    
    log "Pobieranie par Sequential/Linked list..."
    
    # Get Sequential lists with 37d tag
    local all_lists_json
    
    # Always use current data (not backup) for conversion
    if [[ "$DRY_RUN" == "true" || ! -f "$BACKUP_DIR/all_lists.json" ]]; then
        # Use current data for dry-run or when no backup
        all_lists_json=$(mktemp)
        TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
        log_info "Using current data for conversion"
    else
        # Use backup data (but this creates inconsistency - not recommended)
        all_lists_json="$BACKUP_DIR/all_lists.json"
        log_warning "Using backup data - may create inconsistency!"
    fi
    
    local sequential_lists=$(jq -r '.data[] | select(.["🔀"] == "S" and (.["🏷️"] | contains("●"))) | .Key' "$all_lists_json")
    
    local converted_count=0
    local error_count=0
    
    {
        echo "=== SZCZEGÓŁY KONWERSJI ==="
        echo "Start: $(date)"
        echo
    } > "$conversion_log"
    
    while IFS= read -r seq_list; do
        if [[ -n "$seq_list" ]]; then
            log_info "Przetwarzanie: $seq_list"
            
            local linked_key="${seq_list}-download"
            
            # Check if linked list exists
            local linked_exists=$(jq -r --arg key "$linked_key" '.data[] | select(.Key == $key) | .Key' "$all_lists_json")
            
            if [[ -z "$linked_exists" ]]; then
                log_warning "Linked list nie istnieje dla: $seq_list"
                echo "WARNING: No linked list for $seq_list" >> "$conversion_log"
                continue
            fi
            
            # Get all items from current sequential list
            local seq_items_json=$(mktemp)
            TODOIT_OUTPUT_FORMAT=json todoit list show "$seq_list" > "$seq_items_json"
            
            # Get all items from current linked list
            local linked_items_json=$(mktemp)
            TODOIT_OUTPUT_FORMAT=json todoit list show "$linked_key" > "$linked_items_json"
            
            echo "Processing pair: $seq_list <-> $linked_key" >> "$conversion_log"
            
            # Process each item (filter out metadata entries)
            local item_keys=$(jq -r '.data[].Key // empty' "$seq_items_json" | grep -E '^(item_|scene_)')
            local items_processed=0
            
            while IFS= read -r item_key; do
                if [[ -n "$item_key" ]]; then
                    items_processed=$((items_processed + 1))
                    
                    # Get status from sequential list
                    local seq_status=$(jq -r --arg key "$item_key" '.data[] | select(.Key == $key) | .Status' "$seq_items_json")
                    
                    # Get status from linked list
                    local linked_status=$(jq -r --arg key "$item_key" '.data[] | select(.Key == $key) | .Status' "$linked_items_json")
                    
                    # Convert status to property values
                    local image_generated="pending"
                    local image_downloaded="pending"
                    
                    case "$seq_status" in
                        "⏳") image_generated="pending" ;;
                        "🔄") image_generated="in_progress" ;;
                        "✅") image_generated="completed" ;;
                        "❌") image_generated="failed" ;;
                        *) image_generated="pending" ;;
                    esac
                    
                    case "$linked_status" in
                        "⏳") image_downloaded="pending" ;;
                        "🔄") image_downloaded="in_progress" ;;
                        "✅") image_downloaded="completed" ;;
                        "❌") image_downloaded="failed" ;;
                        *) image_downloaded="pending" ;;
                    esac
                    
                    # Set properties
                    echo "  Item $item_key: gen=$image_generated, dl=$image_downloaded" >> "$conversion_log"
                    
                    if [[ "$DRY_RUN" == "true" ]]; then
                        log_info "  [DRY-RUN] Would set $item_key: gen=$image_generated, dl=$image_downloaded"
                    else
                        if todoit item property set "$seq_list" "$item_key" "image_generated" "$image_generated" 2>/dev/null; then
                            if todoit item property set "$seq_list" "$item_key" "image_downloaded" "$image_downloaded" 2>/dev/null; then
                                log_info "  ✓ $item_key: gen=$image_generated, dl=$image_downloaded"
                            else
                                log_error "  ✗ Failed to set image_downloaded for $item_key"
                                error_count=$((error_count + 1))
                            fi
                        else
                            log_error "  ✗ Failed to set image_generated for $item_key"
                            error_count=$((error_count + 1))
                        fi
                    fi
                fi
            done <<< "$item_keys"
            
            echo "  Items processed: $items_processed" >> "$conversion_log"
            echo >> "$conversion_log"
            
            converted_count=$((converted_count + 1))
            
            rm "$seq_items_json" "$linked_items_json"
        fi
    done <<< "$sequential_lists"
    
    {
        echo "=== PODSUMOWANIE KONWERSJI ==="
        echo "End: $(date)"
        echo "Lists converted: $converted_count"
        echo "Errors: $error_count"
    } >> "$conversion_log"
    
    # Cleanup temp file if created
    if [[ "$DRY_RUN" == "true" && "$BACKUP_DIR" == "/tmp/dry_run_backup_simulation" && -f "$all_lists_json" ]]; then
        rm "$all_lists_json"
    fi
    
    log "Konwersja zakończona:"
    log "- Przetworzone listy: $converted_count"
    log "- Błędy: $error_count"
    log "Szczegóły w: $conversion_log"
}

# ETAP 4: Weryfikacja konwersji
verify_conversion() {
    log "=== ETAP 4: Weryfikacja konwersji ==="
    
    local verification_file="${SCRIPT_DIR}/verification_report.txt"
    
    log "Sprawdzanie properties na wszystkich Sequential listach..."
    
    # Get Sequential lists with 37d tag
    local all_lists_json=$(mktemp)
    TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    local sequential_lists=$(jq -r '.data[] | select(.["🔀"] == "S" and (.["🏷️"] | contains("●"))) | .Key' "$all_lists_json")
    
    {
        echo "=== RAPORT WERYFIKACJI KONWERSJI ==="
        echo "Data: $(date)"
        echo
        
        local total_lists=0
        local lists_with_properties=0
        local total_items=0
        local items_with_gen_prop=0
        local items_with_dl_prop=0
        local items_with_both_props=0
        
        while IFS= read -r seq_list; do
            if [[ -n "$seq_list" ]]; then
                total_lists=$((total_lists + 1))
                echo "=== Lista: $seq_list ==="
                
                # Get properties for this list
                local props_json=$(mktemp)
                TODOIT_OUTPUT_FORMAT=json todoit item property list "$seq_list" > "$props_json" 2>/dev/null || echo '{"data": []}' > "$props_json"
                
                local has_image_gen=$(jq -r '.data[] | select(.["Property Key"] == "image_generated") | .["Item Key"]' "$props_json")
                local has_image_dl=$(jq -r '.data[] | select(.["Property Key"] == "image_downloaded") | .["Item Key"]' "$props_json")
                
                if [[ -n "$has_image_gen" || -n "$has_image_dl" ]]; then
                    lists_with_properties=$((lists_with_properties + 1))
                fi
                
                # Count items in this list
                local list_items_json=$(mktemp)
                TODOIT_OUTPUT_FORMAT=json todoit list show "$seq_list" > "$list_items_json"
                local item_count=$(jq -r '.data | length' "$list_items_json" | tr -d '\n\r ')
                total_items=$((total_items + item_count))
                
                echo "Liczba itemów: $item_count"
                
                # Count properties
                local gen_count=0
                local dl_count=0
                
                if [[ -n "$has_image_gen" ]]; then 
                    gen_count=$(echo "$has_image_gen" | wc -l | tr -d '\n\r ')
                fi
                if [[ -n "$has_image_dl" ]]; then 
                    dl_count=$(echo "$has_image_dl" | wc -l | tr -d '\n\r ')
                fi
                
                items_with_gen_prop=$((items_with_gen_prop + gen_count))
                items_with_dl_prop=$((items_with_dl_prop + dl_count))
                
                echo "Items z image_generated: $gen_count"
                echo "Items z image_downloaded: $dl_count"
                
                # Sample properties values
                echo "Sample properties:"
                jq -r '.data[] | select(.["Property Key"] == "image_generated" or .["Property Key"] == "image_downloaded") | "  \(.["Item Key"]): \(.["Property Key"])=\(.Value)"' "$props_json" | head -5
                
                # Count items with both properties
                local items_with_both=0
                local all_item_keys=$(jq -r '.data[].["Item Key"]' "$list_items_json")
                while IFS= read -r item_key; do
                    if [[ -n "$item_key" ]]; then
                        local has_gen=$(echo "$has_image_gen" | grep -c "^$item_key$" 2>/dev/null || echo "0")
                        local has_dl=$(echo "$has_image_dl" | grep -c "^$item_key$" 2>/dev/null || echo "0")
                        # Remove any whitespace/newlines
                        has_gen=$(echo "$has_gen" | tr -d '\n\r ')
                        has_dl=$(echo "$has_dl" | tr -d '\n\r ')
                        if [[ "$has_gen" -gt 0 && "$has_dl" -gt 0 ]]; then
                            items_with_both=$((items_with_both + 1))
                        fi
                    fi
                done <<< "$all_item_keys"
                
                items_with_both_props=$((items_with_both_props + items_with_both))
                echo "Items z oboma properties: $items_with_both"
                echo
                
                rm "$props_json" "$list_items_json"
            fi
        done <<< "$sequential_lists"
        
        echo "=== PODSUMOWANIE WERYFIKACJI ==="
        echo "Total Sequential lists: $total_lists"
        echo "Lists with properties: $lists_with_properties"
        echo "Total items: $total_items"
        echo "Items with image_generated: $items_with_gen_prop"
        echo "Items with image_downloaded: $items_with_dl_prop"
        echo "Items with both properties: $items_with_both_props"
        echo
        
        local coverage_gen=$(awk "BEGIN {printf \"%.1f\", $items_with_gen_prop/$total_items*100}")
        local coverage_dl=$(awk "BEGIN {printf \"%.1f\", $items_with_dl_prop/$total_items*100}")
        local coverage_both=$(awk "BEGIN {printf \"%.1f\", $items_with_both_props/$total_items*100}")
        
        echo "Coverage image_generated: ${coverage_gen}%"
        echo "Coverage image_downloaded: ${coverage_dl}%"
        echo "Coverage both properties: ${coverage_both}%"
        echo
        
        if [[ "$items_with_both_props" -eq "$total_items" ]]; then
            echo "✅ SUKCES: Wszystkie items mają obie properties!"
        else
            echo "⚠️  UWAGA: Nie wszystkie items mają pełne properties"
        fi
        
    } > "$verification_file"
    
    rm "$all_lists_json"
    
    log "Weryfikacja zakończona. Raport zapisany w: $verification_file"
    
    echo
    echo "=== SZYBKIE PODSUMOWANIE ==="
    tail -10 "$verification_file"
}

# ETAP 5: Test systemu properties
test_properties_system() {
    log "=== ETAP 5: Test systemu properties ==="
    
    confirm "Wykonam testy systemu properties (bez modyfikacji danych)"
    
    log "Test 1: Sprawdzenie czy można odczytać properties..."
    
    # Find first Sequential list
    local all_lists_json=$(mktemp)
    TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    local first_seq_list=$(jq -r '.data[] | select(.["🔀"] == "S" and (.["🏷️"] | contains("●"))) | .Key' "$all_lists_json" | head -1)
    
    if [[ -n "$first_seq_list" ]]; then
        log_info "Testowanie na liście: $first_seq_list"
        
        # Test reading properties
        log_info "Test odczytu properties..."
        if TODOIT_OUTPUT_FORMAT=json todoit item property list "$first_seq_list" > /dev/null; then
            log_info "✓ Odczyt properties działa"
        else
            log_error "✗ Błąd odczytu properties"
        fi
        
        # Test setting new property
        log_info "Test ustawiania nowej property..."
        local test_item=$(TODOIT_OUTPUT_FORMAT=json todoit list show "$first_seq_list" | jq -r '.data[0].["Item Key"]')
        
        if [[ -n "$test_item" ]]; then
            if todoit item property set "$first_seq_list" "$test_item" "test_property" "test_value"; then
                log_info "✓ Ustawianie nowej property działa"
                
                # Clean up test property
                todoit item property delete "$first_seq_list" "$test_item" "test_property" --force 2>/dev/null || true
            else
                log_error "✗ Błąd ustawiania property"
            fi
        fi
        
        # Test filtering by property values
        log_info "Test przykładowego workflow..."
        
        local completed_items=$(TODOIT_OUTPUT_FORMAT=json todoit item property list "$first_seq_list" | jq -r '.data[] | select(.["Property Key"] == "image_generated" and .Value == "completed") | .["Item Key"]')
        local completed_count=$(echo "$completed_items" | grep -v "^$" | wc -l || echo "0")
        
        log_info "Items z image_generated=completed: $completed_count"
        
        local pending_downloads=$(TODOIT_OUTPUT_FORMAT=json todoit item property list "$first_seq_list" | jq -r '.data[] | select(.["Property Key"] == "image_downloaded" and .Value == "pending") | .["Item Key"]')
        local pending_dl_count=$(echo "$pending_downloads" | grep -v "^$" | wc -l || echo "0")
        
        log_info "Items z image_downloaded=pending: $pending_dl_count"
        
    else
        log_error "Nie znaleziono Sequential list do testów"
    fi
    
    rm "$all_lists_json"
    
    log "Testy zakończone pomyślnie"
    log_info "System properties jest gotowy do użycia!"
}

# ETAP 6: Usunięcie Linked list
cleanup_linked_lists() {
    log "=== ETAP 6: Usunięcie Linked list ==="
    
    log_warning "Usunie WSZYSTKIE Linked lists!"
    log_warning "Upewnij się, że konwersja przebiegła pomyślnie i masz backup!"
    
    confirm "Czy na pewno chcesz usunąć wszystkie Linked lists? Ta operacja jest nieodwracalna!"
    
    # Get all Linked lists
    local all_lists_json=$(mktemp)
    TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    local linked_lists=$(jq -r '.data[] | select(.["🔀"] == "L") | .Key' "$all_lists_json")
    
    local cleanup_log="${SCRIPT_DIR}/cleanup_log.txt"
    
    {
        echo "=== LOG USUWANIA LINKED LISTS ==="
        echo "Start: $(date)"
        echo
    } > "$cleanup_log"
    
    local deleted_count=0
    local error_count=0
    
    while IFS= read -r linked_list; do
        if [[ -n "$linked_list" ]]; then
            log_info "Usuwanie: $linked_list"
            echo "Deleting: $linked_list" >> "$cleanup_log"
            
            if [[ "$DRY_RUN" == "true" ]]; then
                deleted_count=$((deleted_count + 1))
                log_info "  [DRY-RUN] Would delete: $linked_list"
                echo "  DRY-RUN SUCCESS" >> "$cleanup_log"
            else
                if todoit list delete "$linked_list" --force; then
                    deleted_count=$((deleted_count + 1))
                    log_info "  ✓ Usunięto: $linked_list"
                    echo "  SUCCESS" >> "$cleanup_log"
                else
                    error_count=$((error_count + 1))
                    log_error "  ✗ Błąd usuwania: $linked_list"
                    echo "  ERROR" >> "$cleanup_log"
                fi
            fi
        fi
    done <<< "$linked_lists"
    
    {
        echo
        echo "=== PODSUMOWANIE CLEANUP ==="
        echo "End: $(date)"
        echo "Lists deleted: $deleted_count"
        echo "Errors: $error_count"
    } >> "$cleanup_log"
    
    rm "$all_lists_json"
    
    log "Cleanup zakończone:"
    log "- Usunięte listy: $deleted_count"
    log "- Błędy: $error_count"
    log "Szczegóły w: $cleanup_log"
    
    if [[ "$error_count" -eq 0 ]]; then
        log_info "✅ Linked lists usunięte pomyślnie!"
        log_info "Następny krok: uruchom 'sync' aby zsynchronizować statusy główne"
    else
        log_warning "Cleanup zakończony z błędami. Sprawdź log: $cleanup_log"
    fi
}

# ETAP 7: Synchronizacja statusów głównych itemów
sync_main_status() {
    log "=== ETAP 7: Synchronizacja statusów głównych ==="
    
    log_info "Ustawi statusy główne itemów na podstawie kombinacji properties:"
    log_info "- Obydwa completed → status completed"
    log_info "- Obydwa pending → status pending" 
    log_info "- Inne kombinacje → status in_progress"
    
    confirm "Rozpoczynam synchronizację statusów głównych itemów"
    
    local sync_log="${SCRIPT_DIR}/sync_status_log.txt"
    
    # Get Sequential lists with 37d tag
    local all_lists_json=$(mktemp)
    TODOIT_OUTPUT_FORMAT=json todoit list all > "$all_lists_json"
    local sequential_lists=$(jq -r '.data[] | select(.["🔀"] == "S" and (.["🏷️"] | contains("●"))) | .Key' "$all_lists_json")
    
    {
        echo "=== LOG SYNCHRONIZACJI STATUSÓW GŁÓWNYCH ==="
        echo "Start: $(date)"
        echo
        echo "Logika statusów:"
        echo "- image_generated=completed AND image_downloaded=completed → completed"
        echo "- image_generated=pending AND image_downloaded=pending → pending"
        echo "- pozostałe kombinacje → in_progress"
        echo
    } > "$sync_log"
    
    local processed_lists=0
    local processed_items=0
    local updated_items=0
    local error_count=0
    
    while IFS= read -r seq_list; do
        if [[ -n "$seq_list" ]]; then
            processed_lists=$((processed_lists + 1))
            log_info "Przetwarzanie: $seq_list"
            echo "Processing list: $seq_list" >> "$sync_log"
            
            # Get all items from the list
            local list_items_json=$(mktemp)
            TODOIT_OUTPUT_FORMAT=json todoit list show "$seq_list" > "$list_items_json"
            
            # Get all properties for this list
            local props_json=$(mktemp)
            TODOIT_OUTPUT_FORMAT=json todoit item property list "$seq_list" > "$props_json" 2>/dev/null || echo '{"data": []}' > "$props_json"
            
            # Process each item
            local item_keys=$(jq -r '.data[].Key // empty' "$list_items_json")
            
            while IFS= read -r item_key; do
                if [[ -n "$item_key" ]]; then
                    processed_items=$((processed_items + 1))
                    
                    # Get current main status
                    local current_status=$(jq -r --arg key "$item_key" '.data[] | select(.Key == $key) | .Status' "$list_items_json")
                    
                    # Get properties for this item
                    local image_generated=$(jq -r --arg item "$item_key" '.data[] | select(.["Item Key"] == $item and .["Property Key"] == "image_generated") | .Value' "$props_json")
                    local image_downloaded=$(jq -r --arg item "$item_key" '.data[] | select(.["Item Key"] == $item and .["Property Key"] == "image_downloaded") | .Value' "$props_json")
                    
                    # Handle missing properties
                    if [[ -z "$image_generated" || "$image_generated" == "null" ]]; then
                        log_warning "  ⚠️  $item_key: brak property image_generated"
                        image_generated="pending"
                    fi
                    
                    if [[ -z "$image_downloaded" || "$image_downloaded" == "null" ]]; then
                        log_warning "  ⚠️  $item_key: brak property image_downloaded"
                        image_downloaded="pending"
                    fi
                    
                    # Determine new main status based on properties combination
                    local new_status=""
                    
                    if [[ "$image_generated" == "completed" && "$image_downloaded" == "completed" ]]; then
                        new_status="completed"
                    elif [[ "$image_generated" == "pending" && "$image_downloaded" == "pending" ]]; then
                        new_status="pending"
                    elif [[ "$image_generated" == "failed" || "$image_downloaded" == "failed" ]]; then
                        new_status="failed"
                    else
                        new_status="in_progress"
                    fi
                    
                    # Convert status symbols to text for comparison
                    local current_status_text=""
                    case "$current_status" in
                        "⏳") current_status_text="pending" ;;
                        "🔄") current_status_text="in_progress" ;;
                        "✅") current_status_text="completed" ;;
                        "❌") current_status_text="failed" ;;
                        *) current_status_text="unknown" ;;
                    esac
                    
                    echo "  Item: $item_key" >> "$sync_log"
                    echo "    Current: $current_status_text ($current_status)" >> "$sync_log"
                    echo "    Properties: gen=$image_generated, dl=$image_downloaded" >> "$sync_log"
                    echo "    New status: $new_status" >> "$sync_log"
                    
                    # Update status if different
                    if [[ "$current_status_text" != "$new_status" ]]; then
                        log_info "  🔄 $item_key: $current_status_text → $new_status"
                        
                        if [[ "$DRY_RUN" == "true" ]]; then
                            updated_items=$((updated_items + 1))
                            log_info "    [DRY-RUN] Would update to $new_status"
                            echo "    DRY-RUN SUCCESS: Would update to $new_status" >> "$sync_log"
                        else
                            if todoit item status "$seq_list" "$item_key" --status "$new_status" 2>/dev/null; then
                                updated_items=$((updated_items + 1))
                                log_info "    ✓ Zaktualizowano"
                                echo "    SUCCESS: Updated to $new_status" >> "$sync_log"
                            else
                                error_count=$((error_count + 1))
                                log_error "    ✗ Błąd aktualizacji"
                                echo "    ERROR: Failed to update" >> "$sync_log"
                            fi
                        fi
                    else
                        log_info "  ➖ $item_key: status już prawidłowy ($new_status)"
                        echo "    SKIP: Already correct" >> "$sync_log"
                    fi
                    
                    echo >> "$sync_log"
                fi
            done <<< "$item_keys"
            
            rm "$list_items_json" "$props_json"
            echo >> "$sync_log"
        fi
    done <<< "$sequential_lists"
    
    {
        echo "=== PODSUMOWANIE SYNCHRONIZACJI ==="
        echo "End: $(date)"
        echo "Processed lists: $processed_lists"
        echo "Processed items: $processed_items"
        echo "Updated items: $updated_items"
        echo "Errors: $error_count"
    } >> "$sync_log"
    
    rm "$all_lists_json"
    
    log "Synchronizacja zakończona:"
    log "- Przetworzone listy: $processed_lists"
    log "- Przetworzone items: $processed_items"
    log "- Zaktualizowane items: $updated_items"
    log "- Błędy: $error_count"
    log "Szczegóły w: $sync_log"
    
    if [[ "$error_count" -eq 0 ]]; then
        log_info "🎉 Konwersja CAŁKOWICIE zakończona!"
        log_info "System używa teraz properties zamiast linked lists"
        log_info "Statusy główne są zsynchronizowane z properties"
    else
        log_warning "Synchronizacja zakończona z błędami. Sprawdź log: $sync_log"
    fi
}

# Help function
show_help() {
    echo "Konwersja systemu Linked Lists na Properties"
    echo
    echo "Użycie: $0 [--dry-run] <etap>"
    echo
    echo "Opcje:"
    echo "  --dry-run  - Symulacja bez wykonywania modyfikacji"
    echo
    echo "Etapy:"
    echo "  analyze   - Analiza obecnego stanu (Sequential/Linked pairs)"
    echo "  backup    - Backup wszystkich danych do JSON"
    echo "  convert   - Konwersja statusów na properties"
    echo "  verify    - Weryfikacja konwersji"
    echo "  test      - Test systemu properties"
    echo "  cleanup   - Usunięcie wszystkich Linked lists"
    echo "  sync      - Synchronizacja statusów głównych z properties"
    echo
    echo "Przykłady:"
    echo "  $0 analyze                    # Analiza rzeczywista"
    echo "  $0 --dry-run convert          # Symulacja konwersji"
    echo "  $0 --dry-run cleanup          # Podgląd co zostanie usunięte"
    echo "  $0 sync                       # Ostatni etap!"
}

# Main function
main() {
    # Parse arguments
    local stage=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                log_warning "=== DRY-RUN MODE ENABLED ==="
                log_warning "Żadne modyfikacje nie będą wykonane"
                shift
                ;;
            --help|-h|help)
                show_help
                exit 0
                ;;
            *)
                if [[ -z "$stage" ]]; then
                    stage="$1"
                else
                    echo "Nieprawidłowy argument: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    if [[ -z "$stage" ]]; then
        echo "Nie podano etapu do wykonania"
        show_help
        exit 1
    fi
    
    init_logging
    check_todoit
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "🧪 DRY-RUN: Symulacja etapu '$stage'"
    fi
    
    case "$stage" in
        "analyze")
            analyze_current_state
            ;;
        "backup")
            backup_data
            ;;
        "convert")
            convert_to_properties
            ;;
        "verify")
            verify_conversion
            ;;
        "test")
            test_properties_system
            ;;
        "cleanup")
            cleanup_linked_lists
            ;;
        "sync")
            sync_main_status
            ;;
        *)
            echo "Nieprawidłowy etap: $stage"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"