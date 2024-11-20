import uuid
import base64

from MAMORX.schemas import ReviewJob, ReviewType

def create_review_job(
        filename: str,
        pdf_data: bytes,
        session_id: str,
        review_type: ReviewType
) -> ReviewJob:
    id = uuid.uuid4().hex

    job_to_submit = ReviewJob(
        id=id,
        session_id=session_id,
        filename=filename,
        review_type=review_type,
        pdf_content=base64.b64encode(pdf_data)
    )

    return job_to_submit
