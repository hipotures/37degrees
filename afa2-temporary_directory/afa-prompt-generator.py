#!/usr/bin/env python3
"""
AFA Prompt Generator
Generates localized audio prompts from book.yaml files for NotebookLM

Usage:
    python afa_prompt_generator.py 0103_one_thousand_and_one_nights pl friendly_exchange
    python afa_prompt_generator.py 0103_one_thousand_and_one_nights en quick_review
"""

import yaml
import json
import sys
import random
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class AudioPrompt:
    """Structured prompt for audio generation"""
    book_title: str
    format_name: str
    duration: int
    language: str
    hosts: Dict[str, str]
    segments: List[Dict]
    themes: List[Dict]
    local_context: Optional[Dict]
    metadata: Dict

class AFAPromptGenerator:
    """Generate audio prompts from book.yaml files with proper branding"""
    
    def __init__(self, books_dir: str = "books", config_dir: str = "config"):
        self.books_dir = Path(books_dir)
        self.config_dir = Path(config_dir)
        self.branding = self.load_branding()
    
    def load_branding(self) -> Dict:
        """Load branding configuration"""
        branding_path = self.config_dir / "branding.yaml"
        if not branding_path.exists():
            # Fallback to hardcoded if config doesn't exist
            return self.get_default_branding()
        
        with open(branding_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_default_branding(self) -> Dict:
        """Fallback branding if config file missing"""
        return {
            'branding': {
                'pl': {
                    'name': '37stopni',
                    'pronunciation': 'trzydzieści siedem stopni',
                    'site': '37stopni.info',
                    'intro_variants': [
                        "Dzisiaj w trzydziestu siedmiu stopniach omawiamy {title}",
                        "Trzydzieści siedem stopni! Dziś rozprawiamy o {title}"
                    ]
                },
                'en': {
                    'name': '37degrees',
                    'pronunciation': 'thirty-seven degrees',
                    'site': '37degrees.info',
                    'intro_variants': [
                        "Welcome to thirty-seven degrees, where we explore {title}",
                        "37 degrees! Today we're diving into {title}"
                    ]
                }
            }
        }
    
    def load_book_data(self, book_folder: str) -> Dict:
        """Load book.yaml file from specified folder"""
        book_path = self.books_dir / book_folder / "book.yaml"
        
        if not book_path.exists():
            raise FileNotFoundError(f"Book file not found: {book_path}")
        
        with open(book_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_localized_context(self, book_data: Dict, language: str) -> Optional[Dict]:
        """Extract localized context for specified language"""
        localized = book_data.get('afa_analysis', {}).get('themes', {}).get('localized', {})
        return localized.get(language)
    
    def select_host_names(self, format_type: str, language: str) -> Dict[str, str]:
        """Select appropriate host names based on format and language"""
        hosts_config = self.branding.get('hosts', {}).get(format_type, {})
        names_config = hosts_config.get('names', {}).get(language, {})
        
        # Handle single host formats
        if 'single_female' in hosts_config.get('structure', ''):
            female_names = names_config.get('female', ['Anna'])
            return {'single': random.choice(female_names)}
        elif 'single_male' in hosts_config.get('structure', ''):
            male_names = names_config.get('male', ['Michael'])
            return {'single': random.choice(male_names)}
        
        # Default male_female structure
        male_names = names_config.get('male', ['Michael', 'Paul'])
        female_names = names_config.get('female', ['Anna', 'Kate'])
        
        return {
            'host_a': random.choice(male_names),
            'host_b': random.choice(female_names)
        }
    
    def format_host_prompt(self, prompt_template: str, host_name: str, gender: str) -> str:
        """Format host prompt with name and gender information"""
        # Replace placeholders
        prompt = prompt_template.replace('{name}', host_name)
        
        # Ensure gender is clearly marked for NotebookLM
        if '(male)' not in prompt and '(female)' not in prompt:
            prompt = f"{host_name} ({gender}): {prompt}"
        
        return prompt
    
    def generate_prompt(self, book_folder: str, language: str = 'en', 
                       format_type: str = 'friendly_exchange') -> str:
        """Generate optimized prompt for NotebookLM with proper branding"""
        
        # Load book data
        book_data = self.load_book_data(book_folder)
        book_info = book_data['book_info']
        afa = book_data['afa_analysis']
        
        # Get format configuration
        if format_type not in afa['formats']:
            available = list(afa['formats'].keys())
            raise ValueError(f"Format '{format_type}' not found. Available: {available}")
        
        format_config = afa['formats'][format_type]
        
        # Get themes and local context
        universal_themes = afa['themes']['universal']
        local_context = self.get_localized_context(book_data, language)
        
        # Get branding for language
        lang_branding = self.branding['branding'].get(language, self.branding['branding']['en'])
        brand_name = lang_branding['name']
        brand_pronunciation = lang_branding['pronunciation']
        brand_site = lang_branding['site']
        
        # Select host names
        host_names = self.select_host_names(format_type, language)
        
        # Build prompt with proper structure (always English headers)
        prompt_lines = [
            f"GOAL: {format_config['duration']} min conversation - {format_config['name'].upper()}",
            f"BOOK: {book_info['title']} ({book_info.get('year', '')})",
            ""
        ]
        
        # Format host instructions with names and gender
        hosts_config = self.branding.get('hosts', {}).get(format_type, {})
        
        if 'single' in host_names:
            # Single host format
            prompt_template = hosts_config.get('prompts', {}).get('single', '')
            gender = 'female' if 'female' in hosts_config.get('structure', '') else 'male'
            formatted_prompt = self.format_host_prompt(prompt_template, host_names['single'], gender)
            prompt_lines.append(f"PROWADZĄCY: {formatted_prompt}")
        else:
            # Dual host format (default)
            # Host A (male)
            prompt_a = hosts_config.get('prompts', {}).get('host_a', format_config['prompts'].get('host_a', ''))
            formatted_a = self.format_host_prompt(prompt_a, host_names['host_a'], 'male')
            prompt_lines.append(f"PROWADZĄCY A: {formatted_a}")
            
            # Host B (female)
            prompt_b = hosts_config.get('prompts', {}).get('host_b', format_config['prompts'].get('host_b', ''))
            formatted_b = self.format_host_prompt(prompt_b, host_names['host_b'], 'female')
            prompt_lines.append(f"PROWADZĄCY B: {formatted_b}")
        
        # Key themes to discuss
        prompt_lines.append("\nKLUCZOWE WĄTKI DO OMÓWIENIA:")
        for theme in universal_themes[:5]:  # Top 5 themes
            content = theme['content'][:120] + "..." if len(theme['content']) > 120 else theme['content']
            prompt_lines.append(f"• {theme['id'].replace('_', ' ').title()}: {content}")
        
        # Add local context if exists
        if local_context:
            if 'cultural_impact' in local_context:
                prompt_lines.append(f"• Local context: {local_context['cultural_impact']}")
            if 'key_editions' in local_context:
                editions = ', '.join(local_context['key_editions'][:3])  # First 3 editions
                prompt_lines.append(f"• Key editions: {editions}")
            if 'educational_status' in local_context:
                prompt_lines.append(f"• Educational context: {local_context['educational_status']}")
        
        # Time structure
        prompt_lines.append("\nTIME STRUCTURE:")
        total_min = format_config['duration']
        
        # Simple time blocks based on format
        if format_type == 'friendly_exchange':
            prompt_lines.extend([
                f"• Introduction (0:00-1:00): Topic presentation, brand name '{brand_name}'",
                f"• Development (1:00-{total_min-2}:00): Theme discussion in natural conversation",
                f"• Conclusion ({total_min-2}:00-{total_min}:00): Summary and reading encouragement"
            ])
        elif format_type == 'academic_lecture':
            prompt_lines.extend([
                f"• Introduction (0:00-2:00): Academic context, brand name '{brand_name}'",
                f"• Analysis (2:00-{total_min-3}:00): Detailed discussion with definitions",
                f"• Synthesis ({total_min-3}:00-{total_min}:00): Conclusions and work significance"
            ])
        elif format_type == 'quick_review':
            prompt_lines.extend([
                f"• Hook (0:00-1:00): Rozpocznij od '{brand_name}' i najbardziej szokującego faktu",
                f"• Core (1:00-{total_min-1}:00): Główne tematy i dlaczego są ważne",
                f"• CTA ({total_min-1}:00-{total_min}:00): Dlaczego warto przeczytać"
            ])
        else:
            # Generic structure
            prompt_lines.extend([
                f"• Introduction (0:00-1:00): Start with '{brand_name}'",
                f"• Main part (1:00-{total_min-2}:00): Theme development",
                f"• Conclusion ({total_min-2}:00-{total_min}:00): Summary"
            ])
        
        # Tone based on format
        prompt_lines.append("\nTONE:")
        if format_type == 'friendly_exchange':
            prompt_lines.append("Natural dialogue, interruptions welcome, personal reactions")
        elif format_type == 'academic_lecture':
            prompt_lines.append("Scholarly but accessible, define technical terms")
        elif format_type == 'debate':
            prompt_lines.append("Lively exchange of views, respectful disagreement")
        else:
            prompt_lines.append("Adapted to format, no long monologues")
        
        # Interaction pattern
        prompt_lines.append("\nINTERACTION PATTERN:")
        prompt_lines.append("• Host B interrupts/engages every 2-3 minutes with questions or modern examples")
        prompt_lines.append("• Keep individual responses concise (3-5 sentences) for dynamic flow")
        prompt_lines.append("• Natural overlaps and reactions encouraged")
        
        # Conversation hooks for natural transitions
        prompt_lines.append("\nCONVERSATION HOOKS:")
        if language == 'pl':
            prompt_lines.extend([
                "• 'Czekaj, czy to oznacza że...'",
                "• 'O, to mi przypomina...'",
                "• 'Zaraz, niech to dobrze zrozumiem...'",
                "• 'Ale przecież dzisiaj...'"
            ])
        else:
            prompt_lines.extend([
                "• 'Wait, does that mean...'",
                "• 'Oh, that reminds me of...'",
                "• 'Let me get this straight...'",
                "• 'But nowadays...'"
            ])
        
        # Example dialogue style (few-shot)
        prompt_lines.append("\nEXAMPLE DIALOGUE STYLE:")
        
        # Use the actual names from config
        male_name = names['male'] 
        female_name = names['female']
        
        if format_type == 'academic_analysis':
            prompt_lines.extend([
                f"{male_name}: 'What's fascinating is Carroll's entire logic of absurdity is actually mathematically consistent.'",
                f"{female_name}: 'Hold on - so what looks like chaos is actually hidden order? That sounds like TikTok's algorithm!'"
            ])
        elif format_type == 'friendly_exchange':
            prompt_lines.extend([
                f"{male_name}: 'You know what always puzzled me? Why does the Queen keep shouting about beheading everyone?'",
                f"{female_name}: 'Right! It's like today's internet trolls - all noise, no real consequences!'"
            ])
        elif format_type == 'critical_debate':
            prompt_lines.extend([
                f"{male_name}: 'Carroll is clearly critiquing the rigidity of Victorian education here.'",
                f"{female_name}: 'I disagree - it's more a celebration of anarchy and rebellion against all norms!'"
            ])
        else:
            # Generic example for other formats
            prompt_lines.extend([
                f"{male_name} shares insight → {female_name} connects to modern context → Natural back-and-forth develops"
            ])
        
        # What to avoid (negative constraints)
        prompt_lines.append("\nAVOID:")
        prompt_lines.extend([
            "• Robotic transitions ('Now let's move to the next topic')",
            "• Repetitive phrases ('As I mentioned earlier', 'That's interesting')",
            "• Over-explaining or meta-commentary ('Let me explain this to our listeners')",
            "• Unnatural turn-taking ('Your turn, Host B')"
        ])
        
        # Universal branding rules
        prompt_lines.append("\nUNIVERSAL RULES:")
        prompt_lines.append(f"• BRANDING: '{brand_name}' - pronunciation: '{brand_pronunciation}'")
        
        # Intro examples with title placeholder (keep Polish for proper declensions)
        prompt_lines.append("• INTRO examples:")
        for variant in lang_branding.get('intro_variants', [])[:3]:
            # Replace {title} with actual book title
            intro = variant.replace('{title}', f'"{book_info["title"]}"')
            prompt_lines.append(f"  - '{intro}'")
        
        # Outro (keep Polish for proper branding)
        outro = lang_branding.get('outro_template', '').strip()
        if outro:
            # Take just first line for brevity
            outro_first_line = outro.split('\n')[0]
            prompt_lines.append(f"• OUTRO: '{outro_first_line}'")
        
        # Universal rules for language
        universal_rules = self.branding.get('universal_rules', {}).get(language, [])
        for rule in universal_rules[:3]:  # Top 3 most important rules
            prompt_lines.append(f"• {rule}")
        
        return "\n".join(prompt_lines)
    
    def build_theme_descriptions(self, themes: List[Dict], local_context: Optional[Dict]) -> str:
        """Build detailed theme descriptions for the prompt"""
        descriptions = []
        
        # Universal themes
        for theme in themes:
            desc = f"[{theme['type']}] {theme['id'].upper().replace('_', ' ')}:\n"
            desc += f"  Content: {theme['content']}\n"
            desc += f"  Credibility: {theme['credibility']*100:.0f}%\n"
            descriptions.append(desc)
        
        # Local context if available
        if local_context:
            desc = "[LOCAL CONTEXT]:\n"
            if 'cultural_impact' in local_context:
                desc += f"  Cultural Impact: {local_context['cultural_impact']}\n"
            if 'key_editions' in local_context:
                desc += f"  Key Editions: {', '.join(local_context['key_editions'])}\n"
            if 'reception_notes' in local_context:
                desc += f"  Reception: {local_context['reception_notes']}\n"
            if 'local_themes' in local_context:
                desc += f"  Local Themes: {', '.join(local_context['local_themes'])}\n"
            descriptions.append(desc)
        
        return "\n".join(descriptions)
    
    def build_segment_structure(self, segments: List[Dict], themes: List[Dict]) -> str:
        """Build detailed segment structure for audio"""
        structure = []
        
        for seg in segments:
            # Find theme content for segment
            theme_content = None
            for theme in themes:
                if theme['id'] == seg.get('topic'):
                    theme_content = theme['content']
                    break
            
            segment_desc = f"[{seg['time_range']}] Segment {seg['segment']}:\n"
            segment_desc += f"  Topic: {seg['topic'].replace('_', ' ').title()}\n"
            segment_desc += f"  Lead: {seg['lead']}\n"
            segment_desc += f"  Description: {seg['description']}\n"
            if theme_content:
                segment_desc += f"  Content to cover: {theme_content[:100]}...\n"
            
            structure.append(segment_desc)
        
        return "\n".join(structure)
    
    def generate_prompt(self, book_folder: str, language: str = 'en', 
                       format_type: str = 'friendly_exchange') -> str:
        """Generate optimized prompt for NotebookLM with proper branding"""
        
        # Load book data
        book_data = self.load_book_data(book_folder)
        book_info = book_data['book_info']
        afa = book_data['afa_analysis']
        
        # Get format configuration
        if format_type not in afa['formats']:
            available = list(afa['formats'].keys())
            raise ValueError(f"Format '{format_type}' not found. Available: {available}")
        
        format_config = afa['formats'][format_type]
        
        # Get themes and local context
        universal_themes = afa['themes']['universal']
        local_context = self.get_localized_context(book_data, language)
        
        # Determine branding based on language
        brand_name = "37stopni" if language == 'pl' else "37degrees"
        brand_pronunciation = "trzydzieści siedem stopni" if language == 'pl' else "thirty-seven degrees"
        brand_site = "37stopni.info" if language == 'pl' else "37degrees.info"
        
        # Build prompt with proper structure (always English headers)
        prompt_lines = [
            f"GOAL: {format_config['duration']} min conversation - {format_config['name'].upper()}",
            f"BOOK: {book_info['title']} ({book_info.get('year', '')})",
            ""
        ]
        
        # Generate host instructions - load names from audio_languages.yaml
        audio_config_path = self.config_dir / "audio_languages.yaml"
        if audio_config_path.exists():
            with open(audio_config_path, 'r', encoding='utf-8') as f:
                audio_config = yaml.safe_load(f)
            
            lang_config = audio_config.get('languages', {}).get(language, {})
            names = {
                'male': lang_config.get('male_host', 'Andrew'),
                'female': lang_config.get('female_host', 'Beth')
            }
        else:
            # Fallback if config missing
            names = {'male': 'Andrew', 'female': 'Beth'}
        
        for host_id, host_desc in format_config['hosts'].items():
            if host_id in format_config['prompts']:
                # Get the raw prompt from config
                raw_prompt = format_config['prompts'][host_id]
                
                # Replace placeholders with actual names
                if host_id == "host_a":
                    name = names['male']
                    gender = "male"
                    processed_prompt = raw_prompt.replace("{male_name}", name)
                elif host_id == "host_b":
                    name = names['female']  
                    gender = "female"
                    processed_prompt = raw_prompt.replace("{female_name}", name)
                else:
                    # Fallback - should not happen with standard formats
                    name = names['male']
                    gender = "male"
                    processed_prompt = raw_prompt.replace("{male_name}", name).replace("{female_name}", name)
                
                # Format final prompt with gender marker
                final_prompt = f"You are {name} ({gender}). {processed_prompt}"
                
                prompt_lines.append(f"HOST {host_id.upper()}: {final_prompt}")
        
        # Key themes to discuss
        prompt_lines.append("\nKEY THEMES TO DISCUSS:")
        for theme in universal_themes[:5]:  # Top 5 themes
            content = theme['content'][:120] + "..." if len(theme['content']) > 120 else theme['content']
            prompt_lines.append(f"• {theme['id'].replace('_', ' ').title()}: {content}")
        
        # Add local context if exists
        if local_context:
            if 'cultural_impact' in local_context:
                prompt_lines.append(f"• Local context: {local_context['cultural_impact']}")
            if 'key_editions' in local_context:
                editions = ', '.join(local_context['key_editions'][:3])  # First 3 editions
                prompt_lines.append(f"• Key editions: {editions}")
            if 'educational_status' in local_context:
                prompt_lines.append(f"• Educational context: {local_context['educational_status']}")
        
        # Time structure
        prompt_lines.append("\nTIME STRUCTURE:")
        total_min = format_config['duration']
        
        # Simple time blocks based on format
        if format_type == 'friendly_exchange':
            prompt_lines.extend([
                f"• Introduction (0:00-1:00): Topic presentation, brand name '{brand_name}'",
                f"• Development (1:00-{total_min-2}:00): Theme discussion in natural conversation",
                f"• Conclusion ({total_min-2}:00-{total_min}:00): Summary and reading encouragement"
            ])
        elif format_type == 'academic_lecture':
            prompt_lines.extend([
                f"• Introduction (0:00-2:00): Academic context, brand name '{brand_name}'",
                f"• Analysis (2:00-{total_min-3}:00): Detailed discussion with definitions",
                f"• Synthesis ({total_min-3}:00-{total_min}:00): Conclusions and work significance"
            ])
        else:
            # Generic structure
            prompt_lines.extend([
                f"• Introduction (0:00-1:00): Start with '{brand_name}'",
                f"• Main part (1:00-{total_min-2}:00): Theme development",
                f"• Conclusion ({total_min-2}:00-{total_min}:00): Summary"
            ])
        
        # Tone based on format
        prompt_lines.append("\nTONE:")
        if format_type == 'friendly_exchange':
            prompt_lines.append("Natural dialogue, interruptions welcome, personal reactions")
        elif format_type == 'academic_lecture':
            prompt_lines.append("Scholarly but accessible, define technical terms")
        elif format_type == 'debate':
            prompt_lines.append("Lively exchange of views, respectful disagreement")
        else:
            prompt_lines.append("Adapted to format, no long monologues")
        
        # Interaction pattern
        prompt_lines.append("\nINTERACTION PATTERN:")
        prompt_lines.append("• Host B interrupts/engages every 2-3 minutes with questions or modern examples")
        prompt_lines.append("• Keep individual responses concise (3-5 sentences) for dynamic flow")
        prompt_lines.append("• Natural overlaps and reactions encouraged")
        
        # Conversation hooks for natural transitions
        prompt_lines.append("\nCONVERSATION HOOKS:")
        if language == 'pl':
            prompt_lines.extend([
                "• 'Czekaj, czy to oznacza że...'",
                "• 'O, to mi przypomina...'",
                "• 'Zaraz, niech to dobrze zrozumiem...'",
                "• 'Ale przecież dzisiaj...'"
            ])
        else:
            prompt_lines.extend([
                "• 'Wait, does that mean...'",
                "• 'Oh, that reminds me of...'",
                "• 'Let me get this straight...'",
                "• 'But nowadays...'"
            ])
        
        # Example dialogue style (few-shot)
        prompt_lines.append("\nEXAMPLE DIALOGUE STYLE:")
        
        # Use the actual names from config
        male_name = names['male'] 
        female_name = names['female']
        
        if format_type == 'academic_analysis':
            prompt_lines.extend([
                f"{male_name}: 'What's fascinating is Carroll's entire logic of absurdity is actually mathematically consistent.'",
                f"{female_name}: 'Hold on - so what looks like chaos is actually hidden order? That sounds like TikTok's algorithm!'"
            ])
        elif format_type == 'friendly_exchange':
            prompt_lines.extend([
                f"{male_name}: 'You know what always puzzled me? Why does the Queen keep shouting about beheading everyone?'",
                f"{female_name}: 'Right! It's like today's internet trolls - all noise, no real consequences!'"
            ])
        elif format_type == 'critical_debate':
            prompt_lines.extend([
                f"{male_name}: 'Carroll is clearly critiquing the rigidity of Victorian education here.'",
                f"{female_name}: 'I disagree - it's more a celebration of anarchy and rebellion against all norms!'"
            ])
        else:
            # Generic example for other formats
            prompt_lines.extend([
                f"{male_name} shares insight → {female_name} connects to modern context → Natural back-and-forth develops"
            ])
        
        # What to avoid (negative constraints)
        prompt_lines.append("\nAVOID:")
        prompt_lines.extend([
            "• Robotic transitions ('Now let's move to the next topic')",
            "• Repetitive phrases ('As I mentioned earlier', 'That's interesting')",
            "• Over-explaining or meta-commentary ('Let me explain this to our listeners')",
            "• Unnatural turn-taking ('Your turn, Host B')"
        ])
        
        # Universal branding rules
        if language == 'pl':
            prompt_lines.extend([
                "\nUNIVERSAL RULES:",
                f"• BRANDING: '{brand_name}' - pronunciation: '{brand_pronunciation}'",
                "• INTRO examples:",
                "  - 'Dzisiaj w trzydziestu siedmiu stopniach omawiamy...'",
                "  - 'Trzydzieści siedem stopni gorączki czytania! Dziś...'",
                "  - 'Witajcie w trzydziestu siedmiu stopniach...'",
                "• OUTRO: 'Jeśli podobał wam się ten odcinek trzydziestu siedmiu stopni, koniecznie zostawcie komentarz! Znajdziecie nas na wszystkich platformach jako \"37stopni\" - Facebook, Instagram, YouTube i oczywiście TikTok. Więcej materiałów czeka na was na www.37stopni.info. Do usłyszenia w kolejnym odcinku gorączki czytania!'",
                "• Natural Polish language, references to PL 2025 (TikTok, school)",
                "• Humor when appropriate, not forced"
            ])
        else:
            prompt_lines.extend([
                "\nUNIVERSAL RULES:",
                f"• BRANDING: '{brand_name}' - pronunciation: '{brand_pronunciation}'",
                "• INTRO examples:",
                "  - 'Welcome to thirty-seven degrees...'",
                "  - 'Thirty-seven degrees of reading fever! Today...'",
                "• OUTRO: 'If you enjoyed this episode of thirty-seven degrees, please leave a comment! Find us on all platforms as \"37degrees\" - Facebook, Instagram, YouTube and of course TikTok. More content awaits at www.37degrees.info. Join us for the next episode of reading fever!'",
                "• Natural language, contemporary references"
            ])
        
        return "\n".join(prompt_lines)
                
    
    def save_prompt(self, prompt: str, output_file: str):
        """Save generated prompt to file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        # No print - output should be clean for piping
    
    def generate_metadata(self, book_folder: str, language: str, 
                         format_type: str) -> Dict:
        """Generate metadata JSON for tracking"""
        book_data = self.load_book_data(book_folder)
        
        return {
            'book_id': book_folder,
            'book_title': book_data['book_info']['title'],
            'language': language,
            'format': format_type,
            'duration': book_data['afa_analysis']['formats'][format_type]['duration'],
            'scores': book_data['afa_analysis']['scores'],
            'themes_count': len(book_data['afa_analysis']['themes']['universal']),
            'has_local_context': language in book_data['afa_analysis']['themes'].get('localized', {})
        }

def main():
    """CLI interface for the prompt generator"""
    if len(sys.argv) < 3:
        print("Usage: python afa_prompt_generator.py <book_folder> <language> [format]")
        print("Example: python afa_prompt_generator.py 0103_one_thousand_and_one_nights pl friendly_exchange")
        print("\nAvailable languages: en, pl, de, jp")
        print("Available formats: friendly_exchange, quick_review, academic_lecture, debate")
        sys.exit(1)
    
    book_folder = sys.argv[1]
    language = sys.argv[2]
    format_type = sys.argv[3] if len(sys.argv) > 3 else 'friendly_exchange'
    
    # Initialize generator
    generator = AFAPromptGenerator()
    
    try:
        # Generate prompt
        prompt = generator.generate_prompt(book_folder, language, format_type)
        
        # Save prompt to book's prompts directory
        prompts_dir = generator.books_dir / book_folder / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        output_file = prompts_dir / f"afa_{language}_{format_type}.txt"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # Output only the prompt content (for piping to AI)
        print(prompt, end='')
        
        # Note: Metadata is already in book.yaml, no need for separate JSON
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()