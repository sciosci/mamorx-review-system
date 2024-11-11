import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, field_serializer

from ai_reviewer_arena.configs.logging_cfg import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger("VotesStorage")

PROJECT_HOME = Path(__file__).parent.parent
VOTES_DB_FOLDER = PROJECT_HOME / "arena_data/app_databases"
DEFAULT_VOTES_SQLITE_NAME = "arena_votes.db"
DEFAULT_VOTES_JSONL_NAME = "arena_votes.jsonl"


class Vote(BaseModel):
    session_id: str
    paper_id: str  # New field added
    reviewer_a: str
    reviewer_b: str
    technical_quality: str
    constructiveness: str
    clarity: str
    overall_quality: str
    review_a: str  # New field added
    review_b: str  # New field added
    vote_time: datetime = Field(default_factory=datetime.now)

    @field_serializer("vote_time")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class VotesInterface(ABC):
    @abstractmethod
    def _init_storage(self):
        pass

    @abstractmethod
    def store_vote(self, vote: Vote):
        pass

    @abstractmethod
    def get_all_votes(self) -> List[Vote]:
        pass


class VotesSqlite(VotesInterface):
    def __init__(self, database_path: str | None = None):
        if not database_path:
            database_path = str((VOTES_DB_FOLDER / DEFAULT_VOTES_SQLITE_NAME).resolve())
        self.database_path = database_path
        logger.info(f"Initializing VotesSqlite with database: {database_path}")
        self._init_storage()

    @contextmanager
    def get_db_connection(self):
        conn = sqlite3.connect(self.database_path, detect_types=sqlite3.PARSE_DECLTYPES)
        try:
            yield conn
        finally:
            conn.close()

    def _init_storage(self):
        logger.debug("Initializing SQLite storage")
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    paper_id TEXT,  -- New field added
                    reviewer_a TEXT,
                    reviewer_b TEXT,
                    technical_quality TEXT,
                    constructiveness TEXT,
                    clarity TEXT,
                    overall_quality TEXT,
                    review_a TEXT,  -- New field added
                    review_b TEXT,  -- New field added
                    vote_time TEXT
                )
            """
            )
            conn.commit()
        logger.info("SQLite storage initialized successfully")

    def store_vote(self, vote: Vote):
        logger.debug(f"Storing vote in SQLite: {vote.session_id}")
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO comparisons (session_id, paper_id, reviewer_a, reviewer_b,
                                         technical_quality, constructiveness, clarity, overall_quality, review_a, review_b, vote_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    vote.session_id,
                    vote.paper_id,  # New field added
                    vote.reviewer_a,
                    vote.reviewer_b,
                    vote.technical_quality,
                    vote.constructiveness,
                    vote.clarity,
                    vote.overall_quality,
                    vote.review_a,  # New field added
                    vote.review_b,  # New field added
                    vote.vote_time,
                ),
            )
            conn.commit()
        logger.info(f"Vote stored in SQLite successfully: {vote.session_id}")

    def get_all_votes(self) -> List[Vote]:
        logger.debug("Retrieving all votes from SQLite")
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id, paper_id, reviewer_a, reviewer_b, technical_quality, constructiveness, clarity, overall_quality, review_a, review_b, vote_time
                FROM comparisons
                ORDER BY id
            """
            )
            votes = [
                Vote(**dict(zip([column[0] for column in cursor.description], row)))
                for row in cursor.fetchall()
            ]
        logger.info(f"Retrieved {len(votes)} votes from SQLite")
        return votes


class VotesJSONL(VotesInterface):
    def __init__(self, file_path: str | None = None):
        if not file_path:
            file_path = str((VOTES_DB_FOLDER / DEFAULT_VOTES_JSONL_NAME).resolve())
        self.file_path = file_path
        logger.info(f"Initializing VotesJSONL with file: {file_path}")
        self._init_storage()

    def _init_storage(self):
        logger.debug(f"Initializing JSONL storage: {self.file_path}")
        if not os.path.exists(self.file_path):
            open(self.file_path, "a").close()
            logger.info(f"Created new JSONL file: {self.file_path}")
        else:
            logger.info(f"Using existing JSONL file: {self.file_path}")

    def store_vote(self, vote: Vote):
        logger.debug(f"Storing vote in JSONL: {vote.session_id}")
        with open(self.file_path, "a") as f:
            f.write(vote.model_dump_json() + "\n")
        logger.info(f"Vote stored successfully in JSONL: {vote.session_id}")

    def get_all_votes(self) -> List[Vote]:
        logger.debug(f"Retrieving all votes from JSONL: {self.file_path}")
        votes = []
        with open(self.file_path, "r") as f:
            for line in f:
                votes.append(Vote.model_validate_json(line.strip()))
        logger.info(f"Retrieved {len(votes)} votes from JSONL")
        return votes
