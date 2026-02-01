"""
Feature Extraction Module
Extract fraud-relevant features from text for ML model
"""

import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

class FeatureExtractor:
    def __init__(self):
        # Fraud indicator patterns
        self.urgency_patterns = [
            r'\b(urgent|immediate|asap|right now|act now|hurry|quickly|fast)\b',
            r'\b(limited time|expires|deadline|last chance|final notice)\b',
            r'\b(don\'t wait|call now|respond immediately)\b'
        ]
        
        self.money_patterns = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',  # Dollar amounts
            r'₹\d+(?:,\d{2,3})*(?:\.\d{2})?',  # Rupee amounts
            r'\b(money|cash|dollars|rupees|payment|fee|cost|price|amount)\b',
            r'\b(credit card|bank account|debit card|paypal|venmo)\b',
            r'\b(refund|rebate|prize|lottery|winner|jackpot)\b'
        ]
        
        self.personal_info_patterns = [
            r'\b(social security|ssn|sin|tax id)\b',
            r'\b(credit card|card number|cvv|expiry|expiration)\b',
            r'\b(bank account|routing number|account number)\b',
            r'\b(password|pin|passcode|security code)\b',
            r'\b(date of birth|dob|birthday|mother\'s maiden name)\b'
        ]
        
        self.phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US phone numbers
            r'\b\+\d{1,3}[-.]?\d{3,4}[-.]?\d{3,4}[-.]?\d{3,4}\b'  # International
        ]
        
        self.suspicious_phrases = [
            r'\b(microsoft|apple|google|amazon|paypal|ebay) (support|security|team)\b',
            r'\b(irs|government|police|fbi|homeland security)\b',
            r'\b(suspended|blocked|frozen|compromised|hacked)\b',
            r'\b(verify|confirm|update|validate) (account|information|details)\b',
            r'\b(click here|visit|go to|download|install)\b',
            r'\b(congratulations|winner|selected|chosen|qualified)\b',
            r'\b(free|guaranteed|risk-free|no obligation|limited offer)\b'
        ]
        
        self.emotional_manipulation = [
            r'\b(worried|concerned|scared|afraid|panic|emergency)\b',
            r'\b(arrest|warrant|legal action|lawsuit|court|jail)\b',
            r'\b(family|loved ones|children|safety|security)\b',
            r'\b(help|assist|save|protect|secure)\b'
        ]
        
        self.tech_support_indicators = [
            r'\b(computer|pc|laptop|device|system|software)\b',
            r'\b(virus|malware|infected|compromised|hacked)\b',
            r'\b(technical support|tech support|customer service)\b',
            r'\b(remote access|teamviewer|anydesk|logmein)\b'
        ]
        
        self.financial_indicators = [
            r'\b(bank|credit union|financial institution)\b',
            r'\b(loan|mortgage|credit|debt|investment)\b',
            r'\b(interest rate|apr|fees|charges|penalty)\b',
            r'\b(account|balance|transaction|transfer)\b'
        ]
    
    def extract_features(self, text):
        """Extract all fraud-relevant features from text"""
        text_lower = text.lower()
        
        features = {
            # Basic counts
            'word_count': len(text.split()),
            'char_count': len(text),
            'sentence_count': len(re.findall(r'[.!?]+', text)),
            
            # Fraud indicators
            'urgency_words': self._count_patterns(text_lower, self.urgency_patterns),
            'money_mentions': self._count_patterns(text_lower, self.money_patterns),
            'personal_info_requests': self._count_patterns(text_lower, self.personal_info_patterns),
            'phone_numbers': self._count_patterns(text_lower, self.phone_patterns),
            'suspicious_phrases': self._count_patterns(text_lower, self.suspicious_phrases),
            'emotional_manipulation': self._count_patterns(text_lower, self.emotional_manipulation),
            'tech_support_indicators': self._count_patterns(text_lower, self.tech_support_indicators),
            'financial_indicators': self._count_patterns(text_lower, self.financial_indicators),
            
            # Text characteristics
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'caps_ratio': self._calculate_caps_ratio(text),
            'number_count': len(re.findall(r'\d+', text)),
            
            # Communication patterns
            'callback_requests': self._count_callback_requests(text_lower),
            'time_pressure': self._count_time_pressure(text_lower),
            'authority_claims': self._count_authority_claims(text_lower),
            'verification_requests': self._count_verification_requests(text_lower),
        }
        
        # Calculate composite scores
        features['fraud_score'] = self._calculate_fraud_score(features)
        features['urgency_score'] = self._calculate_urgency_score(features)
        features['manipulation_score'] = self._calculate_manipulation_score(features)
        
        return features
    
    def _count_patterns(self, text, patterns):
        """Count occurrences of regex patterns in text"""
        total_count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            total_count += len(matches)
        return total_count
    
    def _calculate_caps_ratio(self, text):
        """Calculate ratio of uppercase letters to total letters"""
        letters = re.findall(r'[a-zA-Z]', text)
        if not letters:
            return 0.0
        caps = re.findall(r'[A-Z]', text)
        return len(caps) / len(letters)
    
    def _count_callback_requests(self, text):
        """Count requests to call back or contact"""
        patterns = [
            r'\b(call|phone|contact|reach) (back|us|me)\b',
            r'\b(return|give us a) call\b',
            r'\b(dial|press|enter) \d+\b'
        ]
        return self._count_patterns(text, patterns)
    
    def _count_time_pressure(self, text):
        """Count time pressure indicators"""
        patterns = [
            r'\b(expires|deadline|limited time|act now|hurry)\b',
            r'\b(today|tonight|immediately|right now|asap)\b',
            r'\b(before|within) \d+ (hours|minutes|days)\b'
        ]
        return self._count_patterns(text, patterns)
    
    def _count_authority_claims(self, text):
        """Count claims of authority or official status"""
        patterns = [
            r'\b(official|authorized|certified|licensed)\b',
            r'\b(government|federal|state|irs|fbi)\b',
            r'\b(microsoft|apple|google|amazon|bank)\b',
            r'\b(department|agency|bureau|office)\b'
        ]
        return self._count_patterns(text, patterns)
    
    def _count_verification_requests(self, text):
        """Count requests for verification or confirmation"""
        patterns = [
            r'\b(verify|confirm|validate|authenticate)\b',
            r'\b(provide|give|share|tell) (us|me) your\b',
            r'\b(need|require|must have) your\b'
        ]
        return self._count_patterns(text, patterns)
    
    def _calculate_fraud_score(self, features):
        """Calculate composite fraud score based on features"""
        score = 0
        
        # Weight different features
        score += features['urgency_words'] * 2
        score += features['money_mentions'] * 3
        score += features['personal_info_requests'] * 5
        score += features['suspicious_phrases'] * 2
        score += features['emotional_manipulation'] * 2
        score += features['callback_requests'] * 1
        score += features['authority_claims'] * 2
        score += features['verification_requests'] * 3
        
        # Normalize by text length
        if features['word_count'] > 0:
            score = score / features['word_count'] * 100
        
        return min(score, 100)  # Cap at 100
    
    def _calculate_urgency_score(self, features):
        """Calculate urgency score"""
        score = 0
        score += features['urgency_words'] * 3
        score += features['time_pressure'] * 2
        score += features['exclamation_count'] * 0.5
        score += features['caps_ratio'] * 10
        
        return min(score, 100)
    
    def _calculate_manipulation_score(self, features):
        """Calculate emotional manipulation score"""
        score = 0
        score += features['emotional_manipulation'] * 3
        score += features['authority_claims'] * 2
        score += features['verification_requests'] * 2
        
        return min(score, 100)
    
    def get_feature_importance(self, features):
        """Get the most important features for explanation"""
        important_features = []
        
        if features['personal_info_requests'] > 0:
            important_features.append(('personal_info_requests', features['personal_info_requests']))
        
        if features['money_mentions'] > 0:
            important_features.append(('money_mentions', features['money_mentions']))
        
        if features['urgency_words'] > 0:
            important_features.append(('urgency_words', features['urgency_words']))
        
        if features['suspicious_phrases'] > 0:
            important_features.append(('suspicious_phrases', features['suspicious_phrases']))
        
        if features['emotional_manipulation'] > 0:
            important_features.append(('emotional_manipulation', features['emotional_manipulation']))
        
        # Sort by importance (value)
        important_features.sort(key=lambda x: x[1], reverse=True)
        
        return important_features[:5]  # Return top 5