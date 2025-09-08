"""
Utility functions for the Educational Webtoon Generator
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

def validate_api_key(api_key: str) -> bool:
    """Validate that the API key is present and properly formatted."""
    if not api_key:
        return False
    # Basic validation - check if it looks like a valid API key
    return len(api_key) > 20 and api_key.startswith(('AIza', 'sk-'))

def load_character_assets() -> Dict[str, Dict[str, Any]]:
    """Load character assets with metadata."""
    characters = {}
    characters_dir = Path("characters")
    
    if not characters_dir.exists():
        return {}
    
    for char_dir in characters_dir.iterdir():
        if char_dir.is_dir():
            char_name = char_dir.name
            char_data = {
                "name": char_name,
                "assets": [],
                "expressions": [],
                "count": 0
            }
            
            for img_file in char_dir.glob("*.png"):
                char_data["assets"].append(str(img_file))
                
                # Categorize by filename
                filename = img_file.stem.lower()
                if "expression" in filename:
                    char_data["expressions"].append(str(img_file))
            
            char_data["count"] = len(char_data["assets"])
            
            if char_data["assets"]:
                characters[char_name] = char_data
    
    return characters

def create_character_preview(character_path: str, size: Tuple[int, int] = (100, 100)) -> Optional[Image.Image]:
    """Create a preview image for a character."""
    try:
        img = Image.open(character_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        st.error(f"Error creating preview for {character_path}: {e}")
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def create_story_prompt(concept: str, characters: List[str], num_scenes: int, difficulty: str) -> str:
    """Create a detailed prompt for story generation."""
    
    prompt = f"""
    Create an educational webtoon story for children about: {concept}
    
    Parameters:
    - Characters to include: {', '.join(characters)}
    - Number of scenes: {num_scenes}
    - Difficulty level: {difficulty}
    - Target format: Korean webtoon style (vertical scroll)
    
    Requirements:
    1. Make it engaging and age-appropriate for {difficulty.lower()} students
    2. Each scene should teach a specific aspect of the concept
    3. Include dialogue that sounds natural for children
    4. Use the characters meaningfully in the story
    5. Build educational content progressively
    6. Include visual descriptions suitable for image generation
    
    Story Structure:
    - Clear beginning, middle, and end
    - Each scene builds on the previous one
    - Culminates in a clear understanding of the concept
    - Positive, encouraging tone throughout
    
    For each scene, provide:
    - Scene number and title
    - Location/setting description
    - Characters present in the scene
    - Main dialogue (1-2 sentences per character)
    - Action/what happens in the scene
    - Specific educational point being taught
    - Detailed visual description for image generation (including character positions, expressions, background elements)
    
    Format the response as valid JSON with this exact structure:
    {{
        "title": "Engaging story title",
        "concept": "{concept}",
        "target_age": "{difficulty}",
        "learning_objectives": ["objective1", "objective2", "objective3"],
        "scenes": [
            {{
                "scene_number": 1,
                "scene_title": "Scene title",
                "location": "Setting description",
                "characters": ["character1", "character2"],
                "dialogue": "Main dialogue between characters",
                "action": "What happens in this scene",
                "educational_point": "Specific learning point",
                "visual_description": "Detailed scene description for image generation including character positions, expressions, background, lighting, and style"
            }}
        ]
    }}
    """
    
    return prompt

def create_image_prompt(scene_description: str, characters: List[str], style: str = "cartoon") -> str:
    """Create an enhanced prompt for image generation."""
    
    base_prompt = f"""
    Create a high-quality educational webtoon scene in Korean manhwa style:
    
    Scene Description: {scene_description}
    Characters: {', '.join(characters)}
    Art Style: {style}
    
    Visual Requirements:
    - Korean webtoon/manhwa art style with clean lines. However, use English text for any signs or written elements.
    - Bright, vibrant colors suitable for children
    - Clear character expressions and body language
    - Educational and friendly atmosphere
    - Optimized for vertical webtoon panel layout
    - High contrast for good readability
    - Child-friendly and engaging composition
    - Professional illustration quality
    
    Technical Specifications:
    - Clear character details and facial expressions
    - Appropriate background that supports the scene
    - Good lighting and depth
    - Suitable for educational content
    - High resolution and crisp details
    """
    
    return base_prompt

def validate_story_data(story_data: Dict) -> bool:
    """Validate the generated story data structure."""
    required_fields = ["title", "concept", "scenes"]
    
    if not isinstance(story_data, dict):
        return False
    
    for field in required_fields:
        if field not in story_data:
            return False
    
    scenes = story_data.get("scenes", [])
    if not isinstance(scenes, list) or len(scenes) == 0:
        return False
    
    # Validate each scene
    required_scene_fields = ["scene_number", "location", "characters", "dialogue", "action", "educational_point", "visual_description"]
    
    for scene in scenes:
        if not isinstance(scene, dict):
            return False
        
        for field in required_scene_fields:
            if field not in scene:
                return False
        
        if not isinstance(scene["characters"], list):
            return False
    
    return True

def create_error_image(width: int = 400, height: int = 300, message: str = "Image generation failed") -> Image.Image:
    """Create a placeholder image when generation fails."""
    img = Image.new('RGB', (width, height), color='lightgray')
    draw = ImageDraw.Draw(img)
    
    # Try to use a basic font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    bbox = draw.textbbox((0, 0), message, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    draw.text((x, y), message, fill='black', font=font)
    
    return img

def save_generated_content(story_data: Dict, images: List[Image.Image], output_dir: str = "output") -> str:
    """Save generated content to files."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create timestamped directory
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    story_dir = output_path / f"webtoon_{timestamp}"
    story_dir.mkdir(exist_ok=True)
    
    # Save story data
    story_file = story_dir / "story_data.json"
    with open(story_file, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=2, ensure_ascii=False)
    
    # Save individual scene images
    for i, img in enumerate(images):
        if img:
            img_file = story_dir / f"scene_{i+1}.png"
            img.save(img_file, "PNG")
    
    return str(story_dir)
