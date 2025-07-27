# HelpBuddy AI

HelpBuddy AI is an intelligent educational assistant specifically designed to help students understand NCERT Science Class 8 concepts. It uses advanced AI technologies to provide clear, accurate, and age-appropriate explanations for scientific concepts through multiple input methods.

## Features

- **Multiple Input Methods**:
  - 💬 **Text-based questions** - Type questions directly about NCERT Science Class 8 topics
  - 🎤 **Voice input** - Speak your questions using the microphone with real-time transcription
  - 📷 **Image analysis** - Upload images and ask questions about them with multimodal AI processing
  
- **Smart Context Understanding**:
  - Maintains conversation history with timestamps
  - Provides relevant context from previous interactions
  - Uses vector search to find precise information from the NCERT textbook
  - Automatic knowledge base initialization on startup
  - Follow-up question detection and contextual responses

- **Educational Focus**:
  - Specialized in NCERT Science Class 8 curriculum
  - Age-appropriate explanations for 13-14 year old students
  - Examples and analogies to make concepts easier to understand
  - Scope validation to ensure questions are within curriculum
  - Conversation history tracking

- **Safety and Quality**:
  - Content filtering for appropriate responses
  - Input validation and safety checks
  - Educational context verification
  - Automatic tab persistence across sessions

## Technology Stack

- **Core AI**:
  - Google Gemini 2.0 Flash Exp for natural language processing
  - LangGraph for agent workflow management
  - LangSmith for monitoring and tracking

- **Backend & Storage**:
  - ChromaDB for vector storage and retrieval
  - Streamlit for web interface
  - Python 3.12+

- **Features**:
  - Vector-based knowledge retrieval from PDF
  - Speech-to-text processing with streamlit-mic-recorder
  - Image analysis and description with multimodal AI
  - Memory management for conversation context
  - Content safety filters and guardrails
  - Conversation history management and synchronization

## Prerequisites

- Python 3.12 or higher
- Google API key for Gemini AI (required)
- LangSmith API key (optional, for monitoring/tracing)
- NCERT Science Class 8 PDF file

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/itsyourturn/HelpBuddyAI.git
   cd HelpBuddyAI
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   Create a `.env` file in the root directory with:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   # LANGCHAIN_API_KEY=your_langsmith_api_key_here  # Optional, only needed for LangSmith monitoring
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=HelpBuddyAI
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

   CHROMA_PERSIST_DIR=./chroma_db

   MAX_AUDIO_DURATION=60
   MAX_IMAGE_SIZE_MB=10
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   ```

5. **Data Setup**:
   - Place the NCERT Science Class 8 PDF in the `data` folder:
     ```
     data/ncert_science_class8.pdf
     ```
   - The application will automatically initialize the knowledge base on first run

## Running the Application

1. **Start the Application**:
   ```bash
   streamlit run app.py
   ```

2. **Access the Interface**:
   - Open your browser and go to `http://localhost:8501`
   - The application will automatically initialize the knowledge base if not already done
   - All input methods will be disabled until the knowledge base is ready

## Usage

### Text Questions
- Select the "💬 Text" tab
- Type your question about NCERT Science Class 8 topics
- Click "Ask Question" to get a response
- The system maintains conversation context for follow-up questions

### Voice Input
- Select the "🎤 Audio" tab
- Click the microphone icon and speak your question
- The system will automatically transcribe and process your question
- Real-time feedback shows the transcribed text

### Image Analysis
- Select the "📷 Image" tab
- Upload a scientific diagram or image (PNG, JPG, JPEG)
- Type your question about the image
- Click "Ask Question" to get a detailed explanation using multimodal AI

### Session Management
- Use the "Clear Conversation" button in the sidebar to reset the session
- View conversation history with timestamps
- Monitor system status and knowledge base initialization
- Access conversation summary and statistics

## Project Structure

```
HelpBuddyAI/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Project dependencies
├── .env                      # Environment variables (create this)
├── .gitignore               # Git ignore rules
├── data/                    # Data directory
│   └── ncert_science_class8.pdf
├── src/
│   ├── agents/              # AI agent implementation
│   │   └── helpbuddy_agent.py
│   ├── config/              # Configuration settings
│   │   ├── __init__.py      # Settings class
│   │   └── logging_config.py
│   ├── guardrails/          # Content filtering
│   │   └── content_filter.py
│   ├── utils/               # Utility functions
│   │   ├── audio_processor.py
│   │   ├── image_processor.py
│   │   └── memory_manager.py
│   └── vectorstore/         # Vector database management
│       └── chroma_store.py
├── chroma_db/               # ChromaDB storage (auto-generated, gitignored)
└── logs/                    # Application logs
```

## Key Features in Detail

### Knowledge Base Management
- Automatic PDF indexing on startup using ChromaDB
- Vector search with relevance scoring using Google's text-embedding-004
- Context retrieval from NCERT textbook with chunking and overlap
- Scope validation for curriculum alignment
- Collection management and debugging tools

### Conversation Management
- Persistent conversation history with timestamps
- Memory context for related questions and follow-ups
- Session state management with Streamlit
- Memory synchronization between session state and memory manager

### Input Processing
- **Text**: Direct question processing with context and follow-up detection
- **Audio**: Real-time speech recognition and transcription with streamlit-mic-recorder
- **Image**: Multimodal analysis with educational focus using Gemini 2.0 Flash Exp

### Safety & Quality
- Content filtering for inappropriate content with configurable thresholds
- Educational scope validation with comprehensive keyword matching
- Error handling and user feedback with detailed logging
- Automatic retry mechanisms and graceful degradation

### Advanced Features
- Follow-up question detection using keyword analysis
- Conversation history queries (e.g., "What was my first question?")
- Image processing with base64 encoding for multimodal AI
- Memory cleanup and age-based expiration

## Troubleshooting

### Common Issues

1. **"Vector store not initialized"**:
   - Ensure the PDF file is in the correct location: `data/ncert_science_class8.pdf`
   - Check that the filename is exactly `ncert_science_class8.pdf` (not misspelled)
   - Verify sufficient disk space for vector storage

2. **"Google API key error"**:
   - Verify your Google API key is correctly set in the `.env` file
   - Ensure the key has access to Gemini AI and text-embedding-004
   - Check API quota and billing status

3. **"LangSmith API key not set"**:
   - This is optional. If you do not provide `LANGCHAIN_API_KEY`, LangSmith monitoring and tracing will be disabled, but the app will still work fully.

4. **"Audio input not working"**:
   - Check microphone permissions in your browser
   - Ensure you're using a supported browser (Chrome, Firefox, Safari)
   - Verify streamlit-mic-recorder installation

5. **"Knowledge base initialization failed"**:
   - Check the PDF file is not corrupted
   - Verify sufficient disk space for vector storage
   - Check ChromaDB permissions and directory access

6. **"Conversation history issues"**:
    - Clear conversation and restart if needed

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCERT for the Science Class 8 curriculum
- Google for Gemini AI technology and text-embedding-004
- Streamlit for the web framework
- LangChain community for LangGraph and tools
- ChromaDB for vector storage capabilities
- Streamlit-mic-recorder for audio input functionality
