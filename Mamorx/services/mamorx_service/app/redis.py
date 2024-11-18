from redis import Redis
from typing import List, Optional
from app.config import settings
from app.schemas import ReviewJob, ReviewJobStatus, SessionJobKeys

redis_client = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)


def submit_job_to_queue(job: ReviewJob):
    # Add job to queue
    response = redis_client.lpush(settings.redis_queue_name, job.model_dump_json())

    # Get session job data
    session_job_data_json: Optional[str] = redis_client.get(job.session_id)

    if(session_job_data_json == None):
        # Create session
        new_session = SessionJobKeys(
            job_ids=[job.id],
            count=1
        )
        res_creation_session_data = redis_client.set(job.session_id, new_session.model_dump_json())
        return res_creation_session_data
    
    # Parse json string as session job data
    session_job_data: SessionJobKeys = SessionJobKeys.model_validate_json(session_job_data_json)
    
    # Add job id to session job data
    session_job_data.job_ids.append(job.id)
    session_job_data.count += 1

    # Save updated session data
    response = redis_client.set(job.session_id, session_job_data.model_dump_json())
    
    return response


def add_job_data(job_status: ReviewJobStatus):
    response = redis_client.set(job_status.id, job_status.model_dump_json())
    return response


def get_job_data_for_session_id(session_id: str) -> Optional[ReviewJobStatus]:
    # Get session job data
    session_job_data_json: Optional[str] = redis_client.get(session_id)

    if(session_job_data_json == None):
        return None
    
    # Parse json string as session job data
    session_job_data: SessionJobKeys = SessionJobKeys.model_validate_json(session_job_data_json)
    
    # Get individual job data
    job_data = list()
    for job_id in session_job_data.job_ids:
        info_json = redis_client.get(job_id)
        info = ReviewJobStatus.model_validate_json(info_json)
        job_data.append(info)

    return job_data


def get_queue_content() -> List[ReviewJob]:
    queue = redis_client.lrange(settings.redis_queue_name, 0, -1)
    
    parsed_queue = list()
    for json_record in queue:
        parsed_record = ReviewJob.model_validate_json(json_record)
        parsed_record.pdf_content = b""
        parsed_queue.append(parsed_record)

    return parsed_queue