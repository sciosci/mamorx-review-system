import requests
from crewai_tools import BaseTool
import os

# Function to search related papers
class SemanticScholar(BaseTool):
    name:str = "SemanticScholar"
    description:str = """
    This tool is used for searching related papers. 
    The input should the paper title. It is a string.
    It will give back abstracts of the top 10 related papers.
    """
    def _run(self, title:str) -> list[str]:
        match_url =  "https://api.semanticscholar.org/graph/v1/paper/search/match"
        recommend_url = "https://api.semanticscholar.org/recommendations/v1/papers/forpaper/"
        search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        api_key = os.getenv("X_API_KEY")
        if not api_key:
            print("API key is missing. Please set the X_API_KEY environment variable.")
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }
        match_params = {
            "query": title,
            "fields": "title",
            "limit": 1
        }
        title_match_response = requests.get(match_url, headers=headers, params=match_params)
                
        if title_match_response.status_code == 200:
            # test
            matched_title = title_match_response.json()['data'][0]['title']
            paperId = title_match_response.json()['data'][0]['paperId']
            # print(type(paperId))
            # print(title, paperId)

            # Get the exact paper in SS
            if matched_title == title:

                url=recommend_url+paperId    
                params = {
                    "fields": "abstract",
                    "limit": 10,  
                }

                # Search for Recommended Papers
                response = requests.get(url, headers=headers, params=params)
                # Get recommended Papers
                if response.status_code == 200:
                    recommended_papers = response.json()['recommendedPapers']

                    # Recommended Papers could be None
                    if recommended_papers:
                        print(f'{len(recommended_papers)} founded')
                        abstracts = [paper['abstract'] for paper in recommended_papers]
                        # print(len(abstracts))
                    else: 
                        print('No related Paper!')
                        return None
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    return None
            
        # Not the same paper
        else:
            params = {
                "query": title,
                "fields": "abstract",
                "limit": 10  # Number of results to retrieve
            }

            response = requests.get(search_url, headers=headers, params=params)
            if response.status_code == 200:
                entries = response.json()['data']
                abstracts = [entry['abstract'] for entry in entries]
                # print(len(abstracts))
            else:
                print(f"Error: {response.status_code} - {response.text}")
                return None
        return abstracts