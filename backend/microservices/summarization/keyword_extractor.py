#!/usr/bin/env python3
"""
Keyword Extractor Module

This module provides functionality for extracting keywords from text content using YAKE.
It helps identify key topics and themes in article content for better categorization and filtering.
"""

import yake
from backend.core.utils import setup_logger, log_exception

# Initialize logger
logger = setup_logger(__name__)

@log_exception(logger)
def get_keywords(text, num_keywords=1):
    """
    Extracts key phrases from the input text using YAKE keyword extraction.

    Args:
        text (str): The input text to extract keywords from.
        num_keywords (int, optional): Number of keywords to extract. Defaults to 1.

    Returns:
        list: A list of extracted keywords/key phrases.
    """
    kw_extractor = yake.KeywordExtractor(top=num_keywords, lan='en')
    keywords = kw_extractor.extract_keywords(text)
    return [kw[0] for kw in keywords]