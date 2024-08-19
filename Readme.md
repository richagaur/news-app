# News aggregator application

This application fetches news articles from various sources using [News API](https://newsapi.org/).
The articles are processed and stored in Cosmos DB.
A vector index is also created on the articles to help search for user queries.
The summary of the latest news is presented to the user after searching relevant articles from Cosmos DB which is then sent to OpenAI completions API to get the summary of the news.
