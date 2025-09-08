"""
Simple test script to verify the Educational Webtoon Generator setup
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing Python package imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        from google import genai
        print("✅ Google GenAI imported successfully")
    except ImportError as e:
        print(f"❌ Google GenAI import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ PIL (Pillow) imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_local_modules():
    """Test if local modules can be imported."""
    print("\nTesting local module imports...")
    
    try:
        from config import GEMINI_MODEL_TEXT, WEBTOON_CONFIG
        print("✅ config.py imported successfully")
    except ImportError as e:
        print(f"❌ config.py import failed: {e}")
        return False
    
    try:
        from utils import validate_api_key, load_character_assets
        print("✅ utils.py imported successfully")
    except ImportError as e:
        print(f"❌ utils.py import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration."""
    print("\nTesting environment setup...")
    
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        if Path(".env.example").exists():
            print("📝 .env.example found - copy it to .env and add your API key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        return False
    
    if api_key == "your_gemini_api_key_here":
        print("⚠️  Please replace the placeholder API key in .env")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def test_character_assets():
    """Test character assets directory."""
    print("\nTesting character assets...")
    
    characters_dir = Path("characters")
    if not characters_dir.exists():
        print("⚠️  Characters directory not found")
        print("📁 Creating characters directory...")
        characters_dir.mkdir(exist_ok=True)
        return False
    
    png_files = list(characters_dir.rglob("*.png"))
    if not png_files:
        print("⚠️  No PNG files found in characters directory")
        print("📂 Add character PNG files in subdirectories")
        return False
    
    # Count characters by directory
    char_dirs = {}
    for png_file in png_files:
        char_name = png_file.parent.name
        if char_name != "characters":
            char_dirs[char_name] = char_dirs.get(char_name, 0) + 1
    
    print(f"✅ Found {len(char_dirs)} character directories:")
    for char_name, count in char_dirs.items():
        print(f"   📂 {char_name}: {count} PNG files")
    
    return True

def test_api_connection():
    """Test API connection (optional - requires valid API key)."""
    print("\nTesting API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️  Valid API key required for connection test")
            return False
        
        from google import genai
        client = genai.Client(api_key=api_key)
        
        # Simple test request
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents='Say "Hello from Educational Webtoon Generator!"'
        )
        
        if response.text and "Hello" in response.text:
            print("✅ API connection successful!")
            return True
        else:
            print("⚠️  API responded but output unexpected")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Educational Webtoon Generator - System Test")
    print("=" * 50)
    
    tests = [
        ("Package Imports", test_imports),
        ("Local Modules", test_local_modules),
        ("Environment", test_environment),
        ("Character Assets", test_character_assets),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Optional API test
    if results.get("Environment", False):
        print()
        api_test = input("🔗 Test API connection? (y/N): ").lower().strip()
        if api_test == 'y':
            results["API Connection"] = test_api_connection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Ready to generate webtoons!")
        print("\n🚀 Run the application with:")
        print("   streamlit run app_enhanced.py")
        print("   or")
        print("   python demo.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n📝 Setup help:")
        print("   1. Install packages: pip install -r requirements.txt")
        print("   2. Copy .env.example to .env and add your API key")
        print("   3. Add character PNG files to characters/ subdirectories")

if __name__ == "__main__":
    main()
