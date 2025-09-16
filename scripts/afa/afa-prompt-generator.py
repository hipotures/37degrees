#!/usr/bin/env python3
"""
AFA Prompt Generator
Generates localized audio prompts from book.yaml files for NotebookLM

Usage:
    python afa_prompt_generator.py 0103_one_thousand_and_one_nights pl friendly_exchange
    python afa_prompt_generator.py 0103_one_thousand_and_one_nights en quick_review
"""

import copy
import importlib.util
import json
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

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
        self.format_templates = self.load_format_templates()
    
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
        entry = localized.get(language)
        return entry if isinstance(entry, dict) else None

    def load_format_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load format templates from afa_format_selector for non-legacy data"""
        selector_path = Path(__file__).resolve().parents[1] / "afa_format_selector.py"
        if not selector_path.exists():
            return {}

        spec = importlib.util.spec_from_file_location("afa_format_selector_templates", selector_path)
        if spec is None or spec.loader is None:
            return {}

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "FORMAT_TEMPLATES", {}).copy()

    def build_format_from_template(self, format_name: str, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Build full prompt configuration using stored templates"""
        if format_name not in self.format_templates:
            raise ValueError(
                f"Format '{format_name}' has no template definition."
            )

        config = copy.deepcopy(self.format_templates[format_name])
        config['name'] = format_name
        # Allow duration override if provided in book.yaml metadata
        if 'duration' in meta:
            config['duration'] = meta['duration']
        config['confidence'] = meta.get('confidence')
        config['reasoning'] = meta.get('reasoning')
        return config
    
    def get_conversation_hooks(self, format_type: str, language: str) -> List[str]:
        """Get format-specific conversation hooks for natural transitions"""

        hooks_map = {
            'emotional_perspective': {
                'pl': [
                    "'Moment, to bardzo ważne...'",
                    "'To mnie głęboko porusza...'",
                    "'Czuję, że to rezonuje z...'",
                    "'Pozwól, że się tym podzielę...'"
                ],
                'en': [
                    "'This really touches me...'",
                    "'I feel this deeply resonates...'",
                    "'That's so important to recognize...'",
                    "'Let me share something personal...'"
                ]
            },
            'academic_analysis': {
                'pl': [
                    "'Panie profesorze, czy to oznacza...'",
                    "'Przepraszam, czy mógłby Pan rozwinąć...'",
                    "'To nawiązuje do teorii, którą...'",
                    "'Czy to sugeruje, że...'"
                ],
                'en': [
                    "'Professor, does this suggest...'",
                    "'Could you elaborate on...'",
                    "'This connects to the theory that...'",
                    "'If I understand correctly...'"
                ]
            },
            'critical_debate': {
                'pl': [
                    "'Nie zgadzam się z tym podejściem...'",
                    "'Moment, to założenie jest błędne...'",
                    "'Ależ to przeczy interpretacji...'",
                    "'Czy nie uważasz, że...'"
                ],
                'en': [
                    "'I disagree with that approach...'",
                    "'Wait, that assumption is flawed...'",
                    "'But that contradicts the interpretation...'",
                    "'Don\\'t you think that...'"
                ]
            },
            'temporal_context': {
                'pl': [
                    "'W tamtych czasach to wyglądało...'",
                    "'Porównując z dzisiejszymi...'",
                    "'Historia pokazuje nam, że...'",
                    "'Wówczas społeczność...'"
                ],
                'en': [
                    "'Back then it looked like...'",
                    "'Comparing with today\\'s...'",
                    "'History shows us that...'",
                    "'At that time society...'"
                ]
            },
            'cultural_dimension': {
                'pl': [
                    "'W różnych kulturach to...'",
                    "'Ciekawe, jak to odbierają...'",
                    "'Z perspektywy różnych społeczności...'",
                    "'To uniwersalne, czy kulturowe...'"
                ],
                'en': [
                    "'In different cultures this...'",
                    "'Interesting how they perceive...'",
                    "'From various communities\\' perspective...'",
                    "'Is this universal or cultural...'"
                ]
            },
            'social_perspective': {
                'pl': [
                    "'Społecznie to oznacza...'",
                    "'W dzisiejszych realiach...'",
                    "'To ma wpływ na nasze...'",
                    "'Jak to przekłada się na...'"
                ],
                'en': [
                    "'Socially this means...'",
                    "'In today\\'s reality...'",
                    "'This impacts our...'",
                    "'How does this translate to...'"
                ]
            },
            'exploratory_dialogue': {
                'pl': [
                    "'A gdyby spojrzeć na to...'",
                    "'Może warto zbadać...'",
                    "'Ciekawe, co by było gdyby...'",
                    "'Odkrywamy tu coś fascynującego...'"
                ],
                'en': [
                    "'What if we looked at this...'",
                    "'Maybe it\\'s worth exploring...'",
                    "'I wonder what would happen if...'",
                    "'We\\'re discovering something fascinating...'"
                ]
            },
            'narrative_reconstruction': {
                'pl': [
                    "'Wyobraź sobie scenę...'",
                    "'W tym momencie bohater...'",
                    "'Napięcie narasta, gdy...'",
                    "'Czytelnik czuje, że...'"
                ],
                'en': [
                    "'Imagine the scene...'",
                    "'At this moment the character...'",
                    "'Tension builds when...'",
                    "'The reader feels that...'"
                ]
            },
            'friendly_exchange': {
                'pl': [
                    "'Czekaj, czekaj...'",
                    "'O, kurczę, nie pomyślałem...'",
                    "'Ale wiesz co, to mi przypomina...'",
                    "'Hej, czy ty też...'"
                ],
                'en': [
                    "'Wait, wait...'",
                    "'Oh man, I didn\\'t think...'",
                    "'But you know what, this reminds me...'",
                    "'Hey, do you also...'"
                ]
            }
        }

        # Default to English if language not found
        lang = language if language in ['pl', 'en'] else 'en'

        # Get hooks for format, fallback to friendly_exchange if format not found
        return hooks_map.get(format_type, hooks_map['friendly_exchange']).get(lang, hooks_map['friendly_exchange']['en'])

    def get_format_tone(self, format_type: str, language: str) -> str:
        """Get format-specific tone description - always in English for AI instructions"""

        tone_map = {
            'emotional_perspective': "Empathetic, supportive, gentle but honest, therapeutic",
            'academic_analysis': "Formal but accessible, respect for hierarchy, precise, scholarly",
            'critical_debate': "Analytical, confident, constructively critical, intellectual",
            'temporal_context': "Reflective, historical, comparative, contemplative",
            'cultural_dimension': "Culturally open, curious, multi-perspective, tolerant",
            'social_perspective': "Socially conscious, engaged, contemporary, activist",
            'exploratory_dialogue': "Exploratory, spontaneous, hypothesizing, experimental",
            'narrative_reconstruction': "Narrative, immersive, tension-building, theatrical",
            'friendly_exchange': "Natural, casual, enthusiastic, friendly"
        }

        # Always return English - this is AI instruction, not user content
        return tone_map.get(format_type, tone_map['friendly_exchange'])

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
        afa = book_data.get('afa_analysis')
        if not afa:
            raise ValueError(
                f"book.yaml for {book_folder} is missing required 'afa_analysis' section"
            )
        
        formats_section = afa.get('formats', {})
        if not isinstance(formats_section, dict):
            raise ValueError("Invalid format structure in book.yaml")

        format_config: Dict[str, Any]
        if format_type in formats_section and isinstance(formats_section[format_type], dict):
            # Legacy structure preserved in book.yaml
            format_config = copy.deepcopy(formats_section[format_type])
            format_config.setdefault('name', format_type)
        elif formats_section.get('name') == format_type:
            format_config = self.build_format_from_template(format_type, formats_section)
        else:
            available = []
            if 'name' in formats_section and isinstance(formats_section['name'], str):
                available.append(formats_section['name'])
            else:
                available.extend([key for key, value in formats_section.items() if isinstance(value, dict)])
            raise ValueError(f"Format '{format_type}' not found. Available: {available}")

        # Get themes and local context
        themes_section = afa.get('themes', {})
        universal_themes = themes_section.get('universal', [])
        localized_entry = themes_section.get('localized', {}).get(language)
        local_context = localized_entry if isinstance(localized_entry, dict) else None
        processed_local_context = False
        localized_themes = localized_entry if isinstance(localized_entry, list) else []
        
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
            f"BOOK: {book_info['title']} by {book_info.get('author', 'Unknown')} ({book_info.get('year', '')})",
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
            # Handle both old and new theme structure
            if 'content' in theme:
                raw_content = theme['content']
                theme_id = theme['id'].replace('_', ' ').title()
            else:
                raw_content = theme['description']
                theme_id = theme['title']

            # Use full content - no truncation
            content = raw_content
            prompt_lines.append(f"• {theme_id}: {content}")
        
        # Add local context if exists
        if local_context:
            if 'cultural_impact' in local_context:
                prompt_lines.append(f"• Local context: {local_context['cultural_impact']}")
            if 'key_editions' in local_context:
                editions = ', '.join(local_context['key_editions'][:3])  # First 3 editions
                prompt_lines.append(f"• Key editions: {editions}")
            if 'educational_status' in local_context:
                prompt_lines.append(f"• Educational context: {local_context['educational_status']}")
        
        # Conversation flow structure
        prompt_lines.append("\nCONVERSATION FLOW:")
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
            # Use actual structure from YAML if available
            if 'structure' in format_config and format_config['structure']:
                for segment in format_config['structure']:
                    topic = segment['topic'].replace('_', ' ').title()
                    description = segment['description']
                    lead_host = "Host A" if segment['lead'] == 'host_a' else "Host B"
                    prompt_lines.append(f"• {topic} ({lead_host} leads): {description}")
            else:
                # Generic structure fallback
                prompt_lines.extend([
                    f"• Introduction: Start with '{brand_name}'",
                    f"• Main discussion: Theme development",
                    f"• Conclusion: Summary and encouragement"
                ])
        
        # Tone based on format
        # Format-specific tone
        prompt_lines.append("\nTONE:")
        tone = self.get_format_tone(format_type, language)
        prompt_lines.append(tone)
        
        # Interaction pattern
        prompt_lines.append("\nINTERACTION PATTERN:")
        prompt_lines.append("• Host B interrupts/engages every 2-3 minutes with questions or modern examples")
        prompt_lines.append("• Keep individual responses concise (3-5 sentences) for dynamic flow")
        prompt_lines.append("• Natural overlaps and reactions encouraged")
        
        # Format-specific conversation hooks
        prompt_lines.append("\nCONVERSATION HOOKS:")
        hooks = self.get_conversation_hooks(format_type, language)
        for hook in hooks:
            prompt_lines.append(f"• {hook}")
        
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
            theme_type = theme.get('type', 'ANALYSIS')
            theme_id = theme.get('id', theme.get('key', '')).upper().replace('_', ' ')
            desc = f"[{theme_type}] {theme_id}:\n"
            desc += f"  Content: {theme.get('content', theme.get('description', ''))}\n"
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
                if theme.get('id', theme.get('key', '')) == seg.get('topic'):
                    theme_content = theme.get('content', theme.get('description', ''))
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
        afa = book_data.get('afa_analysis')
        if not afa:
            raise ValueError(
                f"book.yaml for {book_folder} is missing required 'afa_analysis' section"
            )
        
        formats_section = afa.get('formats', {})
        if not isinstance(formats_section, dict):
            raise ValueError("Invalid format structure in book.yaml")

        if format_type in formats_section and isinstance(formats_section[format_type], dict):
            format_config = copy.deepcopy(formats_section[format_type])
            format_config.setdefault('name', format_type)
        elif formats_section.get('name') == format_type:
            format_config = self.build_format_from_template(format_type, formats_section)
        else:
            available = []
            if 'name' in formats_section and isinstance(formats_section['name'], str):
                available.append(formats_section['name'])
            else:
                available.extend([key for key, value in formats_section.items() if isinstance(value, dict)])
            raise ValueError(f"Format '{format_type}' not found. Available: {available}")

        themes_section = afa.get('themes', {})
        universal_themes = themes_section.get('universal', [])
        localized_entry = themes_section.get('localized', {}).get(language)
        local_context = localized_entry if isinstance(localized_entry, dict) else None
        processed_local_context = False
        localized_themes = localized_entry if isinstance(localized_entry, list) else []

        lang_branding = self.branding['branding'].get(language, self.branding['branding']['en'])
        brand_name = lang_branding['name']
        brand_pronunciation = lang_branding['pronunciation']
        brand_site = lang_branding['site']
        
        # Build prompt with proper structure (always English headers)
        prompt_lines = [
            f"GOAL: {format_config['duration']} min conversation - {format_config['name'].upper()}",
            f"BOOK: {book_info['title']} by {book_info.get('author', 'Unknown')} ({book_info.get('year', '')})",
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
                
                processed_prompt = processed_prompt.replace("{book_title}", book_info['title'])

                # Format final prompt - processed_prompt already contains "You are {name}"
                final_prompt = f"{name} ({gender}). {processed_prompt}"

                prompt_lines.append(f"HOST {host_id.upper()}: {final_prompt}")
        
        # Key themes to discuss - all themes in one section
        prompt_lines.append("\nKEY THEMES TO DISCUSS:")

        # All universal themes (not just 5)
        for theme in universal_themes:
            # Handle both old and new theme structure
            if 'content' in theme:
                raw_content = theme['content']
                theme_id = theme['id'].replace('_', ' ').title()
            else:
                raw_content = theme['description']
                theme_id = theme['title']

            # Use full content - no truncation
            content = raw_content
            prompt_lines.append(f"• {theme_id}: {content}")

        # Add localized themes for the specific language (same section)
        if localized_themes:
            for theme in localized_themes:
                if isinstance(theme, dict):
                    theme_title = theme.get('title', theme.get('key', '').replace('_', ' ').title())
                    theme_desc = theme.get('description', theme.get('content', ''))
                    prompt_lines.append(f"• {theme_title}: {theme_desc}")
                else:
                    prompt_lines.append(f"• {theme}")
        elif local_context:
            # Handle dictionary-based localized context
            for key, value in local_context.items():
                if value in (None, ''):
                    continue
                readable_key = key.replace('_', ' ').title()
                if isinstance(value, list):
                    value_text = ', '.join(value)
                else:
                    value_text = value
                prompt_lines.append(f"• {readable_key}: {value_text}")
            processed_local_context = True

        # Legacy local context (if still exists)
        if local_context and not processed_local_context:
            if 'cultural_impact' in local_context:
                prompt_lines.append(f"• Additional context: {local_context['cultural_impact']}")
            if 'educational_status' in local_context:
                prompt_lines.append(f"• Educational context: {local_context['educational_status']}")
        
        # Conversation flow structure
        prompt_lines.append("\nCONVERSATION FLOW:")
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
            # Use actual structure from YAML if available
            if 'structure' in format_config and format_config['structure']:
                for segment in format_config['structure']:
                    topic = segment['topic'].replace('_', ' ').title()
                    description = segment['description']
                    lead_host = "Host A" if segment['lead'] == 'host_a' else "Host B"
                    prompt_lines.append(f"• {topic} ({lead_host} leads): {description}")
            else:
                # Generic structure fallback
                prompt_lines.extend([
                    f"• Introduction: Start with '{brand_name}'",
                    f"• Main discussion: Theme development",
                    f"• Conclusion: Summary and encouragement"
                ])
        
        # Tone based on format
        # Format-specific tone
        prompt_lines.append("\nTONE:")
        tone = self.get_format_tone(format_type, language)
        prompt_lines.append(tone)
        
        # Interaction pattern
        prompt_lines.append("\nINTERACTION PATTERN:")
        prompt_lines.append("• Host B interrupts/engages every 2-3 minutes with questions or modern examples")
        prompt_lines.append("• Keep individual responses concise (3-5 sentences) for dynamic flow")
        prompt_lines.append("• Natural overlaps and reactions encouraged")
        
        # Format-specific conversation hooks
        prompt_lines.append("\nCONVERSATION HOOKS:")
        hooks = self.get_conversation_hooks(format_type, language)
        for hook in hooks:
            prompt_lines.append(f"• {hook}")
        
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
        formats_section = book_data.get('afa_analysis', {}).get('formats', {})
        duration = None
        if isinstance(formats_section, dict):
            if format_type in formats_section and isinstance(formats_section[format_type], dict):
                duration = formats_section[format_type].get('duration')
            elif formats_section.get('name') == format_type:
                duration = formats_section.get('duration')

        if duration is None:
            duration = self.format_templates.get(format_type, {}).get('duration', 15)

        themes_section = book_data.get('afa_analysis', {}).get('themes', {})
        localized = themes_section.get('localized', {})

        return {
            'book_id': book_folder,
            'book_title': book_data['book_info']['title'],
            'language': language,
            'format': format_type,
            'duration': duration,
            'scores': book_data['afa_analysis']['scores'],
            'themes_count': len(themes_section.get('universal', [])),
            'has_local_context': language in localized
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
    
    # Initialize generator
    generator = AFAPromptGenerator()
    
    # Auto-select format from book.yaml if not provided
    if len(sys.argv) > 3:
        format_type = sys.argv[3]
    else:
        # Load book data to get format
        try:
            book_data = generator.load_book_data(book_folder)
            formats_section = book_data.get('afa_analysis', {}).get('formats')
            if not isinstance(formats_section, dict):
                print(f"Error: Invalid formats section in book.yaml for {book_folder}", file=sys.stderr)
                sys.exit(1)

            if 'name' in formats_section and isinstance(formats_section['name'], str):
                format_type = formats_section['name']
            else:
                available_formats = [key for key, value in formats_section.items() if isinstance(value, dict)]
                if not available_formats:
                    print(f"Error: No formats found in book.yaml for {book_folder}", file=sys.stderr)
                    sys.exit(1)
                format_type = available_formats[0]
        except Exception as e:
            print(f"Error loading book data: {e}", file=sys.stderr)
            sys.exit(1)
    
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
        
        # Copy to clipboard for easy pasting
        try:
            import subprocess
            # Use xsel with --input flag to properly set clipboard
            subprocess.run(['xsel', '--clipboard', '--input'], 
                          input=prompt, text=True, check=True, timeout=2)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass  # Don't block execution if clipboard fails
        
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
