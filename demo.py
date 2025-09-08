#!/usr/bin/env python3
"""
Demo script for testing the Educational Webtoon Generator
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed."""
    required_packages = [
        'streamlit',
        'google-genai', 
        'pillow',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google-genai':
                import google.genai
            elif package == 'pillow':
                import PIL
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed!")
    return True

def check_environment():
    """Check environment setup."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("📝 Create a .env file with your Gemini API key:")
        print("   GEMINI_API_KEY=your_api_key_here")
        return False
    
    # Load and check API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        return False
    
    if len(api_key) < 20:
        print("⚠️  API key seems too short - please verify")
        return False
    
    print("✅ Environment configuration looks good!")
    return True

def check_characters():
    """Check character assets."""
    characters_dir = Path("characters")
    
    if not characters_dir.exists():
        print("⚠️  Characters directory not found")
        print("📁 The 'characters/' directory contains character PNG files")
        print("   Each character should have its own subdirectory")
        return False
    
    char_count = 0
    for char_dir in characters_dir.iterdir():
        if char_dir.is_dir():
            png_files = list(char_dir.glob("*.png"))
            if png_files:
                char_count += 1
                print(f"   📂 {char_dir.name}: {len(png_files)} PNG files")
    
    if char_count == 0:
        print("⚠️  No character assets found")
        return False
    
    print(f"✅ Found {char_count} character directories with assets!")
    return True

def run_demo():
    """Run the demo application."""
    print("🎭 Educational Webtoon Generator - Demo")
    print("=" * 50)
    
    # Check requirements
    print("\n1. Checking Python packages...")
    if not check_requirements():
        return False
    
    # Check environment
    print("\n2. Checking environment setup...")
    if not check_environment():
        return False
    
    # Check character assets
    print("\n3. Checking character assets...")
    check_characters()  # Non-blocking
    
    print("\n🚀 Starting Streamlit application...")
    print("   Open your browser to: http://localhost:8501")
    print("   Press Ctrl+C to stop the application")
    
    # Run Streamlit
    os.system("streamlit run app_enhanced.py")
    
    return True

def create_sample_env():
    """Create a sample .env file."""
    env_content = """# Educational Webtoon Generator Configuration

# Required: Your Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Use Vertex AI instead of Gemini Developer API
# GOOGLE_GENAI_USE_VERTEXAI=false
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Custom settings
# OUTPUT_DIR=output
# MAX_RETRIES=3
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("📝 Created .env.example file")
    print("   Copy it to .env and add your API key")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            print("🔧 Setting up Educational Webtoon Generator...")
            create_sample_env()
            print("\n📋 Next steps:")
            print("1. Copy .env.example to .env")
            print("2. Add your Gemini API key to .env")
            print("3. Run: python demo.py")
        elif sys.argv[1] == "check":
            print("🔍 Checking system setup...")
            check_requirements()
            check_environment()
            check_characters()
        else:
            print("Usage: python demo.py [setup|check]")
    else:
        run_demo()
