import os
import ssl
import certifi
from dotenv import load_dotenv

# Load Environment variables
load_dotenv()

# Fix SSL certificate issue
try:
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
except Exception:
    pass # Ignore if certifi not available


class Settings:
    """Application settings and configuration"""

    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    # LangSmith Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "HelpBuddyAI")
    LANGCHAIN_ENDPOINT = os.getenv(
        "LANGCHAIN_ENDPOINT",
        "https://api.smith.langchain.com"
        )
    
    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Application Settings
    MAX_AUDIO_DURATION = int(os.getenv("MAX_AUDIO_DURATION", "60"))
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Model Configuration
    GEMINI_MODEL ="gemini-2.0-flash-exp"
    EMBEDDING_MODEL = "models/text-embedding-004"
    TEMPERATURE = 0.1
    MAX_TOKENS = 1000

    # Guardrail Settings
    TOXIC_THRESHOLD = 0.9  # Much higher threshold - only block very toxic content
    SCOPE_KEYWORDS = [
        "science", "physics", "chemistry", "biology", "ncert", "class 8",
        "experiment", "theory", "concept", "lesson", "chapter", "textbook",
        "force", "pressure", "friction", "sound", "light", "electricity",
        "magnet", "cell", "reproduction", "adolescence", "crop", "microorganism",
        "fiber", "plastic", "metal", "coal", "petroleum", "combustion",
        "conservation", "pollution", "solar system", "star", "natural phenomenon",
        "kharif", "rabi", "agriculture", "farming", "plant", "seed", "soil",
        "fertilizer", "pesticide", "irrigation", "harvest", "grain", "wheat",
        "rice", "maize", "pulse", "vegetable", "fruit", "flower"
    ]

    # Data Directory
    DATA_DIR = "./data"
    PDF_PATH = os.path.join(DATA_DIR, "ncert_science_class8.pdf")

    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        # Only GOOGLE_API_KEY is required for core functionality
        if not cls.GOOGLE_API_KEY:
            raise ValueError("Missing required environment variable: GOOGLE_API_KEY")
        # LANGCHAIN_API_KEY (LangSmith) is optional; monitoring is enabled only if present
        return True
