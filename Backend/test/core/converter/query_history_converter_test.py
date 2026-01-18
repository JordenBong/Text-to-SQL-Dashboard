import pytest
from core.converter.query_history_converter import QueryHistoryConverter
from core.model.query_models import QueryHistoryCore, QueryHistoryDO, QueryHistoryVO

class TestQueryHistoryConverter:
    
    @pytest.fixture
    def sample_core(self):
        """Fixture to provide a standard QueryHistoryCore object."""
        return QueryHistoryCore(
            question="What is the total revenue?",
            generated_sql="SELECT SUM(revenue) FROM sales",
            intent_recognized=True,
            operator="data_analyst_01",
            status="success",
            error_message=None,
            table_name="sales",
            ddl_context="CREATE TABLE sales (id INT, revenue DECIMAL)"
        )

    @pytest.fixture
    def sample_do(self):
        """Fixture to provide a standard QueryHistoryDO object."""
        return QueryHistoryDO(
            id=100,
            question="List all products",
            generated_sql="SELECT * FROM products",
            intent_recognized=True,
            operator="admin_user",
            status="completed",
            error_message=None,
            table_name="products",
            ddl_context="CREATE TABLE products (id INT, name TEXT)"
        )

    # --- Core to DO Mapping ---

    def test_core_to_do_mapping(self, sample_core):
        """Verify that Core model maps correctly to Data Object (DO)."""
        result = QueryHistoryConverter.core_to_do(sample_core)
        
        assert result.question == sample_core.question
        assert result.intent_recognized == sample_core.intent_recognized
        assert result.operator == sample_core.operator
        assert result.ddl_context == sample_core.ddl_context


    # --- DO to Core Mapping ---

    def test_do_to_core_mapping(self, sample_do):
        """Verify that Data Object (DO) maps correctly back to Core model."""
        result = QueryHistoryConverter.do_to_core(sample_do)
        
        assert result.question == sample_do.question
        assert result.intent_recognized == sample_do.intent_recognized
        assert result.operator == sample_do.operator
        assert result.ddl_context == sample_do.ddl_context

    # --- Core to VO Mapping ---

    def test_core_to_vo_mapping(self, sample_core):
        """Verify that Core model maps correctly to View Object (VO)."""
        result = QueryHistoryConverter.core_to_vo(sample_core)
        
        assert result.question == sample_core.question
        assert result.status == sample_core.status
        # VO typically hides internal logic like DDL context or raw SQL if desired
        assert result.operator == sample_core.operator

    # --- Edge Cases ---

    def test_converter_with_error_message(self, sample_core):
        """Verify the converter handles optional fields like error_message."""
        sample_core.status = "failed"
        sample_core.error_message = "Syntax error at line 1"
        
        do_result = QueryHistoryConverter.core_to_do(sample_core)
        assert do_result.status == "failed"
        assert do_result.error_message == "Syntax error at line 1"