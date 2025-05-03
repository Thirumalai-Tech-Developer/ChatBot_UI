import streamlit as st
import sqlite3
import bcrypt
import time
import ollama
import streamlit.components.v1 as components
import json
from datetime import datetime

# Database setup
DB_FILE = 'db.json'
CHAT_DB = 'users.db'
MESSAGES_DB = 'messages.db'
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
TITLE = "CodeChat AI"
ASSISTANT_GREETING = "Hello! I'm your AI coding assistant. How can I help you today?"

# Set page config (must be first Streamlit command)
st.set_page_config(
    page_title=TITLE,
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main app styling */
    .stApp {
        background-color: rgba(255, 255, 255, 0.2);
        font-family: 'Inter', sans-serif;
    }
    
    /* Chat container */
    .main-chat-container {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.08);
        padding: 24px;
        margin: 16px;
    }
    
    /* Message bubbles */
    .stChatMessage {
        border-radius: 16px;
        padding: 14px 20px;
        margin: 12px 0;
        max-width: 85%;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    [data-testid="userChatMessage"] {
        background-color: rgba(255, 255, 255, 0.2);
        margin-left: auto;
        border-bottom-right-radius: 4px;
        color: #1a365d;
    }
    
    [data-testid="assistantChatMessage"] {
        background-color: rgba(255, 255, 255, 0.2);
        margin-right: auto;
        border-bottom-left-radius: 4px;
        color: #2d3748;
        border: 1px solid #e2e8f0;
    }
    
    /* Input area */
    .stChatInput {
        background-color: rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 16px;
        border: 1px solid #e2e8f0;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 12px;
        border: none;
        background-color: #4f46e5;
        color: white;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background-color: #4338ca;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Text inputs */
    .stTextInput>div>div>input {
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid #e2e8f0;
    }
    
    /* Header */
    .app-header {
        color: #1e293b;
        margin-bottom: 8px;
    }
    
    .app-subheader {
        color: #64748b;
        font-size: 16px;
        margin-bottom: 32px;
    }
    
    .logo-text {
        font-size: 32px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 8px;
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 12px !important;
        background-color: #60D24C;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: white !important;
    }
    
    /* Code blocks */
    pre {
        border-radius: 12px !important;
        background-color: rgba(0, 0, 0, 0.7) !important;
        padding: 16px !important;
        border: 1px solid #e2e8f0 !important;
        font-family: 'Fira Code', monospace !important;
    }
    
    /* Divider */
    .divider {
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 24px 0;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .stChatMessage {
            max-width: 90%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Add Google Fonts
components.html("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
""", height=0)

# Database functions
def init_db():
    # Initialize users database
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            phone TEXT,
            password_hash TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
    # Initialize messages database
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            session_id TEXT,
            timestamp TEXT,
            role TEXT,
            content TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT,
            created_at TEXT,
            last_activity TEXT,
            title TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, phone, password):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, phone, password_hash) VALUES (?, ?, ?)", 
                  (username, phone, hashed_pw))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

def authenticate_user(username, password):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True
    return False

def save_chat_history(username, messages):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    messages_json = json.dumps(messages)
    c.execute("INSERT INTO chat_history (username, timestamp, messages) VALUES (?, ?, ?)",
              (username, timestamp, messages_json))
    conn.commit()
    conn.close()

def load_chat_history(username):
    conn = sqlite3.connect(CHAT_DB)
    c = conn.cursor()
    c.execute("SELECT timestamp, messages FROM chat_history WHERE username = ? ORDER BY timestamp DESC", (username,))
    history = c.fetchall()
    conn.close()
    return [(ts, json.loads(msg)) for ts, msg in history]

# Chat functions
def generate(prompt, last_assistant_message=None):
    messages = []
    
    # Add only the most relevant context (last assistant message if exists)
    if last_assistant_message:
        messages.append(last_assistant_message)
    
    # Add the current prompt
    messages.append({"role": "user", "content": prompt})
    
    response = ""
    for chunk in ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True):
        if 'message' in chunk:
            text = chunk['message']['content']
            response += text
            yield response

def save_message(username, role, content, session_id=None):
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    
    if not session_id:
        # Create a new session if none exists
        session_id = str(datetime.now().timestamp())
        c.execute("INSERT INTO chat_sessions (session_id, username, created_at, last_activity, title) VALUES (?, ?, ?, ?, ?)",
                 (session_id, username, datetime.now().isoformat(), datetime.now().isoformat(), content[:50]))
    else:
        # Update last activity for existing session
        c.execute("UPDATE chat_sessions SET last_activity = ? WHERE session_id = ?",
                 (datetime.now().isoformat(), session_id))
    
    # Save the message
    c.execute("INSERT INTO messages (username, session_id, timestamp, role, content) VALUES (?, ?, ?, ?, ?)",
              (username, session_id, datetime.now().isoformat(), role, content))
    conn.commit()
    conn.close()
    return session_id

def get_messages(session_id):
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    messages = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return messages

def get_user_sessions(username):
    conn = sqlite3.connect(MESSAGES_DB)
    c = conn.cursor()
    c.execute("SELECT session_id, created_at, last_activity, title FROM chat_sessions WHERE username = ? ORDER BY last_activity DESC", (username,))
    sessions = c.fetchall()
    conn.close()
    return sessions

# Update the show_chat function
def show_chat(the_prompt, agree):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Get only the last assistant message for context (if exists)
        last_assistant_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_assistant_msg = msg
                break
        
        if agree:
            for chunk in generate(the_prompt, last_assistant_msg):
                full_response = chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        else:
            for chunk in generate(the_prompt):
                full_response = chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    
    # Save both user prompt and assistant response
    if 'session_id' not in st.session_state:
        st.session_state.session_id = save_message(st.session_state.username, "user", the_prompt)
    else:
        save_message(st.session_state.username, "user", the_prompt, st.session_state.session_id)
    
    save_message(st.session_state.username, "assistant", full_response, st.session_state.session_id)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# UI Components
def login_register():
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://images.unsplash.com/photo-1551033406-611cf9a28f67?q=80&w=300", width=300)
    
    with col2:
        st.markdown('<div class="logo-text">CodeChat</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-subheader">Your personal AI coding assistant</div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                if st.form_submit_button("Login", type="primary"):
                    if authenticate_user(username, password):
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        
                        # Load chat history if available
                        history = load_chat_history(username)
                        if history:
                            # Get the most recent conversation
                            _, messages = history[0]
                            st.session_state.messages = messages
                        else:
                            st.session_state.messages = [{"role": "assistant", "content": ASSISTANT_GREETING}]
                            
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with tab2:
            with st.form("register_form"):
                username = st.text_input("New Username", key="reg_user")
                phone = st.text_input("Phone Number", key="reg_phone")
                password = st.text_input("New Password", type="password", key="reg_pass")
                if st.form_submit_button("Register", type="primary"):
                    if register_user(username, phone, password):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Username already exists")

def chat_interface():
    st.markdown('<div class="logo-text">CodeChat</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subheader">Ask me anything about coding</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"**👤 {st.session_state.username}**")
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        agree = st.checkbox("Want to memorize Previous Context")
        
        sessions = get_user_sessions(st.session_state.username)
        session_options = []
        
        if sessions:
            st.markdown("**📚 Chat History**")
            session_options = [f"{datetime.fromisoformat(sess[2]).strftime('%Y-%m-%d %H:%M')} - {sess[3]}" 
                             for sess in sessions]
        
        # Add New Chat option at the beginning
        session_options.insert(0, "➕ New Chat")
        
        # Use a unique key for the selectbox to ensure it updates
        selected_session = st.selectbox(
            "Select conversation", 
            session_options, 
            index=0,
            key="session_selector"
        )
        
        # Handle session selection
        if selected_session == "➕ New Chat":
            if st.button("Start New Chat", type="primary"):
                # Clear existing messages and session
                st.session_state.messages = [{"role": "assistant", "content": ASSISTANT_GREETING}]
                if 'session_id' in st.session_state:
                    del st.session_state.session_id
                # Force a rerun to refresh the interface
                st.rerun()
        elif sessions:
            selected_index = session_options.index(selected_session) - 1
            session_id = sessions[selected_index][0]
            
            # Only load if it's a different session
            if 'session_id' not in st.session_state or st.session_state.session_id != session_id:
                messages = get_messages(session_id)
                st.session_state.messages = messages
                st.session_state.session_id = session_id
                st.rerun()
        
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("🚪 Logout", type="primary"):
            st.session_state.clear()
            st.rerun()
        
        # st.markdown("**⚙️ Settings**")
        # context_length = st.slider('Response length', 100, 2000, 400)

    # Initialize new chat session if none exists
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": ASSISTANT_GREETING}]
        if 'session_id' not in st.session_state:
            st.session_state.session_id = save_message(
                st.session_state.username, 
                "assistant", 
                ASSISTANT_GREETING
            )

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your coding question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        show_chat(prompt, agree)

init_db()
if not st.session_state.get('authenticated'):
    login_register()
else:
    chat_interface()
