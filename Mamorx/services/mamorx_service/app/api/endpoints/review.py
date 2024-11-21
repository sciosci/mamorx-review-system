from typing import Annotated, List
from fastapi import APIRouter, UploadFile, File, Header

from MAMORX.schemas import ReviewJobStatus, ReviewType, SessionJobs, ReviewJob
from app.redis import \
    submit_job_to_queue, \
    add_job_data, \
    get_job_data_for_session_id, \
    get_queue_content
from app.helper.utils import create_review_job


router = APIRouter()


@router.post("/submit-pdf-to-queue", response_model=ReviewJobStatus)
async def submit_pdf_to_queue(
    pdf_file: Annotated[UploadFile, File()],
    review_type: ReviewType,
    session_id: Annotated[str, Header()]
):
    # Read file contents
    pdf_data = await pdf_file.read()
    
    job_to_submit = create_review_job(
        filename=pdf_file.filename,
        pdf_data=pdf_data,
        session_id=session_id,
        review_type=review_type
    )

    # Submit job to queue
    submit_job_to_queue(job_to_submit)

    # Create job status object
    review_status = ReviewJobStatus(
        id=job_to_submit.id,
        status="Queued",
        filename=pdf_file.filename,
        review_type=review_type,
        result=None
    )

    # Add job status to database (using redis for simplicity)
    add_job_data(review_status)

    return review_status


@router.get("/review-jobs", response_model=SessionJobs)
async def get_jobs_for_session_id(
    session_id: Annotated[str, Header()]
):
    # Query jobs with session_id
    job_list = get_job_data_for_session_id(session_id)

    if(job_list == None):
        job_list = list()

    # Create SessionJobs Object
    session_jobs = SessionJobs(
        count=len(job_list),
        jobs=job_list
    )

    return session_jobs


@router.get("/queue", response_model=List[ReviewJob])
async def get_queue():
    queue = get_queue_content()

    return queue