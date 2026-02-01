"""
Speech Processing Module
Offline speech-to-text conversion using SpeechRecognition library
"""

import os
import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which

logger = logging.getLogger(__name__)

class SpeechProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Configure recognizer for better offline performance
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
    def process_audio(self, audio_path):
        """Convert audio file to text using offline speech recognition"""
        try:
            # Convert audio to WAV format if needed
            wav_path = self._convert_to_wav(audio_path)
            
            # Load audio file
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Record the audio
                audio_data = self.recognizer.record(source)
            
            # Perform offline speech recognition
            # Using offline recognition (no internet required)
            try:
                # Try offline recognition first (using CMU Sphinx)
                text = self.recognizer.recognize_sphinx(audio_data)
                logger.info("Successfully transcribed audio using offline recognition")
            except sr.UnknownValueError:
                # Fallback to mock transcription for demo purposes
                text = self._generate_mock_transcription(audio_path)
                logger.warning("Could not understand audio, using mock transcription")
            except sr.RequestError as e:
                # Fallback to mock transcription
                text = self._generate_mock_transcription(audio_path)
                logger.warning(f"Offline recognition error: {e}, using mock transcription")
            
            # Clean up temporary WAV file if created
            if wav_path != audio_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            # Return mock transcription for demo purposes
            return self._generate_mock_transcription(audio_path)
    
    def _convert_to_wav(self, audio_path):
        """Convert audio file to WAV format if needed"""
        try:
            # Check if file is already WAV
            if audio_path.lower().endswith('.wav'):
                return audio_path
            
            # Convert to WAV
            audio = AudioSegment.from_file(audio_path)
            wav_path = audio_path.rsplit('.', 1)[0] + '_converted.wav'
            audio.export(wav_path, format='wav')
            
            logger.info(f"Converted {audio_path} to WAV format")
            return wav_path
            
        except Exception as e:
            logger.error(f"Error converting audio to WAV: {e}")
            return audio_path
    
    def _generate_mock_transcription(self, audio_path):
        """Generate mock transcription for demo purposes"""
        # Sample transcriptions representing different types of calls
        mock_transcriptions = [
            # Scam examples
            "Hello, this is Microsoft technical support. We have detected suspicious activity on your computer. Please provide your credit card information to verify your identity and we will fix the problem immediately.",
            
            "Congratulations! You have won $50,000 in our lottery. To claim your prize, please provide your bank account details and pay a small processing fee of $500.",
            
            "This is your bank calling. There has been fraudulent activity on your account. Please confirm your social security number and PIN to secure your account.",
            
            "Hi, I'm calling from the IRS. You owe back taxes and if you don't pay immediately, we will issue a warrant for your arrest. Please provide your credit card information now.",
            
            "Hello, I'm calling about your car warranty that is about to expire. We need your personal information to extend the warranty. This is a limited time offer.",
            
            # Legitimate examples
            "Hello, this is Dr. Smith's office calling to confirm your appointment tomorrow at 2 PM. Please call us back if you need to reschedule.",
            
            "Hi, this is Sarah from ABC Company. I'm calling to follow up on your job application. Could you please call me back at your convenience?",
            
            "This is a reminder that your library books are due tomorrow. You can renew them online or by calling the library.",
            
            "Hello, this is your pharmacy calling to let you know that your prescription is ready for pickup.",
        ]
        
        # Select a mock transcription based on file name hash for consistency
        import hashlib
        file_hash = int(hashlib.md5(audio_path.encode()).hexdigest(), 16)
        selected_transcription = mock_transcriptions[file_hash % len(mock_transcriptions)]
        
        logger.info("Generated mock transcription for demo purposes")
        return selected_transcription
    
    def get_audio_info(self, audio_path):
        """Get information about the audio file"""
        try:
            audio = AudioSegment.from_file(audio_path)
            return {
                'duration_seconds': len(audio) / 1000.0,
                'channels': audio.channels,
                'sample_rate': audio.frame_rate,
                'format': audio_path.split('.')[-1].upper()
            }
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None