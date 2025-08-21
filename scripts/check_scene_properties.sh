#!/bin/bash

# Check if scene properties match their parent item names in TODOIT
# Usage: ./check_scene_properties.sh [list_key]

LIST_KEY=${1:-"0037_wuthering_heights"}

echo "Checking scene properties alignment for list: $LIST_KEY"
echo "========================================="

# Get all scenes from the list
SCENES=$(python -c "
import sys
sys.path.append('.')
from mcp_todoit import todo_get_list_items

result = todo_get_list_items('$LIST_KEY', None, None)
if result['success']:
    for item in result['items']:
        if item['item_key'].startswith('scene_'):
            print(item['item_key'])
")

TOTAL_ERRORS=0

for SCENE in $SCENES; do
    echo ""
    echo "Checking $SCENE..."
    
    # Extract expected scene number from parent item name (e.g., scene_0001 -> 0001)
    EXPECTED_NUM=$(echo "$SCENE" | sed 's/scene_//')
    
    # Check scene_style subitem properties
    STYLE_PROPERTY=$(python -c "
import sys
sys.path.append('.')
from mcp_todoit import todo_get_item_property

result = todo_get_item_property('$LIST_KEY', 'scene_style', 'scene_style_pathfile', '$SCENE')
if result['success']:
    print(result['property_value'])
else:
    print('NOT_FOUND')
")
    
    # Check image_dwn subitem properties  
    DWN_PROPERTY=$(python -c "
import sys
sys.path.append('.')
from mcp_todoit import todo_get_item_property

result = todo_get_item_property('$LIST_KEY', 'image_dwn', 'dwn_pathfile', '$SCENE')
if result['success']:
    print(result['property_value'])
else:
    print('NOT_FOUND')
")
    
    # Validate scene_style_pathfile
    if [[ "$STYLE_PROPERTY" == "NOT_FOUND" ]]; then
        echo "  ❌ scene_style_pathfile: NOT FOUND"
        ((TOTAL_ERRORS++))
    else
        # Extract scene number from path (e.g., scene_0001.yaml -> 0001)
        STYLE_NUM=$(echo "$STYLE_PROPERTY" | grep -o 'scene_[0-9]\{4\}' | sed 's/scene_//')
        if [[ "$STYLE_NUM" == "$EXPECTED_NUM" ]]; then
            echo "  ✅ scene_style_pathfile: $STYLE_PROPERTY"
        else
            echo "  ❌ scene_style_pathfile: $STYLE_PROPERTY (expected scene_$EXPECTED_NUM.yaml)"
            ((TOTAL_ERRORS++))
        fi
    fi
    
    # Validate dwn_pathfile
    if [[ "$DWN_PROPERTY" == "NOT_FOUND" ]]; then
        echo "  ❌ dwn_pathfile: NOT FOUND"
        ((TOTAL_ERRORS++))
    else
        # Extract scene number from path (e.g., scene_0001.png -> 0001)
        DWN_NUM=$(echo "$DWN_PROPERTY" | grep -o 'scene_[0-9]\{4\}' | sed 's/scene_//')
        if [[ "$DWN_NUM" == "$EXPECTED_NUM" ]]; then
            echo "  ✅ dwn_pathfile: $DWN_PROPERTY"
        else
            echo "  ❌ dwn_pathfile: $DWN_PROPERTY (expected scene_$EXPECTED_NUM.png)"
            ((TOTAL_ERRORS++))
        fi
    fi
done

echo ""
echo "========================================="
if [[ $TOTAL_ERRORS -eq 0 ]]; then
    echo "🎉 All scene properties are correctly aligned!"
else
    echo "❌ Found $TOTAL_ERRORS property misalignment(s)"
fi
echo "========================================="

exit $TOTAL_ERRORS