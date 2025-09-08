#!/usr/bin/env python3
"""
EduToon Viewer - Professional fullscreen display for generated webtoons
"""

import streamlit as st
import json
from pathlib import Path
from PIL import Image
import io

def main():
    st.set_page_config(
        page_title="EduToon Viewer",
        page_icon="📱",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Professional CSS for clean webtoon display
    st.markdown("""
    <style>
    /* Global styling */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    .webtoon-title {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 2rem;
        border-radius: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .webtoon-container {
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e1e8ed;
    }
    
    .educational-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* Hide Streamlit elements */
    .stApp > header {display: none;}
    .stDeployButton {display: none;}
    #MainMenu {display: none;}
    footer {display: none;}
    .stToolbar {display: none;}
    
    /* Image container */
    .webtoon-image {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        margin: 1rem 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Temporary debug section
    st.write("🔍 Debug Information:")
    st.write(f"Session state has {len(st.session_state)} keys")
    
    # Show all session state keys for debugging
    if st.checkbox("Show all session state keys (debug)"):
        for key in st.session_state.keys():
            value_type = type(st.session_state[key]).__name__
            st.write(f"- {key}: {value_type}")
    
    # Check if we have webtoon data
    if hasattr(st.session_state, 'webtoon_image') and st.session_state.webtoon_image:
        st.success("✅ Webtoon image found in session state!")
        story_data = getattr(st.session_state, 'story_data', {})
        webtoon_image = st.session_state.webtoon_image
        
        # Display title
        title = story_data.get('title', 'Educational Webtoon')
        st.markdown(f'<div class="webtoon-title">📚 {title}</div>', unsafe_allow_html=True)
        
        # Back button
        if st.button("🔙 Back to Generator"):
            st.switch_page("app_enhanced.py")
        
        # Main webtoon display
        st.markdown('<div class="webtoon-container">', unsafe_allow_html=True)
        
        try:
            # Display the webtoon image
            st.markdown('<div class="webtoon-image">', unsafe_allow_html=True)
            st.image(
                webtoon_image,
                use_container_width=True,
                caption=f"Educational Webtoon: {title}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying image: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Educational information
        if any(key in story_data for key in ['concept', 'target_age', 'learning_objectives']):
            st.markdown('<div class="educational-info">', unsafe_allow_html=True)
            st.markdown("### 📖 Educational Information")
            
            if 'concept' in story_data:
                st.markdown(f"**📚 Concept:** {story_data['concept']}")
            
            if 'target_age' in story_data:
                st.markdown(f"**🎯 Target Age:** {story_data['target_age']}")
            
            if 'learning_objectives' in story_data:
                st.markdown("**📋 Learning Objectives:**")
                for obj in story_data['learning_objectives']:
                    st.markdown(f"• {obj}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # No webtoon data available - provide helpful guidance
        st.error("❌ No webtoon image found in session state")
        st.markdown('<div class="webtoon-title">📱 EduToon Viewer</div>', unsafe_allow_html=True)
        
        st.warning("📱 No webtoon found!")
        st.info("To view a webtoon here, please:")
        st.markdown("""
        1. 📝 Go back to the main generator
        2. 🎨 Generate a webtoon 
        3. 📱 Click the "VIEW WEBTOON FULLSCREEN" button
        """)
        
        if st.button("🔙 Go Back to Generator"):
            st.switch_page("app_enhanced.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
