# HACKDAY MOCKS: Mock Azure services we don't have access to
import logging

logger = logging.getLogger(__name__)


class MockTextAnalyticsClient:
    """Mock Azure AI Language client for language detection"""

    def __init__(self, endpoint, credential):
        logger.warning("HACKDAY: Using mock TextAnalyticsClient - always returns 'en'")
        self.endpoint = endpoint

    def detect_language(self, documents):
        """Always return English"""
        class MockLanguage:
            iso6391_name = "en"

        class MockResult:
            primary_language = MockLanguage()

        return [MockResult()]


class MockSearchClient:
    """Mock Azure AI Search client for RAG"""

    def __init__(self, endpoint, index_name, credential):
        logger.warning("HACKDAY: Using mock SearchClient - RAG will return empty results")
        self.endpoint = endpoint
        self.index_name = index_name

    def search(self, search_text, vector_queries=None, select=None, top=5):
        """Return empty search results"""
        logger.info(f"HACKDAY: Mock search for: {search_text}")
        return []
