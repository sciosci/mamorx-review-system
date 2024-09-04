import os
import json
import time
import requests
from crewai_tools import BaseTool

class NoveltyTool(BaseTool):
    name:str = "novelty-tool"
    description:str = ""
        
    def _run(self, argument: dict) -> list[str]:
        pass
    
    def extract_references(self, file):
        print("============================")
        print("Extracting References (Step: 1/7)")
        print("============================")
        
        references_dict = {}
        references = file.get("references", [])
        for ref in references:
            title = ref.get("title")
            abstract = ref.get("abstract")
            if title and abstract:
                references_dict[title] = abstract
        print(references_dict)
        return references_dict

    def generate_search(self, client, argument):
        print("============================")
        print("GENERATING SEARCH PHRASES (Step: 2/7)")
        print("============================")
        # Generate Keywords
        search_phrases = []

        # First Search Phrase 
        messages = [{
            "role": "user",
            "content": f'''
            Given the abstract of an academic paper below, generate a search phrase of less than 10 words to find related papers in the field. Return ONLY this phrase
            This phrase should be useful for searching for similar papers in academic databases. Use general terms that reflect domain-specific field knowledge to 
            enable a fruitful search. 

            Abstract: {argument['abstract']}
            '''
        }]

        keywords = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=128,
            messages=messages
        )

        content = keywords.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0].text
        else:
            content = str(content)

        final_kw = content.strip()
        print(f"First phrase: {final_kw}\n")
        search_phrases.append(final_kw)
        
        # Second Search Phrase
        messages = [{
            "role": "user",
            "content": f'''
            Given the abstract of an academic paper and a previously generated search phrase, create a new, broader search phrase of less than 10 words. 
            This new phrase should expand the search scope to include related concepts or methodologies not covered by the first phrase. 
            Return ONLY this new phrase.

            Abstract: {argument['abstract']}
            Previous search phrase: {search_phrases}
            '''
        }]

        keywords = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=128,
            messages=messages
        )

        content = keywords.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0].text
        else:
            content = str(content)

        final_kw = content.strip()
        print(f"Second phrase: {final_kw}\n")
        search_phrases.append(final_kw)
        
        # Third Search Phrase
        messages = [{
            "role": "user",
            "content": f'''
            Given an academic paper abstract and two previously generated search phrases, create a final, even broader search phrase of less than 10 words. 
            This phrase should capture the most general concepts related to the paper's field of study, potentially including interdisciplinary connections. 
            The goal is to cast the widest possible net for related research. Return ONLY this new phrase.

            Abstract: {argument['abstract']}
            Previous search phrase: {search_phrases}
            '''
        }]

        keywords = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=128,
            messages=messages
        )

        content = keywords.content
        if isinstance(content, list) and len(content) > 0:
            content = content[0].text
        else:
            content = str(content)

        final_kw = content.strip()
        print(f"Third phrase: {final_kw}\n")
        search_phrases.append(final_kw)
        return search_phrases

    def search_related_papers(self, client, argument, search_phrases):
        print("============================")
        print("SEARCHING FOR RELATED PAPERS (Step: 3/7)")
        print("============================")
        search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        api_key = os.getenv("X_API_KEY")
        
        related_papers = {}
        if not api_key:
            print("API key is missing. Please set the X_API_KEY environment variable.")
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }
        
        # Search 1:
        params = {
            "query": search_phrases[0],
            "fields": "title,abstract",
            "limit": 10  # Number of results to retrieve
        }

        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            response_json = response.json()
            if 'data' in response_json:
                entries = response_json['data']
                print(f'Query 1 produced {len(entries)} results')
                related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
            else:
                print("No 'data' key in the response. Response structure:")
                print(json.dumps(response_json, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        # Search 2:
        time.sleep(1)
        params = {
            "query": search_phrases[1],
            "fields": "title,abstract",
            "limit": 10  # Number of results to retrieve
        }

        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            response_json = response.json()
            if 'data' in response_json:
                entries = response_json['data']
                print(f'Query 2 produced {len(entries)} results')
                related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
            else:
                print("No 'data' key in the response. Response structure:")
                print(json.dumps(response_json, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
        # Search 3:
        time.sleep(1)
        params = {
            "query": search_phrases[2],
            "fields": "title,abstract",
            "limit": 10  # Number of results to retrieve
        }

        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            response_json = response.json()
            if 'data' in response_json:
                entries = response_json['data']
                print(f'Query 3 produced {len(entries)} results')
                related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
            else:
                print("No 'data' key in the response. Response structure:")
                print(json.dumps(response_json, indent=2))
        else:
            print(f"Error: {response.status_code} - {response.text}")
        print("Titles of Related Papers Found:")
        print(list(related_papers.keys()))
        return related_papers
    
    def remove_cited(self, cited_papers, related_papers):
        print("============================")
        print("REMOVING CITATIONS FROM RECOMMENDED PAPERS (Step: 4/7)")
        print("============================")
        
        # Take in list of cited papers
        # papers.toUpper()
        # see if any cited paper equals temp(toUpper(related_papers))
        # if so, remove from dict
        cited_titles = [paper.upper() for paper in cited_papers]
        filtered_papers = {title: abstract for title, abstract in related_papers.items() if title.upper() not in cited_titles}
        
        print(f"Number of cited papers found in recommendation set: {len(related_papers.keys()) - len(filtered_papers.keys())}")
        return filtered_papers
        
    def filter_papers(self, client, argument, related_papers):
        print("============================")
        print("FILTERING FOR RELEVANT PAPERS (Step: 5/7)")
        print("============================")
        
        filtered_dict = {}
        
        for title, abstract in related_papers.items():
            messages = [{
                "role": "user",
                "content":f'''
                Assess the relevancy of the following paper to the core paper. Be strict in your assessment
                and only consider it relevant if it closely relates to the core concept.
                If the core paper and the paper to assess are the same thing, your assessment is "Irrelevant"
                Core Paper:
                Title: {argument['title']}
                Abstract: {argument['abstract']}
                
                Paper to Assess:
                Title: {title}
                Abstract: {abstract}
                
                Provide your assessment as a single word: "Relevant" or "Irrelevant".
                Only output the single word with no other text or explanation
                '''
            }]
            
            response = client.messages.create(
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
                max_tokens=2,
                messages=messages
            )
            content = response.content
            if isinstance(content, list) and len(content) > 0:
                content = content[0].text
            else:
                content = str(content)

            res = content.strip()
            if res.lower() == "relevant":
                filtered_dict[title] = abstract
            
        print(f"Original length: {len(related_papers.keys())}")
        print(f"Filtered length: {len(filtered_dict.keys())}")
        
        return filtered_dict

    
    def assess_novelty(self, client, argument, filtered_dict):
        print("============================")
        print("ASSESSING NOVELTY (Step: 6/7)")
        print("============================")
        
        
        # Loop through for novelty assessment.
        results = []
        for title, abstract in filtered_dict.items():
            print(f"Comparing with: {title} \n")
            messages = [{
                "role": "user",
                "content": f'''
                As a novelty assessor, compare the following proposed academic paper abstract with an existing paper's abstract.
                Evaluate whether the new paper presents a significantly novel idea or approach compared to the existing paper.
                
                New Paper: 
                Title: {argument['title']}
                Abstract: {argument['abstract']}
                
                Existing Paper
                Title: {title}
                Abstract: {abstract}
                
                Please consider:
                1. A brief comparison of the key ideas, methods, or findings
                2. An assessment of the novelty of the new paper compared to the existing one.
                3. A clear decision: Is the new paper sufficiently novel compared to this existing paper? Answer with "Novel" or "Not Novel".
                
                However, in your response, simply provide a decision and a 2-3 sentence justification for your decision.
                
                Format your response as follows:
                
                Decision: [Novel/Not Novel]
                
                Justification: [Your Assessment Here]
                '''
            }]
            response = client.messages.create(
                model="anthropic.claude-3-5-sonnet-20240620-v1:0",
                max_tokens=256,
                messages=messages
            )
            
            # Format response to text only:
            response = response.content
            if isinstance(response, list) and len(response) > 0:
                response = response[0].text
            else:
                response = str(response)

            response = response.strip()
            results.append({
                'existing_title': title,
                'assessment': response
            })
            print(f"{response}\n")
            print('-----------------------------------------')
            
        return results
        
    ### Make final step to summarize the entire novelty assessment into a single decision with explanation
    def summarize_results(self, client, results):
        print("============================")
        print("SUMMARIZING RESULTS (Step: 7/7)")
        print("============================")
        
        messages = [{
            'role': 'user',
            'content': f'''
                Given the following novelty assessment results, please summarize whether the proposed paper is novel or not. If any of the comparisons deem the paper as NOT NOVEL, 
                start the summary with ‘NOT NOVEL’, followed by an explanation that includes the title of the conflicting paper(s). If the paper is considered NOVEL, start the summary 
                with ‘NOVEL’, and then provide a brief justification of what makes it novel.

                Here are the assessment results:
                {results}
            '''
        }]
        response = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            max_tokens=256,
            messages=messages
        )
        # Format response to text only:
        response = response.content
        if isinstance(response, list) and len(response) > 0:
            response = response[0].text
        else:
            response = str(response)

        response = response.strip()
        print(f"FINAL ASSESSMENT: \n{response}\n")
        return response
