from MultiAgentWorkflow import MultiAgentWorkflow
from pdf_processor import PdfProcessor
from baselines import generate_barebones_review, generate_liang_etal_review
import json
import os

class ReviewSystemWorkflow:
    def __init__(self, base_dir, pdf_path, prompts_file, model_id):
        self.base_dir = base_dir
        self.pdf_path = pdf_path
        self.prompts_file = prompts_file
        self.model_id = model_id
        self.output_dir = os.path.join(self.base_dir, 'output_files', 'generated_reviews')
        os.makedirs(self.output_dir, exist_ok=True)


    def extract_organized_text(self,json_data):
        organized_text = ""
        seen_sections = set()
        list_of_reference = []

        # Ensure we're working with the correct structure
        pdf_parse = json_data.get('pdf_parse', json_data)



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

        return organized_text.strip(), title, abstract, list_of_reference


    # Brandley's tool
    # input from extract information
    # output is the suggestion for commenting on the novelty of the paper


    # Pawin's tool
    # 
    #


    
    def run_workflow(self):
        # Step 1: Process the PDF
        pdf_processor = PdfProcessor()
        parsed_pdf_path = pdf_processor.process_pdf_file(self.pdf_path)
        
        # Step 2: Load the parsed PDF data
        with open(parsed_pdf_path, 'r') as f:
            parsed_pdf_data = json.load(f)

        organized_text = self.extract_organized_text(parsed_pdf_data)[0]

        output_dir = os.path.join(self.base_dir, 'output_files', 'temp')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, 'organized_text.txt')

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(organized_text)

        # Step 3: Generate the baseline reviews

        liang_etal_review = generate_liang_etal_review(title="Title", paper=organized_text)

        with open(os.path.join(self.output_dir, 'liang_etal_review.txt'), 'w') as f:
            f.write(liang_etal_review)
        
        barebones_review = generate_barebones_review(paper=organized_text)

        with open(os.path.join(self.output_dir, 'barebones_review.txt'), 'w') as f:
            f.write(barebones_review)


        # Step 4: Initialize the MultiAgentWorkflow


        workflow = MultiAgentWorkflow(
            base_dir=self.base_dir,
            model_id=self.model_id,
            prompts_file=self.prompts_file,
            text_file=output_file_path,
            novelty_assessment_file=os.path.join(self.base_dir, 'ai_reviewer', 'novelty_pawin.txt')
        )
        
       
        result = workflow.initiate_workflow()

        return result


