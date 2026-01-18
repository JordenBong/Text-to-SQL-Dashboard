import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Path setting
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = str (BASE_DIR / 'ai_models/ocsvm_model.pkl')
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

class QueryIntentRecognizer:
    def __init__(self):
        self.embedder = None
        self.svm_model = None

    def lazy_load(self):
        if self.embedder is None:
            self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        if self.svm_model is None:
            self.svm_model = joblib.load(MODEL_PATH)

    def predict(self, question):
        
        embedding = self.embedder.encode([question], convert_to_numpy=True)
        prediction = self.svm_model.predict(embedding)[0]
        return prediction


