import os
import tempfile
from typing import Annotated, Literal
from fastapi import APIRouter, UploadFile, Form, File

from app.reviewer import reviewer_workflow
from MAMORX.schemas import ReviewResult


router = APIRouter()

@router.post("/review-pdf-paper", response_model=ReviewResult)
async def review_pdf_paper(
    pdf_file: Annotated[UploadFile, File()],
    review_type: Literal["barebones", "liangetal", "multiagent", "mamorx"]
):
    file_content = pdf_file.file

    file_content_bytes = file_content.read()

    review_result = ReviewResult()

    try:
        # Save PDF content to temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            try:
                temp_pdf.write(file_content_bytes)
                temp_pdf.flush()

                print(temp_pdf.name)
                review_result = reviewer_workflow.generate_review(
                    pdf_file_path=temp_pdf.name,
                    review_method=review_type
                )
            
            finally:
                # Cleanup
                os.unlink(temp_pdf.name)
    except Exception as e:
        return f"Error analyzing PDF: {str(e)}"

    return review_result