from azure.cosmos import CosmosClient
import yaml
import os

class CosmosDBClient:
    config_file_path = os.path.join(os.path.dirname(__file__), "conf/config.yaml")
    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)
        COSMOS_DB_ENDPOINT = config['cosmos_db_endpoint']
        COSMOS_DB_KEY = config['cosmos_db_key']
        DATABASE_NAME = config['database_name']
        CONTAINER_NAME = config['container_name']

    def __init__(self):
        self.client = CosmosClient(self.COSMOS_DB_ENDPOINT, self.COSMOS_DB_KEY)
        self.database = self.client.get_database_client(self.DATABASE_NAME)
        self.container = self.database.get_container_client(self.CONTAINER_NAME)

    def write_articles(self, articles):
        for article in articles:
            self.container.upsert_item(article)

    # Perform a vector search on the Cosmos DB container
def vector_search(container, vectors, similarity_score=0.02, num_results=5):
    # Execute the query
    results = container.query_items(
        query= '''
        SELECT TOP @num_results  c.overview, VectorDistance(c.vector, @embedding) as SimilarityScore 
        FROM c
        WHERE VectorDistance(c.vector,@embedding) > @similarity_score
        ORDER BY VectorDistance(c.vector,@embedding)
        ''',
        parameters=[
            {"name": "@embedding", "value": vectors},
            {"name": "@num_results", "value": num_results},
            {"name": "@similarity_score", "value": similarity_score}
        ],
        enable_cross_partition_query=True, populate_query_metrics=True)
    results = list(results)
    # Extract the necessary information from the results
    formatted_results = []
    for result in results:
        score = result.pop('SimilarityScore')
        formatted_result = {
            'SimilarityScore': score,
            'document': result
        }
        formatted_results.append(formatted_result)

    # #print(formatted_results)
    metrics_header = dict(container.client_connection.last_response_headers)
    #print(json.dumps(metrics_header,indent=4))
    return formatted_results
        
   
    
    