import streamlit as st
import requests
import json

# Setup Page
st.set_page_config(page_title="Groww MF Premium", page_icon="💎", layout="centered")

# Custom CSS for Vercel-ready Premium Aesthetics (Glassmorphism + Dark Mode)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Background and Body */
    .stApp {
        background: radial-gradient(circle at top center, #1a2a6c 0%, #0c0d13 100%);
        color: #ffffff;
        font-family: 'Outfit', sans-serif;
    }

    /* Hide Streamlit elements */
    header, footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
    }

    /* Header Styling */
    .premium-header {
        text-align: center;
        background: linear-gradient(90deg, #ffffff, #8e9eab);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .premium-sub {
        text-align: center;
        color: #a0a0b0;
        font-size: 1.2rem;
        font-weight: 300;
        margin-bottom: 3rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .card-title {
        color: #5669ff;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        display: block;
    }
    
    .card-desc {
        color: #d0d0d0;
        font-size: 0.9rem;
        line-height: 1.4;
    }

    /* Chat Styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Input Styling */
    .stChatInputContainer {
        border-radius: 2rem !important;
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 2rem !important;
    }
    
    /* Central Glow Orb Wrapper */
    .orb-wrapper {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .glowing-orb {
        width: 120px;
        height: 120px;
        background: url('https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png'); /* Placeholder, we'll use a better CSS orb */
        background: radial-gradient(circle, #5669ff 0%, transparent 70%);
        border-radius: 50%;
        filter: blur(20px);
        opacity: 0.6;
        animation: pulse 4s infinite ease-in-out;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.6; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    
    .orb-img {
        position: absolute;
        width: 100px;
        z-index: 2;
    }

</style>
""", unsafe_allow_html=True)

# Central Orb Section
st.markdown("""
<div class='orb-wrapper'>
    <div class='glowing-orb'></div>
    <img class='orb-img' src='https://cdn3d.iconscout.com/3d/premium/thumb/abstract-sphere-8647087-6880053.png' alt='AI Orb'>
</div>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<div class='premium-header'>Groww Mutual Fund Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-sub'>Facts-only assistant for Tata Mutual Fund details. No investment advice.</div>", unsafe_allow_html=True)

# Glass Cards Section
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class='glass-card'>
        <span class='card-title'>📊 NAV & Analytics</span>
        <span class='card-desc'>Access real-time NAV and benchmark-beating performance metrics.</span>
    </div>
    <div class='glass-card'>
        <span class='card-title'>🕵️ Fund Insights</span>
        <span class='card-desc'>Deep dives into fund manager strategy and management tenure.</span>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class='glass-card'>
        <span class='card-title'>🛡️ Risk & Tax</span>
        <span class='card-desc'>Detailed walkthrough of exit loads, stamp duty, and tax efficiency.</span>
    </div>
    <div class='glass-card'>
        <span class='card-title'>⚡ Quick Liquidity</span>
        <span class='card-desc'>Minimum SIP amounts and redemption turnaround times.</span>
    </div>
    """, unsafe_allow_html=True)

# Backend URL
BACKEND_URL = "http://localhost:8000/chat"

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Type / for commands or ask a question..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Bot Response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Analyzing context..."):
                response = requests.post(BACKEND_URL, json={"query": prompt})
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error("Engine offline. Please start app_backend.py")

# Footer Disclaimer
st.markdown("""
<div style='text-align: center; color: #606070; font-size: 0.8rem; margin-top: 5rem; font-weight: 300;'>
    Nexio may make mistakes. Check important information. <a href='#' style='color: #a0a0b0; text-decoration: underline;'>Privacy Notice</a>
</div>
""", unsafe_allow_html=True)
