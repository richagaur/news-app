import gradio as gr
from time import sleep
import time 
from openai_client import OpenAIClient
from cosmos_client import CosmosDBClient

openai_client = OpenAIClient()
cosmos_client = CosmosDBClient()
news_container = cosmos_client.container
cache_container = cosmos_client.cache_container

chat_history = []

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="News Assistant")
    
    msg = gr.Textbox(label="Ask me about any news topic!")
    clear = gr.Button("Clear")

    def user(user_message, chat_history):
        # Create a timer to measure the time it takes to complete the request
        start_time = time.time()
        # Get LLM completion
        response_payload, cached = openai_client.chat_completion(cache_container, news_container, user_message)
        # Stop the timer
        end_time = time.time()
        elapsed_time = round((end_time - start_time) * 1000, 2)
        print(response_payload)
        # Append user message and response to chat history
        details = f"\n (Time: {elapsed_time}ms)"
        if cached:
            details += " (Cached)"
        chat_history.append([user_message, response_payload + details])
        
        return gr.update(value=""), chat_history
    
    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False)

    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the Gradio interface
demo.launch(debug=True)