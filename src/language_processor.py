"""
Language Processing Module
Multilingual support for English, Hindi, and Telugu with language detection
"""

import re
import logging
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

logger = logging.getLogger(__name__)

# Set seed for consistent language detection
DetectorFactory.seed = 0

class LanguageProcessor:
    def __init__(self):
        self.supported_languages = ['en', 'hi', 'te']
        
        # Language-specific patterns
        self.language_patterns = {
            'hi': re.compile(r'[\u0900-\u097F]+'),  # Devanagari script
            'te': re.compile(r'[\u0C00-\u0C7F]+'),  # Telugu script
            'en': re.compile(r'[a-zA-Z]+')          # Latin script
        }
        
        # Common fraud keywords in different languages
        self.fraud_keywords = {
            'en': [
                'urgent', 'immediate', 'act now', 'limited time', 'congratulations',
                'winner', 'prize', 'lottery', 'free', 'guaranteed', 'risk-free',
                'credit card', 'bank account', 'social security', 'ssn', 'pin',
                'password', 'verify', 'confirm', 'suspended', 'blocked',
                'microsoft', 'apple', 'google', 'amazon', 'paypal', 'irs',
                'government', 'police', 'arrest', 'warrant', 'legal action',
                'refund', 'rebate', 'stimulus', 'grant', 'inheritance'
            ],
            'hi': [
                'तुरंत', 'जल्दी', 'अभी', 'मुफ्त', 'पुरस्कार', 'लॉटरी',
                'बैंक', 'खाता', 'पैसा', 'रुपये', 'क्रेडिट कार्ड',
                'पासवर्ड', 'पिन', 'सत्यापित', 'पुष्टि', 'बंद',
                'सरकार', 'पुलिस', 'गिरफ्तारी', 'कानूनी कार्रवाई'
            ],
            'te': [
                'త్వరగా', 'వెంటనే', 'ఉచితం', 'బహుమతి', 'లాటరీ',
                'బ్యాంకు', 'ఖాతా', 'డబ్బు', 'రూపాయలు', 'క్రెడిట్ కార్డ్',
                'పాస్‌వర్డ్', 'పిన్', 'ధృవీకరించు', 'నిర్ధారణ', 'మూసివేయబడింది',
                'ప్రభుత్వం', 'పోలీసు', 'అరెస్టు', 'చట్టపరమైన చర్య'
            ]
        }
    
    def detect_language(self, text):
        """Detect the primary language of the text"""
        try:
            # Clean text for detection
            cleaned_text = self._clean_text_for_detection(text)
            
            if not cleaned_text.strip():
                return 'en'  # Default to English
            
            # Use langdetect library
            detected = detect(cleaned_text)
            
            # Map to supported languages
            if detected in self.supported_languages:
                return detected
            else:
                # Fallback to script-based detection
                return self._detect_by_script(text)
                
        except LangDetectException:
            # Fallback to script-based detection
            return self._detect_by_script(text)
        except Exception as e:
            logger.warning(f"Language detection error: {e}")
            return 'en'  # Default to English
    
    def _detect_by_script(self, text):
        """Detect language based on script patterns"""
        script_counts = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = pattern.findall(text)
            script_counts[lang] = len(''.join(matches))
        
        # Return language with most characters
        if script_counts:
            return max(script_counts, key=script_counts.get)
        else:
            return 'en'
    
    def _clean_text_for_detection(self, text):
        """Clean text for better language detection"""
        # Remove numbers, punctuation, and special characters
        cleaned = re.sub(r'[0-9\W_]+', ' ', text)
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
    def preprocess_text(self, text):
        """Preprocess text for fraud detection"""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '.', text)
        
        # Normalize phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'PHONE_NUMBER', text)
        
        # Normalize email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL_ADDRESS', text)
        
        # Normalize URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'URL', text)
        
        # Normalize currency amounts
        text = re.sub(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', 'CURRENCY_AMOUNT', text)
        text = re.sub(r'₹\d+(?:,\d{2,3})*(?:\.\d{2})?', 'CURRENCY_AMOUNT', text)
        
        return text
    
    def extract_multilingual_features(self, text):
        """Extract language-specific features for fraud detection"""
        features = {
            'detected_language': self.detect_language(text),
            'is_mixed_language': self._is_mixed_language(text),
            'fraud_keywords_count': 0,
            'language_specific_patterns': {}
        }
        
        # Count fraud keywords across all languages
        text_lower = text.lower()
        for lang, keywords in self.fraud_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            features['fraud_keywords_count'] += count
            features['language_specific_patterns'][lang] = count
        
        return features
    
    def _is_mixed_language(self, text):
        """Check if text contains multiple languages"""
        script_counts = {}
        
        for lang, pattern in self.language_patterns.items():
            matches = pattern.findall(text)
            if matches:
                script_counts[lang] = len(''.join(matches))
        
        # Consider mixed if more than one script has significant presence
        significant_scripts = [lang for lang, count in script_counts.items() if count > 10]
        return len(significant_scripts) > 1
    
    def translate_response(self, response, target_language='en'):
        """Translate response to target language (mock implementation)"""
        # This is a mock implementation for demo purposes
        # In a real system, you would use an offline translation model
        
        if target_language == 'en':
            return response
        
        # Mock translations for common response fields
        translations = {
            'hi': {
                'is_fraud': 'धोखाधड़ी_है',
                'risk_score': 'जोखिम_स्कोर',
                'predicted_category': 'अनुमानित_श्रेणी',
                'explanations': 'स्पष्टीकरण'
            },
            'te': {
                'is_fraud': 'మోసం_ఉంది',
                'risk_score': 'రిస్క్_స్కోర్',
                'predicted_category': 'అంచనా_వర్గం',
                'explanations': 'వివరణలు'
            }
        }
        
        if target_language in translations:
            # This is a simplified mock translation
            logger.info(f"Mock translation to {target_language} applied")
        
        return response