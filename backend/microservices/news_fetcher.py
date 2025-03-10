"""News Fetcher Service (Compatibility Module)

This is a compatibility module that imports from the new location in data_services.
Existing code that imports from this location will continue to work.

For new code, please import directly from backend.microservices.data_services.news_fetcher
"""

# Import all functions from the new location to maintain backward compatibility
from backend.microservices.data_services.news_fetcher import fetch_news, write_to_file

# Re-export the functions to maintain the same interface
__all__ = ['fetch_news', 'write_to_file']





