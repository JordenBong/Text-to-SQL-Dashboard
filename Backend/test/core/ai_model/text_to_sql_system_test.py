import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from core.ai_model.text_to_sql_system import TextToSQLSystem  # Replace with actual filename

class TestTextToSQLSystem:

    @patch('core.ai_model.text_to_sql_system.TFT5ForConditionalGeneration.from_pretrained')
    @patch('core.ai_model.text_to_sql_system.T5Tokenizer.from_pretrained')
    @patch('core.ai_model.text_to_sql_system.QueryIntentRecognizer')
    def setup_method(self, method, mock_intent, mock_tokenizer, mock_model):
        """Initializes the system with mocked dependencies before each test."""
        self.system = TextToSQLSystem()
        self.mock_model = self.system.t5_model
        self.mock_tokenizer = self.system.t5_tokenizer
        self.mock_intent_recognizer = self.system.query_intent_recognizer

    def test_predict_intent_true(self):
        """Test that predict_intent returns True when result is np.int64(1)."""
        self.mock_intent_recognizer.predict.return_value = np.int64(1)
        
        result = self.system.predict_intent("Show me users")
        
        assert result is True
        self.mock_intent_recognizer.predict.assert_called_once_with("Show me users")

    def test_predict_intent_false(self):
        """Test that predict_intent returns False for non-db queries."""
        self.mock_intent_recognizer.predict.return_value = np.int64(0)
        
        result = self.system.predict_intent("What is the weather?")
        
        assert result is False

    def test_generate_sql_intent_rejected(self):
        """Test that generate_sql returns error message if intent is not DB-related."""
        # Mock intent recognizer to return False
        self.mock_intent_recognizer.predict.return_value = np.int64(0)
        
        response = self.system.generate_sql("Hello", needPredictIntent=True, ddl_context="CREATE TABLE...")
        
        assert response == "Please ask something related to query data from database."
        # Ensure the model was never actually called
        self.mock_model.generate.assert_not_called()

    def test_generate_sql_success(self):
        """Test successful SQL generation flow."""
        # Setup mocks
        self.mock_intent_recognizer.predict.return_value = np.int64(1)
        self.mock_tokenizer.return_value = {'input_ids': [1, 2], 'attention_mask': [1, 1]}
        
        # Mock the model output
        mock_output = MagicMock()
        self.mock_model.generate.return_value = [mock_output]
        self.mock_tokenizer.decode.return_value = "SELECT * FROM users"

        # Execute
        result = self.system.generate_sql(
            "List users", 
            needPredictIntent=True, 
            ddl_context="TABLE users"
        )

        # Verify
        assert result == "SELECT * FROM users"
        self.mock_model.generate.assert_called_once()
        self.mock_tokenizer.decode.assert_called_once()

    def test_generate_sql_skip_intent_check(self):
        """Verify intent check is skipped if needPredictIntent is False."""
        self.mock_tokenizer.return_value = {'input_ids': [1], 'attention_mask': [1]}
        self.mock_model.generate.return_value = [MagicMock()]
        self.mock_tokenizer.decode.return_value = "SELECT 1"

        self.system.generate_sql("Force SQL", needPredictIntent=False, ddl_context="...")

        # Intent recognizer should NOT have been called
        self.mock_intent_recognizer.predict.assert_not_called()