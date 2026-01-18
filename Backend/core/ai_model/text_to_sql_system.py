import numpy as np
from pathlib import Path
from core.ai_model.query_intent_recognizer import QueryIntentRecognizer
from transformers import TFT5ForConditionalGeneration, T5Tokenizer, GenerationConfig

# Path setting
BASE_DIR = Path(__file__).resolve().parent
REMOTE_MODEL_PATH = "JordenBong/T5-Small-Text-to-SQL"

# Initialize text-to-sql models
class TextToSQLSystem:
    def __init__(self):
        self.t5_model = None  # Don't load yet
        self.t5_tokenizer = None
        self.query_intent_recognizer = QueryIntentRecognizer()

    def _lazy_load_model(self):
        if self.t5_model is None:
            print("Loading T5 model... this may take a moment.")
            self.t5_model = TFT5ForConditionalGeneration.from_pretrained(
                REMOTE_MODEL_PATH, subfolder="t5_small_text2sql_model"
            )
            self.t5_tokenizer = T5Tokenizer.from_pretrained(
                REMOTE_MODEL_PATH, subfolder="t5_small_text2sql_model"
            )
            self.gen_config = GenerationConfig.from_pretrained(
                REMOTE_MODEL_PATH, subfolder="t5_small_text2sql_model"
            )
            self.gen_config.max_length = 512

    def predict_intent(self, question):
        """Determine if question is database-related"""
        result = self.query_intent_recognizer.predict(question)
        if result == np.int64(1):
          return True
        return False


    def generate_sql(self, question, needPredictIntent, ddl_context):
        """Generate SQL using your T5 model"""
        self._lazy_load_model()

        # user request to check intent or not
        if needPredictIntent:
            # study user intent
            intent = self.predict_intent(question)

            # detected as not db-related question
            if not intent:
                response = "Please ask something related to query data from database."
                return response
            
        # input formatting
        input_text = f"Question: {question} | {ddl_context}"

        # continue predict sql
        inputs = self.t5_tokenizer(input_text, return_tensors='tf', max_length=128, padding=True, truncation=True)

        outputs = self.t5_model.generate(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            generation_config=self.gen_config
        )
        sql_query = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return sql_query



  
