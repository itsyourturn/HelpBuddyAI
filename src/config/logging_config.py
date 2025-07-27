import logging
import os
from pathlib import Path


def setup_logging():
    """Setup logging configuration for HelpBuddy AI"""

    # Create logs directory using absolute path
    from datetime import datetime
    
    base_dir = Path(__file__).parent.parent.parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # Generate timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"helpbuddy_{timestamp}.log"

    # Configure logging with absolute path and timestamp
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Set specific logger levels
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured for HelpBuddy AI")


# Setup logging when imported
setup_logging()
