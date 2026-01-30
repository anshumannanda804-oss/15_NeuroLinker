"""
NeuroLinker - Main Application
AI-Powered Decision Management System with Advanced Analytics & Learning
"""

import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
import os
import time
from auth import AuthenticationManager, render_login_page
from database import db
from decision_recorder import DecisionRecorder, QuickChat
from suggestions_engine import SuggestionEngine, ViewDecisionsAssistant
from groq import Groq
import json
from streamlit_lottie import st_lottie
import requests
from PIL import Image, ImageDraw
import io
from voice_system import init_voice_system, render_voice_button_with_feedback, process_voice_input, render_voice_controls
import re

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
client = Groq(api_key=GROQ_API_KEY)


def detect_language(text: str) -> str:
    """
    Detect if text is in Hindi or English
    Returns 'hi' for Hindi, 'en' for English (default)
    """
    if not text:
        return 'en'
    
    # Devanagari script range (Hindi characters)
    devanagari_pattern = re.compile('[\u0900-\u097F]')
    
    # Count Devanagari characters
    devanagari_count = len(devanagari_pattern.findall(text))
    
    # If more than 20% of characters are Devanagari, it's Hindi
    if devanagari_count > len(text) * 0.2:
        return 'hi'
    
    return 'en'

# Page configuration - Minimal UI
st.set_page_config(
    page_title="NeuroLinker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Enhanced custom CSS with animations and modern design
st.markdown("""
<style>
    /* Hide sidebar navigation */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main container */
    .main-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header styling */
    .header-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        animation: slideIn 0.6s ease-out;
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
    }
    
    .header-title p {
        margin: 10px 0 0 0;
        opacity: 0.9;
        font-size: 1.1em;
    }
    
    /* Section header styling */
    h2 {
        color: #764ba2;
        border-bottom: 3px solid #667eea;
        padding-bottom: 12px;
        margin-bottom: 25px !important;
        font-weight: 700 !important;
    }
    
    /* Chat message styling */
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .chat-message {
        padding: 15px 18px;
        border-radius: 12px;
        margin: 12px 0;
        animation: fadeIn 0.4s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20px;
        border-bottom-right-radius: 4px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .ai-message {
        background: white;
        color: #333;
        margin-right: 20px;
        border: 1px solid #e0e0e0;
        border-bottom-left-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Card styling */
    .feature-card {
        background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 15px 0;
        border: 2px solid #667eea;
        border-left: 6px solid #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        transition: all 0.3s ease;
        animation: slideUp 0.5s ease-out;
    }
    
    .feature-card h3 {
        color: #764ba2;
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1.4em;
        font-weight: 700;
    }
    
    .feature-card p {
        color: #555;
        margin: 0;
        line-height: 1.6;
        font-size: 0.95em;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.25);
        background: linear-gradient(135deg, #f0f4ff 0%, #fff0f7 100%);
        border-color: #764ba2;
    }
    
    /* Lottie animation container styling */
    .lottie-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%);
        border-radius: 15px;
        padding: 20px 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        cursor: pointer !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        cursor: pointer !important;
    }
    
    .stButton > button:active {
        transform: translateY(0);
        cursor: pointer !important;
    }
    
    .stButton > button:disabled {
        cursor: not-allowed !important;
        opacity: 0.6;
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button {
        border-radius: 10px 10px 0 0;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Stat boxes */
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stat-value {
        font-size: 2.5em;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .stat-label {
        opacity: 0.9;
        font-size: 0.95em;
    }
    
    /* Success/warning styling */
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 15px;
        color: #155724;
        margin: 15px 0;
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 15px;
        color: #856404;
        margin: 15px 0;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
    }
</style>
""", unsafe_allow_html=True)


# Function to load Lottie animations from URL with timeout
@st.cache_data
def load_lottie_url(url, timeout=5):
    """Load Lottie animation from URL with timeout and error handling"""
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        return None
    return None


# Lottie animation URLs - High reliability animations from LottieFiles
LOTTIE_BRAIN = "https://assets2.lottiefiles.com/packages/lf20_jvgwbczs.json"
LOTTIE_ROBOT = "https://assets5.lottiefiles.com/packages/lf20_h3s4lgq4.json"
LOTTIE_DATA = "https://assets10.lottiefiles.com/packages/lf20_iq4dqvmy.json"
LOTTIE_TECH = "https://assets6.lottiefiles.com/packages/lf20_h1p0oi0f.json"
LOTTIE_CELEBRATE = "https://assets4.lottiefiles.com/packages/lf20_mf4yemoy.json"
LOTTIE_LOADING = "https://assets5.lottiefiles.com/packages/lf20_5rKM1R.json"
LOTTIE_SUCCESS = "https://assets1.lottiefiles.com/packages/lf20_jjqweb4r.json"
LOTTIE_ANALYSIS = "https://assets6.lottiefiles.com/packages/lf20_iq4dqvmy.json"
LOTTIE_THINKING = "https://assets2.lottiefiles.com/packages/lf20_gtje04cj.json"
LOTTIE_CHART = LOTTIE_DATA  # Use data animation for charts
LOTTIE_CHAT = "https://assets7.lottiefiles.com/packages/lf20_zngvwjob.json"  # Chat/message animation
LOTTIE_SETTINGS = "https://assets3.lottiefiles.com/packages/lf20_kxn9qwkl.json"  # Settings/gear animation
LOTTIE_DASHBOARD = "https://assets9.lottiefiles.com/packages/lf20_cse3xfkh.json"  # Dashboard/analytics
LOTTIE_CHECK = "https://assets4.lottiefiles.com/packages/lf20_z8nxqzcm.json"  # Checkmark animation


# Initialize session state
AuthenticationManager.init_session()


def render_landing_page(user_name: str):
    """Render main landing page with enhanced UI and animations"""
    
    st.markdown("""
    <div class="header-title">
        <h1>🧠 NeuroLinker</h1>
        <p>AI-Powered Intelligent Decision Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(f"Welcome back, **{user_name}**! 👋")
    
    # Quick stats with animations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        decisions_count = len(db.get_user_decisions(st.session_state.user_id)) if 'user_id' in st.session_state else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Decisions Recorded</div>
            <div class="stat-value">{decisions_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-label">Learning Active</div>
            <div class="stat-value">✓</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-label">AI Insights</div>
            <div class="stat-value">↑</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-label">Latest: Today</div>
            <div class="stat-value">📅</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # All Features with animations
    st.markdown("## 🎯 Features")
    col1, col2, col3 = st.columns(3, gap="large")
    
    # Feature 1: Record Decision
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: #764ba2; margin: 0 0 15px 0; font-size: 1.3em;">📝 Record Decision</h3>
        """, unsafe_allow_html=True)
        
        # Show large animation with multiple fallbacks
        record_animation = load_lottie_url(LOTTIE_ROBOT)
        if record_animation:
            st_lottie(record_animation, height=200, key="record_anim", speed=1)
        else:
            st.markdown('<div style="text-align: center; font-size: 5em; padding: 30px;">🤖</div>', unsafe_allow_html=True)
        
        st.markdown("""
                <p style="color: #555; margin: 15px 0; line-height: 1.5; font-size: 0.95em;">Document choices with AI assistance. Have natural conversations about your goals and reasoning.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 Start Recording", key="record_btn", use_container_width=True):
            st.session_state.current_page = "record_decision"
            st.rerun()
    
    # Feature 2: Review Decisions
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: #764ba2; margin: 0 0 15px 0; font-size: 1.3em;">📊 Review Decisions</h3>
        """, unsafe_allow_html=True)
        
        # Show large animation with multiple fallbacks
        data_animation = load_lottie_url(LOTTIE_DATA)
        if data_animation:
            st_lottie(data_animation, height=200, key="chart_anim", speed=1)
        else:
            st.markdown('<div style="text-align: center; font-size: 5em; padding: 30px;">📈</div>', unsafe_allow_html=True)
        
        st.markdown("""
                <p style="color: #555; margin: 15px 0; line-height: 1.5; font-size: 0.95em;">Review past decisions and understand patterns in your decision-making journey with analytics.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Review Decisions", key="view_btn", use_container_width=True):
            st.session_state.current_page = "view_decisions"
            st.rerun()
    
    # Feature 3: AI Insights
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: #764ba2; margin: 0 0 15px 0; font-size: 1.3em;">🚀 AI Insights</h3>
        """, unsafe_allow_html=True)
        
        # Show large animation with multiple fallbacks
        tech_animation = load_lottie_url(LOTTIE_TECH)
        if tech_animation:
            st_lottie(tech_animation, height=200, key="rocket_anim", speed=1)
        else:
            st.markdown('<div style="text-align: center; font-size: 5em; padding: 30px;">🚀</div>', unsafe_allow_html=True)
        
        st.markdown("""
                <p style="color: #555; margin: 10px 0; line-height: 1.5;">Get AI-powered suggestions based on your decision patterns, constraints, and historical outcomes.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Get Suggestions", key="suggest_btn", use_container_width=True):
            st.session_state.current_page = "suggestions"
            st.rerun()
    
    st.markdown("---")
    
    # Professional Navigation Bar
    st.markdown("""
    <style>
        .nav-bar-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 15px 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-bar-title {
            color: white;
            font-size: 1.1em;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .nav-buttons {
            display: flex;
            gap: 10px;
        }
    </style>
    <div class="nav-bar-container">
        <span class="nav-bar-title">⚡ Quick Navigation</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons in a clean row
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4, gap="small")
    
    with nav_col1:
        if st.button("💬 Chat History", key="nav_chat", use_container_width=True):
            st.session_state.current_page = "chat_history"
            st.rerun()
    
    with nav_col2:
        if st.button("📊 Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with nav_col3:
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
    
    with nav_col4:
        if st.button("🚪 Logout", key="nav_logout", use_container_width=True, type="primary", help="Sign out from your account"):
            AuthenticationManager.logout()


def render_record_decision_page(user_id: int, user_name: str):
    """Render decision recording interface"""
    
    # Get user's language preference
    # Get user's language preference
    user_prefs = db.get_user_preferences(user_id)
    user_language = user_prefs.get('language', 'en') if user_prefs else 'en'
    
    # Initialize session state variables safely FIRST
    if 'decision_chat' not in st.session_state:
        st.session_state.decision_chat = []
    if 'recorder_started' not in st.session_state:
        st.session_state.recorder_started = False
    
    # Get current decision status early
    if 'decision_recorder' not in st.session_state or st.session_state.decision_recorder is None:
        st.session_state.decision_recorder = DecisionRecorder(language=user_language)
    
    recorder = st.session_state.decision_recorder
    
    # Ensure recorder is initialized
    if recorder is None:
        recorder = DecisionRecorder(language=user_language)
        st.session_state.decision_recorder = recorder
    
    # Initialize chat if needed
    if not st.session_state.recorder_started and len(st.session_state.decision_chat) == 0:
        opening_msg = recorder.start_conversation()
        st.session_state.decision_chat = [{"role": "assistant", "content": opening_msg}]
        st.session_state.recorder_started = True
    
    # Try to extract any missed information from full conversation
    if len(st.session_state.decision_chat) >= 4:  # Only after several exchanges
        recorder._extract_from_full_conversation()
    
    collected_data = recorder.get_collected_data()
    missing = recorder.get_missing_fields()
    is_complete = recorder.is_decision_complete()
    
    # Top Navigation Bar
    st.markdown("""
    <style>
        .nav-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 12px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-title {
            color: white;
            font-size: 1.3em;
            font-weight: 600;
            margin: 0;
        }
        .nav-status {
            color: rgba(255,255,255,0.9);
            font-size: 0.85em;
            margin-top: 4px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    nav_status = "✅ Ready to Save!" if is_complete else f"⏳ {len(missing)} items needed"
    
    st.markdown(f"""
    <div class="nav-bar">
        <div>
            <div class="nav-title">💬 Chat About Your Decision</div>
            <div class="nav-status">{nav_status}</div>
        </div>
        <div style="text-align: right;">
            <span style="color: white; font-weight: 600;">{len(st.session_state.decision_chat)} messages</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons - always visible at top
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 1.2, 0.8, 0.8])
    
    with nav_col1:
        if st.button("← Home", key="nav_home_top", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
    
    with nav_col2:
        if st.button("🌐 Lang", key="nav_lang_top", use_container_width=True):
            st.session_state.show_lang_menu = not st.session_state.get('show_lang_menu', False)
    
    with nav_col3:
        if st.button("ℹ️ Info", key="nav_info_top", use_container_width=True):
            st.session_state.show_decision_info = not st.session_state.get('show_decision_info', False)
    
    with nav_col4:
        if st.button("🔄 New", key="nav_new_top", use_container_width=True):
            st.session_state.decision_recorder = None
            st.session_state.recorder_started = False
            st.session_state.decision_chat = []
            st.rerun()
    
    with nav_col5:
        if is_complete:
            save_button_label = "✅ Save Decision"
            if st.button(save_button_label, key="save_decision_nav", use_container_width=True, type="primary"):
                try:
                    # Validate collected data
                    if not collected_data.get('description'):
                        st.error("❌ Decision description is missing")
                        st.stop()
                    
                    # Prepare decision data
                    decision_data = {
                        'title': collected_data.get('description', 'Untitled')[:100],
                        'description': collected_data.get('description', ''),
                        'goal': collected_data.get('goal', ''),
                        'constraints': collected_data.get('constraints', []),
                        'alternatives': collected_data.get('alternatives', []),
                        'final_choice': collected_data.get('final_choice', ''),
                        'reasoning': collected_data.get('reasoning', ''),
                        'expected_outcome': collected_data.get('expected_outcome', ''),
                        'memory_layer': 'private',
                        'outcome_status': 'pending'
                    }
                    
                    # Save to database
                    decision_id = db.save_decision(user_id, decision_data)
                    
                    if not decision_id:
                        st.error("❌ Failed to generate decision ID. Please try again.")
                        st.stop()
                    
                    # Verify decision was saved
                    saved_decision = db.get_decision(user_id, decision_id)
                    if not saved_decision:
                        st.error("❌ Failed to verify saved decision. Please try again.")
                        st.stop()
                    
                    # Save chat history linked to decision
                    chat_saved_count = 0
                    if len(st.session_state.decision_chat) > 0:
                        for i, msg in enumerate(st.session_state.decision_chat):
                            # Pair user messages with AI responses
                            if msg.get('role') == 'user' and i + 1 < len(st.session_state.decision_chat):
                                next_msg = st.session_state.decision_chat[i + 1]
                                if next_msg.get('role') == 'assistant':
                                    try:
                                        db.save_chat_message(
                                            user_id,
                                            msg.get('content', ''),
                                            next_msg.get('content', ''),
                                            chat_type="decision_recording",
                                            decision_id=decision_id
                                        )
                                        chat_saved_count += 1
                                    except Exception as chat_err:
                                        st.warning(f"⚠️ Could not save some chat messages: {str(chat_err)}")
                                        # Continue saving other messages
                    
                    # Show success message
                    st.success(f"✅ Decision saved successfully! 🎉 ({chat_saved_count} chat exchanges saved)")
                    st.balloons()
                    
                    # Clear session state for next recording
                    st.session_state.decision_recorder = None
                    st.session_state.recorder_started = False
                    st.session_state.decision_chat = []
                    
                    # Navigate to landing after a short delay
                    time.sleep(2)
                    st.session_state.current_page = "landing"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving decision: {str(e)}")
                    import traceback
                    st.write(traceback.format_exc())
        else:
            # Show disabled button with helpful message
            disabled_label = f"⏳ Need: {', '.join(missing[:2])}" if missing else "✅ Save"
            st.button(disabled_label[:50], key="save_disabled_btn", use_container_width=True, disabled=True, help=f"Required: {', '.join(missing)}" if missing else "Ready to save!")
            
            # Show what's missing below the disabled button
            if missing:
                with st.info("⏳ **Incomplete** - Please provide:", icon="ℹ️"):
                    for i, field in enumerate(missing, 1):
                        st.markdown(f"**{i}.** {field}")
    
    st.markdown("---")
    
    # Info panel - collapsible below nav
    if st.session_state.get('show_decision_info', False):
        with st.expander("📋 Collected Information", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Collected:**")
                if collected_data['description']:
                    st.markdown(f"📌 **Decision:** {collected_data['description']}")
                if collected_data['goal']:
                    st.markdown(f"🎯 **Goal:** {collected_data['goal']}")
                if collected_data['constraints']:
                    st.markdown(f"⚠️ **Constraints:** {', '.join(collected_data['constraints'])}")
            
            with col2:
                st.markdown("**✅ Collected:**")
                if collected_data['alternatives']:
                    st.markdown(f"🔄 **Alternatives:** {', '.join(collected_data['alternatives'])}")
                if collected_data['final_choice']:
                    st.markdown(f"✔️ **Choice:** {collected_data['final_choice']}")
                if collected_data['reasoning']:
                    st.markdown(f"💡 **Reasoning:** {collected_data['reasoning']}")
            
            if missing:
                st.warning(f"⚠️ **Still needed to complete:** {', '.join(missing)}")
            else:
                st.success("✅ All information collected! Ready to save.")
        
        st.markdown("---")
    
    # Main chat area with animation
    col_chat_anim, col_chat = st.columns([1, 4])
    with col_chat_anim:
        chat_anim = load_lottie_url(LOTTIE_CHAT)
        if chat_anim:
            st_lottie(chat_anim, height=80, key="record_chat", speed=1)
        else:
            st.markdown('<div style="font-size: 2.5em; text-align: center;">💬</div>', unsafe_allow_html=True)
    
    with col_chat:
        st.markdown("### 💬 Conversation")
    
    # Chat history in a nice styled container
    st.markdown("""
    <style>
        .chat-container-custom {
            background: white;
            border-radius: 12px;
            padding: 15px;
            height: 400px;
            overflow-y: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Display chat history
    with st.container(border=True):
        st.markdown('<div style="height: 350px; overflow-y: auto;">', unsafe_allow_html=True)
        for msg in st.session_state.decision_chat:
            if msg['role'] == 'user':
                with st.chat_message("user"):
                    st.write(msg['content'])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg['content'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    # User input stays at bottom - clean and focused
    st.markdown("---")
    
    # Voice input and text input with columns
    col_voice, col_text = st.columns([1, 4], gap="small")
    
    user_input = None
    
    with col_voice:
        voice_clicked, _ = render_voice_button_with_feedback()
        
        # Handle voice input immediately and auto-process
        if voice_clicked and st.session_state.get('voice_enabled', False):
            # Process voice input directly
            transcribed = process_voice_input(st.session_state.voice_system)
            if transcribed:
                # Automatically process the voice input without waiting for text input
                user_input = transcribed
                # Don't store in session, just use it directly below
            else:
                st.stop()  # Stop if voice input failed
    
    with col_text:
        # Only show text input if voice wasn't just used
        if user_input is None:
            user_input = st.chat_input("💬 Tell me more about your decision... (type 'save' to save when complete)", key="chat_input")
    
    if user_input:
        user_input_lower = user_input.lower().strip()
        
        # AUTO-DETECT LANGUAGE from user input
        detected_lang = detect_language(user_input)
        
        # If language changed from default, reinitialize recorder with new language
        if hasattr(st.session_state.decision_recorder, 'language') and st.session_state.decision_recorder.language != detected_lang:
            st.session_state.decision_recorder = DecisionRecorder(language=detected_lang)
            # Reset chat but keep the opening message in new language
            opening_msg = st.session_state.decision_recorder.start_conversation()
            st.session_state.decision_chat = [{"role": "assistant", "content": opening_msg}]
            st.session_state.recorder_started = True
        
        # Check for save command
        save_commands = ['save', 'save decision', 'save now', 'save my decision', 'done', 'submit', 'पूरा', 'save करो', 'हो गया']
        is_save_command = any(user_input_lower == cmd.lower() or user_input_lower.startswith(cmd.lower()) for cmd in save_commands)
        
        if is_save_command:
            # User wants to save
            # Show user message
            with st.chat_message("user"):
                st.write(f"💾 {user_input}")
            
            # Check if decision is complete
            if is_complete:
                st.success("✅ All information collected! Saving your decision...")
                
                try:
                    # Validate collected data
                    if not collected_data.get('description'):
                        st.error("❌ Decision description is missing")
                        st.stop()
                    
                    # Prepare decision data
                    decision_data = {
                        'title': collected_data.get('description', 'Untitled')[:100],
                        'description': collected_data.get('description', ''),
                        'goal': collected_data.get('goal', ''),
                        'constraints': collected_data.get('constraints', []),
                        'alternatives': collected_data.get('alternatives', []),
                        'final_choice': collected_data.get('final_choice', ''),
                        'reasoning': collected_data.get('reasoning', ''),
                        'expected_outcome': collected_data.get('expected_outcome', ''),
                        'memory_layer': 'private',
                        'outcome_status': 'pending'
                    }
                    
                    # Save to database
                    decision_id = db.save_decision(user_id, decision_data)
                    
                    if not decision_id:
                        st.error("❌ Failed to generate decision ID. Please try again.")
                        st.stop()
                    
                    # Verify decision was saved
                    saved_decision = db.get_decision(user_id, decision_id)
                    if not saved_decision:
                        st.error("❌ Failed to verify saved decision. Please try again.")
                        st.stop()
                    
                    # Save chat history linked to decision
                    chat_saved_count = 0
                    if len(st.session_state.decision_chat) > 0:
                        for i, msg in enumerate(st.session_state.decision_chat):
                            # Pair user messages with AI responses
                            if msg.get('role') == 'user' and i + 1 < len(st.session_state.decision_chat):
                                next_msg = st.session_state.decision_chat[i + 1]
                                if next_msg.get('role') == 'assistant':
                                    try:
                                        db.save_chat_message(
                                            user_id,
                                            msg.get('content', ''),
                                            next_msg.get('content', ''),
                                            chat_type="decision_recording",
                                            decision_id=decision_id
                                        )
                                        chat_saved_count += 1
                                    except Exception as chat_err:
                                        st.warning(f"⚠️ Could not save some chat messages: {str(chat_err)}")
                    
                    # Show success message
                    st.success(f"✅ Decision saved successfully! 🎉 ({chat_saved_count} chat exchanges saved)")
                    st.balloons()
                    
                    # Add AI confirmation message
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write("🎉 **Your decision has been saved successfully!** Your insights have been preserved and I'll use them to provide better suggestions in the future. Thank you for using NeuroLinker!")
                    
                    st.session_state.decision_chat.append({"role": "assistant", "content": "Your decision has been saved successfully!"})
                    
                    # Clear session state for next recording
                    st.session_state.decision_recorder = None
                    st.session_state.recorder_started = False
                    st.session_state.decision_chat = []
                    
                    # Navigate to landing after a short delay
                    time.sleep(2)
                    st.session_state.current_page = "landing"
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving decision: {str(e)}")
                    
                    # Show AI message about error
                    with st.chat_message("assistant", avatar="🤖"):
                        st.write(f"❌ Sorry, I couldn't save your decision. Error: {str(e)}")
            else:
                # Decision not complete
                with st.chat_message("assistant", avatar="🤖"):
                    missing_text = f"⏳ I still need to collect some more information before we can save. Please provide:\n\n" + "\n".join([f"• {item}" for item in missing])
                    st.write(missing_text)
                
                st.session_state.decision_chat.append({"role": "user", "content": user_input})
                st.session_state.decision_chat.append({"role": "assistant", "content": missing_text})
                st.rerun()
        else:
            # Regular chat message
            # Add user message to display
            with st.chat_message("user"):
                st.write(user_input)
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                ai_response = recorder.get_ai_response(user_input)
            
            # Add AI response to display
            with st.chat_message("assistant", avatar="🤖"):
                st.write(ai_response)
            
            # Add to chat history
            st.session_state.decision_chat.append({"role": "user", "content": user_input})
            st.session_state.decision_chat.append({"role": "assistant", "content": ai_response})
            
            # Save chat to database
            db.save_chat_message(
                user_id,
                user_input,
                ai_response,
                chat_type="decision_recording"
            )
            
            st.rerun()
    
    # Floating save section - collapsible and unobtrusive
    st.markdown("---")
    
    # Create three columns for action buttons - keep bottom clean
    col_actions = st.columns([1, 1, 1, 1])
    
    with col_actions[0]:
        if st.button("← Back Home", key="back_home_chat", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
    
    with col_actions[1]:
        if st.button("🔄 New Chat", key="new_chat_action", use_container_width=True):
            st.session_state.decision_recorder = None
            st.session_state.recorder_started = False
            st.session_state.decision_chat = []
            st.rerun()
    
    with col_actions[2]:
        if is_complete:
            if st.button("✅ Save Decision", key="save_decision_chat", use_container_width=True, type="primary"):
                # Prepare decision data
                decision_data = {
                    'title': collected_data['description'][:50] if collected_data['description'] else "Untitled",
                    'description': collected_data['description'],
                    'goal': collected_data['goal'],
                    'constraints': collected_data['constraints'],
                    'alternatives': collected_data['alternatives'],
                    'final_choice': collected_data['final_choice'],
                    'reasoning': collected_data['reasoning'],
                    'expected_outcome': collected_data['expected_outcome'],
                    'memory_layer': 'private',
                    'outcome_status': 'pending'
                }
                
                # Save to database
                decision_id = db.save_decision(user_id, decision_data)
                
                # Save chat history linked to decision
                for msg in st.session_state.decision_chat[1:]:  # Skip opening message
                    if msg['role'] == 'user':
                        idx = st.session_state.decision_chat.index(msg)
                        if idx + 1 < len(st.session_state.decision_chat):
                            ai_msg = st.session_state.decision_chat[idx + 1]
                            db.save_chat_message(
                                user_id,
                                msg['content'],
                                ai_msg['content'],
                                chat_type="decision_recording",
                                decision_id=decision_id
                            )
                
                # Animated success state
                col_anim, col_msg = st.columns([1, 2])
                with col_anim:
                    success_anim = load_lottie_url(LOTTIE_SUCCESS)
                    if success_anim:
                        st_lottie(success_anim, height=100, key="save_success", speed=1)
                    else:
                        st.markdown('<div style="font-size: 3em; text-align: center;">✅</div>', unsafe_allow_html=True)
                
                with col_msg:
                    st.markdown("""
                    <div style="padding: 20px; background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); 
                                border-radius: 10px; border-left: 4px solid #22c55e;">
                        <h3 style="color: #166534; margin: 0;">🎉 Decision Recorded!</h3>
                        <p style="color: #15803d; margin: 5px 0;">Your decision has been saved and is now part of NeuroLinker's learning profile.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.balloons()
                time.sleep(2)
                st.session_state.current_page = "landing"
                st.rerun()


def render_view_decisions_page(user_id: int, user_name: str):
    """Render decision viewing interface"""
    
    # Header with animation
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        analysis_anim = load_lottie_url(LOTTIE_ANALYSIS)
        if analysis_anim:
            st_lottie(analysis_anim, height=80, key="view_analysis_anim", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">📊</div>', unsafe_allow_html=True)
    
    with col_title:
        st.markdown("## 📖 Review Your Decisions")
    
    # Get user's decisions
    decisions = db.get_user_decisions(user_id)
    
    if not decisions:
        col_empty1, col_empty2 = st.columns([1, 2])
        with col_empty1:
            thinking_anim = load_lottie_url(LOTTIE_THINKING)
            if thinking_anim:
                st_lottie(thinking_anim, height=120, key="empty_thinking", speed=1)
            else:
                st.markdown('<div style="font-size: 4em; text-align: center;">🤔</div>', unsafe_allow_html=True)
        with col_empty2:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%); 
                        border-radius: 10px; border-left: 4px solid #667eea;">
                <h3 style="color: #764ba2; margin-top: 0;">No Decisions Yet</h3>
                <p>Start by recording a decision to see your collection here!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("← Back to Home", key="back_home_decisions"):
            st.session_state.current_page = "landing"
            st.rerun()
        return
    
    # Initialize assistant
    if 'view_assistant' not in st.session_state:
        st.session_state.view_assistant = ViewDecisionsAssistant(decisions)
        st.session_state.view_chat = []
    
    assistant = st.session_state.view_assistant
    
    # Display opening message if first time
    if not st.session_state.view_chat:
        opening = assistant.start_review_session()
        st.session_state.view_chat.append({"role": "assistant", "content": opening})
    
    # Stats bar
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; padding: 15px; margin-bottom: 20px;
                color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
        <span style="font-weight: 600; font-size: 1.1em;">📚 {len(decisions)} Decisions Recorded</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat
    with st.container(border=True):
        st.markdown('<div style="height: 350px; overflow-y: auto;">', unsafe_allow_html=True)
        for msg in st.session_state.view_chat:
            if msg['role'] == 'user':
                with st.chat_message("user"):
                    st.write(msg['content'])
            else:
                with st.chat_message("assistant", avatar="📊"):
                    st.write(msg['content'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User input
    user_query = st.chat_input("Ask about your decisions...")
    
    if user_query:
        with st.chat_message("user"):

            st.write(user_query)
        
        with st.spinner("Reviewing your decisions..."):
            response = assistant.get_review_response(user_query)
        
        with st.chat_message("assistant"):
            st.write(response)
        
        st.session_state.view_chat.append({"role": "user", "content": user_query})
        st.session_state.view_chat.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    st.divider()
    
    # Decision list sidebar
    with st.expander("📋 Your Decisions Summary"):
        for decision in decisions:
            st.markdown(f"""
            **{decision['title']}**
            - Created: {decision['created_at'][:10]}
            - Status: {decision['outcome_status']}
            - Description: {decision['description'][:100]}...
            """)
    
    if st.button("← Back", key="back_decisions_detail"):
        st.session_state.current_page = "landing"
        st.rerun()


def render_suggestions_page(user_id: int, user_name: str):
    """Render AI suggestions interface"""
    
    # Header with animation
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        rocket_anim = load_lottie_url(LOTTIE_TECH)
        if rocket_anim:
            st_lottie(rocket_anim, height=80, key="suggestions_rocket", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">🚀</div>', unsafe_allow_html=True)
    
    with col_title:
        st.markdown("## 🚀 AI Suggestions & Insights")
    
    # Get user's decisions for context
    decisions = db.get_user_decisions(user_id)
    
    if not decisions:
        col_empty1, col_empty2 = st.columns([1, 2])
        with col_empty1:
            thinking_anim = load_lottie_url(LOTTIE_THINKING)
            if thinking_anim:
                st_lottie(thinking_anim, height=120, key="suggestions_empty", speed=1)
            else:
                st.markdown('<div style="font-size: 4em; text-align: center;">💭</div>', unsafe_allow_html=True)
        with col_empty2:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%); 
                        border-radius: 10px; border-left: 4px solid #667eea;">
                <h3 style="color: #764ba2; margin-top: 0;">No Decisions Yet</h3>
                <p>Record some decisions to get personalized AI suggestions!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("← Back to Home", key="back_home_suggestions"):
            st.session_state.current_page = "landing"
            st.rerun()
        return
    
    # Initialize suggestion engine
    if 'suggestion_engine' not in st.session_state:
        st.session_state.suggestion_engine = SuggestionEngine(decisions)
        st.session_state.suggestion_chat = []
    
    engine = st.session_state.suggestion_engine
    
    # Display opening if first time
    if not st.session_state.suggestion_chat:
        opening = engine.start_suggestion_session(decisions[-1] if decisions else None)
        st.session_state.suggestion_chat.append({"role": "assistant", "content": opening})
    
    # Info bar with animation
    col_info_anim, col_info, col_settings = st.columns([1, 3, 1])
    with col_info_anim:
        info_anim = load_lottie_url(LOTTIE_CELEBRATE)
        if info_anim:
            st_lottie(info_anim, height=80, key="suggestions_info", speed=1)
        else:
            st.markdown('<div style="font-size: 2.5em; text-align: center;">✨</div>', unsafe_allow_html=True)
    
    with col_info:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; padding: 15px;
                    color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
            <span style="font-weight: 600; font-size: 1.1em;">✨ AI-Powered Insights</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_settings:
        with st.popover("⚙️ Settings", use_container_width=True):
            st.markdown("### Animation Speed")
            anim_speed = st.slider(
                "Adjust animation speed:",
                min_value=0.5,
                max_value=2.0,
                value=1.0,
                step=0.1,
                key="suggestion_anim_speed",
                help="Control the playback speed of animations"
            )
            st.caption(f"Current speed: {anim_speed}x")
    
    # Display chat
    with st.container(border=True):
        st.markdown('<div style="height: 350px; overflow-y: auto;">', unsafe_allow_html=True)
        for msg in st.session_state.suggestion_chat:
            if msg['role'] == 'user':
                with st.chat_message("user"):
                    st.write(msg['content'])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg['content'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # User input
    user_input = st.chat_input("Ask for suggestions or insights...")
    
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.spinner("Analyzing your decisions..."):
            response = engine.get_suggestion_response(user_input, decisions[-1] if decisions else None)
        
        with st.chat_message("assistant"):
            st.write(response)
        
        st.session_state.suggestion_chat.append({"role": "user", "content": user_input})
        st.session_state.suggestion_chat.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    st.divider()
    
    # Additional analysis options
    tab1, tab2 = st.tabs(["Pattern Analysis", "Decision Deep Dive"])
    
    with tab1:
        if st.button("📊 Analyze My Decision Patterns", key="analyze_patterns"):
            with st.spinner("Analyzing patterns..."):
                analysis = engine.get_pattern_analysis()
                st.markdown(analysis)
    
    with tab2:
        selected_decision = st.selectbox(
            "Select a decision to analyze:",
            [(d['title'], d['id']) for d in decisions],
            format_func=lambda x: x[0]
        )
        
        if st.button("🔍 Analyze This Decision", key="analyze_selected"):
            with st.spinner("Deep diving..."):
                analysis = engine.get_decision_analysis(
                    next(d for d in decisions if d['id'] == selected_decision[1])
                )
                st.markdown(analysis)
    
    if st.button("← Back", key="back_suggestions_final"):
        st.session_state.current_page = "landing"
        st.rerun()


def render_chat_history_page(user_id: int):
    """Render chat history with adaptive learning insights"""
    
    # Header with animation
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        data_anim = load_lottie_url(LOTTIE_DATA)
        if data_anim:
            st_lottie(data_anim, height=80, key="history_data", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">📊</div>', unsafe_allow_html=True)
    
    with col_title:
        st.markdown("## 💬 Chat & Learning History")
    
    # Get chat history
    chat_history = db.get_chat_history(user_id, include_hidden=False)
    
    if not chat_history:
        col_empty1, col_empty2 = st.columns([1, 2])
        with col_empty1:
            loading_anim = load_lottie_url(LOTTIE_LOADING)
            if loading_anim:
                st_lottie(loading_anim, height=120, key="history_empty", speed=1)
            else:
                st.markdown('<div style="font-size: 4em; text-align: center;">📭</div>', unsafe_allow_html=True)
        with col_empty2:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%); 
                        border-radius: 10px; border-left: 4px solid #667eea;">
                <h3 style="color: #764ba2; margin-top: 0;">No Chat History Yet</h3>
                <p>Start recording decisions to build your learning profile!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("← Back"):
            st.session_state.current_page = "landing"
            st.rerun()
        return
    
    # Stats bar
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; padding: 15px; margin-bottom: 20px;
                color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
        <span style="font-weight: 600; font-size: 1.1em;">💾 {len(chat_history)} Conversations Recorded</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chat_type_filter = st.selectbox(
            "Filter by type:",
            ["All", "decision_recording", "suggestion", "reflection"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Most Recent", "Oldest First"]
        )
    
    with col3:
        search_query = st.text_input("🔍 Search conversations:")
    
    st.divider()
    
    # Filter and sort
    filtered_chats = chat_history
    
    if chat_type_filter != "All":
        filtered_chats = [c for c in filtered_chats if c.get('chat_type') == chat_type_filter]
    
    if search_query:
        filtered_chats = [c for c in filtered_chats if search_query.lower() in c.get('user_message', '').lower() or search_query.lower() in c.get('ai_response', '').lower()]
    
    if sort_by == "Oldest First":
        filtered_chats = list(reversed(filtered_chats))
    
    # Display chats with animations
    st.markdown(f"### Showing {len(filtered_chats)} conversations")
    
    for idx, chat in enumerate(filtered_chats):
        with st.expander(f"💬 {chat['timestamp'][:10]} - {chat['user_message'][:60]}...", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**You:**")
                st.info(chat['user_message'])
            
            with col2:
                st.markdown("**AI:**")
                st.success(chat['ai_response'])
            
            # Show metadata
            st.caption(f"Type: {chat.get('chat_type', 'general')} | Time: {chat['timestamp']}")
    
    st.divider()
    
    # Learning insights with animation
    col_insight_anim, col_insight = st.columns([1, 4])
    with col_insight_anim:
        insight_anim = load_lottie_url(LOTTIE_BRAIN)
        if insight_anim:
            st_lottie(insight_anim, height=100, key="learning_insights", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">🧠</div>', unsafe_allow_html=True)
    
    with col_insight:
        st.markdown("### 🧠 AI Learning Insights")
    
    total_chats = len(filtered_chats)
    recent_chats = len([c for c in chat_history if (datetime.now() - datetime.fromisoformat(c['timestamp'])).days < 7])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total Conversations</div>
            <div class="stat-value">{total_chats}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">This Week</div>
            <div class="stat-value">{recent_chats}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Learning Status</div>
            <div class="stat-value">🔄</div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("← Back"):
        st.session_state.current_page = "landing"
        st.rerun()


def render_analytics_page(user_id: int):
    """Render analytics and insights dashboard"""
    
    # Animated header
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        chart_anim = load_lottie_url(LOTTIE_CHART)
        if chart_anim:
            st_lottie(chart_anim, height=80, key="analytics_chart", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">📊</div>', unsafe_allow_html=True)
    
    with col_title:
        st.markdown("## 📊 Decision Analytics & AI Learning Dashboard")
    
    decisions = db.get_user_decisions(user_id)
    
    if not decisions:
        col_empty1, col_empty2 = st.columns([1, 2])
        with col_empty1:
            thinking_anim = load_lottie_url(LOTTIE_THINKING)
            if thinking_anim:
                st_lottie(thinking_anim, height=120, key="analytics_empty", speed=1)
            else:
                st.markdown('<div style="font-size: 4em; text-align: center;">🤔</div>', unsafe_allow_html=True)
        with col_empty2:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%); 
                        border-radius: 10px; border-left: 4px solid #667eea;">
                <h3 style="color: #764ba2; margin-top: 0;">No Data Yet</h3>
                <p>Start recording decisions to unlock AI analytics and insights!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("← Back"):
            st.session_state.current_page = "landing"
            st.rerun()
        return
    
    # Overview metrics with enhanced styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; padding: 15px; margin-bottom: 20px;
                color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
        <span style="font-weight: 600; font-size: 1.1em;">📈 Performance Overview</span>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Total Decisions</div>
            <div class="stat-value">{len(decisions)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        completed = len([d for d in decisions if d.get('outcome_status') == 'completed'])
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Completed</div>
            <div class="stat-value">{completed}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending = len([d for d in decisions if d.get('outcome_status') == 'pending'])
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Pending</div>
            <div class="stat-value">{pending}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_constraints = sum(len(d.get('constraints', [])) for d in decisions) / len(decisions) if decisions else 0
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Avg Constraints</div>
            <div class="stat-value">{avg_constraints:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Adaptive Learning Section with animation
    col_adapt_anim, col_adapt = st.columns([1, 4])
    with col_adapt_anim:
        adapt_anim = load_lottie_url(LOTTIE_ROBOT)
        if adapt_anim:
            st_lottie(adapt_anim, height=100, key="adaptive_learning", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">🤖</div>', unsafe_allow_html=True)
    
    with col_adapt:
        st.markdown("### 🤖 AI Adaptive Learning Status")
    
    # Learning metrics
    chat_history = db.get_chat_history(user_id, include_hidden=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Interactions Tracked:**")
        st.write(f"- Total conversations: {len(chat_history)}")
        st.write(f"- Decision recordings: {len([d for d in decisions if d])}")
        st.write(f"- Feedback sessions: {completed}")
    
    with col2:
        st.markdown("**AI Learning Progress:**")
        learning_progress = min(100, (len(decisions) * 10) + (len(chat_history) * 2))
        st.progress(min(learning_progress / 100, 1.0))
        st.write(f"Learning Level: {min(learning_progress, 100):.0f}%")
    
    st.markdown("The AI learns from your:")
    st.write("✅ Decision patterns and preferences")
    st.write("✅ Constraints and limitations you face")
    st.write("✅ Outcomes and results of past decisions")
    st.write("✅ Feedback and interactions")
    
    st.divider()
    
    # Decision distribution
    st.markdown("### 📉 Decision Insights")
    
    tab1, tab2, tab3 = st.tabs(["Status Distribution", "Recent Decisions", "Decision Types"])
    
    with tab1:
        status_counts = {}
        for d in decisions:
            status = d.get('outcome_status', 'pending')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            st.bar_chart(status_counts)
    
    with tab2:
        st.markdown("**Most Recent Decisions:**")
        for d in decisions[-5:]:
            st.markdown(f"""
            <div class="feature-card">
            <h4>{d.get('title', 'Untitled')}</h4>
            <p>{d.get('description', '')[:100]}...</p>
            <small>Status: {d.get('outcome_status', 'pending')} | Created: {d.get('created_at', '')[:10]}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        # Category analysis
        categories = {}
        for d in decisions:
            title = d.get('title', 'Other')[:20]
            categories[title] = categories.get(title, 0) + 1
        
        if categories:
            st.write("Decision categories recorded:")
            for cat, count in categories.items():
                st.write(f"- {cat}: {count}")
    
    if st.button("← Back"):
        st.session_state.current_page = "landing"
        st.rerun()


def render_settings_page(user_id: int):
    """Render privacy and settings page"""
    
    # Animated header
    col_anim, col_title = st.columns([1, 3])
    with col_anim:
        tech_anim = load_lottie_url(LOTTIE_TECH)
        if tech_anim:
            st_lottie(tech_anim, height=80, key="settings_tech", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">⚙️</div>', unsafe_allow_html=True)
    
    with col_title:
        st.markdown("## ⚙️ Privacy & Settings")
    
    # Settings intro bar
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; padding: 15px; margin-bottom: 20px;
                color: white; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
        <span style="font-weight: 600; font-size: 1.1em;">🎯 Manage Your NeuroLinker Experience</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current preferences
    prefs = db.get_user_preferences(user_id)
    
    # Language section with animation and styling
    col_lang_anim, col_lang = st.columns([1, 4])
    with col_lang_anim:
        lang_anim = load_lottie_url(LOTTIE_DATA)
        if lang_anim:
            st_lottie(lang_anim, height=100, key="language_settings", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">🌐</div>', unsafe_allow_html=True)
    
    with col_lang:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f5f7ff 0%, #fff5f9 100%); 
                    border-radius: 10px; padding: 20px;
                    border-left: 4px solid #667eea;">
            <h3 style="color: #764ba2; margin-top: 0;">🌐 Language Support</h3>
            <p style="color: #666;">NeuroLinker automatically detects your language! Write in English or Hindi, and I'll respond in the same language.</p>
            <p style="color: #999; font-size: 0.9em;">✅ English (अंग्रेजी) | ✅ Hindi (हिंदी)</p>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Privacy section with animation and styling
    col_privacy_anim, col_privacy = st.columns([1, 4])
    with col_privacy_anim:
        privacy_anim = load_lottie_url(LOTTIE_TECH)
        if privacy_anim:
            st_lottie(privacy_anim, height=100, key="privacy_settings", speed=1)
        else:
            st.markdown('<div style="font-size: 3em; text-align: center;">🔒</div>', unsafe_allow_html=True)
    
    with col_privacy:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fef5f9 0%, #fff5f9 100%); 
                    border-radius: 10px; padding: 20px;
                    border-left: 4px solid #ec4899;">
            <h3 style="color: #be185d; margin-top: 0;">🔒 Data Privacy</h3>
        """, unsafe_allow_html=True)
        
        share_with_ai = st.checkbox(
            "🤖 Allow AI to use my past decisions for suggestions",
            value=prefs.get('share_data_with_ai', False),
            help="When enabled, AI will have access to your past decisions to provide better suggestions."
        )
        
        view_chat = st.checkbox(
            "💬 Let me view my chat history with the system",
            value=prefs.get('view_chat_history', True),
            help="When enabled, you can review all conversations you've had with the AI."
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Save button
    if st.button("💾 Save Preferences", use_container_width=True):
        db.update_user_preferences(user_id, {
            'share_data_with_ai': share_with_ai,
            'view_chat_history': view_chat
        })
        
        col_anim, col_msg = st.columns([1, 2])
        with col_anim:
            success_anim = load_lottie_url(LOTTIE_SUCCESS)
            if success_anim:
                st_lottie(success_anim, height=100, key="settings_success", speed=1)
            else:
                st.markdown('<div style="font-size: 3em; text-align: center;">✅</div>', unsafe_allow_html=True)
        
        with col_msg:
            st.markdown("""
            <div style="padding: 15px; background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%); 
                        border-radius: 10px; border-left: 4px solid #22c55e;">
                <p style="color: #166534; margin: 0; font-weight: 600;">✅ Preferences saved successfully!</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Chat history section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #f5f7ff 100%); 
                border-radius: 10px; padding: 20px;
                border-left: 4px solid #0284c7;">
        <h3 style="color: #0c4a6e; margin-top: 0;">📋 Chat History</h3>
    """, unsafe_allow_html=True)
    
    if view_chat:
        chat_history = db.get_chat_history(user_id, include_hidden=False)
        
        if chat_history:
            st.write(f"**Total conversations:** {len(chat_history)}")
            
            if st.checkbox("Show detailed chat history"):
                with st.container(border=True):
                    st.markdown('<div style="height: 350px; overflow-y: auto;">', unsafe_allow_html=True)
                    for chat in chat_history[-10:]:  # Show last 10
                        with st.expander(f"💬 Chat - {chat['timestamp']}"):
                            st.write(f"**You:** {chat['user_message'][:100]}...")
                            st.write(f"**AI:** {chat['ai_response'][:100]}...")
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No chat history yet.")
    else:
        st.info("💬 Chat history is disabled in your privacy settings.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Account information section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fef08a 100%); 
                border-radius: 10px; padding: 20px;
                border-left: 4px solid #d97706;">
        <h3 style="color: #92400e; margin-top: 0;">📊 Account Information</h3>
    """, unsafe_allow_html=True)
    
    user = db.get_user(user_id)
    if user:
        st.write(f"**📧 Email:** {user['email']}")
        st.write(f"**👤 Name:** {user.get('full_name', 'Not set')}")
        st.write(f"**📅 Member Since:** {user['created_at'][:10]}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Bottom navigation
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.current_page = "landing"
            st.rerun()
    
    with nav_col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()


# Main app logic
def main():
    # Check authentication
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "landing"
    
    # Initialize voice system
    init_voice_system()
    
    user_info = AuthenticationManager.get_current_user()
    
    # Store user_id in session for global access
    st.session_state.user_id = user_info['user_id']
    
    # Route to appropriate page
    if st.session_state.current_page == "landing":
        render_landing_page(user_info['name'])
    
    elif st.session_state.current_page == "record_decision":
        render_record_decision_page(user_info['user_id'], user_info['name'])
    
    elif st.session_state.current_page == "view_decisions":
        render_view_decisions_page(user_info['user_id'], user_info['name'])
    
    elif st.session_state.current_page == "suggestions":
        render_suggestions_page(user_info['user_id'], user_info['name'])
    
    elif st.session_state.current_page == "chat_history":
        render_chat_history_page(user_info['user_id'])
    
    elif st.session_state.current_page == "analytics":
        render_analytics_page(user_info['user_id'])
    
    elif st.session_state.current_page == "settings":
        render_settings_page(user_info['user_id'])


if __name__ == "__main__":
    main()
