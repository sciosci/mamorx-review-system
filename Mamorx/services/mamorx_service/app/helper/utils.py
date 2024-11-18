import uuid
import base64
from datetime import datetime

from app.schemas import ReviewJob, ReviewType

def create_review_job(
        pdf_data: bytes,
        session_id: str,
        review_type: ReviewType
) -> ReviewJob:
    id = uuid.uuid4().hex

    job_to_submit = ReviewJob(
        id=id,
        session_id=session_id,
        review_type=review_type,
        pdf_content=base64.b64encode(pdf_data)
    )

    return job_to_submit
