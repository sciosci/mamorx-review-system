from MAMORX.schemas import Paper, WorkflowPrompt

from MAMORX.review_generator.baselines import generate_barebones_review, generate_liang_etal_review
from MAMORX.utils import load_workflow_prompt
from MAMORX.utils.pdf_processor import PDFProcessor

class ReviewerWorkflow:
    def __init__(self, prompt_file_path: str, output_dir: str):
        self.workflow_prompts = load_workflow_prompt(prompt_file_path)
        self.output_dir = output_dir
        self.pdf_processor = PDFProcessor(output_dir)


    def extract_organized_text(self, json_data: str):
        pass


    def run_workflow(self) -> Paper:
        pass


    def get_prompts(self) -> WorkflowPrompt:
        return self.workflow_prompts
    

    def generate_barebones(self):
        pass