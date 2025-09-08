#!/bin/bash

# Educational Webtoon Generator Launcher
echo "🎨 Starting Educational Webtoon Generator..."
echo "================================================"

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing..."
    pip3 install streamlit
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your GOOGLE_API_KEY"
    echo "Example:"
    echo "GOOGLE_API_KEY=your_api_key_here"
    echo ""
    echo "You can still run the app, but you'll need to enter your API key manually."
    echo ""
fi

# Launch the enhanced application
echo "🚀 Launching Enhanced Webtoon Generator..."
echo "📱 The app will open in your browser automatically"
echo "🌐 URL: http://localhost:8501"
echo ""
echo "To stop the application, press Ctrl+C"
echo "================================================"

streamlit run app_enhanced.py --server.port 8501 --server.headless true
