from openai import AzureOpenAI

openai_endpoint = config['openai_endpoint']
openai_key = config['openai_key']
openai_api_version = config['openai_api_version']
openai_embeddings_deployment = config['openai_embeddings_deployment']
openai_embeddings_dimensions = int(config['openai_embeddings_dimensions'])
openai_completions_deployment = config['openai_completions_deployment']


# Create the OpenAI client
openai_client = AzureOpenAI(azure_endpoint=openai_endpoint, api_key=openai_key, api_version=openai_api_version)

# generate openai embeddings
def generate_embeddings(text):    
    '''
    Generate embeddings from string of text.
    This will be used to vectorize data and user input for interactions with Azure OpenAI.
    '''
    print("Generating embeddings for: ", text, " with model: ", openai_embeddings_deployment)
    response = openai_client.embeddings.create(input=text, 
                                               model=openai_embeddings_deployment,
                                               dimensions=openai_embeddings_dimensions)
    embeddings =response.model_dump()
    return embeddings['data'][0]['embedding']

def get_chat_history(container, completions=3):
    results = container.query_items(
        query= '''
        SELECT TOP @completions *
        FROM c
        ORDER BY c._ts DESC
        ''',
        parameters=[
            {"name": "@completions", "value": completions},
        ], enable_cross_partition_query=True)
    results = list(results)
    return results

def generate_completion(user_prompt, vector_search_results, chat_history):
    
    system_prompt = '''
    You are an intelligent assistant for movies. You are designed to provide helpful answers to user questions about movies in your database.
    You are friendly, helpful, and informative and can be lighthearted. Be concise in your responses, but still friendly.
        - Only answer questions related to the information provided below. Provide at least 3 candidate movie answers in a list.
        - Write two lines of whitespace between each answer in the list.
    '''

    # Create a list of messages as a payload to send to the OpenAI Completions API

    # system prompt
    messages = [{'role': 'system', 'content': system_prompt}]

    #chat history
    for chat in chat_history:
        messages.append({'role': 'user', 'content': chat['prompt'] + " " + chat['completion']})
    
    #user prompt
    messages.append({'role': 'user', 'content': user_prompt})

    #vector search results
    for result in vector_search_results:
        messages.append({'role': 'system', 'content': json.dumps(result['document'])})

    print("Messages going to openai", messages)
    # Create the completion
    response = openai_client.chat.completions.create(
        model = openai_completions_deployment,
        messages = messages,
        temperature = 0.1
    )    
    return response.model_dump()


def chat_completion(cache_container, movies_container, user_input):
    # Generate embeddings from the user input
    user_embeddings = generate_embeddings(user_input)
    # Query the chat history cache first to see if this question has been asked before
    cache_results = vector_search(container = cache_container, vectors = user_embeddings, similarity_score=0.99, num_results=1)
    if len(cache_results) > 0:
        print("\n Cached Result\n")
        return cache_results[0]['document']['completion']
        
    else:
    
        #perform vector search on the movie collection
        print("\n New result\n")
        search_results = vector_search(movies_container, user_embeddings)
        print("Getting Chat History\n")
        #chat history
        chat_history = get_chat_history(cache_container, 3)
        #generate the completion
        print("Generating completions \n")
        completions_results = generate_completion(user_input, search_results, chat_history)
        print("Caching response \n")
        #cache the response
        cache_response(cache_container, user_input, user_embeddings, completions_results)
        print("\n")
        # Return the generated LLM completion
        return completions_results['choices'][0]['message']['content'] 
    
def chat_completion(cache_container, movies_container, user_input):
    print("starting completion")
    # Generate embeddings from the user input
    user_embeddings = generate_embeddings(user_input)
    # Query the chat history cache first to see if this question has been asked before
    cache_results = get_cache(container = cache_container, vectors = user_embeddings, similarity_score=0.99, num_results=1)

    #perform vector search on the movie collection
    print("New result\n")
    search_results = vector_search(movies_container, user_embeddings)
    print("Getting Chat History\n")
    #chat history
    chat_history = get_chat_history(cache_container, 3)
    #generate the completion
    print("Generating completions \n")
    completions_results = generate_completion(user_input, search_results, chat_history)
    print("Caching response \n")
    #cache the response
    cache_response(cache_container, user_input, user_embeddings, completions_results)
    print("\n")
    # Return the generated LLM completion
    return completions_results['choices'][0]['message']['content'], False