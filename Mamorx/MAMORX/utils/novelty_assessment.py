import os
import json
import time
import requests
import logging
from requests import Response
from typing import Dict, List
from ratelimit import limits, sleep_and_retry
from anthropic import AnthropicBedrock

from MAMORX.schemas import PaperArgument, APIConfigs, NoveltyAssessmentResult

logger = logging.getLogger(__name__)

@sleep_and_retry
@limits(calls=50, period=60)
def send_prompt_via_anthropic_bedrock(client: AnthropicBedrock, model_id: str, messages, max_tokens: int) -> str:
    response = client.messages.create(
            model=model_id,
            max_tokens=max_tokens,
            messages=messages
        )
    
    content = response.content
    if isinstance(content, list) and len(content) > 0:
        content = content[0].text
    else:
        content = str(content)

    content = content.strip()

    return content


@sleep_and_retry
@limits(calls=1, period=5)
def make_semantic_scholar_api_request(search_url: str, headers: Dict, params: Dict) -> Response:
    response = requests.get(search_url, headers=headers, params=params)
    return response
    
# Not used
# def extract_references(file):
#     print("============================")
#     print("Extracting References (Step: 1/7)")
#     print("============================")
    
#     references_dict = {}
#     references = file.get("references", [])
#     for ref in references:
#         title = ref.get("title")
#         abstract = ref.get("abstract")
#         if title and abstract:
#             references_dict[title] = abstract
#     print(references_dict)
#     return references_dict


def generate_search(client, argument, model_id: str):
    logging.info("============================")
    logging.info("GENERATING SEARCH PHRASES (Step: 2/7)")
    logging.info("============================")
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

    final_kw = send_prompt_via_anthropic_bedrock(
        client, 
        model_id, 
        messages,
        128
        )
    logging.info(f"First phrase: {final_kw}\n")
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

    final_kw = send_prompt_via_anthropic_bedrock(
        client, 
        model_id, 
        messages,
        128
        )
    logging.info(f"Second phrase: {final_kw}\n")
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

    final_kw = send_prompt_via_anthropic_bedrock(
        client, 
        model_id, 
        messages,
        128
        )
    logging.info(f"Third phrase: {final_kw}\n")
    search_phrases.append(final_kw)
    return search_phrases


