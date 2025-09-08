import streamlit as st
import os
from PIL import Image
import io
import base64
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Google GenAI
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Google GenAI library not installed. Please run: pip install google-genai")
    st.stop()

class WebtoonGenerator:
    def __init__(self):
        """Initialize the Webtoon Generator with API client."""
        self.client = None
        self.setup_client()
        
    def setup_client(self):
        """Setup the Google GenAI client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("Please set your GEMINI_API_KEY in the .env file")
            return
            
        try:
            # Check if using Vertex AI
            use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() == "true"
            
            if use_vertexai:
                project = os.getenv("GOOGLE_CLOUD_PROJECT")
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
                if not project:
                    st.error("Please set GOOGLE_CLOUD_PROJECT for Vertex AI")
                    return
                self.client = genai.Client(
                    vertexai=True,
                    project=project,
                    location=location
                )
            else:
                self.client = genai.Client(api_key=api_key)
                
        except Exception as e:
            st.error(f"Failed to initialize GenAI client: {str(e)}")
    
    def load_characters(self) -> Dict[str, List[str]]:
        """Load character images from the characters directory."""
        characters = {}
        characters_dir = Path("characters")
        
        if not characters_dir.exists():
            st.warning("Characters directory not found. Creating empty character list.")
            return {}
        
        for char_dir in characters_dir.iterdir():
            if char_dir.is_dir():
                char_name = char_dir.name
                char_images = []
                
                for img_file in char_dir.glob("*.png"):
                    char_images.append(str(img_file))
                
                if char_images:
                    characters[char_name] = sorted(char_images)
        
        return characters
    
    def generate_story_outline(self, concept: str, characters: List[str], num_scenes: int = 6, difficulty: str = "Elementary") -> Optional[Dict]:
        """Generate educational story outline using Gemini 2.5 Flash."""
        if not self.client:
            st.error("API client not initialized")
            return None
        
        prompt = f"""
        Create an educational webtoon story outline for kids about: {concept}
        
        Characters to include: {', '.join(characters)}
        Number of scenes: {num_scenes}
        Difficulty level: {difficulty}
        
        Create a story that:
        1. Is engaging and fun for children
        2. Teaches the concept clearly and progressively
        3. Uses the characters meaningfully
        4. Has dialogue and action in each scene
        5. Follows Korean webtoon style (vertical scroll, dramatic moments)
        
        For each scene, provide:
        - Scene number
        - Location/setting
        - Characters present
        - Key dialogue
        - Action description
        - Educational point being taught
        - Visual composition description
        
        Format as JSON with this structure:
        {{
            "title": "Story Title",
            "concept": "{concept}",
            "target_age": "age range",
            "scenes": [
                {{
                    "scene_number": 1,
                    "location": "description",
                    "characters": ["character1", "character2"],
                    "dialogue": "main dialogue",
                    "action": "what happens",
                    "educational_point": "what is being taught",
                    "visual_description": "detailed scene description for image generation"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=0.7,
                    max_output_tokens=2048
                )
            )
            
            if response.text:
                story_data = json.loads(response.text)
                return story_data
            else:
                st.error("No response text received")
                return None
            
        except Exception as e:
            st.error(f"Failed to generate story: {str(e)}")
            return None
    
    def get_character_reference_images(self, character_names: List[str]) -> List[Image.Image]:
        """Get reference images for specified characters."""
        reference_images = []
        
        # Load character assets (simple version for basic app)
        characters_dir = Path("characters")
        if not characters_dir.exists():
            return reference_images
        
        for char_name in character_names:
            char_folder = characters_dir / char_name
            if char_folder.exists() and char_folder.is_dir():
                # Find first PNG file in character folder
                png_files = list(char_folder.glob("*.png"))
                if png_files:
                    try:
                        char_image = Image.open(png_files[0])
                        # Resize if too large (for API efficiency)
                        if char_image.size[0] > 512 or char_image.size[1] > 512:
                            char_image.thumbnail((512, 512), Image.Resampling.LANCZOS)
                        reference_images.append(char_image)
                        st.info(f"🎭 Using character reference: {char_name}")
                    except Exception as e:
                        st.warning(f"⚠️ Could not load character image for {char_name}: {e}")
        
        return reference_images
    
    def generate_scene_image(self, scene_description: str, characters: List[str], style: str = "cartoon") -> Optional[Image.Image]:
        """Generate scene image using character references and Gemini image generation."""
        if not self.client:
            st.error("API client not initialized")
            return None
        
        # Get character reference images
        reference_images = self.get_character_reference_images(characters)
        
        # Create enhanced prompt based on whether we have character references
        if reference_images:
            enhanced_prompt = f"""Create a Korean webtoon-style scene based on the provided character reference images.

Scene Description: {scene_description}

Characters to include: {', '.join(characters)}

Style Requirements:
- Korean webtoon art style ({style})
- Use the provided character images as visual references for the characters' appearance
- Maintain the characters' distinctive visual features from the reference images
- Bright, colorful, educational and child-friendly
- Suitable for vertical webtoon layout
- Clean line art with vibrant colors

Keep the characters' original designs but place them in the described scene context."""
        else:
            # Fallback to text-only prompt
            enhanced_prompt = f"""
            Create a high-quality webtoon scene illustration in Korean manhwa style:
            
            Scene: {scene_description}
            Characters: {', '.join(characters)}
            Style: {style}, colorful, expressive, clean lines
            
            Visual requirements:
            - Korean webtoon/manhwa art style
            - Vibrant colors suitable for children
            - Clear character expressions
            - Educational and friendly atmosphere
            - Suitable for vertical webtoon layout
            - High contrast and clear details
            - Child-friendly and engaging composition
            
            The image should be optimized for a webtoon panel with good readability and visual appeal.
            """
        
        try:
            # Prepare contents: prompt + reference images
            contents = [enhanced_prompt] + reference_images  # type: ignore
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=contents,
            )
            
            # Extract image from response
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data is not None and part.inline_data.data:
                            # Handle base64 encoded image data from Gemini
                            try:
                                # Try base64 decode first (Gemini returns base64 encoded images)
                                decoded_data = base64.b64decode(part.inline_data.data)
                                image = Image.open(io.BytesIO(decoded_data))
                            except Exception:
                                # Fallback to direct binary data
                                image = Image.open(io.BytesIO(part.inline_data.data))
                            return image
            
            st.warning("No image generated in response")
            return None
            
        except Exception as e:
            st.error(f"Failed to generate image: {str(e)}")
            return None
    
    def create_webtoon_layout(self, story_data: Optional[Dict], scene_images: List[Optional[Image.Image]]) -> Optional[Image.Image]:
        """Create a full webtoon layout combining all scenes."""
        if not story_data or not story_data.get("scenes") or not scene_images:
            return None
        
        # Webtoon dimensions (typical mobile webtoon size)
        panel_width = 800
        panel_height = 600
        padding = 20
        title_height = 100
        
        scenes = story_data["scenes"]
        total_height = title_height + (panel_height + padding) * len(scenes) + padding
        
        # Create webtoon canvas
        webtoon = Image.new('RGB', (panel_width + 2 * padding, total_height), 'white')
        
        # Add title (we'll keep it simple for now)
        current_y = padding
        
        # Add each scene
        for i, (scene, img) in enumerate(zip(scenes, scene_images)):
            if img:
                # Resize image to fit panel
                img_resized = img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
                webtoon.paste(img_resized, (padding, current_y))
            
            current_y += panel_height + padding
        
        return webtoon

def main():
    st.set_page_config(
        page_title="Educational Webtoon Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎭 Educational Webtoon Generator")
    st.markdown("Create engaging educational webtoons for kids using AI!")
    
    # Initialize generator
    generator = WebtoonGenerator()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Load characters
        characters_dict = generator.load_characters()
        
        if not characters_dict:
            st.warning("No characters found. Please ensure character PNG files are in the 'characters/' directory.")
            return
        
        st.subheader("👥 Select Characters")
        selected_characters = []
        
        for char_name, char_images in characters_dict.items():
            if st.checkbox(f"{char_name} ({len(char_images)} assets)", key=f"char_{char_name}"):
                selected_characters.append(char_name)
                
                # Show character preview
                if char_images:
                    try:
                        img = Image.open(char_images[0])
                        st.image(img, caption=char_name, width=100)
                    except Exception as e:
                        st.error(f"Error loading {char_name}: {e}")
        
        st.subheader("📖 Story Settings")
        num_scenes = st.slider("Number of Scenes", 3, 10, 6)
        difficulty = st.selectbox("Difficulty Level", ["Preschool", "Elementary", "Middle School"])
        art_style = st.selectbox("Art Style", ["cartoon", "anime", "cute", "colorful"])
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Story Concept")
        concept = st.text_area(
            "Enter the educational concept or topic you want to teach:",
            placeholder="Example: How photosynthesis works, The water cycle, Basic addition, Friendship and kindness...",
            height=100
        )
        
        if st.button("🎬 Generate Webtoon", type="primary", disabled=not (concept and selected_characters)):
            if not concept:
                st.error("Please enter a story concept!")
                return
            if not selected_characters:
                st.error("Please select at least one character!")
                return
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Generate story outline
            status_text.text("🤖 Generating story outline...")
            progress_bar.progress(20)
            
            story_data = generator.generate_story_outline(
                concept, selected_characters, num_scenes, difficulty
            )
            
            if not story_data:
                st.error("Failed to generate story outline")
                return
            
            # Step 2: Generate images for each scene
            status_text.text("🎨 Generating scene images...")
            scene_images = []
            
            if story_data and "scenes" in story_data:
                for i, scene in enumerate(story_data["scenes"]):
                    progress = 20 + (60 * (i + 1) / len(story_data["scenes"]))
                    progress_bar.progress(int(progress))
                    status_text.text(f"🎨 Generating image for scene {i + 1}...")
                    
                    scene_img = generator.generate_scene_image(
                        scene["visual_description"],
                        scene["characters"],
                        art_style
                    )
                    scene_images.append(scene_img)
                    
                    # Small delay to avoid rate limiting
                    time.sleep(1)
            
            # Step 3: Create webtoon layout
            status_text.text("📱 Creating webtoon layout...")
            progress_bar.progress(90)
            
            webtoon_image = generator.create_webtoon_layout(story_data, scene_images)
            
            progress_bar.progress(100)
            status_text.text("✅ Webtoon generated successfully!")
            
            # Display results
            st.success("🎉 Your educational webtoon is ready!")
            
            # Store in session state for display
            st.session_state.story_data = story_data
            st.session_state.scene_images = scene_images
            st.session_state.webtoon_image = webtoon_image
    
    with col2:
        st.header("🎯 Selected Characters")
        if selected_characters:
            for char in selected_characters:
                st.write(f"✅ {char}")
        else:
            st.write("No characters selected")
    
    # Display generated content
    if hasattr(st.session_state, 'story_data') and st.session_state.story_data:
        st.header("📚 Generated Story")
        
        story = st.session_state.story_data
        if story and isinstance(story, dict):
            st.subheader(f"📖 {story.get('title', 'Educational Story')}")
            st.write(f"**Concept:** {story.get('concept', '')}")
            st.write(f"**Target Age:** {story.get('target_age', '')}")
            
            # Scene-by-scene display
            if hasattr(st.session_state, 'scene_images') and "scenes" in story:
                for i, (scene, img) in enumerate(zip(story["scenes"], st.session_state.scene_images)):
                    st.subheader(f"Scene {scene['scene_number']}: {scene['location']}")
                    
                    scene_col1, scene_col2 = st.columns([1, 1])
                    
                    with scene_col1:
                        if img:
                            st.image(img, caption=f"Scene {i + 1}", use_column_width=True)
                        else:
                            st.write("Image generation failed")
                    
                    with scene_col2:
                        st.write(f"**Characters:** {', '.join(scene['characters'])}")
                        st.write(f"**Dialogue:** {scene['dialogue']}")
                        st.write(f"**Action:** {scene['action']}")
                        st.write(f"**Educational Point:** {scene['educational_point']}")
                    
                    st.divider()
            
            # Full webtoon display
            if hasattr(st.session_state, 'webtoon_image') and st.session_state.webtoon_image:
                st.header("📱 Complete Webtoon")
                st.image(
                    st.session_state.webtoon_image,
                    caption="Full Educational Webtoon",
                    use_column_width=True
                )
                
                # Download button
                buf = io.BytesIO()
                st.session_state.webtoon_image.save(buf, format='PNG')
                byte_im = buf.getvalue()
                
                st.download_button(
                    label="📥 Download Webtoon",
                    data=byte_im,
                    file_name=f"educational_webtoon_{story.get('title', 'story').replace(' ', '_')}.png",
                    mime="image/png"
                )

if __name__ == "__main__":
    main()
