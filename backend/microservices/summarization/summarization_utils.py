#!/usr/bin/env python3
"""
Summarization Utilities Module

This module provides core summarization functionality that can be used by other modules
without creating circular dependencies.

Key Features:
- Text summarization using Google Gemini API
"""

import google.generativeai as genai
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception

# Initialize logger
logger = setup_logger(__name__)

# Configure Gemini with your API key from environment variables
genai.configure(api_key=Config.GEMINI_API_KEY)

@log_exception(logger)
def run_summarization(text):
    """
    Generates a concise summary of the provided text using Google Gemini API.

    Args:
        text (str): The input text to be summarized.

    Returns:
        str: A summarized version of the input text (approximately 150 words).
             Returns an error message if summarization fails.

    Note:
        Uses Google Gemini's latest model with specific parameters:
        - Temperature: 0.5
        - Max output tokens: 200
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            f"""You are a helpful assistant that summarizes text in approximately 150 words.

Please summarize the following text:

{text}""",
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=200
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        return "Error generating summary"