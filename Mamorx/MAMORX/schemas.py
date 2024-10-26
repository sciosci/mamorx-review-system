from pathlib import Path
from typing import TypedDict, Optional, List

class PDFReviewResult(TypedDict):
    full_path: Path
    name: str
    result: str


class ReviewResult(TypedDict):
    review_content: str
    time_elapsed: int


class PaperReviewResult(TypedDict):
    paper_id: str
    title: str
    pdf_path: str
    human_reviewer: Optional[str]
    barebones: Optional[ReviewResult]
    liang_etal: Optional[ReviewResult]
    multi_agent_without_knowledge: Optional[ReviewResult]
    multi_agent_with_knowledge: Optional[ReviewResult]


class APIConfigs(TypedDict):
    anthropic_model_id: str
    openai_api_key: str
    semantic_scholar_api_key: str
    openai_model_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str


class AgentPrompt(TypedDict):
    system_prompt: str
    task_prompt: Optional[str]


class MultiAgentPrompt(TypedDict):
    leader: AgentPrompt
    clarity_agent: AgentPrompt
    impact_agent: AgentPrompt
    experiment_agent: AgentPrompt
    manager: AgentPrompt


class WorkflowPrompt(TypedDict):
    barebones: AgentPrompt
    liang_et_al: AgentPrompt
    multi_agent_without_knowledge: MultiAgentPrompt
    multi_agent_with_knowledge: MultiAgentPrompt


class GrobidConfig(TypedDict):
    grobid_server: str
    batch_size: int
    sleep_time: int
    timeout: int
    coordinates: List[str]