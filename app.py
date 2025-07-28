import streamlit as st
import os
import logging
import base64
from datetime import datetime
from dotenv import load_dotenv
from streamlit_mic_recorder import speech_to_text

# Import HelpBuddy components
from src.agents.helpbuddy_agent import HelpBuddyAgent
from src.config.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Configure logging (file + console)
setup_logging()
logger = logging.getLogger(__name__)

# Verify PDF file exists
pdf_path = os.path.join("data", "ncert_science_class8.pdf")
if not os.path.exists(pdf_path):
    logger.error(f"Required PDF file not found: {pdf_path}")
    st.error("Error: Required textbook PDF file not found. Please make sure the NCERT Science Class 8 PDF is in the data folder.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="HelpBuddy AI",
    # page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        color: #000000;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
        color: #000000;
    }
    .bot-message {
        background-color: #e8f4fd;
        border-left-color: #1f77b4;
        color: #000000;
    }
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_helpbuddy():
    """Initialize HelpBuddy AI agent"""
    return HelpBuddyAgent()

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>HelpBuddy AI</h1>
        <p>Your study Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize components
    try:
        helpbuddy = initialize_helpbuddy()
        
        # Check if vector store is ready
        vectorstore_ready = helpbuddy.vector_store.is_initialized()
        if not vectorstore_ready:
            st.info("Initializing knowledge base from NCERT Science Class 8 PDF...")
            with st.spinner("Loading and indexing PDF content..."):
                success = helpbuddy.initialize_knowledge_base()
                vectorstore_ready = success
                if success:
                    st.success("Knowledge base initialized successfully!")
                else:
                    st.error("Failed to initialize knowledge base. Please check the PDF file.")
                    st.stop()
        
        # Initialize session state
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        if "last_processed_query" not in st.session_state:
            st.session_state.last_processed_query = ""
        
        # Synchronize existing conversation history with memory manager
        if st.session_state.conversation_history and len(helpbuddy.memory_manager.conversations) == 0:
            success = helpbuddy.sync_conversation_history(st.session_state.conversation_history)
            if success:
                logger.info(f"Synchronized {len(st.session_state.conversation_history) // 2} conversation pairs with memory manager")
            else:
                logger.error("Failed to synchronize conversation history with memory manager")
            
        # Input container with tabs
        input_container = st.container()
        with input_container:
            # Use st.session_state to track the active tab
            if "active_tab" not in st.session_state:
                st.session_state.active_tab = "💬 Text"

            tab_options = ["💬 Text", "🎤 Audio", "📷 Image"]
            selected_tab = st.radio(
                "Select input mode:",
                tab_options,
                index=tab_options.index(st.session_state.active_tab),
                horizontal=True,
                key="tab_radio"
            )
            st.session_state.active_tab = selected_tab

            # Initialize variables for later use
            text_input = ""
            text_submit = False
            audio_text = ""
            uploaded_file = None
            image_question = ""
            image_submit = False

            if selected_tab == "💬 Text":
                text_input = st.text_area("Type your question about NCERT Science Class 8:", 
                                        key="text_input", 
                                        height=100,
                                        disabled=not vectorstore_ready)
                text_submit = st.button("Ask Question", key="text_submit", disabled=not vectorstore_ready)
            elif selected_tab == "🎤 Audio":
                st.markdown("##### Speak your question about NCERT Science Class 8")
                st.markdown("Click the microphone icon and speak your question")
                if vectorstore_ready:
                    audio_text = speech_to_text(
                        language='en',
                        key="audio_input",
                        use_container_width=True
                    )
                else:
                    st.info("Audio input is disabled until the knowledge base is ready.")
                    audio_text = None
                if audio_text and vectorstore_ready:
                    st.info("Recorded Text: " + audio_text)
                    try:
                        # Check if this audio query was already processed
                        if audio_text != st.session_state.last_processed_query:
                            result = helpbuddy.process_query(audio_text, has_image=False, image_data=None)
                            response = result.get("response", "Sorry, I couldn't process your question.")
                            current_time = datetime.now().strftime("%H:%M")
                            st.session_state.conversation_history.append({
                                "role": "user", 
                                "content": audio_text,
                                "timestamp": current_time
                            })
                            st.session_state.conversation_history.append({
                                "role": "assistant", 
                                "content": response,
                                "timestamp": current_time
                            })
                            st.session_state.last_processed_query = audio_text
                    except Exception as e:
                        st.error("I'm having trouble processing your voice input. Please try again or use text input.")
                        logger.error(f"Audio processing error: {str(e)}")
            elif selected_tab == "📷 Image":
                uploaded_file = st.file_uploader("Upload an image:", type=["png", "jpg", "jpeg"], disabled=not vectorstore_ready)
                if uploaded_file:
                    st.image(uploaded_file, caption="Uploaded Image")
                    st.session_state.current_image = uploaded_file
                image_question = st.text_area("Ask a question about the image:", 
                                            key="image_question", 
                                            height=100,
                                            disabled=not vectorstore_ready)
                image_submit = st.button("Ask Question", key="image_submit", disabled=not vectorstore_ready)
    
    except Exception as e:
        st.error("Unable to initialize HelpBuddy AI. Please check your API keys and try again.")
        st.info("Make sure your Google API key is correctly set in the .env file")
        logger.error(f"Initialization error: {str(e)}")
        return
    
    # Sidebar with session management
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("Session Management")
        if st.button("Clear Conversation"):
            st.session_state.conversation_history = []
            st.session_state.last_processed_query = ""
            helpbuddy.clear_conversation_memory()
            st.success("Conversation cleared!")
            st.rerun()
            
        st.markdown("---")

        # About section
        st.header("About")
        st.markdown("""
        **HelpBuddy AI** is powered by:
        - Google Gemini 2.5+
        - NCERT Science class 8
        - Advanced Guardrails
        - LangChain Agent Framework
        - LangSmith Monitoring (Optional)
        """)

        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area - Handle query submission
    query = None
    image_data = None
    
    # Check which input is active and has data
    if text_input and text_submit:  # Only process text when submit button is clicked
        query = text_input
        logger.info(f"Processing text query: {query}")
    elif uploaded_file and image_question and image_submit:  # Handle image input when submit button is clicked
        query = image_question
        image_data = base64.b64encode(uploaded_file.getvalue()).decode()
        logger.info(f"Processing image query: '{query}' with image data length: {len(image_data)}")
    else:
        logger.info("No active query to process")
    
    # Process query if we have one (audio is handled separately in its tab)
    if query and query != st.session_state.last_processed_query:
        try:
            # Process query through agent
            result = helpbuddy.process_query(query=query, has_image=(image_data is not None), image_data=image_data)
            
            # Extract response from result
            response = result.get("response", "Sorry, I couldn't process your question.")
            
            # Update conversation history with timestamps
            current_time = datetime.now().strftime("%H:%M")
            st.session_state.conversation_history.append({
                "role": "user", 
                "content": query,
                "timestamp": current_time
            })
            st.session_state.conversation_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": current_time
            })
            
            # Mark this query as processed
            st.session_state.last_processed_query = query
            
            # No need for st.rerun() - Streamlit will automatically rerun when session state changes
        except Exception as e:
            st.error("Sorry, I'm having trouble processing your question right now. Please try again.")
            logger.error(f"Query processing error: {str(e)}")

    # Main content area - full width
    # Display conversation history
    st.header("Conversation")
    st.caption("💡 Newest messages appear at the top")
        
    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display conversation history in reverse order (newest first)
        # But group user and assistant messages together
        conversation_pairs = []
        i = 0
        while i < len(st.session_state.conversation_history):
            if i + 1 < len(st.session_state.conversation_history):
                user_msg = st.session_state.conversation_history[i]
                assistant_msg = st.session_state.conversation_history[i + 1]
                if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                    conversation_pairs.append((user_msg, assistant_msg))
                    i += 2
                else:
                    # Handle orphaned messages
                    conversation_pairs.append((user_msg, None))
                    i += 1
            else:
                # Handle last message if odd number
                conversation_pairs.append((st.session_state.conversation_history[i], None))
                i += 1
        
        # Display conversation pairs in reverse order (newest first)
        for user_msg, assistant_msg in reversed(conversation_pairs):
            timestamp = user_msg.get("timestamp", "")
            
            # Display user message first
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> <small style="color: #666;">{timestamp}</small><br>
                {user_msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Display assistant response if available
            if assistant_msg:
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>HelpBuddy:</strong> <small style="color: #666;">{timestamp}</small><br>
                    {assistant_msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            
    st.markdown("---")

    # Removed status panel - not needed for user experience

if __name__ == "__main__":
    main()
