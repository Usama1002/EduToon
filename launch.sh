#!/bin/bash

# Educational Webtoon Generator Launcher Script

echo "🎭 Educational Webtoon Generator"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Function to install requirements
install_requirements() {
    echo "📦 Installing Python packages..."
    if command -v pip3 &> /dev/null; then
        pip3 install -r requirements.txt
    else
        pip install -r requirements.txt
    fi
}

# Function to check if requirements are installed
check_requirements() {
    python3 -c "
import sys
try:
    import streamlit, google.genai, PIL, dotenv
    print('✅ All required packages are installed!')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Missing package: {e}')
    sys.exit(1)
"
}

# Function to check environment setup
check_environment() {
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo "📝 Please edit .env and add your Gemini API key"
            return 1
        else
            echo "❌ .env.example not found"
            return 1
        fi
    fi
    
    if grep -q "your_gemini_api_key_here" .env; then
        echo "⚠️  Please update your Gemini API key in .env file"
        return 1
    fi
    
    echo "✅ Environment setup looks good!"
    return 0
}

# Function to check character assets
check_characters() {
    if [ ! -d "characters" ]; then
        echo "⚠️  Characters directory not found"
        echo "📁 Creating characters directory..."
        mkdir -p characters
        echo "   Please add character PNG files in subdirectories"
        return 1
    fi
    
    char_count=$(find characters -name "*.png" | wc -l)
    if [ $char_count -eq 0 ]; then
        echo "⚠️  No character PNG files found in characters/ directory"
        return 1
    fi
    
    echo "✅ Found $char_count character assets!"
    return 0
}

# Function to run the application
run_app() {
    echo "🚀 Starting Educational Webtoon Generator..."
    echo "   Open your browser to: http://localhost:8501"
    echo "   Press Ctrl+C to stop the application"
    echo ""
    
    if command -v streamlit &> /dev/null; then
        streamlit run app_enhanced.py
    else
        python3 -m streamlit run app_enhanced.py
    fi
}

# Main execution
case "${1:-run}" in
    "install")
        echo "🔧 Installing dependencies..."
        install_requirements
        ;;
    "check")
        echo "🔍 Checking system setup..."
        check_requirements
        check_environment
        check_characters
        ;;
    "setup")
        echo "🔧 Setting up Educational Webtoon Generator..."
        install_requirements
        if check_requirements; then
            check_environment
            check_characters
            echo ""
            echo "✅ Setup complete! Run './launch.sh' to start the application"
        fi
        ;;
    "run")
        echo "🔍 Checking prerequisites..."
        
        # Check requirements
        if ! check_requirements; then
            echo "Installing missing packages..."
            install_requirements
            if ! check_requirements; then
                echo "❌ Failed to install required packages"
                exit 1
            fi
        fi
        
        # Check environment
        if ! check_environment; then
            echo "❌ Please configure your .env file first"
            exit 1
        fi
        
        # Check characters (non-blocking)
        check_characters
        
        # Run the application
        run_app
        ;;
    *)
        echo "Usage: $0 [install|check|setup|run]"
        echo ""
        echo "Commands:"
        echo "  install  - Install Python dependencies"
        echo "  check    - Check system setup"
        echo "  setup    - Complete setup process"
        echo "  run      - Run the application (default)"
        echo ""
        echo "Quick start: $0 setup"
        ;;
esac
