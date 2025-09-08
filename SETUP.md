# 🎭 Educational Webtoon Generator - Setup Guide

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **Gemini API Key** from Google AI Studio
3. **Character assets** (PNG files organized in directories)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Get Your Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it in your `.env` file

### 4. Run the Application

```bash
streamlit run app_enhanced.py
```

Or use the demo script:
```bash
python demo.py
```

## 📁 Character Assets Setup

The application uses character PNG files from the `characters/` directory. Each character should have its own subdirectory:

```
characters/
├── Armie/
│   ├── Armie_Asset_01.png
│   ├── Armie_Asset_02.png
│   └── ...
├── Bearnice/
│   ├── Bearnice_Expressions_01.png
│   ├── Bearnice_Expressions_02.png
│   └── ...
└── [other_characters]/
```

## 🔧 Advanced Configuration

### Using Vertex AI (Optional)

If you prefer to use Vertex AI instead of the Gemini Developer API:

1. Set up Google Cloud Project
2. Enable Vertex AI API
3. Configure authentication
4. Update your `.env`:

```
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Configuration Options

Edit `config.py` to customize:

- **Webtoon dimensions**: Panel size, padding, layout
- **Generation settings**: Temperature, max tokens, retry attempts
- **Art styles**: Available style options
- **Educational levels**: Target age groups

## 🎨 Usage Instructions

### 1. Select Characters
- Choose characters from the available assets
- Preview images help you select appropriate characters
- You can select multiple characters for your story

### 2. Configure Story
- **Number of Scenes**: 3-10 scenes (6 recommended)
- **Educational Level**: Preschool, Elementary, or Middle School
- **Art Style**: Cartoon, Anime, Cute, Colorful, or Realistic

### 3. Enter Educational Concept
Be specific about what you want to teach:

**Good examples:**
- "How photosynthesis works - plants use sunlight, water, and carbon dioxide to make their own food"
- "The water cycle: evaporation, condensation, and precipitation"
- "Basic addition using everyday objects like apples and toys"

**Avoid vague concepts:**
- "Science"
- "Math"
- "Learning"

### 4. Generate Webtoon
1. Click "Generate Educational Webtoon"
2. Wait for story generation (10-30 seconds)
3. Wait for image generation (1-2 minutes per scene)
4. Review and download your webtoon!

## 📊 Features

### Story Generation
- **AI-Powered**: Uses Gemini 2.5 Flash for intelligent story creation
- **Educational Focus**: Tailored for specific learning objectives
- **Age-Appropriate**: Content adapted to selected difficulty level
- **Character Integration**: Meaningful use of selected characters

### Image Generation
- **High Quality**: Uses Gemini image generation (Nano Banana)
- **Korean Webtoon Style**: Vertical layout optimized for mobile
- **Consistent Style**: Maintains visual coherence across scenes
- **Error Handling**: Automatic retry and fallback options

### Output Options
- **Individual Scenes**: View and download separate scene images
- **Complete Webtoon**: Full vertical layout ready for sharing
- **Story Data**: JSON export of complete story structure
- **Auto-Save**: Optional automatic saving of generated content

## 🛠️ Troubleshooting

### Common Issues

**"API client not initialized"**
- Check your API key in `.env`
- Verify the key is valid and has quota available

**"No characters found"**
- Ensure PNG files are in `characters/` subdirectories
- Check file permissions and formats

**"Image generation failed"**
- This may happen due to API rate limits
- The app will retry automatically
- Fallback placeholder images will be shown

**"Story generation failed"**
- Check your internet connection
- Verify API quota hasn't been exceeded
- Try simplifying your concept description

### Performance Tips

1. **Smaller Stories**: Start with 3-4 scenes for faster generation
2. **Simple Concepts**: Clear, specific educational topics work best
3. **Character Selection**: 2-3 characters are usually optimal
4. **Rate Limiting**: Wait between generations to avoid API limits

## 📁 File Structure

```
nano-banana/
├── app.py                 # Basic Streamlit application
├── app_enhanced.py        # Enhanced application with full features
├── config.py             # Configuration settings
├── utils.py              # Utility functions
├── demo.py               # Demo and testing script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── README.md            # Project documentation
└── characters/          # Character asset directory
    ├── Armie/
    ├── Bearnice/
    └── [other characters]/
```

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Checking System Status
```bash
python demo.py check
```

### Backup Generated Content
Generated webtoons are saved in the `output/` directory (if auto-save is enabled).

## 🎯 Educational Applications

Perfect for teaching:
- **Science Concepts**: Photosynthesis, weather, ecosystems
- **Mathematics**: Basic operations, geometry, problem-solving
- **History**: Historical events, cultural concepts
- **Language Arts**: Vocabulary, storytelling, reading comprehension
- **Social Skills**: Friendship, cooperation, empathy
- **Life Skills**: Health, safety, environmental awareness

## 💡 Tips for Best Results

1. **Be Specific**: Detailed concepts generate better stories
2. **Age-Appropriate**: Match difficulty to your target audience
3. **Character Relevance**: Choose characters that fit your story theme
4. **Scene Planning**: 4-6 scenes work well for most concepts
5. **Visual Descriptions**: The AI generates better images with detailed scene descriptions

## 🆘 Support

If you encounter issues:

1. Check this setup guide
2. Run `python demo.py check` to diagnose problems
3. Review error messages in the Streamlit interface
4. Check API quotas and limits
5. Verify character assets are properly organized

## 🔐 Security Notes

- Keep your API key secure and never commit it to version control
- The `.env` file is ignored by git by default
- Consider using environment variables in production deployments
- Monitor your API usage to avoid unexpected charges

## 🎉 Enjoy Creating!

You're now ready to create engaging educational webtoons for kids! Start with simple concepts and experiment with different characters and styles to find what works best for your educational goals.
