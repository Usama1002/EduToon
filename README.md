# Educational Webtoon Generator

A web application that creates immersive educational webtoons for kids using AI. The app combines character selection, story generation, and image creation to produce engaging learning content.

## Features

- **Character Selection**: Choose from existing character assets
- **Story Generation**: Uses Gemini 2.5 Flash to create educational storylines
- **Image Generation**: Uses Gemini Nano Banana for scene illustrations
- **Korean-style Layout**: Full-page webtoon format
- **Educational Focus**: Designed for explaining learning concepts

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Gemini API key:
   - Create a `.env` file in the project root
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Select characters from the available character gallery
2. Enter an educational concept or storyline
3. Choose story parameters (number of scenes, difficulty level)
4. Generate your webtoon!

## Character Assets

The app uses existing character PNG files located in the `characters/` directory:
- Armie (10 assets)
- Bearnice (12 expressions)
- Bogart (13 expressions)
- Brick (10 expressions)
- Grit (12 expressions)
- Oz (various assets)
- Plato (various assets)
- Stax (various assets)
- Yang (various assets)
- Yin (various assets)

## API Usage

- **Gemini 2.5 Flash**: Story and scene generation
- **Gemini Image Generation (Nano Banana)**: Scene illustration creation

## Educational Applications

Perfect for:
- Teaching science concepts
- Historical events
- Mathematical principles
- Language learning
- Social skills
- Environmental awareness
