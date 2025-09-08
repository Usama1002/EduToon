import streamlit as st
import os
from PIL import Image
import io
import base64
import time
from pathlib import Path
from dotenv import load_dotenv

# Import local modules
from config import *
from utils import *

# Load environment variables
load_dotenv()

# Import Google GenAI
try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Google GenAI library not installed. Please run: pip install google-genai")
    st.stop()

class EnhancedWebtoonGenerator:
    def __init__(self):
        """Initialize the Enhanced Webtoon Generator."""
        self.client = None
        self.setup_client()
        
    def setup_client(self):
        """Setup the Google GenAI client with error handling."""
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or not validate_api_key(api_key):
            st.error("❌ Invalid or missing GEMINI_API_KEY. Please check your .env file.")
            st.info("📝 Create a .env file with: GEMINI_API_KEY=your_api_key_here")
            return
            
        try:
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
                st.success("✅ Connected to Vertex AI")
            else:
                self.client = genai.Client(api_key=api_key)
                st.success("✅ Connected to Gemini Developer API")
                
        except Exception as e:
            st.error(f"❌ Failed to initialize GenAI client: {str(e)}")
    
    def generate_educational_story(self, concept: str, characters: List[str], num_scenes: int, difficulty: str) -> Optional[Dict]:
        """Generate educational story with enhanced error handling."""
        if not self.client:
            st.error("API client not initialized")
            return None
        
        prompt = create_story_prompt(concept, characters, num_scenes, difficulty)
        
        try:
            with st.spinner("🤖 Generating educational story..."):
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL_TEXT,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json',
                        temperature=STORY_CONFIG["temperature"],
                        max_output_tokens=STORY_CONFIG["max_output_tokens"]
                    )
                )
                
                if not response.text:
                    st.error("No response received from API")
                    return None
                
                story_data = json.loads(response.text)
                
                # Validate story structure
                if not validate_story_data(story_data):
                    st.error("Generated story data is invalid")
                    return None
                
                return story_data
                
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse story response: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Failed to generate story: {str(e)}")
            return None
    
    def get_character_reference_images(self, character_names: List[str]) -> List[Image.Image]:
        """Get reference images for specified characters."""
        reference_images = []
        
        # Load character assets
        characters_dict = load_character_assets()
        
        for char_name in character_names:
            if char_name in characters_dict and characters_dict[char_name]["assets"]:
                # Use the first available asset as reference
                char_image_path = characters_dict[char_name]["assets"][0]
                try:
                    char_image = Image.open(char_image_path)
                    # Resize if too large (for API efficiency)
                    if char_image.size[0] > 512 or char_image.size[1] > 512:
                        char_image.thumbnail((512, 512), Image.Resampling.LANCZOS)
                    reference_images.append(char_image)
                    st.info(f"🎭 Using character reference: {char_name} from {Path(char_image_path).name}")
                except Exception as e:
                    st.warning(f"⚠️ Could not load character image for {char_name}: {e}")
        
        return reference_images
    
    def generate_scene_image_with_retry(self, scene_description: str, characters: List[str], style: str = "cartoon") -> Optional[Image.Image]:
        """Generate scene image with character reference images and retry logic."""
        if not self.client:
            return None
        
        # Get character reference images
        reference_images = self.get_character_reference_images(characters)
        
        # Create enhanced prompt that references the character images
        if reference_images:
            prompt = f"""Create a Korean webtoon-style scene based on the provided character reference images. 

Scene Description: {scene_description}

Characters to include: {', '.join(characters)}

Style Requirements:
- Korean webtoon art style ({style})
- Use the provided character images as visual references for the characters' appearance
- Maintain the characters' distinctive visual features from the reference images
- Bright, colorful, educational and child-friendly
- Vertical panel format suitable for webtoons
- Clean line art with vibrant colors

Keep the characters' original designs but place them in the described scene context."""
        else:
            # Fallback to text-only prompt if no character images available
            prompt = create_image_prompt(scene_description, characters, style)
        
        for attempt in range(IMAGE_CONFIG["max_retries"]):
            try:
                # Prepare contents: prompt + reference images
                contents = [prompt] + reference_images  # type: ignore
                
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL_IMAGE,
                    contents=contents,
                )
                
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
                
                if attempt < IMAGE_CONFIG["max_retries"] - 1:
                    time.sleep(IMAGE_CONFIG["retry_delay"])
                    
            except Exception as e:
                if attempt < IMAGE_CONFIG["max_retries"] - 1:
                    st.warning(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(IMAGE_CONFIG["retry_delay"])
                else:
                    st.error(f"Failed to generate image after {IMAGE_CONFIG['max_retries']} attempts: {str(e)}")
        
        # Return error placeholder image
        return create_error_image(WEBTOON_CONFIG["panel_width"], WEBTOON_CONFIG["panel_height"])
    
    def create_enhanced_webtoon_layout(self, story_data: Dict, scene_images: List[Optional[Image.Image]]) -> Optional[Image.Image]:
        """Create an enhanced webtoon layout with title and better spacing."""
        if not story_data or "scenes" not in story_data or not scene_images:
            return None
        
        scenes = story_data["scenes"]
        panel_width = WEBTOON_CONFIG["panel_width"]
        panel_height = WEBTOON_CONFIG["panel_height"]
        padding = WEBTOON_CONFIG["padding"]
        title_height = WEBTOON_CONFIG["title_height"]
        
        # Calculate total height
        total_height = title_height + (panel_height + padding) * len(scenes) + padding * 2
        
        # Create webtoon canvas
        webtoon = Image.new('RGB', (panel_width + 2 * padding, total_height), 'white')
        
        # Add title section (simplified for now)
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(webtoon)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
        except:
            title_font = ImageFont.load_default()
        
        title_text = story_data.get("title", "Educational Webtoon")
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (panel_width + 2 * padding - title_width) // 2
        
        draw.text((title_x, padding), title_text, fill='black', font=title_font)
        
        # Add scenes
        current_y = title_height + padding
        
        for i, (scene, img) in enumerate(zip(scenes, scene_images)):
            if img:
                # Resize image to fit panel while maintaining aspect ratio
                img_resized = img.resize((panel_width, panel_height), Image.Resampling.LANCZOS)
                webtoon.paste(img_resized, (padding, current_y))
            else:
                # Create placeholder
                placeholder = create_error_image(panel_width, panel_height, f"Scene {i+1}")
                webtoon.paste(placeholder, (padding, current_y))
            
            current_y += panel_height + padding
        
        return webtoon

def main():
    st.set_page_config(
        page_title="Educational Webtoon Generator",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        padding: 1rem 0;
    }
    .character-preview {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
    }
    .scene-container {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🎭 Educational Webtoon Generator</h1>', unsafe_allow_html=True)
    st.markdown("Transform learning concepts into engaging Korean-style webtoons for kids!")
    
    # Initialize generator
    generator = EnhancedWebtoonGenerator()
    
    if not generator.client:
        st.stop()
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Load character assets
        characters_dict = load_character_assets()
        
        if not characters_dict:
            st.warning("⚠️ No characters found in the 'characters/' directory.")
            st.info("Please ensure character PNG files are organized in subdirectories.")
            return
        
        st.subheader("👥 Select Characters")
        selected_characters = []
        
        # Character selection with previews
        for char_name, char_data in characters_dict.items():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.checkbox(f"Select {char_name}", key=f"char_{char_name}", label_visibility="hidden"):
                    selected_characters.append(char_name)
            
            with col2:
                st.write(f"**{char_name}** ({char_data['count']} assets)")
                
                # Show preview image
                if char_data["assets"]:
                    try:
                        preview_img = create_character_preview(char_data["assets"][0])
                        if preview_img:
                            st.image(preview_img, width=80)
                    except Exception as e:
                        st.error(f"Error loading preview: {e}")
        
        st.subheader("📖 Story Configuration")
        num_scenes = st.slider("Number of Scenes", 
                              WEBTOON_CONFIG["min_scenes"], 
                              WEBTOON_CONFIG["max_scenes"], 
                              STORY_CONFIG["default_scenes"])
        
        difficulty = st.selectbox("Educational Level", DIFFICULTY_LEVELS)
        art_style = st.selectbox("Art Style", IMAGE_CONFIG["supported_styles"])
        
        st.subheader("🎨 Generation Options")
        auto_save = st.checkbox("Auto-save generated content", value=True)
        show_individual_scenes = st.checkbox("Show individual scenes", value=True)
    
    # Main content area
    st.header("📝 Educational Concept")
    
    # Concept input with examples
    concept_examples = [
        "How plants make food through photosynthesis",
        "The water cycle and weather patterns",
        "Basic addition and subtraction with fun examples",
        "The importance of friendship and kindness",
        "How the solar system works",
        "The life cycle of a butterfly",
        "Why we need to recycle and protect the environment"
    ]
    
    example_text = "**Example concepts:** " + " • ".join(concept_examples)
    st.markdown(example_text)
    
    concept = st.text_area(
        "Enter the educational concept or topic:",
        placeholder="Example: How photosynthesis works - plants use sunlight, water, and carbon dioxide to make their own food...",
        height=120,
        help="Be specific about what you want to teach. Include key points you want covered."
    )
    
    # Generation controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        generate_button = st.button(
            "🎬 Generate Educational Webtoon", 
            type="primary", 
            disabled=not (concept and selected_characters),
            help="Generate a complete educational webtoon based on your inputs"
        )
    
    with col2:
        if st.button("🔄 Clear All"):
            for key in list(st.session_state.keys()):
                if isinstance(key, str) and key.startswith(('story_', 'scene_', 'webtoon_')):
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        st.write(f"**Selected:** {len(selected_characters)} characters")
    
    # Validation messages
    if generate_button:
        if not concept.strip():
            st.error("❌ Please enter an educational concept!")
            st.stop()
        
        if not selected_characters:
            st.error("❌ Please select at least one character!")
            st.stop()
        
        if len(concept.strip()) < 10:
            st.warning("⚠️ Please provide a more detailed concept description.")
            st.stop()
    
    # Generation process
    if generate_button:
        with st.container():
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Generate story
                status_text.info("🤖 Creating educational story outline...")
                progress_bar.progress(10)
                
                story_data = generator.generate_educational_story(
                    concept, selected_characters, num_scenes, difficulty
                )
                
                if not story_data:
                    st.error("❌ Failed to generate story. Please try again.")
                    st.stop()
                
                progress_bar.progress(30)
                status_text.success("✅ Story outline created!")
                
                # Step 2: Generate scene images
                status_text.info("🎨 Generating scene illustrations...")
                scene_images = []
                
                scenes = story_data.get("scenes", [])
                for i, scene in enumerate(scenes):
                    progress = 30 + (50 * (i + 1) / len(scenes))
                    progress_bar.progress(int(progress))
                    status_text.info(f"🎨 Creating illustration for scene {i + 1}/{len(scenes)}...")
                    
                    scene_img = generator.generate_scene_image_with_retry(
                        scene["visual_description"],
                        scene["characters"],
                        art_style
                    )
                    scene_images.append(scene_img)
                    
                    # Rate limiting
                    if i < len(scenes) - 1:
                        time.sleep(1)
                
                # Step 3: Create webtoon layout
                status_text.info("📱 Assembling complete webtoon...")
                progress_bar.progress(85)
                
                webtoon_image = generator.create_enhanced_webtoon_layout(story_data, scene_images)
                
                progress_bar.progress(100)
                status_text.success("🎉 Educational webtoon generated successfully!")
                
                # Save to session state
                st.session_state.story_data = story_data
                st.session_state.scene_images = scene_images
                st.session_state.webtoon_image = webtoon_image
                
                # Auto-save if enabled
                if auto_save:
                    try:
                        save_path = save_generated_content(story_data, scene_images)
                        st.success(f"💾 Content saved to: {save_path}")
                    except Exception as e:
                        st.warning(f"⚠️ Auto-save failed: {e}")
    
    # Display generated content
    if hasattr(st.session_state, 'story_data') and st.session_state.story_data:
        st.header("📚 Generated Educational Story")
        
        story = st.session_state.story_data
        
        # Story header
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"📖 {story.get('title', 'Educational Story')}")
            st.write(f"**📚 Concept:** {story.get('concept', '')}")
            st.write(f"**🎯 Target Age:** {story.get('target_age', '')}")
            
            if "learning_objectives" in story:
                st.write("**📋 Learning Objectives:**")
                for obj in story["learning_objectives"]:
                    st.write(f"• {obj}")
        
        with col2:
            st.metric("Scenes Created", len(story.get("scenes", [])))
            st.metric("Characters Used", len(selected_characters))
        
        # Individual scenes display
        if show_individual_scenes and hasattr(st.session_state, 'scene_images'):
            st.subheader("🎬 Individual Scenes")
            
            scenes = story.get("scenes", [])
            for i, (scene, img) in enumerate(zip(scenes, st.session_state.scene_images)):
                with st.container():
                    st.markdown(f'<div class="scene-container">', unsafe_allow_html=True)
                    
                    scene_col1, scene_col2 = st.columns([1, 1])
                    
                    with scene_col1:
                        st.markdown(f"**Scene {scene['scene_number']}: {scene.get('scene_title', scene['location'])}**")
                        if img:
                            st.image(img, caption=f"Scene {i + 1}", use_column_width=True)
                        else:
                            st.error("Image generation failed for this scene")
                    
                    with scene_col2:
                        st.write(f"**📍 Location:** {scene['location']}")
                        st.write(f"**👥 Characters:** {', '.join(scene['characters'])}")
                        st.write(f"**💬 Dialogue:** {scene['dialogue']}")
                        st.write(f"**🎭 Action:** {scene['action']}")
                        st.write(f"**🎓 Educational Point:** {scene['educational_point']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.divider()
        
        # Complete webtoon display
        if hasattr(st.session_state, 'webtoon_image') and st.session_state.webtoon_image:
            st.header("📱 Complete Educational Webtoon")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.image(
                    st.session_state.webtoon_image,
                    caption="Full Educational Webtoon - Korean Style Layout",
                    use_column_width=True
                )
            
            with col2:
                st.markdown("### 📥 Download Options")
                
                # Download button for webtoon
                buf = io.BytesIO()
                st.session_state.webtoon_image.save(buf, format='PNG')
                byte_im = buf.getvalue()
                
                filename = sanitize_filename(f"educational_webtoon_{story.get('title', 'story')}")
                
                st.download_button(
                    label="📱 Download Complete Webtoon",
                    data=byte_im,
                    file_name=f"{filename}.png",
                    mime="image/png",
                    help="Download the complete webtoon as PNG"
                )
                
                # Download story data
                story_json = json.dumps(story, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download Story Data",
                    data=story_json.encode('utf-8'),
                    file_name=f"{filename}_story.json",
                    mime="application/json",
                    help="Download story data as JSON"
                )
                
                st.markdown("### 📊 Story Statistics")
                st.metric("Total Scenes", len(story.get("scenes", [])))
                st.metric("Average Words per Scene", 
                         sum(len(scene.get("dialogue", "").split()) + len(scene.get("action", "").split()) 
                             for scene in story.get("scenes", [])) // max(len(story.get("scenes", [])), 1))

if __name__ == "__main__":
    main()
