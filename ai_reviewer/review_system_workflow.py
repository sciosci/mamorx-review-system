from MultiAgentWorkflow import MultiAgentWorkflow
from pdf_processor import PdfProcessor
import json
import os

def extract_organized_text(json_data):
    organized_text = ""
    seen_sections = set()

    # Ensure we're working with the correct structure
    pdf_parse = json_data.get('pdf_parse', json_data)


    # Extract title by accessing the 'title' key in the JSON data
    for key in ['title', 'pdf_parse.title']:
        try:
            title = json_data
            for k in key.split('.'):
                title = title[k]
                organized_text += f"Title: {title}\n\n"
        except (KeyError,TypeError):
            title = 'Unnamed Title'
            organized_text += f"Title: {title}\n\n"
            

    # Extract abstract
    for key in ['abstract', 'pdf_parse.abstract.text']:
        try:
            abstract = json_data
            for k in key.split('.'):
                abstract = abstract[k]
                organized_text += f"Abstract: {abstract}\n\n"
        except (KeyError,TypeError):
            abstract = 'No abstract found'
            organized_text += f"Abstract: {abstract}\n\n"

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

    # Extract figures and tables
    if 'ref_entries' in pdf_parse:
        organized_text += "Figures and Tables:\n\n"
        for ref_key, ref_value in pdf_parse['ref_entries'].items():
            if ref_value['type_str'] in ['figure', 'table']:
                organized_text += f"{ref_value['text']}\n\n"
                if ref_value['type_str'] == 'table' and 'content' in ref_value:
                    organized_text += f"Table content: {ref_value['content']}\n\n"

    return organized_text.strip()

class ReviewSystemWorkflow:
    def __init__(self, base_dir, pdf_path, prompts_file, model_id):
        self.base_dir = base_dir
        self.pdf_path = pdf_path
        self.prompts_file = prompts_file
        self.model_id = model_id

    
    def run_workflow(self):
        # Step 1: Process the PDF
        pdf_processor = PdfProcessor()
        parsed_pdf_path = pdf_processor.process_pdf_file(self.pdf_path)
        
        # Step 2: Load the parsed PDF data
        with open(parsed_pdf_path, 'r') as f:
            parsed_pdf_data = json.load(f)

        # Step 2.5: extract the text from the parsed PDF data
        title = parsed_pdf_data['title']

        organized_text = extract_organized_text(parsed_pdf_data)

        output_dir = os.path.join(self.base_dir, 'output_files', 'temp')
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, 'organized_text.txt')

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n\n")
            f.write(organized_text)

        # Step 3: Initialize the MultiAgentWorkflow
        workflow = MultiAgentWorkflow(
            base_dir=self.base_dir,
            model_id=self.model_id,
            prompts_file=self.prompts_file,
            text_file=output_file_path
        )
        
       
        result = workflow.initiate_workflow()

        return result


