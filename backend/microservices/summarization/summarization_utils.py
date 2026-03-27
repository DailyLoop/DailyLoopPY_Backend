#!/usr/bin/env python3
"""
Summarization Utilities Module

This module provides core summarization functionality that can be used by other modules
without creating circular dependencies.

Key Features:
- Text summarization using Google Gemini API
"""

from google import genai
from google.genai import types
from backend.core.config import Config
from backend.core.utils import setup_logger, log_exception

# Initialize logger
logger = setup_logger(__name__)

# Initialize Gemini client with API key from environment variables
# Use v1 API (not v1beta) where gemini-1.5-flash is available
_client = genai.Client(api_key=Config.GEMINI_API_KEY)

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
        Uses Google Gemini's gemini-1.5-flash model (fastest) with specific parameters:
        - Temperature: 0.5
        - Max output tokens: 200
    """
    try:
        logger.info(f"[SUMMARIZATION DEBUG] Starting summarization. Text length: {len(text)}")
        logger.info(f"[SUMMARIZATION DEBUG] Client type: {type(_client)}")
        logger.info(f"[SUMMARIZATION DEBUG] Client API key set: {'***' if Config.GEMINI_API_KEY else 'NOT SET'}")

        logger.info(f"[SUMMARIZATION DEBUG] Calling gemini-1.5-flash model...")
        response = _client.models.generate_content(
            model='gemini-2.0-flash-lite',
            contents=f"""You are a helpful assistant that summarizes text in approximately 150 words.

Please summarize the following text:

{text}""",
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=200
            )
        )
        logger.info(f"[SUMMARIZATION DEBUG] API call succeeded. Response type: {type(response)}")
        logger.info(f"[SUMMARIZATION DEBUG] Response text length: {len(response.text)}")
        return response.text.strip()
    except Exception as e:
        logger.error(f"[SUMMARIZATION ERROR] Full exception type: {type(e).__name__}")
        logger.error(f"[SUMMARIZATION ERROR] Full exception: {str(e)}")
        logger.error(f"[SUMMARIZATION ERROR] Exception repr: {repr(e)}")
        import traceback
        logger.error(f"[SUMMARIZATION ERROR] Traceback: {traceback.format_exc()}")
        return "Error generating summary"