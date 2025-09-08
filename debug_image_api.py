#!/usr/bin/env python3
"""
Simple Gemini Image Generation Test
Based on official documentation examples
"""

import os
import sys
from pathlib import Path
from io import BytesIO
import base64
from datetime import datetime

try:
    from google import genai
    from PIL import Image
    import dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install google-genai pillow python-dotenv")
    sys.exit(1)

def test_simple_image_generation():
    """Test basic image generation following official docs exactly"""
    print("🚀 Simple Gemini Image Generation Test")
    print("=" * 50)
    
    # Load environment
    dotenv.load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEY in .env")
        return False
    
    # Initialize client
    try:
        client = genai.Client(api_key=api_key)
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Create output directory
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Test prompt (from official docs)
    prompt = "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    
    print(f"📝 Prompt: {prompt}")
    print("🔄 Generating image...")
    
    try:
        # Generate content using the exact pattern from docs
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
        )
        
        print("📊 Response received. Analyzing...")
        
        # Debug: Print response structure
        if hasattr(response, 'candidates'):
            print(f"📋 Found {len(response.candidates) if response.candidates else 0} candidates")
            
            if response.candidates:
                candidate = response.candidates[0]
                print(f"📋 Candidate content type: {type(candidate.content)}")
                
                if candidate.content and hasattr(candidate.content, 'parts') and candidate.content.parts:
                    print(f"📋 Found {len(candidate.content.parts)} parts")
                    
                    for i, part in enumerate(candidate.content.parts):
                        print(f"📋 Part {i}: text={part.text is not None}, inline_data={part.inline_data is not None}")
                        
                        if part.text is not None:
                            print(f"📄 Text response: {part.text}")
                        
                        if part.inline_data is not None:
                            print(f"📷 Image data found!")
                            print(f"📋 MIME type: {part.inline_data.mime_type}")
                            print(f"📋 Data size: {len(part.inline_data.data) if part.inline_data.data else 0} bytes")
                            
                            if part.inline_data.data:
                                try:
                                    # Save the image
                                    image = Image.open(BytesIO(part.inline_data.data))
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    filename = f"simple_test_{timestamp}.png"
                                    filepath = output_dir / filename
                                    image.save(filepath)
                                    print(f"✅ Image saved successfully: {filepath}")
                                    print(f"📏 Image size: {image.size}")
                                    return True
                                except Exception as e:
                                    print(f"❌ Failed to process image data: {e}")
                                    # Try to save raw data for debugging
                                    try:
                                        raw_file = output_dir / f"raw_data_{timestamp}.bin"
                                        with open(raw_file, 'wb') as f:
                                            f.write(part.inline_data.data)
                                        print(f"💾 Raw data saved for debugging: {raw_file}")
                                    except Exception as e2:
                                        print(f"❌ Could not even save raw data: {e2}")
                            else:
                                print("❌ Image data is empty")
                else:
                    print("❌ No content parts found")
            else:
                print("❌ No candidates found")
        else:
            print("❌ Response has no candidates attribute")
            
        print("❌ No valid image data found in response")
        return False
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_alternative_approach():
    """Test using a different approach or model"""
    print("\n🔄 Testing Alternative Approach...")
    print("=" * 50)
    
    # Load environment
    dotenv.load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    # Try with different model or configuration
    try:
        client = genai.Client(api_key=api_key)
        
        # Try a very simple prompt
        simple_prompt = "Generate a simple red circle on white background"
        print(f"📝 Simple prompt: {simple_prompt}")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[simple_prompt],
        )
        
        # Check if this gives us any different results
        print("📊 Alternative response structure:")
        print(f"Response type: {type(response)}")
        print(f"Has candidates: {hasattr(response, 'candidates')}")
        
        return False  # We'll analyze the response structure
        
    except Exception as e:
        print(f"❌ Alternative test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Gemini Image Generation Debug Test")
    print("This script will help diagnose image generation issues")
    print()
    
    # Test 1: Official example
    success1 = test_simple_image_generation()
    
    # Test 2: Alternative approach
    success2 = test_alternative_approach()
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if success1:
        print("✅ Image generation is working!")
    else:
        print("❌ Image generation failed")
        print("\n💡 Possible issues:")
        print("1. API might not support image generation with your key/plan")
        print("2. Model might be text-only in your region")
        print("3. Different response format than expected")
        print("4. API key might not have image generation permissions")
        
        print("\n🔧 Try these solutions:")
        print("1. Check if your API key supports image generation")
        print("2. Try using 'gemini-pro-vision' model instead")
        print("3. Verify your billing/quota settings")
        print("4. Check Google AI Studio for model availability")

if __name__ == "__main__":
    main()
