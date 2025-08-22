#!/bin/bash

# Test obu formatów błędów ChatGPT
source scripts/todoit-a3.sh

echo "=== Test parse_chatgpt_error - oba formaty ==="

# Test 1: Format z czasem (agent format)
test_output1="ChatGPT Plus usage limit reached|5|23
BŁĄD: scene_0006 image_gen - ChatGPT Plus limit."

echo "Test 1 - Format z czasem:"
echo "Input: $test_output1"
result1=$(parse_chatgpt_error "$test_output1")
echo "Timestamp: $result1"
if [ -n "$result1" ]; then
    echo "Date: $(date -d "@$result1" "+%Y-%m-%d %H:%M:%S %Z")"
    sleep_time=$(calculate_chatgpt_sleep_time "$result1")
    echo "Sleep time: $sleep_time seconds ($(($sleep_time/60)) minutes)"
fi
echo ""

# Test 2: Format "tomorrow" (nowy)
test_output2="ChatGPT Plus usage limit reached - image generation will be available again tomorrow"

echo "Test 2 - Format 'tomorrow' (6h sleep):"
echo "Input: $test_output2"
result2=$(parse_chatgpt_error "$test_output2")
echo "Timestamp: $result2"
if [ -n "$result2" ]; then
    echo "Date: $(date -d "@$result2" "+%Y-%m-%d %H:%M:%S %Z")"
    sleep_time=$(calculate_chatgpt_sleep_time "$result2")
    echo "Sleep time: $sleep_time seconds ($(($sleep_time/60)) minutes, $(($sleep_time/3600)) hours)"
fi
echo ""

# Test 3: Format fallback
test_output3="You've hit the plus plan limit for image generation requests. You can create more images when the limit resets in 2 hours and 15 minutes."

echo "Test 3 - Format fallback:"
echo "Input: $test_output3"
result3=$(parse_chatgpt_error "$test_output3")
echo "Timestamp: $result3"
if [ -n "$result3" ]; then
    echo "Date: $(date -d "@$result3" "+%Y-%m-%d %H:%M:%S %Z")"
    sleep_time=$(calculate_chatgpt_sleep_time "$result3")
    echo "Sleep time: $sleep_time seconds ($(($sleep_time/60)) minutes)"
fi
echo ""

echo "=== Test zakończony ==="
