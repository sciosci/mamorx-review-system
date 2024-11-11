import json
import logging
import random
from pathlib import Path
from typing import ClassVar, List

from pydantic import BaseModel

from ai_reviewer_arena.configs.logging_cfg import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger("PaperRegistry")

PROJECT_HOME = Path(__file__).parent.parent
DEFAULT_PAPER_PATH = PROJECT_HOME / "arena_data/resources/papers/paper_reviews.jsonl"


class Paper(BaseModel):
    paper_id: str
    title: str
    pdf_path: str
    human_reviewer: List[str]
    barebones: List[str]
    liang_etal: List[str]
    multi_agent_without_knowledge: List[str]

    # Class attribute listing all reviewer fields
    REVIEWER_FIELDS: ClassVar[List[str]] = [
        "human_reviewer",
        "barebones",
        "liang_etal",
        "multi_agent_without_knowledge",
    ]

    def get_all_valid_reviewer_ids(self) -> List[str]:
        """
        Returns a list of all valid reviewer IDs.
        A reviewer ID is considered valid if its corresponding field is a non-empty list
        and contains at least one non-empty string.
        Uses the REVIEWER_FIELDS class attribute to determine reviewer fields.
        """
        valid_reviewer_ids = []

        for field in self.REVIEWER_FIELDS:
            value = getattr(self, field)
            if isinstance(value, list) and len(value) > 0:
                # Check if there's at least one non-empty string in the list
                if any(len(str(item).strip()) > 0 for item in value):
                    valid_reviewer_ids.append(field)

        logger.debug(
            f"Valid reviewer IDs for paper {self.paper_id}: {valid_reviewer_ids}"
        )
        return valid_reviewer_ids


class PaperRegistry:
    def __init__(self):
        self._paper_list: List[Paper] = []
        logger.info("Initialized PaperRegistry")

    @classmethod
    def from_jsonl(cls, file_path: str) -> "PaperRegistry":
        """
        Imports papers from a JSONL file and converts each item into a Paper object.

        Args:
        - file_path: The path to the JSONL file.

        Returns:
        - An instance of PaperRegistry containing the list of Paper objects.
        """
        registry = cls()
        with open(file_path, "r") as file:
            for line in file:
                paper_data = json.loads(line.strip())
                paper = Paper(**paper_data)
                registry._paper_list.append(paper)
                logger.debug(f"Added paper {paper.paper_id} to registry")
        logger.info(f"Loaded {len(registry._paper_list)} papers from {file_path}")
        return registry

    def get_paper_list(self) -> List[Paper]:
        """
        Returns the list of Paper objects.

        Returns:
        - A list of Paper objects.
        """
        logger.debug("Returning paper list")
        return self._paper_list

    def get_paper_count(self) -> int:
        """
        Returns the number of papers in the PaperRegistry.

        Returns:
        - An integer representing the number of papers.
        """
        count = len(self._paper_list)
        logger.debug(f"Paper count: {count}")
        return count

    def sample_paper_position(self) -> int:
        """
        Randomly samples a paper from the PaperRegistry and returns its position.

        Returns:
        - An integer representing the position of the sampled paper.
        """
        if not self._paper_list:
            logger.error("Paper list is empty.")
            raise ValueError("Paper list is empty.")
        pos = random.randint(0, len(self._paper_list) - 1)
        logger.debug(f"Sampled paper position: {pos}")
        return pos

    def get_next_position(self, cur_pos: int) -> int:
        """
        Returns the next position in the PaperRegistry based on the current position.

        Args:
        - cur_pos: The current position.

        Returns:
        - The next position, or the first position if cur_pos is the last.
        """
        if not self._paper_list:
            logger.error("Paper list is empty.")
            raise ValueError("Paper list is empty.")
        next_pos = (cur_pos + 1) if cur_pos + 1 < len(self._paper_list) else 0
        logger.debug(f"Next position from {cur_pos}: {next_pos}")
        return next_pos

    def get_previous_position(self, cur_pos: int) -> int:
        """
        Returns the previous position in the PaperRegistry based on the current position.

        Args:
        - cur_pos: The current position.

        Returns:
        - The previous position, or the last position if cur_pos is the first.
        """
        if not self._paper_list:
            logger.error("Paper list is empty.")
            raise ValueError("Paper list is empty.")
        prev_pos = (cur_pos - 1) if cur_pos > 0 else len(self._paper_list) - 1
        logger.debug(f"Previous position from {cur_pos}: {prev_pos}")
        return prev_pos

    def get_paper_at_position(self, pos: int) -> Paper:
        """
        Returns the Paper object at the specified position.

        Args:
        - pos: The position of the Paper in the list.

        Returns:
        - The Paper object at the specified position.
        """
        if not self._paper_list:
            logger.error("Paper list is empty.")
            raise ValueError("Paper list is empty.")
        if pos < 0 or pos >= len(self._paper_list):
            logger.error(f"Position {pos} out of bounds.")
            raise IndexError("Position out of bounds.")
        logger.debug(f"Returning paper at position {pos}")
        return self._paper_list[pos]


paper_registry = PaperRegistry.from_jsonl(str(DEFAULT_PAPER_PATH))
logger.info(f"Paper registry loaded from default path: {str(DEFAULT_PAPER_PATH)}")
