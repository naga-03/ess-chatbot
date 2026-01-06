import streamlit as st
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.chatbot import ESSChatbot
from data.profile_manager import ProfileManager

# Page configuration
st.set_page_config(
    page_title="ESS Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #e7f3ff;
        align-items: flex-end;
    }
    .chat-message.bot {
        background-color: #f0f2f6;
        align-items: flex-start;
    }
    .chat-message .message-content {
        width: 100%;
        padding: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = ESSChatbot()

if 'profile_manager' not in st.session_state:
    st.session_state.profile_manager = ProfileManager()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

chatbot = st.session_state.chatbot

# Title
st.title("🤖 Employee Self-Service (ESS) Chatbot")
st.markdown("---")

# Sidebar for info and login
with st.sidebar:
    st.header("📋 Information")
    
    # Show login status
    if chatbot.auth_manager.is_authenticated():
        user = chatbot.auth_manager.get_current_user()
        st.success(f"✅ Logged in as: **{user['name']}**")
        st.info(f"Employee ID: {user['employee_id']}\nDepartment: {user['department']}")
        
        if st.button("🚪 Logout", key="logout_btn"):
            chatbot.auth_manager.logout()
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
            
        # --- Profile Management Section ---
        st.markdown("---")
        st.subheader("⚙️ Update Profile")
        
        # Phone Update Flow
        with st.expander("📱 Phone Number"):
            new_phone = st.text_input("New Phone (+91...)", key="new_phone_input")

            if st.button("Update Phone", key="update_phone_btn"):
                result = st.session_state.profile_manager.update_phone_number(user['employee_id'], new_phone)
                if result['status'] == 'success':
                    st.success("Updated successfully!")
                    st.info("Please logout and login again to see changes.")
                else:
                    st.error(result['message'])

        # Emergency Contact Update Flow
        with st.expander("🚑 Emergency Contact"):
            em_phone = st.text_input("New Emergency Phone", key="em_phone_input")
            if st.button("Update Contact", key="update_em_btn"):
                result = st.session_state.profile_manager.update_emergency_contact_number(user['employee_id'], em_phone)
                if result['status'] == 'success':
                    st.success("Updated successfully!")
                    st.info("Please logout and login again to see changes.")
                else:
                    st.error(result['message'])
        # ----------------------------------
        
    else:
        st.warning("⚠️ Not logged in")
        st.markdown("### Login")
        
        # Demo credentials display
        with st.expander("📝 Demo Credentials"):
            st.code("""
E001 / pass123
E002 / pass456
E003 / pass789
            """)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            emp_id = st.text_input("Employee ID", key="login_id", placeholder="E001")
        with col2:
            password = st.text_input("Password", type="password", key="login_pwd", placeholder="pass123")
        
        if st.button("🔓 Login", key="login_btn"):
            success, message = chatbot.auth_manager.login(emp_id, password)
            if success:
                st.success(message)
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()
            else:
                st.error(message)
    
    st.markdown("---")
    st.markdown("### 📚 Quick Help")
    st.markdown("""
**General Queries (No Login):**
- What is the leave policy?
- When are company holidays?
- HR contact information
- Company information
- Employee benefits

**Employee-Specific Queries (Login Required):**

**Leave Management:**
- How many leaves do I have?
- Am I applicable to take sick leave?
- Show my leave history for this year
- Has my leave been approved?

**Payroll & Tax:**
- Show my payslip for this month
- Show my tax calculation for 2025
- What is my current salary?

**Personal Information:**
- Who is my manager?
- What is my department?
- Show my attendance record
- Show my birthday / work anniversary

**Career Development:**
- What are my skills?
- When is the appraisal cycle?
- Show my goals and objectives
- I want to apply for leave

**Account Updates:**
- Update my phone number
- Change my emergency contact
    """)

# Main chat area
st.markdown("### 💬 Chat")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**Bot:** {message['content']}")
        if message.get('details'):
            with st.expander("📊 Details"):
                st.json(message['details'])

# Chat input
query = st.chat_input("Ask me something about HR policies, benefits, or your employee information...", key="user_input")

if query:
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })
    
    # Process the query
    response = chatbot.process_message(query)
    
    # Guide user to sidebar for updates if intent matches
    if response.get('intent') == 'update_phone':
        st.sidebar.warning("👉 Please use the 'Update Profile' > 'Phone Number' section in the sidebar to proceed.")
    elif response.get('intent') == 'update_emergency_contact':
        st.sidebar.warning("👉 Please use the 'Update Profile' > 'Emergency Contact' section in the sidebar to proceed.")
    
    # Format bot response - clean up extracted entities to show only relevant ones
    if response.get('success'):
        bot_message = response.get('message', 'Response received.')
        
        # Filter entities to only show meaningful ones
        entities = response.get('entities', {})
        cleaned_entities = {}
        
        for key, value in entities.items():
            if key == 'leave_duration':
                # Only include if days or weeks were actually extracted
                if value.get('days') or value.get('weeks'):
                    cleaned_entities[key] = value
            elif key == 'named_entities':
                # Only include named_entities if there's meaningful data
                if value.get('person') or value.get('date') or value.get('other'):
                    cleaned_entities[key] = value
            elif value and isinstance(value, list) and len(value) > 0:
                # Include non-empty lists
                cleaned_entities[key] = value
        
        details = {
            'intent': response.get('intent'),
            'intent_name': response.get('intent_name'),
            'confidence': response.get('confidence'),
            'data': response.get('data')
        }
        
        # Only include extracted_entities if there's something meaningful
        if cleaned_entities:
            details['extracted_entities'] = cleaned_entities
    else:
        bot_message = response.get('message', 'Unable to process your request.')
        details = {
            'intent': response.get('intent'),
            'reason': response.get('message')
        }
    
    # Add bot response to history
    st.session_state.chat_history.append({
        "role": "bot",
        "content": bot_message,
        "details": details
    })
    
    # Rerun to display the new message
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# Footer with system info
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🔄 Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

with col2:
    if st.button("❓ Show Help", key="show_help"):
        st.info("""
**Commands:**
- /login <employee_id> <password>
- /logout
- /status
- /help

Type these directly in the chat to execute them.
        """)

with col3:
    st.caption(f"Chat messages: {len(st.session_state.chat_history)}")
