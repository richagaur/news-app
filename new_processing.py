from transformers import pipeline
from bs4 import BeautifulSoup
import requests


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
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Scrape based on common HTML tags used for article content
        paragraphs = soup.find_all('p')

        article_content = ""
        #print("paragraphs: " +  paragraphs)
        for para in paragraphs:
            print("para: " + para.get_text())
            article_content = ' '.join(para.get_text())

        return article_content.strip()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content: {e}")
        return None
