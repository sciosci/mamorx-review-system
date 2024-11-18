from pydantic import BaseModel
from typing import Literal, Optional, List
from MAMORX.schemas import ReviewResult

ReviewType = Literal["barebones", "liangetal", "multiagent", "mamorx"]

class ReviewJob(BaseModel):
    id: str #Hash of pdf file
    session_id: str
    review_type: ReviewType
    pdf_content: bytes


class ReviewJobStatus(BaseModel):
    id: str
    status: Literal["Queued", "In-progress", "Completed"]
    result: Optional[ReviewResult] = None


class SessionJobs(BaseModel):
    count: int
    jobs: List[ReviewJobStatus]


class SessionJobKeys(BaseModel):
    count: int
    job_ids: List[str]