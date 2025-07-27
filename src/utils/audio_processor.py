import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Audio processing for speech-to-text conversion"""

    def __init__(self):
        """Initialize audio processor"""
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

    def audio_to_text(self, audio_file_path: str) -> Optional[str]:
        """
        Convert audio file to text using speech recognition

        Args:
            audio_file_path: Path to audio file

        Returns:
            Recognized text or None if failed
        """
        try:
            logger.info(f"Processing audio file: {audio_file_path}")

            # Convert audio to WAV format if needed
            wav_path = self._convert_to_wav(audio_file_path)

            # Use speech recognition
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Record the audio
                audio_data = self.recognizer.record(source)

                # Recognize speech using Google Web Speech API
                text = self.recognizer.recognize_google(
                    audio_data,
                    language='en-US'
                )

                logger.info(f"Successfully recognized: {text}")

                # Clean up temporary file if created
                if wav_path != audio_file_path:
                    os.unlink(wav_path)
                
                return text.strip()
            
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        
        except sr.RequestError as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None
        
        except Exception  as e:
            logger.error(f"Error processing audio: {str(e)}")
            return None
        
    def _convert_to_wav(self, audio_file_path: str) -> str:
        """
        Convert audio file to WAV format

        Args:
            audio_file_path: Input audio file path

        Returns:
            Path to WAV file
        """
        try:
            file_extension = os.path.splitext(audio_file_path)[1].lower()

            if file_extension == '.wav':
                return audio_file_path
            
            logger.info(f"Converting {file_extension} to WAV")

            # Load audio file
            if file_extension == '.mp3':
                audio = AudioSegment.from_mp3(audio_file_path)
            elif file_extension == '.m4a':
                audio = AudioSegment.from_file(audio_file_path, "m4a")
            elif file_extension == '.ogg':
                audio = AudioSegment.from_ogg(audio_file_path)
            else:
                # Try generic approach
                audio = AudioSegment.from_file(audio_file_path)
            
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.wav'
            ) as tmp_file:
                wav_path = tmp_file.name
            
            # Export as WAV
            audio.export(wav_path, format="wav")

            logger.info(f"Converted to WAV: {wav_path}")
            return wav_path
        
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            # Return original path if conversion fails
            return audio_file_path
    
    def preprocess_audio(self, audio_file_path: str) -> str:
        """
        Preprocess audio for better recognition

        Args:
            audio_file_path: Input audio file path

        Returns:
            Path to processed audio file
        """
        try:
            # Load audio
            audio = AudioSegment.from_file(audio_file_path)

            # Normalize audio
            normalized_audio = audio.normalize()

            # Apply noise reduction (simple high-pass filter)
            # Remove frequencies below 300 Hz (typical noise)
            filtered_audio = normalized_audio.high_pass_filter(300)

            # Ensure reasonable volume
            if filtered_audio.dbFS < -30:
                # Boost quite audio
                filtered_audio = filtered_audio - (15 - filtered_audio.dbFS)
            elif filtered_audio.dbFS > -10:
                # Reduce loud audio
                filtered_audio = filtered_audio - (filtered_audio.dbFS + 10)
            
            # Create temporary file for processed audio
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix='.wav'
            ) as tmp_file:
                processed_path = tmp_file.name
            
            # Export processed audio
            filtered_audio.export(processed_path, format="wav")

            logger.info("Audio preprocessing completed")
            return processed_path
        
        except Exception as e:
            logger.error(f"Error preprocessing audio: {str(e)}")
            return audio_file_path
        
    def validate_audio_file(self, audio_file_path: str) -> bool:
        """
        Validate audio file

        Args:
            audio_file_path: Path to audio file

        Rerurns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(audio_file_path):
                logger.error(f"Audio file not found: {audio_file_path}")
                return False
            
            # Check file size (max 50MB)
            file_size = os.path.getsize(audio_file_path)
            if file_size > 50 * 1024 * 1024:
                logger.error("Audio file too large (>50MB)")
                return False
            
            # Try to load audio file
            audio = AudioSegment.from_file(audio_file_path)

            # Check duration (max 5 minutes)
            duration_seconds = len(audio) / 1000
            if duration_seconds > 300:
                logger.error("Audio file too long (>5 minutes)")
                return False
            
            # Check if audio has content
            if duration_seconds < 0.5:
                logger.error("Audio file too short (<0.5 seconds)")
                return False
            
            logger.info(f"Audio file validation passed: {duration_seconds:.1f}s")
            return True
        
        except Exception as e:
            logger.error(f"Error validating audio file: {str(e)}")
            return False
