#!/bin/bash

echo "🔧 Setting up Gemini Image Generation Test Environment"
echo "================================================"

# Install required packages
echo "📦 Installing required Python packages..."
pip3 install -r requirements_test.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating example .env file..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env file and add your GOOGLE_API_KEY:"
    echo "   GOOGLE_API_KEY=your_actual_api_key_here"
    echo ""
else
    echo "✅ .env file exists"
fi

echo ""
echo "🚀 Ready to run image generation tests!"
echo "Run: python3 test_image_generation.py"
