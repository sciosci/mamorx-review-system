import requests
from crewai_tools import BaseTool
import os

# Function to search related papers
class SemanticScholar(BaseTool):
    name:str = "SemanticScholar"
    description:str = """
    This tool is used for searching related papers according to given keywords. 
    The input should be a string concatnating keywords with "+", e.g. "keyword1+keyword2+keyword3".
    It will give back titles and abstracts of the top ranked 10 papers.
    """
    def _run(self, query):
        SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
        api_key=os.getenv("X_API_KEY")
        headers = {
            "x-api-key": api_key,  # Add your API key here if required
            "Content-Type": "application/json",
        }
        
        params = {
            "query": query,
            "fields": "title, abstract",
            "limit": 10  # Number of results to retrieve
        }
        
        response = requests.get(SEMANTIC_SCHOLAR_API_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
