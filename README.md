# HelpBuddy AI

HelpBuddy AI is an intelligent educational assistant specifically designed to help students understand NCERT Science Class 8 concepts. It uses advanced AI technologies to provide clear, accurate, and age-appropriate explanations for scientific concepts through multiple input methods.

## Use Case Overview

### **Primary Use Case: Educational AI Assistant**
HelpBuddy AI serves as an intelligent study companion for **NCERT Science Class 8 students** (ages 13-14), providing personalized learning support through multiple interaction modalities.

### **Target Users:**
- **Students**: NCERT Science Class 8 students seeking homework help and concept clarification
- **Educators**: Teachers looking for supplementary teaching tools
- **Parents**: Guardians wanting to support their children's science education

### **Learning Scenarios:**
- **Homework Assistance**: Getting help with science assignments and problems
- **Exam Preparation**: Reviewing concepts and practicing questions
- **Concept Clarification**: Understanding difficult scientific topics
- **Visual Learning**: Learning through diagrams, charts, and images
- **Auditory Learning**: Learning through voice interactions

## Problem Statement

### **Core Problems:**

1. **Limited Access to Personalized Learning Support**
   - Students often struggle to get immediate help with science concepts
   - Traditional tutoring is expensive and not always available
   - Teachers have limited time for individual student support

2. **Difficulty in Understanding Complex Scientific Concepts**
   - Abstract scientific concepts are hard to visualize
   - Students need multiple explanations and examples
   - Language barriers and technical terminology confusion

3. **Lack of Interactive Learning Methods**
   - Traditional textbooks are static and one-dimensional
   - Students learn differently (visual, auditory, textual)
   - Limited engagement with learning materials

4. **Inconsistent Quality of Educational Content**
   - Internet sources may be unreliable or inappropriate
   - Content may not be age-appropriate
   - Information may not align with curriculum standards

5. **Limited Context-Aware Learning Support**
   - No memory of previous interactions
   - Inability to handle follow-up questions
   - Lack of personalized learning paths

## Solution Architecture

### **1. Multi-Modal Learning Interface**

**Problem**: Students have different learning preferences and needs
**Solution**: Three input methods for maximum accessibility

- **Text-based learning**: Direct question typing for detailed explanations
- **Voice-based learning**: Speech-to-text for students with typing difficulties
- **Visual learning**: Image upload and analysis for diagrams/charts

### **2. Intelligent Knowledge Base**

**Problem**: Unreliable and non-curriculum-aligned information sources
**Solution**: Vectorized NCERT textbook with semantic search

- **ChromaDB Vector Store**: PDF indexing of NCERT Science Class 8 textbook
- **Semantic Search**: Using Google's text-embedding-004 for context-aware retrieval
- **Curriculum Alignment**: Ensures all content matches NCERT standards

### **3. Context-Aware Conversation Management**

**Problem**: No memory of previous interactions or learning context
**Solution**: Advanced memory management system

- **Conversation History**: Timestamped interaction tracking
- **Follow-up Detection**: Intelligent recognition of related questions
- **Context Retrieval**: Relevant information from previous sessions
- **Memory Cleanup**: Age-based conversation management

### **4. Safety and Quality Assurance**

**Problem**: Inappropriate or inaccurate content exposure
**Solution**: Multi-layered content filtering

- **Educational Scope Validation**: Ensures questions are within curriculum
- **Age-Appropriate Filtering**: Content suitable for 13-14 year olds
- **Safety Checks**: Comprehensive response validation

### **5. Personalized Learning Experience**

**Problem**: One-size-fits-all approach doesn't work for all students
**Solution**: Adaptive response generation

- **Age-Appropriate Explanations**: Tailored for 13-14 year old students
- **Multiple Explanation Styles**: Different approaches for different learners
- **Progressive Complexity**: Building understanding step by step

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
  - LangChain for agent workflow and tool integration
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

## Architecture Overview

HelpBuddy AI uses a **traditional LangChain agent pattern** with the following components:

- **HelpBuddyAgent**: Main agent class that orchestrates all functionality
- **ChromaStore**: Vector database management for knowledge retrieval
- **ContentFilter**: Safety and content filtering mechanisms
- **ImageProcessor**: Multimodal AI processing for image analysis
- **MemoryManager**: Conversation history and context management
- **AudioProcessor**: Speech-to-text processing capabilities

The agent follows a **sequential workflow** where each query is processed through multiple stages:
1. Input validation and preprocessing
2. Context retrieval from vector store
3. Response generation using Gemini AI
4. Content filtering and safety checks
5. Memory management and history updates

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
- LangChain community for agent framework and tools
- ChromaDB for vector storage capabilities
- Streamlit-mic-recorder for audio input functionality
