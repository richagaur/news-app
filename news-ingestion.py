import requests
from cosmos_client import CosmosDBClient
from datetime import datetime
import news_processing
import asyncio
from openai_client import OpenAIClient
import hashlib


cosmos_client = CosmosDBClient()
openai_client = OpenAIClient()
# Init
api_key='fb8fa1da87d1482081783da21aa77cf8'


async def fetch_news_articles():
    url = 'https://newsapi.org/v2/top-headlines?country=in&apiKey='+api_key
    articles = []
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        print(f"Total articles: {len(articles)}" + "\n")
    else:
        print(f"Error fetching articles: {response.text}" + "\n")

    return await process_news_articles(articles)

async def process_article(raw_article, browser):
    try:
        article, final_url = await news_processing.process_urls(raw_article.get("url"), browser)
        if article is not None:
            # Infer the category of the article
            category = news_processing.infer_category(article.title, article.text)

            combined_text = f"title: {article.title} content: {article.text}"
            vector = openai_client.generate_embeddings(combined_text)
            hash_object = hashlib.sha256(article.title.encode())
            id = hash_object.hexdigest()
            processed_article = {
                "id": id,
                "source": {
                    "name": raw_article.get("source", {}).get("name"),
                    "url": raw_article.get("url")
                },
                "title": article.title,
                "author": raw_article.get("author"),
                "publishedDate": str(raw_article.get("publishedAt")),
                "content": article.text,
                "summary": "",  # Summarization to be handled separately
                "url": final_url,
                "vector": vector,  
                "tags": list(article.tags) ,  
                "category": category 
            }
            print(f"Processed article: {processed_article['title']}")
            return processed_article
    except Exception as e:
        print(f"Error processing article {raw_article.get('url')}: {e}")
    return None

async def process_news_articles(articles):
    browser = await news_processing.open_browser()
    processed_articles = []
    for raw_article in articles:
        processed_article = await process_article(raw_article, browser)
        if processed_article is not None:
            processed_articles.append(processed_article)
    # tasks = [process_article(raw_article, browser) for raw_article in articles]
    # processed_articles = await asyncio.gather(*tasks)
    # processed_articles = [article for article in processed_articles if article is not None]
    
    # # Close the browser and return the processed articles
    await news_processing.close_browser(browser)
    return processed_articles

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    processed_articles = loop.run_until_complete(fetch_news_articles())
    if len(processed_articles) > 0:
        cosmos_client.write_articles(processed_articles)
    else:
        print("No articles were processed.")
