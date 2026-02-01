"""
Model Training Module
Train and retrain fraud detection models
OFFLINE-FIRST, SAFE FOR SMALL DATASETS
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

logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self):
        self.language_processor = LanguageProcessor()
        self.model_path = "models/fraud_model.joblib"
        self.model_info_path = "models/model_info.json"

        # Scam categories
        self.scam_categories = {
            "tech_support": 0,
            "financial": 1,
            "romance": 2,
            "lottery_prize": 3,
            "phishing": 4,
            "robocall": 5,
            "legitimate": 6
        }

    def train_model(self, training_data=None):
        """
        Train fraud detection model.
        Uses FULL dataset for training to avoid crashes on small datasets.
        """
        try:
            # Load training data
            if training_data and "training_data" in training_data:
                data = training_data["training_data"]
            else:
                data = self.get_default_training_data()

            # Prepare data
            texts, labels = self._prepare_training_data(data)

            # Build ML pipeline
            pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),
                    stop_words="english",
                    lowercase=True,
                    min_df=1,
                    max_df=0.95
                )),
                ("classifier", LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42
                ))
            ])

            # TRAIN ON FULL DATASET (SAFE MODE)
            pipeline.fit(texts, labels)

            # Basic accuracy (sandbox metric)
            accuracy = pipeline.score(texts, labels)

            # Save model
            os.makedirs("models", exist_ok=True)
            joblib.dump(pipeline, self.model_path)

            # Save model metadata
            model_info = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "algorithm": "TF-IDF + Logistic Regression",
                "training_samples": len(texts),
                "accuracy": float(accuracy),
                "categories": {v: k for k, v in self.scam_categories.items()},
                "offline_mode": True
            }

            with open(self.model_info_path, "w") as f:
                json.dump(model_info, f, indent=2)

            logger.info("Model trained successfully in offline-safe mode")

            return {
                "status": "success",
                "message": "Model trained successfully",
                "training_samples": len(texts),
                "accuracy": float(accuracy),
                "model_path": self.model_path,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _prepare_training_data(self, data):
        """Prepare texts and labels"""
        texts = []
        labels = []

        for item in data:
            text = item.get("text", "")
            category = item.get("category", "legitimate")

            processed_text = self.language_processor.preprocess_text(text)
            texts.append(processed_text)

            label = self.scam_categories.get(
                category, self.scam_categories["legitimate"]
            )
            labels.append(label)

        return texts, labels

    def get_default_training_data(self):
        """Default multilingual training dataset"""
        return [
            # Tech Support
            {"text": "This is Microsoft support. Your computer is infected. Share card details.", "category": "tech_support"},
            {"text": "Apple security calling. Verify your password immediately.", "category": "tech_support"},

            # Financial
            {"text": "Your bank account will be blocked. Share OTP now.", "category": "financial"},
            {"text": "Credit card suspended. Confirm CVV immediately.", "category": "financial"},

            # Romance
            {"text": "I love you but I need money to come meet you.", "category": "romance"},
            {"text": "Please send funds for visa fees.", "category": "romance"},

            # Lottery
            {"text": "You won a lottery. Pay processing fee to receive prize.", "category": "lottery_prize"},
            {"text": "Congratulations! Claim your reward today.", "category": "lottery_prize"},

            # Phishing
            {"text": "Your PayPal account will be suspended. Click the link now.", "category": "phishing"},
            {"text": "Amazon security alert. Verify your account.", "category": "phishing"},

            # Robocall
            {"text": "IRS notice. Pay tax immediately or face arrest.", "category": "robocall"},
            {"text": "Car warranty expiring. Press 1 now.", "category": "robocall"},

            # Legitimate
            {"text": "Doctor appointment reminder tomorrow at 2 PM.", "category": "legitimate"},
            {"text": "Calling to confirm your restaurant reservation.", "category": "legitimate"},
            {"text": "Your pharmacy prescription is ready.", "category": "legitimate"},

            # Hindi
            {"text": "आपका बैंक खाता बंद होने वाला है, तुरंत ओटीपी बताएं।", "category": "financial"},
            {"text": "आपका डॉक्टर अपॉइंटमेंट कल है।", "category": "legitimate"},

            # Telugu
            {"text": "మీ బ్యాంక్ ఖాతా బ్లాక్ అవుతుంది. వెంటనే ఓటీపీ చెప్పండి.", "category": "financial"},
            {"text": "మీ డాక్టర్ అపాయింట్మెంట్ రేపు ఉంది.", "category": "legitimate"}
        ]
