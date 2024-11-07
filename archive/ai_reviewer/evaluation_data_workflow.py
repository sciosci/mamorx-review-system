from pydantic import BaseModel
from typing import Optional
from MultiAgentWorkflow import MultiAgentWorkflow
from pdf_processor import PdfProcessor
from baselines import generate_barebones_review, generate_liang_etal_review
from FigureTool.FigureTool import FigureTool, PaperArgument, ExtractedFigureCaption
from NoveltyTool.NoveltyTool import NoveltyTool
from anthropic import AnthropicBedrock
import json
import re
import os


def text_converter(text:str)->str:
    # A function that takes a text and converts it to a JSONL compatible format
    text = text.replace('\n', '\\n')
    text = text.replace("\'","\\'" )
    text = re.sub(r'([{}\[\]])', r'\\\1', text)
    text = re.sub(r'(?<!\\)\\(?!["\\/bfnrt])', r'\\\\', text)

    return text 

class Paper(BaseModel):
    paper_id: str
    title: str
    pdf_path: str
    human_reviewer: Optional[str]
    barebones: Optional[str]
    liang_etal: Optional[str]
    multi_agent_without_knowledge: Optional[str]
    multi_agent_with_knowledge: Optional[str]



def generate_jsonl_line(paper_id: str, title: str, pdf_path: str, 
                        human_reviewer_path: str, barebones_path: str, 
                        liang_etal_path: str, multi_agent_without_knowledge_path: str, 
                        multi_agent_with_knowledge_path: str) -> str:
    
    def read_and_process(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return text_converter(content)
        except FileNotFoundError:
            print(f"Warning: File not found - {file_path}")
            return ""
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
            return ""

    paper = Paper(
        paper_id=paper_id,
        title=title,
        pdf_path=pdf_path,
        human_reviewer=human_reviewer_path,
        barebones=read_and_process(barebones_path),
        liang_etal=read_and_process(liang_etal_path),
        multi_agent_without_knowledge=read_and_process(multi_agent_without_knowledge_path),
        multi_agent_with_knowledge=read_and_process(multi_agent_with_knowledge_path)
    )

    # Convert to a single-line JSON string
    jsonl_line = json.dumps(paper.dict(), ensure_ascii=False, separators=(',', ':'))
    return jsonl_line



class ReviewSystemWorkflow:
    def __init__(self, base_dir, pdf_path, human_reviewer_path, prompts_file, model_id):
        self.base_dir = base_dir
        self.pdf_path = pdf_path
        self.human_reviewer_path = human_reviewer_path
        self.prompts_file = prompts_file
        self.model_id = model_id
        self.output_dir = os.path.join(self.base_dir, 'generated_reviews')
        self.temp_output_dir = os.path.join(self.base_dir, 'temp')
        self.novelty_tool = NoveltyTool()
        self.figure_tool = FigureTool()
        self.client = AnthropicBedrock(
            aws_access_key=os.getenv("AWS_ACCESS_KEY_ID"),  
            aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),  
            aws_region=os.getenv("AWS_DEFAULT_REGION")
        )
        os.makedirs(self.output_dir, exist_ok=True)


    def extract_organized_text(self,json_data):
        organized_text = ""
        seen_sections = set()
        list_of_reference = []

        # Ensure we're working with the correct structure
        pdf_parse = json_data.get('pdf_parse', json_data)

        # Extract paper ID
        paper_id = json_data.get('paper_id', 'No paper ID found')


        # Extract title by accessing the 'title' key in the JSON data
        title = None
        for key in ['title', 'pdf_parse.title']:
            try:
                temp = json_data
                for k in key.split('.'):
                    temp = temp[k]
                title = temp
                break
            except (KeyError,TypeError):
                continue

        organized_text += f"Title: {title or 'No title found'}\n\n"
                

        # Extract abstract
        abstract = None
        for key in ['abstract', 'pdf_parse.abstract.text']:
            try:
                temp = json_data
                for k in key.split('.'):
                    temp = temp[k]
                if isinstance(temp, list) and temp and 'text'in temp[0]:
                    abstract = temp[0]['text']
                elif isinstance(temp, str):
                    abstract = temp
                break
            except (KeyError,TypeError):
                continue
        organized_text += f"Abstract: {abstract or 'No abstract found'}\n\n"

        # Extract body text
        if 'body_text' in pdf_parse:
            for body_item in pdf_parse['body_text']:
                section = body_item.get('section', 'Unnamed Section')
                sec_num = body_item.get('sec_num')
                
                if section not in seen_sections:
                    seen_sections.add(section)
                    if sec_num:
                        organized_text += f"{sec_num}. {section}:\n\n"
                    else:
                        organized_text += f"{section}:\n\n"
                
                organized_text += body_item['text'] + "\n\n"

        # Extract a list of references titles in strings
        if 'bib_entries' in pdf_parse:
            for bibref in pdf_parse['bib_entries']:
                try :
                    list_of_reference.append(pdf_parse['bib_entries'][bibref]['title'])
                except (KeyError, TypeError):
                    continue



        # Extract figures and tables
        if 'ref_entries' in pdf_parse:
            organized_text += "Figures and Tables:\n\n"
            for ref_key, ref_value in pdf_parse['ref_entries'].items():
                if ref_value['type_str'] in ['figure', 'table']:
                    organized_text += f"{ref_value['text']}\n\n"
                    if ref_value['type_str'] == 'table' and 'content' in ref_value:
                        organized_text += f"Table content: {ref_value['content']}\n\n"

        return organized_text.strip(), paper_id, title, abstract, list_of_reference





    
    def run_workflow(self):
        # Step 1: Process the PDF
        pdf_processor = PdfProcessor()
        parsed_pdf_path = pdf_processor.process_pdf_file(self.pdf_path)
        
        # Step 2: Load the parsed PDF data
        with open(parsed_pdf_path, 'r', encoding="utf-8") as f:
            parsed_pdf_data = json.load(f)

        organized_text, paper_id, title, abstract, list_of_reference = self.extract_organized_text(parsed_pdf_data)

        output_dir = os.path.join(self.base_dir, 'temp')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, 'organized_text.txt')

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(organized_text)

        # Step 3: Generate the baseline reviews
        # Ensure the directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        liang_etal_review = generate_liang_etal_review(title="Title", paper=organized_text, prompt_file=self.prompts_file)

        with open(os.path.join(self.output_dir,'liang_etal_review.txt'), 'w', encoding="utf-8") as f:
            f.write(liang_etal_review)
        
        barebones_review = generate_barebones_review(paper=organized_text, prompt_file=self.prompts_file)

        with open(os.path.join(self.output_dir, 'barebones_review.txt'), 'w', encoding="utf-8") as f:
            f.write(barebones_review)

        # Step 4: Initialize the MultiAgentWorkflow without knowledge here
        workflow = MultiAgentWorkflow(
            base_dir=self.base_dir,
            model_id=self.model_id,
            prompts_file=self.prompts_file,
            text_file= output_file_path,
            output_path= os.path.join(self.output_dir, 'final_review_without_knowledge.txt'),
            system_type='multi_agent_without_knowledge'
        )
        result_without_knowledge = workflow.initiate_workflow()
        # Step 5: Initialize the MultiAgentWorkflow with knowledge here

        paper_argument = PaperArgument(title=title, abstract=abstract)
        # Step 5.1 : Assess Novelty
        search_phrases = self.novelty_tool.generate_search(self.client, paper_argument)
        related_papers = self.novelty_tool.search_related_papers(self.client, paper_argument, search_phrases)
        final_related_papers = self.novelty_tool.remove_cited(list_of_reference, related_papers)
        filter_papers = self.novelty_tool.filter_papers(self.client, paper_argument, final_related_papers)
        novelty_assessment = self.novelty_tool.assess_novelty(self.client, paper_argument, filter_papers)
        novelty_summary = self.novelty_tool.summarize_results(self.client, novelty_assessment)
        
        os.makedirs(self.temp_output_dir, exist_ok=True)

        with open(os.path.join(self.temp_output_dir, 'novelty_assessment.txt'), 'w', encoding="utf-8") as f:
            for item in novelty_assessment:
                f.write(f"{item}\n")

        # Step 5.2 : Assess Image Caption
        image_caption_dict = self.figure_tool.extract_figures_and_captions(self.pdf_path)
        figure_critic_assessment = self.figure_tool.assess_figures_and_captions(self.client, paper_argument, image_caption_dict)

        with open(os.path.join(self.temp_output_dir, 'figure_critic_assessment.txt'), 'w', encoding="utf-8") as f:
            f.write(figure_critic_assessment)
                  
        # Step 5.3: Initialize the MultiAgentWorkflow with knowledge here
        workflow = MultiAgentWorkflow(
            base_dir=self.base_dir,
            model_id=self.model_id,
            prompts_file=self.prompts_file,
            text_file=output_file_path,
            output_path= os.path.join(self.output_dir, 'final_review_with_knowledge.txt'),
            novelty_assessment_path=os.path.join(self.temp_output_dir, 'novelty_assessment.txt'),
            figure_critic_assessment_path=os.path.join(self.temp_output_dir, 'figure_critic_assessment.txt'),
            system_type='multi_agent_with_knowledge'
        )

        
       
        result_with_knowledge = workflow.initiate_workflow()
        # Step 6: Post-processing
        with open(os.path.join(self.output_dir, 'final_review_with_knowledge.txt'), 'r', encoding="utf-8") as f:
            final_review = f.read()

        message = [{"role": "user",
                    "content":f"""
                    Your task is to incorporate a novelty assessment and a critical assessment of figures in an academic paper into the existing review of the paper. The primary goal for the review is to provide a well-balanced review, which include the discussion of the strength of the paper, details, limitations as well as providing constructive criticism that will help the authors improve their work in the future.

                    Key instructions:
                    1. Prioritize incorporating the critical feedback from the 2 assessments, especially regarding novelty and figure quality.
                    2. If the novelty assessment indicates a lack of novelty, this must be clearly stated in the final review, along with the reasons provided.
                    3. Do not paraphrase or change the review unless for the part where the novelty and figure assessments needed to be incorporated.

                    Remember, the purpose of the task is to help authors improve their work.
                    
                    
                    --- START OF NOVELTY ASSESSMENT--- {novelty_assessment} --- END OF NOVELTY ASSESSMENT ---
                    --- START OF FIGURE CRITIC ASSESSMENT--- {figure_critic_assessment} --- END OF FIGURE CRITIC ASSESSMENT ---
                    --- START OF REVIEW--- {final_review} --- END OF REVIEW ---

                    Based on these inputs, generate the comprehensive review that incorporates the elements of the two assessments into the review with a focus on providing constructive criticism and areas for improvement.
                    """}
        ]

        response = self.client.messages.create(
                model= self.model_id,
                max_tokens= 2048,
                messages= message
        )

        response = response.content
        if isinstance(response, list) and len(response)>0:
            response = response[0].text
        else:
            response = str(response)
        
        response = response.strip()

        paper_json =generate_jsonl_line(paper_id, title, self.pdf_path, 
                        self.human_reviewer_path, os.path.join(self.output_dir, 'barebones_review.txt'), 
                        os.path.join(self.output_dir,'liang_etal_review.txt'), os.path.join(self.output_dir, 'final_review_without_knowledge.txt'), 
                        os.path.join(self.output_dir, 'final_review_with_knowledge.txt'))

        print(paper_json)
        with open(os.path.join(self.output_dir, 'reviews.json'), 'w', encoding="utf-8") as f:
            f.write(paper_json)
    
    
        return paper_json
    
