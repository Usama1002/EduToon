#!/usr/bin/env python3
"""
Test script to debug character loading
"""

import sys
from pathlib import Path

# Add the current directory to path so we can import utils
sys.path.append('.')

from utils import load_character_assets, create_character_preview

def test_character_loading():
    print("🔍 Testing Character Asset Loading")
    print("=" * 50)
    
    # Check if characters directory exists
    characters_dir = Path("characters")
    print(f"📁 Characters directory exists: {characters_dir.exists()}")
    
    if characters_dir.exists():
        print(f"📂 Characters directory contents:")
        for item in characters_dir.iterdir():
            if item.is_dir():
                png_files = list(item.glob("*.png"))
                print(f"  {item.name}: {len(png_files)} PNG files")
                for png_file in png_files[:3]:  # Show first 3 files
                    print(f"    - {png_file.name}")
                if len(png_files) > 3:
                    print(f"    ... and {len(png_files) - 3} more")
    
    print("\n🎭 Loading character assets...")
    characters = load_character_assets()
    
    print(f"📊 Found {len(characters)} characters:")
    for char_name, char_data in characters.items():
        print(f"\n👤 {char_name}:")
        print(f"  📄 Assets: {char_data['count']}")
        print(f"  🎭 Expressions: {len(char_data['expressions'])}")
        print(f"  📁 First asset: {char_data['assets'][0] if char_data['assets'] else 'None'}")
        
        # Test preview creation
        if char_data['assets']:
            preview = create_character_preview(char_data['assets'][0])
            if preview:
                print(f"  🖼️  Preview: ✅ ({preview.size})")
            else:
                print(f"  🖼️  Preview: ❌")
    
    if not characters:
        print("❌ No characters loaded!")
        print("\n🔧 Debugging suggestions:")
        print("1. Check if 'characters/' directory exists")
        print("2. Check if subdirectories contain .png files")
        print("3. Check file permissions")
    else:
        print(f"\n✅ Successfully loaded {len(characters)} characters!")

if __name__ == "__main__":
    test_character_loading()
