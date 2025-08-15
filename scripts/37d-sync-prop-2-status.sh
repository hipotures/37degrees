#!/bin/bash

# 37d-sync-prop-2-status.sh
# Skrypt do synchronizacji statusu głównego z properties dla list z określonym tagiem
# Bazuje na logice z convert-linked-to-properties.sh

# Sprawdź czy podano tag
if [ -z "$1" ]; then
    echo "Błąd: Podaj tag list do synchronizacji"
    echo "Użycie: $0 <tag>"
    echo "Przykład: $0 37d"
    exit 1
fi

TAG="$1"

# Funkcja synchronizacji statusu dla jednego itemu
sync_item_status() {
    local list_key="$1"
    local item_key="$2"
    
    # Pobierz właściwości itemu z JSON
    local properties=$(TODOIT_OUTPUT_FORMAT=json todoit item property list "$list_key" 2>/dev/null | jq -r --arg item "$item_key" '.[$item] // {}')
    local image_generated=$(echo "$properties" | jq -r '.image_generated // "pending"')
    local image_downloaded=$(echo "$properties" | jq -r '.image_downloaded // "pending"')
    
    # Określ nowy status na podstawie properties (logika z convert-linked-to-properties.sh)
    local new_status
    if [[ "$image_generated" == "completed" && "$image_downloaded" == "completed" ]]; then
        new_status="completed"
    elif [[ "$image_generated" == "pending" && "$image_downloaded" == "pending" ]]; then
        new_status="pending"
    elif [[ "$image_generated" == "failed" || "$image_downloaded" == "failed" ]]; then
        new_status="failed"
    else
        new_status="in_progress"
    fi
    
    # Ustaw nowy status
    todoit item status "$list_key" "$item_key" --status "$new_status" 2>/dev/null
    
    echo "  $item_key: gen=$image_generated, dl=$image_downloaded → $new_status"
}

# Znajdź listy z określonym tagiem
echo "🔍 Szukam list z tagiem: $TAG"

# Pobierz wszystkie listy z danym tagiem używając TODOIT_OUTPUT_FORMAT=json
LISTS=$(TODOIT_OUTPUT_FORMAT=json todoit list all --tag "$TAG" 2>/dev/null | jq -r '.data[]?.Key' 2>/dev/null)

if [ -z "$LISTS" ]; then
    echo "❌ Nie znaleziono list z tagiem: $TAG"
    exit 1
fi

echo "📋 Znalezione listy:"
echo "$LISTS"
echo ""

# Synchronizuj każdą listę
for list_key in $LISTS; do
    echo "🔄 Synchronizuję listę: $list_key"
    
    # Pobierz wszystkie itemy z listy (klucze z JSON object)
    ITEMS=$(TODOIT_OUTPUT_FORMAT=json todoit item property list "$list_key" 2>/dev/null | jq -r 'keys[]?' 2>/dev/null)
    
    if [ -z "$ITEMS" ]; then
        echo "  ⚠️ Brak itemów w liście"
        continue
    fi
    
    # Synchronizuj każdy item
    for item_key in $ITEMS; do
        sync_item_status "$list_key" "$item_key"
    done
    
    echo "  ✅ Zakończono synchronizację listy: $list_key"
    echo ""
done

echo "🎉 Synchronizacja zakończona dla wszystkich list z tagiem: $TAG"