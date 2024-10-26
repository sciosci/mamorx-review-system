from MAMORX.schemas import PaperReviewResult, WorkflowPrompt, APIConfigs

from MAMORX.review_generator.baselines import generate_barebones_review, generate_liang_etal_review
from MAMORX.utils import load_workflow_prompt
from MAMORX.utils.pdf_processor import PDFProcessor

class ReviewerWorkflow:
    def __init__(self, prompt_file_path: str, output_dir: str, api_config: APIConfigs):
        self.workflow_prompts = load_workflow_prompt(prompt_file_path)
        self.output_dir = output_dir
        self.pdf_processor = PDFProcessor(output_dir)
        self.api_config = api_config


    def extract_organized_text(self, json_data: str):
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


    def run_workflow(self, pdf_file_path: str) -> PaperReviewResult:
        # Parse PDF
        paper = self.pdf_processor.process_pdf_file(pdf_file_path)

        # Extract information from paper
        organized_text, paper_id, title, abstract, list_of_reference = self.extract_organized_text(paper)
        
        # Generate barebones review
        barebones = generate_barebones_review(
            paper=organized_text,
            prompts=self.workflow_prompts['barebones'],
            api_config=self.api_config
        )

        # Generate liange etal review
        liang_etal = generate_liang_etal_review(
            title=title,
            paper=organized_text,
            prompts=self.workflow_prompts['liang_et_al'],
            api_config=self.api_config
        )

        # Create paper object
        paper_review_result = PaperReviewResult(
            paper_id=paper_id,
            title=title,
            pdf_path=pdf_file_path,
            barebones=barebones,
            liang_etal=liang_etal
        )


        return paper_review_result


    def get_prompts(self) -> WorkflowPrompt:
        return self.workflow_prompts
    

    def generate_barebones(self):
        pass