def search_related_papers(client, argument, search_phrases, api_config: APIConfigs, model_id: str):
    logging.info("============================")
    logging.info("SEARCHING FOR RELATED PAPERS (Step: 3/7)")
    logging.info("============================")
    search_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    api_key = api_config["semantic_scholar_api_key"]
    
    related_papers = {}
    if not api_key:
        logging.error("API key is missing. Please set the X_API_KEY environment variable.")
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

    response = make_semantic_scholar_api_request(search_url, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        if 'data' in response_json:
            entries = response_json['data']
            logging.info(f'Query 1 produced {len(entries)} results')
            related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
        else:
            logging.warning("No 'data' key in the response. Response structure:")
            logging.warning(json.dumps(response_json, indent=2))
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
    
    # Search 2:
    params = {
        "query": search_phrases[1],
        "fields": "title,abstract",
        "limit": 10  # Number of results to retrieve
    }

    response = make_semantic_scholar_api_request(search_url, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        if 'data' in response_json:
            entries = response_json['data']
            logging.info(f'Query 2 produced {len(entries)} results')
            related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
        else:
            logging.warning("No 'data' key in the response. Response structure:")
            logging.warning(json.dumps(response_json, indent=2))
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
    # Search 3:
    params = {
        "query": search_phrases[2],
        "fields": "title,abstract",
        "limit": 10  # Number of results to retrieve
    }

    response = make_semantic_scholar_api_request(search_url, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        if 'data' in response_json:
            entries = response_json['data']
            logging.info(f'Query 3 produced {len(entries)} results')
            related_papers.update({entry['title']: entry['abstract'] for entry in entries if 'title' in entry and 'abstract' in entry})
        else:
            logging.warning("No 'data' key in the response. Response structure:")
            logging.warning(json.dumps(response_json, indent=2))
    else:
        logging.error(f"Error: {response.status_code} - {response.text}")
    logging.info("Titles of Related Papers Found:")
    logging.info(list(related_papers.keys()))
    return related_papers


def remove_cited(cited_papers, related_papers, model_id: str):
    logging.info("============================")
    logging.info("REMOVING CITATIONS FROM RECOMMENDED PAPERS (Step: 4/7)")
    logging.info("============================")
    
    # Take in list of cited papers
    # papers.toUpper()
    # see if any cited paper equals temp(toUpper(related_papers))
    # if so, remove from dict
    cited_titles = [paper.upper() for paper in cited_papers]
    filtered_papers = {title: abstract for title, abstract in related_papers.items() if title.upper() not in cited_titles}
    
    logging.info(f"Number of cited papers found in recommendation set: {len(related_papers.keys()) - len(filtered_papers.keys())}")
    return filtered_papers
    
    
def filter_papers(client, argument, related_papers, model_id: str):
    logging.info("============================")
    logging.info("FILTERING FOR RELEVANT PAPERS (Step: 5/7)")
    logging.info("============================")
    
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
        
        res = send_prompt_via_anthropic_bedrock(
            client, 
            model_id, 
            messages,
            2
        )
        if res.lower() == "relevant":
            filtered_dict[title] = abstract
        
    logging.info(f"Original length: {len(related_papers.keys())}")
    logging.info(f"Filtered length: {len(filtered_dict.keys())}")
    
    return filtered_dict


def assess_novelty(client, argument, filtered_dict, model_id: str):
    logging.info("============================")
    logging.info("ASSESSING NOVELTY (Step: 6/7)")
    logging.info("============================")
    
    
    # Loop through for novelty assessment.
    results = []
    for title, abstract in filtered_dict.items():
        logging.info(f"Comparing with: {title} \n")
        messages = [{
            "role": "user",
            "content": f'''
            As a skeptical novelty assessor, compare the following proposed academic paper abstract with an existing paper's abstract.
            Evaluate whether the new paper presents a significantly novel idea or approach compared to the existing paper. It is paramount
            that you do not let any non-novel paper slip by and look at the overlap through a critical lens. 
            
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
        response = send_prompt_via_anthropic_bedrock(
            client, 
            model_id, 
            messages,
            256
        )
        results.append({
            'existing_title': title,
            'assessment': response
        })
        logging.info(f"{response}\n")
        logging.info('-----------------------------------------')
        
    return results
    
    
### Make final step to summarize the entire novelty assessment into a single decision with explanation
def summarize_results(client, results, model_id: str):
    logging.info("============================")
    logging.info("SUMMARIZING RESULTS (Step: 7/7)")
    logging.info("============================")
    
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
    response = send_prompt_via_anthropic_bedrock(
            client, 
            model_id, 
            messages,
            256
        )
    logging.info(f"FINAL ASSESSMENT: \n{response}\n")
    return response


def generate_novelty_assessment(title: str, abstract: str, list_of_reference: List[str], api_config: APIConfigs) -> NoveltyAssessmentResult:
    # Initialize Client
    client = AnthropicBedrock(
        aws_access_key=api_config["aws_access_key_id"],
        aws_secret_key=api_config["aws_secret_access_key"],
        aws_region=api_config["aws_default_region"]
    )
    
    
    # Create paper argument
    paper_argument = PaperArgument(
        title=title,
        abstract=abstract
    )
    
    # Perform novelty assessment steps
    search_phrases = generate_search(client, paper_argument, model_id=api_config["anthropic_model_id"])
    related_papers = search_related_papers(client, paper_argument, search_phrases, api_config, model_id=api_config["anthropic_model_id"])
    final_related_papers = remove_cited(list_of_reference, related_papers, model_id=api_config["anthropic_model_id"])
    filtered_papers = filter_papers(client, paper_argument, final_related_papers, model_id=api_config["anthropic_model_id"])
    novelty_assessment = assess_novelty(client, paper_argument, filtered_papers, model_id=api_config["anthropic_model_id"])
    novelty_summary = summarize_results(client, novelty_assessment, model_id=api_config["anthropic_model_id"])
    
    novelty_assessment_result = NoveltyAssessmentResult(
        assessment=novelty_assessment,
        summary=novelty_summary
    )
    
    return novelty_assessment_result
