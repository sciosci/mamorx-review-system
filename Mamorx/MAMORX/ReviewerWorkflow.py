from MAMORX.schemas import Paper, WorkflowPrompt

from MAMORX.review_generator.baselines import generate_barebones_review, generate_liang_etal_review
from MAMORX.utils import load_workflow_prompt

class ReviewerWorkflow:
    def __init__(self, prompt_file_path: str):
        self.workflow_prompts = load_workflow_prompt(prompt_file_path)


    def extract_organized_text(self, json_data: str):
        pass


    def run_workflow(self) -> Paper:
        pass


    def get_prompts(self) -> WorkflowPrompt:
        return self.workflow_prompts