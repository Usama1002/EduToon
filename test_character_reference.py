#!/usr/bin/env python3
"""
Test script for text+image input with character references
"""

import os
import sys
from pathlib import Path
from io import BytesIO
import base64

try:
    from google import genai
    from PIL import Image
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

def test_character_image_generation():
    """Test image generation with character reference"""
    
    # Initialize client
    client = genai.Client()
    
    # Find a character image to use as reference
    characters_dir = Path("characters")
    reference_image = None
    
    for char_folder in characters_dir.iterdir():
        if char_folder.is_dir():
            png_files = list(char_folder.glob("*.png"))
            if png_files:
                reference_image = Image.open(png_files[0])
                print(f"📸 Using reference image: {png_files[0]}")
                break
    
    if not reference_image:
        print("❌ No character reference image found")
        return
    
    # Create prompt
    prompt = """Create a Korean webtoon-style educational scene using the character from the provided reference image. 

The character should be in a classroom setting, holding a book and looking excited about learning math. 

Style Requirements:
- Korean webtoon art style
- Use the provided character image as visual reference for the character's appearance
- Maintain the character's distinctive visual features from the reference image
- Bright, colorful, educational and child-friendly
- Clean line art with vibrant colors

Keep the character's original design but place them in the educational scene context."""

    try:
        print("🔄 Generating image with character reference...")
        
        # Call API with text + image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt, reference_image],
        )
        
        # Process response
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.text is not None:
                        print(f"📄 Response text: {part.text}")
                    elif part.inline_data is not None and part.inline_data.data:
                        # Decode base64 image data
                        decoded_data = base64.b64decode(part.inline_data.data)
                        generated_image = Image.open(BytesIO(decoded_data))
                        
                        # Save result
                        output_path = "character_scene_test.png"
                        generated_image.save(output_path)
                        print(f"✅ Generated image saved as: {output_path}")
                        print(f"📏 Image size: {generated_image.size}")
                        
                        return True
            else:
                print("❌ No content parts in response")
        else:
            print("❌ No candidates in response")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("❌ No image data found in response")
    return False

if __name__ == "__main__":
    print("🎭 Testing Character Reference Image Generation")
    print("=" * 60)
    test_character_image_generation()
