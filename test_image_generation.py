#!/usr/bin/env python3
"""
Gemini Image Generation API Test Script
Tests both text-to-image and image editing capabilities
"""

import os
import sys
from pathlib import Path
from io import BytesIO
import base64
import time
from datetime import datetime
from typing import Optional, List

try:
    from google import genai
    from google.genai import types
    from PIL import Image
    import dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install google-genai pillow python-dotenv")
    sys.exit(1)

class GeminiImageTester:
    def __init__(self):
        """Initialize the Gemini client with API key"""
        # Load environment variables
        dotenv.load_dotenv()
        
        # Get API key
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            print("Please set your API key in .env file or environment")
            sys.exit(1)
        
        # Initialize client
        try:
            self.client = genai.Client(api_key=self.api_key)
            print("✅ Gemini client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini client: {e}")
            sys.exit(1)
        
        # Model for image generation
        self.model = "gemini-2.5-flash-image-preview"
        
        # Create output directory
        self.output_dir = Path("test_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
    def save_image(self, image_data: bytes, filename: str) -> str:
        """Save image data to file with base64 decoding support"""
        filepath = self.output_dir / filename
        try:
            # Try to decode as base64 first (Gemini returns base64 encoded images)
            try:
                decoded_data = base64.b64decode(image_data)
                image = Image.open(BytesIO(decoded_data))
            except Exception:
                # If base64 decode fails, try direct binary data
                image = Image.open(BytesIO(image_data))
            
            image.save(filepath)
            print(f"💾 Image saved: {filepath}")
            print(f"📏 Image size: {image.size}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Failed to save image {filename}: {e}")
            return ""
    
    def test_text_to_image(self) -> bool:
        """Test basic text-to-image generation"""
        print("\n🎨 Testing Text-to-Image Generation...")
        print("=" * 50)
        
        prompts = [
            {
                "name": "simple_scene",
                "prompt": "A cute cartoon banana character with a friendly smile, wearing a tiny chef's hat, in a bright kitchen setting"
            },
            {
                "name": "educational_scene", 
                "prompt": "A colorful educational scene showing a friendly robot teacher explaining math to children in a classroom, cartoon style, bright colors"
            },
            {
                "name": "webtoon_panel",
                "prompt": "A single comic book panel in a Korean webtoon style. A young student character looking excited while holding a science book. Bright, colorful background with sparkles. Clean line art."
            }
        ]
        
        success_count = 0
        
        for i, test in enumerate(prompts, 1):
            print(f"\n📝 Test {i}: {test['name']}")
            print(f"Prompt: {test['prompt']}")
            
            try:
                # Generate image
                print("🔄 Generating image...")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[test['prompt']],
                )
                
                # Process response
                image_saved = False
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text is not None:
                                print(f"📄 Response text: {part.text}")
                            elif part.inline_data is not None and part.inline_data.data:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"text_to_image_{test['name']}_{timestamp}.png"
                                saved_path = self.save_image(part.inline_data.data, filename)
                                if saved_path:
                                    image_saved = True
                                    success_count += 1
                    else:
                        print("❌ No content parts found in response")
                else:
                    print("❌ No candidates found in response")
                
                if not image_saved:
                    print("❌ No image data found in response")
                else:
                    print("✅ Text-to-image test passed")
                    
            except Exception as e:
                print(f"❌ Text-to-image test failed: {e}")
            
            # Brief pause between requests
            time.sleep(2)
        
        print(f"\n📊 Text-to-Image Results: {success_count}/{len(prompts)} tests passed")
        return success_count > 0
    
    def prepare_test_image(self) -> Optional[Image.Image]:
        """Create or load a test image for editing tests"""
        print("\n🖼️  Preparing test image for editing...")
        
        # Check if we have existing character images
        characters_dir = Path("characters")
        if characters_dir.exists():
            # Find the first available character image
            for char_folder in characters_dir.iterdir():
                if char_folder.is_dir():
                    for img_file in char_folder.glob("*.png"):
                        try:
                            test_image = Image.open(img_file)
                            print(f"📸 Using existing character image: {img_file}")
                            return test_image
                        except Exception:
                            continue
        
        # If no character images, create a simple test image
        print("🎨 Creating simple test image...")
        try:
            # Create a simple colored rectangle
            test_image = Image.new('RGB', (400, 400), color='lightblue')
            test_path = self.output_dir / "test_input.png"
            test_image.save(test_path)
            print(f"💾 Test image created: {test_path}")
            return test_image
        except Exception as e:
            print(f"❌ Failed to create test image: {e}")
            return None
    
    def test_image_editing(self) -> bool:
        """Test image editing capabilities"""
        print("\n✏️  Testing Image Editing...")
        print("=" * 50)
        
        # Prepare test image
        test_image = self.prepare_test_image()
        if not test_image:
            print("❌ Could not prepare test image for editing")
            return False
        
        editing_tests = [
            {
                "name": "add_elements",
                "prompt": "Add a small rainbow in the top-right corner of this image. Keep everything else exactly the same."
            },
            {
                "name": "style_change",
                "prompt": "Transform this image into a cartoon anime style while keeping the same composition and main elements."
            },
            {
                "name": "color_adjustment",
                "prompt": "Make this image warmer and more vibrant, increasing the saturation and adding a golden hour lighting effect."
            }
        ]
        
        success_count = 0
        
        for i, test in enumerate(editing_tests, 1):
            print(f"\n📝 Edit Test {i}: {test['name']}")
            print(f"Prompt: {test['prompt']}")
            
            try:
                # Generate edited image
                print("🔄 Processing image edit...")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[test['prompt'], test_image],
                )
                
                # Process response
                image_saved = False
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text is not None:
                                print(f"📄 Response text: {part.text}")
                            elif part.inline_data is not None and part.inline_data.data:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"image_edit_{test['name']}_{timestamp}.png"
                                saved_path = self.save_image(part.inline_data.data, filename)
                                if saved_path:
                                    image_saved = True
                                    success_count += 1
                    else:
                        print("❌ No content parts found in response")
                else:
                    print("❌ No candidates found in response")
                
                if not image_saved:
                    print("❌ No image data found in response")
                else:
                    print("✅ Image editing test passed")
                    
            except Exception as e:
                print(f"❌ Image editing test failed: {e}")
            
            # Brief pause between requests
            time.sleep(2)
        
        print(f"\n📊 Image Editing Results: {success_count}/{len(editing_tests)} tests passed")
        return success_count > 0
    
    def test_webtoon_specific(self) -> bool:
        """Test webtoon-specific image generation"""
        print("\n📚 Testing Webtoon-Specific Generation...")
        print("=" * 50)
        
        webtoon_prompts = [
            {
                "name": "educational_panel",
                "prompt": "Create a Korean webtoon-style panel showing a cute animal character explaining basic math (2+2=4) to children. Vertical format, bright colors, speech bubble with clear text '2 + 2 = 4!'. Clean line art, educational and friendly atmosphere."
            },
            {
                "name": "character_expression",
                "prompt": "A single Korean webtoon character panel showing a young student with surprised expression, eyes wide, mouth open in amazement. Simple background with sparkle effects. Vertical panel format suitable for webtoon."
            },
            {
                "name": "science_lesson",
                "prompt": "Korean webtoon panel: A friendly teacher character pointing to a simple diagram of the solar system. Speech bubble saying 'This is our Solar System!'. Colorful, educational, child-friendly art style. Vertical panel format."
            }
        ]
        
        success_count = 0
        
        for i, test in enumerate(webtoon_prompts, 1):
            print(f"\n📝 Webtoon Test {i}: {test['name']}")
            print(f"Prompt: {test['prompt']}")
            
            try:
                # Generate webtoon panel
                print("🔄 Generating webtoon panel...")
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[test['prompt']],
                )
                
                # Process response
                image_saved = False
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.text is not None:
                                print(f"📄 Response text: {part.text}")
                            elif part.inline_data is not None and part.inline_data.data:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"webtoon_{test['name']}_{timestamp}.png"
                                saved_path = self.save_image(part.inline_data.data, filename)
                                if saved_path:
                                    image_saved = True
                                    success_count += 1
                    else:
                        print("❌ No content parts found in response")
                else:
                    print("❌ No candidates found in response")
                
                if not image_saved:
                    print("❌ No image data found in response")
                else:
                    print("✅ Webtoon generation test passed")
                    
            except Exception as e:
                print(f"❌ Webtoon generation test failed: {e}")
            
            # Brief pause between requests
            time.sleep(2)
        
        print(f"\n📊 Webtoon Generation Results: {success_count}/{len(webtoon_prompts)} tests passed")
        return success_count > 0
    
    def run_all_tests(self):
        """Run all image generation tests"""
        print("🚀 Starting Gemini Image Generation API Tests")
        print("=" * 60)
        print(f"Model: {self.model}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {
            "text_to_image": False,
            "image_editing": False,
            "webtoon_specific": False
        }
        
        # Run tests
        try:
            results["text_to_image"] = self.test_text_to_image()
            results["image_editing"] = self.test_image_editing()
            results["webtoon_specific"] = self.test_webtoon_specific()
        except KeyboardInterrupt:
            print("\n⚠️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error during testing: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(results.values())
        total_tests = len(results)
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} test categories passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Image generation API is working correctly.")
        elif passed_tests > 0:
            print("⚠️  Some tests passed. API is partially working.")
        else:
            print("❌ All tests failed. Check your API key and connection.")
        
        print(f"\n📁 Generated images saved in: {self.output_dir}")

def main():
    """Main function"""
    print("Gemini Image Generation API Tester")
    print("This script tests text-to-image and image editing capabilities")
    print()
    
    try:
        tester = GeminiImageTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n👋 Testing cancelled by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
