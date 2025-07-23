#!/usr/bin/env python3
"""
Builds prompts for AI image generation based on book scene descriptions
Shows EXACTLY what will be sent to the AI, including negative prompts
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional


class PromptBuilder:
    def __init__(self, book_yaml_path: str):
        """Initialize with book YAML configuration"""
        self.book_path = Path(book_yaml_path)
        with open(self.book_path, 'r', encoding='utf-8') as f:
            self.book_data = yaml.safe_load(f)
        
        # Load InvokeAI style presets
        self.style_presets = self._load_invokeai_style_presets()
    
    def build_scene_prompt(self, slide_index: int) -> str:
        """Build COMPLETE prompt for a specific scene as it will be sent to AI"""
        if slide_index < 0 or slide_index >= len(self.book_data['slides']):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = self.book_data['slides'][slide_index]
        scene = slide['scene']
        custom_art_style = self.book_data.get('custom_art_style', {})
        template_art_style = self.book_data.get('template_art_style', '')
        ai_generation = self.book_data.get('ai_generation', {})
        tech_specs = self.book_data.get('technical_specs', {})
        
        # Build the COMPLETE prompts
        positive_prompt = self._build_full_positive_prompt(slide, custom_art_style, template_art_style)
        negative_prompt = self._build_full_negative_prompt(custom_art_style, template_art_style)
        
        # Build COMPLETE prompt data showing EVERYTHING sent to AI
        prompt_data = {
            'positive_prompt': positive_prompt,
            'negative_prompt': negative_prompt,
            'resolution': tech_specs.get('resolution', '1080x1920'),
            'model': ai_generation.get('model_name', 'Dreamshaper XL v2 Turbo'),
            'model_key': ai_generation.get('model_key', 'c81f2f9b-cabd-40ec-b6f4-d3172c10bafc'),
            'steps': ai_generation.get('steps', 30),
            'cfg_scale': ai_generation.get('cfg_scale', 7.5),
            'sampler': ai_generation.get('sampler', 'euler_a'),
            'template_used': template_art_style if template_art_style and template_art_style not in ['', '-'] else 'custom'
        }
        
        return yaml.dump(prompt_data, 
                        default_flow_style=False, 
                        allow_unicode=True,
                        sort_keys=False,
                        width=200)  # Wide to accommodate long prompts
    
    def _build_full_positive_prompt(self, slide: Dict, custom_art_style: Dict, template_art_style: str) -> str:
        """Build the COMPLETE positive prompt as sent to AI"""
        scene = slide.get('scene', {})
        
        if template_art_style and template_art_style not in ['', '-']:
            # Using template style from loaded presets
            if template_art_style in self.style_presets:
                template = self.style_presets[template_art_style].get('positive_prompt', '{prompt}')
                scene_elements = self._build_scene_elements(scene)
                return template.replace('{prompt}', scene_elements)
            else:
                # Unknown template - show available
                print(f"Warning: Template '{template_art_style}' not found!")
                print(f"Available templates: {', '.join(sorted(self.style_presets.keys()))}")
                return f"[TEMPLATE NOT FOUND: {template_art_style}] {self._build_scene_elements(scene)}"
        else:
            # Using custom art style - build FULL prompt
            prompt_parts = []
            
            # 1. Primary style directive
            prompt_parts.append(custom_art_style.get('primary_style', 'illustration'))
            
            # 2. Complexity
            prompt_parts.append(f"style of {custom_art_style.get('complexity', 'simple artwork')}")
            
            # 3. Scene elements
            scene_elements = self._build_scene_elements(scene)
            if scene_elements:
                prompt_parts.append(scene_elements)
            
            # 4. Color palette
            color_palette = custom_art_style.get('color_palette', {})
            if color_palette.get('base'):
                colors = ", ".join(color_palette['base'][:3])
                prompt_parts.append(f"color palette: {colors}")
            
            # 5. Technical requirements
            prompt_parts.extend([
                "vertical composition",
                "clear space in upper third for text overlay",
                custom_art_style.get('line_work', 'clean lines'),
                custom_art_style.get('color_technique', 'flat colors'),
                custom_art_style.get('overall_feeling', 'whimsical')
            ])
            
            return ", ".join(prompt_parts)
    
    def _build_scene_elements(self, scene: Dict) -> str:
        """Build scene-specific elements"""
        scene_parts = []
        
        # Elements
        elements = scene.get('elements', [])
        if elements:
            scene_parts.append(", ".join(elements))
        
        # Composition
        if scene.get('composition'):
            scene_parts.append(f"composition: {scene['composition']}")
        
        # Atmosphere/mood
        if scene.get('atmosphere'):
            scene_parts.append(f"{scene['atmosphere']} mood")
        
        # Background
        if scene.get('background'):
            scene_parts.append(f"background: {scene['background']}")
            
        return ", ".join(scene_parts)
    
    def _build_full_negative_prompt(self, custom_art_style: Dict, template_art_style: str) -> str:
        """Build the COMPLETE negative prompt as sent to AI"""
        if template_art_style and template_art_style not in ['', '-']:
            # Template styles have their own negatives
            if template_art_style in self.style_presets:
                return self.style_presets[template_art_style].get('negative_prompt', 'text, watermark')
            else:
                return "text, watermark"  # Default for unknown templates
        else:
            # Using custom style negative prompt
            negative_parts = [
                "text", "letters", "words", "typography", "writing",
                "watermark", "signature", "logo"
            ]
            
            # Add style-specific negatives from 'avoid' field
            avoid = custom_art_style.get('avoid', '')
            if avoid:
                negative_parts.append(avoid)
            
            # Add default negatives for non-photorealistic style
            negative_parts.extend([
                "photorealistic", "3d render", "complex textures",
                "detailed shading", "realistic lighting",
                "ugly", "deformed", "noisy", "blurry"
            ])
            
            return ", ".join(negative_parts)
    
    def _load_invokeai_style_presets(self) -> Dict[str, Dict]:
        """Load InvokeAI style presets from file"""
        preset_paths = [
            Path("/home/xai/DEV/invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json"),
            Path.home() / "DEV/invokeai/.venv/lib/python3.12/site-packages/invokeai/app/services/style_preset_records/default_style_presets.json",
        ]
        
        for preset_path in preset_paths:
            if preset_path.exists():
                try:
                    with open(preset_path, 'r', encoding='utf-8') as f:
                        presets_data = json.load(f)
                    
                    # Convert to dictionary for easy lookup
                    presets = {}
                    for preset in presets_data:
                        name = preset.get('name')
                        if name:
                            presets[name] = preset.get('preset_data', {})
                    
                    return presets
                except Exception as e:
                    print(f"Error loading presets: {e}")
        
        return {}
    
    def save_scene_prompt(self, slide_index: int, output_path: str):
        """Save COMPLETE scene prompt to YAML file"""
        prompt = self.build_scene_prompt(slide_index)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
    
    def get_scene_summary(self, slide_index: int) -> str:
        """Get a human-readable summary of the scene"""
        slide = self.book_data['slides'][slide_index]
        return f"Scene {slide_index + 1} ({slide['type']}): {slide['text'][:50]}..."


def main():
    """Generate COMPLETE prompts for any book"""
    import sys
    if len(sys.argv) > 1:
        book_yaml = sys.argv[1]
    else:
        book_yaml = 'books/little_prince/book.yaml'
    
    builder = PromptBuilder(book_yaml)
    book_dir = Path(book_yaml).parent
    
    print("=== SCENE 1 COMPLETE PROMPT (Exactly what AI receives) ===")
    print(builder.build_scene_prompt(0))
    
    print("\n=== GENERATING ALL SCENE PROMPTS WITH FULL DETAILS ===")
    output_dir = book_dir / 'prompts'
    output_dir.mkdir(exist_ok=True)
    
    for i in range(len(builder.book_data['slides'])):
        output_path = output_dir / f"scene_{i:02d}_prompt.yaml"
        builder.save_scene_prompt(i, str(output_path))
        print(f"Saved: {output_path} - {builder.get_scene_summary(i)}")
    
    print("\nAll prompts now show EXACTLY what will be sent to AI, including negative prompts!")


if __name__ == "__main__":
    main()