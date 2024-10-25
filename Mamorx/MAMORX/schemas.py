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