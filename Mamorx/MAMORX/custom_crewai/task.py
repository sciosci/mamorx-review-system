from crewai import Task
from pydantic import (
    field_validator
)

class CustomTask(Task):
    # @field_validator("output_file")
    @classmethod
    def output_file_validation(cls, value: str) -> str:
        """Use the provided output path directly"""
        return value