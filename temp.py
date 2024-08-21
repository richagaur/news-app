import asyncio
from pyppeteer import launch
from newspaper import Article
import requests


async def fetch_final_url_and_content(page, initial_url):
    try:
        await page.goto(initial_url, {'waitUntil': 'networkidle2'})
        # Wait for the page to load completely
        await page.waitForSelector('body')  # or another selector that indicates the page is fully loaded
        
        # Get the final URL after redirects
        final_url = page.url
        
        # Get the page content
        content = await page.content()
        
        return final_url, content
    except Exception as e:
        print(f"Error fetching content from {initial_url}: {e}")
        return None, None

async def process_urls(urls, executable_path):
    browser = await launch({
        'executablePath': executable_path,
        'headless': True,  # Run in headless mode (no UI)
    })
    
    page = await browser.newPage()
    
    results = []
    for url in urls:
        final_url, content = await fetch_final_url_and_content(page, url)
        
        if final_url and content:
            try:
                # Use newspaper3k to parse the content
                article = Article(final_url)
                article.download()
                article.parse()
                
                results.append({
                    'Final URL': final_url,
                    'Title': article.title,
                    'Authors': article.authors,
                    'Publication Date': article.publish_date,
                    'Content': article.text,
                    'Tags': article.tags
                    
                })
            except Exception as e:
                print(f"Error parsing article from {final_url}: {e}")
        else:
            results.append({
                'Final URL': url,
                'Title': 'Error',
                'Authors': [],
                'Publication Date': None,
                'Content': 'Error fetching content'
            })
    
    await browser.close()
    return results

api_key='fb8fa1da87d1482081783da21aa77cf8'

# /v2/top-headlines
url = 'https://newsapi.org/v2/top-headlines?country=in&apiKey='+api_key

articles = []

response = requests.get(url)
if response.status_code == 200:
    news_data = response.json()
    articles = news_data.get("articles", [])
    print(f"Total articles: {len(articles)}" + "\n")
else:
    print(f"Error fetching articles: {response.text}" + "\n")

urls = []

for article in articles:
        url = article.get("url")
        urls.append(url)


chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# Process the URLs
loop = asyncio.get_event_loop()
results = loop.run_until_complete(process_urls(urls, chrome_path))



# Output the results
for result in results:
    print("Final URL:", result['Final URL'])
    print("Title:", result['Title'])
    print("Authors:", result['Authors'])
    print("Publication Date:", result['Publication Date'])
    print("Content:", result['Content'])
    print("Tags:", result['Tags'])
    print("\n")

