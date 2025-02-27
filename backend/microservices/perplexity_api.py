# perplexity_api.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

YOUR_API_KEY = os.getenv("PERPLEXITY_API_KEY")
BASE_URL = os.getenv("PERPLEXITY_BASE_URL", "https://api.perplexity.ai")
MODEL = "sonar-pro"

# Initialize the client with Perplexity base URL
client = OpenAI(api_key=YOUR_API_KEY, base_url=BASE_URL)

def fetch_articles(keyword):
    """
    Uses the Perplexity Sonar model to fetch latest articles for a given keyword.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a news aggregator AI. Return ONLY a valid JSON object with the following structure:\n"
                "{\n"
                '  "keyword": "the_search_keyword",\n'
                '  "articles": [\n'
                "    {\n"
                '      "title": "Article title",\n'
                '      "author": "Author name",\n'
                '      "source": "Source name",\n'
                '      "publishedAt": "ISO date",\n'
                '      "url": "Article URL",\n'
                '      "urlToImage": "Image URL or null",\n'
                '      "context": "Article category",\n'
                '      "summary": "Brief summary",\n'
                '      "text": "Article text"\n'
                "    }\n"
                "  ]\n"
                "}\n"
                "Do not include any explanatory text before or after the JSON."
            )
        },
        {"role": "user", "content": f"Find the latest news articles about {keyword}"}
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    
    # Extract the text from the first choice
    text = response.choices[0].message.content
    
    # Try to find JSON content within the response
    try:
        # Look for JSON object between curly braces
        import re
        json_match = re.search(r'({[\s\S]*})', text)
        if json_match:
            json_text = json_match.group(1)
            articles = json.loads(json_text)
        else:
            articles = json.loads(text)
        return articles
    except Exception as e:
        raise Exception(f"Error parsing JSON: {e}\nResponse text: {text}")



def summarize_article(article_content):
    """
    Uses the Perplexity Sonar model to generate a summary (about 150 words) for the provided article content.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that summarizes text in approximately 150 words. "
                "Please summarize the following article content."
            )
        },
        {
            "role": "user",
            "content": article_content
        }
    ]
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    summary = response.choices[0].message.content.strip()
    return summary


if __name__ == '__main__':
    # Test the article fetching functionality
    print("Testing article fetching...")
    try:
        articles = fetch_articles("artificial intelligence")
        print(f"Successfully fetched {len(articles)} articles")
        print("Sample article:")
        print(json.dumps(articles[0], indent=2))
    except Exception as e:
        print(f"Error fetching articles: {e}")

    # Test the summarization functionality
    print("\nTesting article summarization...")
    try:
        sample_text = """
        Artificial intelligence has transformed various industries, from healthcare to transportation.
        Machine learning algorithms can now diagnose diseases, drive cars, and even create art.
        The rapid advancement of AI technology has raised both excitement about its potential and
        concerns about its impact on society and the workforce.
        """
        summary = summarize_article(sample_text)
        print("Summary:")
        print(summary)
    except Exception as e:
        print(f"Error generating summary: {e}")