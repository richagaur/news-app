from transformers import pipeline
import asyncio
from pyppeteer import launch
from newspaper import Article
import requests
import random


async def open_browser():
    executable_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    browser = await launch({
            'executablePath': executable_path,
            'headless': True,  # Run in headless mode (no UI)
        })
    return browser

async def close_browser(browser):
    await browser.close()
        
async def fetch_final_url_and_content(url, browser, timeout=60000, retries=3):
    for attempt in range(retries):
        try:
            page = await browser.newPage()
            await page.goto(url, {'waitUntil': 'networkidle2'})
            # Wait for a more general condition or different selector
            await page.waitForSelector('body', timeout = timeout)  # Wait for the network to be idle
            content = await page.content()
            # Get the final URL after redirects
            final_url = page.url
            await page.close()
            return final_url, content
        except Exception as e:
            print(f"Attempt {attempt + 1} - Error fetching content from {url}: {e}")
            await asyncio.sleep(random.uniform(1, 3))  # Random sleep to avoid retrying too quickly
    return None, None

async def process_urls(url, browser):
    
    try:
        final_url, content = await fetch_final_url_and_content(url, browser)
        if final_url and content:
            # Use newspaper3k to parse the content
            article = Article(final_url)
            article.download()
            article.parse()
            return article, final_url
        else:
            return None, None
    except Exception as e:
        print(f"Error retrieving article from {url}: {e}")
        return None, None

# Initialize the text classification pipeline
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define possible categories
categories = ["Sports", "Technology", "Politics", "Business", "Health", "Entertainment"]

def infer_category(article_title, article_content):
    # Combine title and content for classification
    text = f"{article_title}. {article_content}"
    
    # Classify the text into one of the categories
    result = classifier(text, candidate_labels=categories)

    # The category with the highest score is selected
    return result['labels'][0]

def categorize_article_with_openai(article_title, article_content):
    categories = ["Sports", "Technology", "Politics", "Business", "Health", "Entertainment"]

    prompt = f"Given the following news article title and content, determine which category it belongs to from the following list: {', '.join(categories)}.\n\n" \
             f"Title: {article_title}\n" \
             f"Content: {article_content}\n\n" \
             f"Category:"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=10,
        n=1,
        stop=None,
        temperature=0
    )

    return response.choices[0].text.strip()


def scrape_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # If the URL is an RSS feed, you'll need to parse it differently
        if "rss" in url:
            soup = BeautifulSoup(response.content, 'xml')  # Use 'xml' parser for RSS feeds
            paragraphs = soup.find_all('description')  # RSS feeds often store content in 'description' or 'content' tags
        else:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')  # For standard HTML pages, scrape paragraphs

        article_content = ""
        for para in paragraphs:
            article_content += para.get_text() + " "  # Correctly concatenate paragraph texts

        return article_content.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content: {e}")
        return None
