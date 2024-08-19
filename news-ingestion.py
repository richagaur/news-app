import uuid
import requests
from newsapi import NewsApiClient
from cosmos_client import CosmosDBClient
from datetime import datetime
import new_processing


cosmos_client = CosmosDBClient()
# Init
api_key='fb8fa1da87d1482081783da21aa77cf8'
newsapi = NewsApiClient(api_key=api_key)

# /v2/top-headlines/sources
#sources = newsapi.get_sources()

# /v2/top-headlines
url = 'https://newsapi.org/v2/top-headlines?country=in&apiKey='+api_key
print(url)
#news_sources = newsapi.get_top_headlines(language='en',
#                                          country='in')

articles = []

response = requests.get(url)
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get("articles", [])
    print(f"Total articles: {len(articles)}" + "\n")
else:
    print(f"Error fetching articles: {response.text}" + "\n")
    
processed_articles = []

for article in articles:
        
        content = new_processing.scrape_article_content(article.get("url"))

        print(f"Processed article: {content}" + "\n")
        # Infer the category of the article

        # #category = new_processing.categorize_article_with_openai(article.get("title"), content)
        # category = new_processing.infer_category(article.get("title"), content)

        # print(f"Category: {category}" + "\n")

        # processed_article = {
        #     "id": str(uuid.uuid4()),
        #     "source": {
        #         "name": article.get("source", {}).get("name"),
        #         "url": article.get("url")
        #     },
        #     "title": article.get("title"),
        #     "author": article.get("author"),
        #     "publishedDate": article.get("publishedAt", datetime.utcnow().isoformat()),
        #     "content": content,
        #     "summary": "",  # Summarization to be handled separately
        #     "url": article.get("url"),
        #     "vector": [],  # Vector to be added during processing
        #     "tags": [],    # Tags can be added during processing
        #     "category": category # Category can be inferred during processing
        # }
        # processed_articles.append(processed_article)

    # Convert to JSON and write to blob storage
    #outputBlob.set(json.dumps(processed_articles, indent=4))
    
    # Write to Cosmos DB
if processed_articles:
    cosmos_client.write_articles(processed_articles)

