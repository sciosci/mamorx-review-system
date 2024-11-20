from pathlib import Path
from typing import TypedDict, Optional, List, Any, Literal
from pydantic import BaseModel

class PDFReviewResult(TypedDict):
    full_path: Path
    name: str
    result: str


class ReviewResult(TypedDict):
    review_content: str
    time_elapsed: float
    novelty_assessment: Optional[str]
    figure_critic_assessment: Optional[str]


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
    figure_critic_url: str


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


class MultiAgentCrewReviewResult(TypedDict):
    crew: Any #Crew
    crew_output: Any #CrewOutput
    review: str
    usage_metrics: Any
    
    
class PaperArgument(TypedDict):
    title: str
    abstract: str
    
    
class NoveltyAssessmentResult(TypedDict):
    assessment: str
    summary: str


ReviewType = Literal["barebones", "liangetal", "multiagent", "mamorx"]

JobStatus = Literal["Queued", "In-progress", "Completed", "Expired", "Error"]


class ReviewJob(BaseModel):
    id: str #Hash of pdf file
    session_id: str
    filename: str
    review_type: ReviewType
    pdf_content: bytes


class ReviewJobStatus(BaseModel):
    id: str
    status: JobStatus
    filename: str
    review_type: ReviewType
    result: Optional[ReviewResult] = None


class SessionJobs(BaseModel):
    count: int
    jobs: List[ReviewJobStatus]


class SessionJobKeys(BaseModel):
    count: int
    job_ids: List[str]