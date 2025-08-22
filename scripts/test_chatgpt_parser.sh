#!/bin/bash

# Test funkcji parsowania ChatGPT error
source scripts/todoit-a3.sh

echo "=== Test parse_chatgpt_error ==="

# Test 1: Format agent output
test_output1="ChatGPT Plus usage limit reached|5|23
BŁĄD: scene_0006 image_gen - ChatGPT Plus limit. Thread ID: 68a6385c"

echo "Test 1 - Agent format:"
echo "Input: $test_output1"
result1=$(parse_chatgpt_error "$test_output1")
echo "Timestamp: $result1"
if [ -n "$result1" ]; then
    echo "Date: $(date -d "@$result1" "+%Y-%m-%d %H:%M:%S %Z")"
    sleep_time=$(calculate_chatgpt_sleep_time "$result1")
    echo "Sleep time: $sleep_time seconds ($(($sleep_time/60)) minutes)"
fi
echo ""

# Test 2: Format fallback
test_output2="You've hit the plus plan limit for image generation requests. You can create more images when the limit resets in 5 hours and 23 minutes."

echo "Test 2 - Fallback format:"
echo "Input: $test_output2"
result2=$(parse_chatgpt_error "$test_output2")
echo "Timestamp: $result2"
if [ -n "$result2" ]; then
    echo "Date: $(date -d "@$result2" "+%Y-%m-%d %H:%M:%S %Z")"
    sleep_time=$(calculate_chatgpt_sleep_time "$result2")
    echo "Sleep time: $sleep_time seconds ($(($sleep_time/60)) minutes)"
fi
echo ""

# Test 3: Nie pasujący format
test_output3="Some other error message"

echo "Test 3 - No match:"
echo "Input: $test_output3"
result3=$(parse_chatgpt_error "$test_output3")
echo "Timestamp: '$result3'"
echo ""

echo "=== Test zakończony ==="
