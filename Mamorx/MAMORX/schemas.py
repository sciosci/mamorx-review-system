from pathlib import Path
from typing import TypedDict, Optional

class PDFReviewResult(TypedDict):
    full_path: Path
    name: str
    result: str


class Paper(TypedDict):
    paper_id: str
    title: str
    pdf_path: str
    human_reviewer: Optional[str]
    barebones: Optional[str]
    liang_etal: Optional[str]
    multi_agent_without_knowledge: Optional[str]
    multi_agent_with_knowledge: Optional[str]


class APIConfigs(TypedDict):
    openai_api_key: str
    x_api_key: str
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
    grobid_port: str
    batch_size: int
    sleep_time: int
    generateIDs: bool
    consolidate_header: bool
    consolidate_citations: bool
    include_raw_citations: bool
    include_raw_affiliations: bool
    max_workers: int