import base64
import json
import uuid

import gradio as gr


def generate_short_uuid():
    # Generate a UUID
    uuid_val = uuid.uuid4()

    # Encode the UUID using base64 and remove padding
    short_uuid = base64.urlsafe_b64encode(uuid_val.bytes).rstrip(b"=").decode("ascii")

    return short_uuid


def get_session_id(request: gr.Request | None):
    if request is None:
        return generate_short_uuid()

    if request.session_hash is None:
        return generate_short_uuid()

    return request.session_hash


def import_papers_from_jsonl(file_path):
    """
    Reads a JSONL file and converts it back to a list of dictionaries.

    Args:
    - file_path: The path to the JSONL file to read.

    Returns:
    - A list of dictionaries, each representing a paper.
    """
    papers = []
    with open(file_path, "r") as file:
        for line in file:
            paper = json.loads(line.strip())
            papers.append(paper)
    return papers


def export_papers_to_jsonl(papers, file_path):
    """
    Exports the list of papers to a JSONL file.

    Args:
    - papers: List of dictionaries containing paper information and reviews.
    - file_path: The path where the JSONL file will be saved.
    """
    with open(file_path, "w") as file:
        for paper in papers:
            json_line = json.dumps(paper)
            file.write(json_line + "\n")
