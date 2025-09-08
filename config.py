"""
Configuration settings for the Educational Webtoon Generator
"""

# API Configuration
GEMINI_MODEL_TEXT = "gemini-2.0-flash-001"
GEMINI_MODEL_IMAGE = "gemini-2.5-flash-image-preview"

# Webtoon Layout Configuration
WEBTOON_CONFIG = {
    "panel_width": 800,
    "panel_height": 600,
    "padding": 20,
    "title_height": 100,
    "max_scenes": 10,
    "min_scenes": 3
}

# Story Generation Configuration
STORY_CONFIG = {
    "max_output_tokens": 2048,
    "temperature": 0.7,
    "default_scenes": 6
}

# Image Generation Configuration
IMAGE_CONFIG = {
    "default_style": "cartoon",
    "supported_styles": ["cartoon", "anime", "cute", "colorful", "realistic"],
    "max_retries": 3,
    "retry_delay": 1
}

# Educational Levels
DIFFICULTY_LEVELS = [
    "Preschool",
    "Elementary", 
    "Middle School"
]

# Supported image formats
SUPPORTED_FORMATS = [".png", ".jpg", ".jpeg"]

# Character directory
CHARACTERS_DIR = "characters"
