"""
Fraud Detection Engine
ML-based fraud detection using TF-IDF and Logistic Regression
"""

import os
import json
import joblib
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import logging

from .language_processor import LanguageProcessor
from .feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

class FraudDetector:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.language_processor = LanguageProcessor()
        self.feature_extractor = FeatureExtractor()
        self.model_path = 'models/fraud_model.joblib'
        self.model_info_path = 'models/model_info.json'
        
        # Scam categories
        self.scam_categories = {
            0: 'tech_support',
            1: 'financial',
            2: 'romance',
            3: 'lottery_prize',
            4: 'phishing',
            5: 'robocall',
            6: 'legitimate'
        }
        
        # Risk thresholds
        self.risk_thresholds = {
            'low': 30,
            'medium': 60,
            'high': 80
        }
    
    def initialize(self):
        """Initialize the fraud detector with pre-trained model or create new one"""
        try:
            self.load_model()
            logger.info("Fraud detector initialized successfully")
        except Exception as e:
            logger.warning(f"Could not load existing model: {e}")
            logger.info("Creating new model with default training data")
            self._create_default_model()
    
    def load_model(self):
        """Load the trained model from disk"""
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
            logger.info("Model loaded successfully")
        else:
            raise FileNotFoundError("Model file not found")
    
    def save_model(self):
        """Save the trained model to disk"""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        
        # Save model info
        model_info = {
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'categories': self.scam_categories,
            'features': 'TF-IDF + Custom Features',
            'algorithm': 'Logistic Regression'
        }
        
        with open(self.model_info_path, 'w') as f:
            json.dump(model_info, f, indent=2)
    
    def analyze_text(self, text):
        """Analyze text for fraud indicators"""
        try:
            # Preprocess text
            processed_text = self.language_processor.preprocess_text(text)
            
            # Detect language
            language = self.language_processor.detect_language(text)
            
            # Get prediction
            prediction_proba = self.pipeline.predict_proba([processed_text])[0]
            prediction = self.pipeline.predict([processed_text])[0]
            
            # Calculate risk score (0-100)
            fraud_probability = max(prediction_proba[:-1])  # Exclude legitimate class
            risk_score = int(fraud_probability * 100)
            
            # Determine if fraud
            is_fraud = prediction != len(self.scam_categories) - 1  # Not legitimate
            
            # Get predicted category
            predicted_category = self.scam_categories[prediction]
            
            # Extract features for explanation
            features = self.feature_extractor.extract_features(text)
            explanations = self._generate_explanations(features, prediction_proba)
            
            # Determine risk level
            risk_level = self._get_risk_level(risk_score)
            
            return {
                'is_fraud': bool(is_fraud),
                'risk_score': risk_score,
                'risk_level': risk_level,
                'predicted_category': predicted_category,
                'confidence': float(max(prediction_proba)),
                'language_detected': language,
                'explanations': explanations,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_version': '1.0.0'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            raise
    
    def _generate_explanations(self, features, prediction_proba):
        """Generate human-readable explanations for the prediction"""
        explanations = []
        
        # Check for high-risk features
        if features['urgency_words'] > 0:
            explanations.append(f"Contains {features['urgency_words']} urgency indicators")
        
        if features['money_mentions'] > 0:
            explanations.append(f"Contains {features['money_mentions']} financial references")
        
        if features['personal_info_requests'] > 0:
            explanations.append("Requests personal information")
        
        if features['phone_numbers'] > 0:
            explanations.append("Contains phone numbers")
        
        if features['suspicious_phrases'] > 0:
            explanations.append(f"Contains {features['suspicious_phrases']} suspicious phrases")
        
        if features['emotional_manipulation'] > 0:
            explanations.append("Uses emotional manipulation tactics")
        
        # Add confidence-based explanations
        max_prob = max(prediction_proba)
        if max_prob > 0.8:
            explanations.append("High confidence prediction based on learned patterns")
        elif max_prob > 0.6:
            explanations.append("Moderate confidence prediction")
        else:
            explanations.append("Low confidence prediction - manual review recommended")
        
        return explanations
    
    def _get_risk_level(self, risk_score):
        """Determine risk level based on score"""
        if risk_score >= self.risk_thresholds['high']:
            return 'high'
        elif risk_score >= self.risk_thresholds['medium']:
            return 'medium'
        elif risk_score >= self.risk_thresholds['low']:
            return 'low'
        else:
            return 'very_low'
    
    def get_model_info(self):
        """Get information about the current model"""
        try:
            if os.path.exists(self.model_info_path):
                with open(self.model_info_path, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'status': 'No model info available',
                    'categories': self.scam_categories
                }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': 'Could not retrieve model information'}
    
    def _create_default_model(self):
        """Create a default model with sample training data"""
        from .model_trainer import ModelTrainer
        trainer = ModelTrainer()
        
        # Use default training data
        default_data = trainer.get_default_training_data()
        trainer.train_model({'training_data': default_data})
        
        # Load the newly created model
        self.load_model()