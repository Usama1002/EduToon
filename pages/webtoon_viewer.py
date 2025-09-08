#!/usr/bin/env python3
"""
Webtoon Viewer - Clean display page for generated webtoons
"""

import streamlit as st
import json
from pathlib import Path
from PIL import Image
import io

def main():
    st.set_page_config(
        page_title="Educational Webtoon Viewer",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for clean webtoon display
    st.markdown("""
    <style>
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0;
    }
    .webtoon-title {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .webtoon-container {
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 20px;
        margin: 20px 0;
    }
    .stApp > header {
        display: none;
    }
    .stDeployButton {
        display: none;
    }
    #MainMenu {
        display: none;
    }
    footer {
        display: none;
    }
    .stToolbar {
        display: none;
    }
    .fullscreen-button {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: #2E86AB;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 20px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get webtoon data from URL parameters or session state
    query_params = st.query_params
    
    # Check if we have webtoon data
    if hasattr(st.session_state, 'webtoon_image') and st.session_state.webtoon_image:
        story_data = getattr(st.session_state, 'story_data', {})
        webtoon_image = st.session_state.webtoon_image
        
        # Display title
        title = story_data.get('title', 'Educational Webtoon')
        st.markdown(f'<h1 class="webtoon-title">📚 {title}</h1>', unsafe_allow_html=True)
        
        # Display webtoon in container
        with st.container():
            st.markdown('<div class="webtoon-container">', unsafe_allow_html=True)
            
            # Main webtoon display
            st.image(
                webtoon_image,
                use_column_width=True,
                caption=""
            )
            
            # Educational info at bottom
            if 'concept' in story_data:
                st.markdown("---")
                st.markdown(f"**📖 Educational Concept:** {story_data['concept']}")
            
            if 'target_age' in story_data:
                st.markdown(f"**🎯 Target Age:** {story_data['target_age']}")
            
            if 'learning_objectives' in story_data:
                st.markdown("**📋 What You'll Learn:**")
                for obj in story_data['learning_objectives']:
                    st.markdown(f"• {obj}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Fullscreen note
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("💡 **Tip:** Use browser's fullscreen mode (F11) for the best reading experience!")
    
    else:
        # No webtoon data available
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.error("📱 No webtoon data found!")
        st.info("Please generate a webtoon first using the main application.")
        
        if st.button("🔙 Go Back to Generator"):
            st.switch_page("app_enhanced.py")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
