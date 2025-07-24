#!/usr/bin/env python3
"""
Emoji utilities for text rendering
Provides emoji to text replacement functionality
"""

# Common emoji replacements for Polish youth content
# Internal emoji data - not exported
_EMOJI_REPLACEMENTS = {
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


def has_emojis(text: str) -> bool:
    """
    Check if text contains emojis
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains emojis
    """
    for emoji in _EMOJI_REPLACEMENTS.keys():
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
    
    print("=== Emoji Detection Tests ===\n")
    
    for text in test_texts:
        has_emoji = has_emojis(text)
        
        print(f"Text: {text}")
        print(f"Has emoji: {has_emoji}")
        print("-" * 50)