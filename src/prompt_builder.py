#!/usr/bin/env python3
"""
Prompt builder for AI scene generation
Builds YAML prompts combining art style and scene descriptions
"""

import yaml
from typing import Dict, Any
from pathlib import Path


class PromptBuilder:
    """Builds YAML prompts for AI scene generation"""
    
    def __init__(self, book_yaml_path: str):
        """Initialize with book YAML file"""
        self.book_yaml_path = Path(book_yaml_path)
        self.book_data = self._load_book_data()
        
    def _load_book_data(self) -> Dict[str, Any]:
        """Load book YAML configuration"""
        with open(self.book_yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def build_scene_prompt(self, slide_index: int) -> str:
        """
        Build YAML prompt for a specific scene
        
        Args:
            slide_index: Index of the slide (0-based)
            
        Returns:
            YAML string with complete scene prompt
        """
        if slide_index >= len(self.book_data['slides']):
            raise ValueError(f"Slide index {slide_index} out of range")
        
        slide = self.book_data['slides'][slide_index]
        custom_art_style = self.book_data.get('custom_art_style', {})
        template_art_style = self.book_data.get('template_art_style', '')
        book_info = self.book_data['book_info']
        technical_specs = self.book_data.get('technical_specs', {})
        
        # Build the complete prompt structure
        prompt_data = {
            'scene_generation': {
                'template_art_style': template_art_style if template_art_style else 'custom',
                'custom_art_style': custom_art_style,
                'scene_details': {
                    'slide_type': slide['type'],
                    'elements': slide['scene']['elements'],
                    'composition': slide['scene']['composition'],
                    'camera_angle': slide['scene']['camera_angle'],
                    'focus_point': slide['scene']['focus_point'],
                    'atmosphere': slide['scene']['atmosphere'],
                    'background': slide['scene']['background']
                },
                'generation_instructions': {
                    'maintain_consistency': "Keep visual style consistent across all scenes",
                    'text_space': "Leave clear space in upper third of image (above 66% height) for text overlay",
                    'mood': f"Match the {slide['scene']['atmosphere']} atmosphere",
                    'quality': "High quality, detailed illustration suitable for video",
                    'no_text': "Do not include any text, letters, words, or written elements in the image",
                    'style_emphasis': "Emphasize whimsical, childlike wonder with simplified forms and dreamlike quality",
                    'magical_elements': "Add subtle magical touches - floating stars, soft glows, ethereal particles that enhance the fairy-tale atmosphere"
                }
            }
        }
        
        # Convert to YAML with nice formatting
        return yaml.dump(prompt_data, 
                        default_flow_style=False, 
                        allow_unicode=True,
                        sort_keys=False,
                        width=80)
    
    def build_all_scene_prompts(self) -> Dict[int, str]:
        """
        Build prompts for all scenes in the book
        
        Returns:
            Dictionary mapping slide index to YAML prompt
        """
        prompts = {}
        for i in range(len(self.book_data['slides'])):
            prompts[i] = self.build_scene_prompt(i)
        return prompts
    
    def save_scene_prompt(self, slide_index: int, output_path: str):
        """Save scene prompt to YAML file"""
        prompt = self.build_scene_prompt(slide_index)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
    
    def get_scene_summary(self, slide_index: int) -> str:
        """Get a human-readable summary of the scene"""
        slide = self.book_data['slides'][slide_index]
        return f"Scene {slide_index + 1} ({slide['type']}): {slide['text'][:50]}..."


def main():
    """Example usage"""
    # Create prompt builder for Little Prince
    builder = PromptBuilder('books/little_prince/book.yaml')
    
    # Generate prompt for first scene
    print("=== SCENE 1 PROMPT (YAML) ===")
    print(builder.build_scene_prompt(0))
    
    # Generate and save all prompts
    print("\n=== GENERATING ALL SCENE PROMPTS ===")
    output_dir = Path('books/little_prince/prompts')
    output_dir.mkdir(exist_ok=True)
    
    for i in range(len(builder.book_data['slides'])):
        output_file = output_dir / f"scene_{i+1:02d}_prompt.yaml"
        builder.save_scene_prompt(i, output_file)
        print(f"Saved: {output_file} - {builder.get_scene_summary(i)}")


if __name__ == "__main__":
    main()