#!/usr/bin/env python3
"""
Emoji utilities for text rendering
Provides emoji to text replacement functionality
"""

# Common emoji replacements for Polish youth content
EMOJI_REPLACEMENTS = {
    # Faces and emotions
    '😊': ':)',
    '😃': ':D',
    '😄': ':D',
    '😁': ':D',
    '😆': 'xD',
    '😂': 'xD',
    '🤣': 'XD',
    '😍': '<3',
    '😘': ':*',
    '😎': 'B)',
    '🤔': '?',
    '😏': ';)',
    '😉': ';)',
    '😢': ':(',
    '😭': ":'(",
    '😱': ':O',
    '😮': ':o',
    '🙄': '-_-',
    '😴': 'zzz',
    '🤯': '!!!',
    '🥰': '<3',
    '🤩': '*_*',
    
    # Hearts and symbols
    '❤️': '<3',
    '💕': '<3',
    '💖': '<3',
    '💗': '<3',
    '💘': '<3',
    '💙': '<3',
    '💚': '<3',
    '💛': '<3',
    '💜': '<3',
    '🖤': '<3',
    '💔': '</3',
    '⭐': '*',
    '🌟': '*',
    '✨': '*',
    '🔥': '[FIRE]',
    '💥': '[BOOM]',
    '⚡': '[FLASH]',
    '🌈': '[RAINBOW]',
    
    # Objects and activities
    '📚': '[BOOK]',
    '📖': '[BOOK]',
    '📝': '[NOTE]',
    '✏️': '[PENCIL]',
    '🎬': '[MOVIE]',
    '🎭': '[DRAMA]',
    '🎨': '[ART]',
    '🎵': '[MUSIC]',
    '🎶': '[MUSIC]',
    '🏆': '[TROPHY]',
    '🎯': '[TARGET]',
    '💡': '[IDEA]',
    '🔍': '[SEARCH]',
    '👁️': '[EYE]',
    '👀': '[EYES]',
    '🗣️': '[SPEAK]',
    '💬': '[CHAT]',
    '💭': '[THINK]',
    
    # Gestures
    '👍': '+1',
    '👎': '-1',
    '👏': '[CLAP]',
    '🙏': '[PRAY]',
    '✋': '[STOP]',
    '👋': '[WAVE]',
    '💪': '[STRONG]',
    '🤝': '[HANDSHAKE]',
    '✌️': 'V',
    '🤟': '\\m/',
    
    # Time and nature
    '🌅': '[SUNRISE]',
    '🌄': '[SUNRISE]',
    '🌙': '[MOON]',
    '☀️': '[SUN]',
    '🌞': '[SUN]',
    '⏰': '[CLOCK]',
    '⏳': '[TIME]',
    '🌺': '[FLOWER]',
    '🌸': '[FLOWER]',
    '🌼': '[FLOWER]',
    
    # Arrows and checkmarks
    '➡️': '->',
    '⬅️': '<-',
    '⬆️': '^',
    '⬇️': 'v',
    '↗️': '^',
    '✅': '[OK]',
    '✔️': '[OK]',
    '❌': '[X]',
    '❓': '?',
    '❗': '!',
    '‼️': '!!',
    '⁉️': '?!',
    
    # Other common emojis
    '🇵🇱': '[PL]',
    '🌍': '[WORLD]',
    '🌎': '[WORLD]',
    '🌏': '[WORLD]',
    '🚀': '[ROCKET]',
    '💯': '100%',
    '🎉': '[PARTY]',
    '🎊': '[PARTY]',
    '🏃': '[RUN]',
    '🚶': '[WALK]',
    '💃': '[DANCE]',
    '🕺': '[DANCE]',
    
    # Food and entertainment
    '🍿': '[POPCORN]',
    '☕': '[COFFEE]',
    '🍵': '[TEA]',
    
    # Weather  
    '❄️': '[SNOW]',
    '☃️': '[SNOWMAN]',
    '🌧️': '[RAIN]',
    '⛅': '[CLOUDY]',
    '🌤️': '[SUNNY]',
}


def replace_emojis(text: str, custom_replacements: dict = None) -> str:
    """
    Replace emojis with text equivalents
    
    Args:
        text: Text containing emojis
        custom_replacements: Optional custom emoji replacement dictionary
        
    Returns:
        Text with emojis replaced by text equivalents
    """
    replacements = EMOJI_REPLACEMENTS.copy()
    
    # Add custom replacements if provided
    if custom_replacements:
        replacements.update(custom_replacements)
    
    # Replace emojis
    result = text
    for emoji, replacement in replacements.items():
        result = result.replace(emoji, replacement)
    
    return result


def remove_emojis(text: str) -> str:
    """
    Remove all emojis from text
    
    Args:
        text: Text containing emojis
        
    Returns:
        Text with emojis removed
    """
    result = text
    for emoji in EMOJI_REPLACEMENTS.keys():
        result = result.replace(emoji, '')
    
    # Remove any remaining Unicode emoji ranges
    # This is a simplified approach - for production use consider regex with full Unicode ranges
    import re
    # Remove most common emoji Unicode ranges
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    result = emoji_pattern.sub('', result)
    
    # Clean up multiple spaces
    result = ' '.join(result.split())
    
    return result


def has_emojis(text: str) -> bool:
    """
    Check if text contains emojis
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains emojis
    """
    for emoji in EMOJI_REPLACEMENTS.keys():
        if emoji in text:
            return True
    
    # Check for other Unicode emoji ranges
    import re
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    return bool(emoji_pattern.search(text))


if __name__ == "__main__":
    # Test the functions
    test_texts = [
        "Czy wiesz, że najważniejsze jest niewidoczne dla oczu? 👁️",
        "Książka pełna mądrości 📚 i piękna ✨",
        "Kochamy czytać! ❤️📖 To nasz ulubiony sposób na spędzanie czasu 🌟",
        "🔥 Gorąca nowość! 🎬 Film na podstawie książki już w kinach! 🍿",
        "Test emotek: 😊😎🤔😍💕🔥📚✨"
    ]
    
    print("=== Emoji Replacement Tests ===\n")
    
    for text in test_texts:
        replaced = replace_emojis(text)
        removed = remove_emojis(text)
        has_emoji = has_emojis(text)
        
        print(f"Original: {text}")
        print(f"Replaced: {replaced}")
        print(f"Removed:  {removed}")
        print(f"Has emoji: {has_emoji}")
        print("-" * 50)