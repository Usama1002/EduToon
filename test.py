from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

import base64
from dotenv import load_dotenv

load_dotenv()

client = genai.Client()

prompt = (
    "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
)

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt],
)


print("Generated Image:")
print(response.candidates[0].content.parts)
print("===================================")

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None and part.inline_data.data:
        print(f"📄 MIME type: {part.inline_data.mime_type}")
        print(f"📊 Data size: {len(part.inline_data.data)} bytes")
        print(f"🔍 First 20 bytes: {part.inline_data.data[:20]}")
        print(f"🔍 Last 20 bytes: {part.inline_data.data[-20:]}")
        
        # Check if data might be base64 encoded
        try:
            # Try to decode as base64
            decoded_data = base64.b64decode(part.inline_data.data)
            print(f"🔓 Decoded size: {len(decoded_data)} bytes")
            print(f"🔍 Decoded first 20 bytes: {decoded_data[:20]}")
            
            # Try to open decoded data
            image_bytes = BytesIO(decoded_data)
            image = Image.open(image_bytes)
            image.save("decoded_image.png")
            print("✅ BASE64 DECODED - Image saved successfully as 'decoded_image.png'")
            print(f"📏 Image size: {image.size}")
            print(f"🎨 Image mode: {image.mode}")
            
        except Exception as decode_error:
            print(f"❌ Base64 decode failed: {decode_error}")
            
            # Try saving raw data first
            with open("raw_image.png", "wb") as f:
                f.write(part.inline_data.data)
            print("💾 Raw data saved as 'raw_image.png'")
            
            # Try to open with PIL
            try:
                image_bytes = BytesIO(part.inline_data.data)
                image_bytes.seek(0)  # Reset to beginning
                image = Image.open(image_bytes)
                image.save("generated_image.png")
                print("✅ Image saved successfully as 'generated_image.png'")
                print(f"📏 Image size: {image.size}")
                print(f"🎨 Image mode: {image.mode}")
            except Exception as e:
                print(f"❌ PIL error: {e}")
                
                # Try alternative approach - save directly and reopen
                try:
                    with open("direct_save.png", "wb") as f:
                        f.write(part.inline_data.data)
                    # Try to open the saved file
                    image = Image.open("direct_save.png")
                    print("✅ Direct save method worked!")
                    print(f"📏 Image size: {image.size}")
                    print(f"🎨 Image mode: {image.mode}")
                except Exception as e2:
                    print(f"❌ Direct save also failed: {e2}")