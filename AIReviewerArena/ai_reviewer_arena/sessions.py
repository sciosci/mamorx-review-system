import json
import logging
import pickle
import sqlite3
from collections.abc import ValuesView as ABCValuesView
from datetime import datetime
from pathlib import Path
from typing import (Any, Dict, ItemsView, KeysView, Optional, Set, TypeVar,
                    Union, ValuesView)

from ai_reviewer_arena.configs.logging_cfg import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger("SessionRegistry")

PROJECT_HOME = Path(__file__).parent.parent
SESSION_DB_FOLDER = PROJECT_HOME / "arena_data/app_databases"
DEFAULT_DB_NAME = "sessions.db"

T = TypeVar("T")


class SessionValuesView(ABCValuesView):
    def __init__(self, session):
        self._session = session

    def __iter__(self):
        yield self._session._session_id
        yield self._session._start_time
        yield self._session._end_time
        yield self._session._ip_address
        yield self._session._user_agent
        yield from self._session._data.values()

    def __len__(self):
        return 5 + len(self._session._data)  # 5 special attributes + custom data


class Session:
    def __init__(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        if not session_id:
            logger.error("Attempted to create Session with empty session_id")
            raise ValueError("session_id is required")

        self._session_id: str = session_id
        self._start_time: datetime = datetime.now()
        self._end_time: Optional[datetime] = None
        self._ip_address: Optional[str] = ip_address
        self._user_agent: Optional[str] = user_agent
        self._data: Dict[str, Any] = {}
        logger.info(f"Created new Session with id: {session_id}")

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def end_time(self) -> Optional[datetime]:
        return self._end_time

    @end_time.setter
    def end_time(self, value: Optional[datetime]) -> None:
        self._end_time = value

    @property
    def ip_address(self) -> Optional[str]:
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value: Optional[str]) -> None:
        self._ip_address = value

    @property
    def user_agent(self) -> Optional[str]:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: Optional[str]) -> None:
        self._user_agent = value

    def __getitem__(self, key: str) -> Any:
        if key == "session_id":
            return self._session_id
        elif key == "start_time":
            return self._start_time
        elif key in ["end_time", "ip_address", "user_agent"]:
            return getattr(self, key)
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ["session_id", "start_time"]:
            logger.warning(f"Attempted to set immutable attribute: {key}")
            raise AttributeError(f"'{key}' is immutable")
        elif key in ["end_time", "ip_address", "user_agent"]:
            setattr(self, key, value)
            logger.debug(f"Set {key} to {value} for session {self._session_id}")
        else:
            if value is None:
                logger.warning(f"Attempted to set None value for key: {key}")
                raise ValueError("Cannot set None value in Session object")
            self._data[key] = value
            logger.debug(
                f"Set custom data {key}={value} for session {self._session_id}"
            )

    def __delitem__(self, key: str) -> None:
        if key in ["session_id", "start_time", "end_time", "ip_address", "user_agent"]:
            raise AttributeError(f"Cannot delete '{key}' from Session object")
        del self._data[key]

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return (
                item
                in ["session_id", "start_time", "end_time", "ip_address", "user_agent"]
                or item in self._data
            )
        return False

    def __iter__(self):
        yield from ["session_id", "start_time", "end_time", "ip_address", "user_agent"]
        yield from self._data

    def get(self, key: str, default: T | None = None) -> Union[Any, T]:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: str, default: T | None = None) -> Union[Any, T]:
        if key in ["session_id", "start_time", "end_time", "ip_address", "user_agent"]:
            raise AttributeError(f"Cannot pop '{key}' from Session object")
        return self._data.pop(key, default)

    def clear(self) -> None:
        self._data.clear()

    def update(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if key not in ["session_id", "start_time"]:
                self[key] = value

    def keys(self) -> KeysView[str]:
        combined_keys = {
            **self._data,
            "session_id": None,
            "start_time": None,
            "end_time": None,
            "ip_address": None,
            "user_agent": None,
        }
        return KeysView(combined_keys)

    def values(self) -> ValuesView[Any]:
        return SessionValuesView(self)

    def items(self) -> ItemsView[str, Any]:
        return ItemsView(
            dict(
                list(self._data.items())
                + [
                    ("session_id", self._session_id),
                    ("start_time", self._start_time),
                    ("end_time", self._end_time),
                    ("ip_address", self._ip_address),
                    ("user_agent", self._user_agent),
                ]
            )
        )

    def __repr__(self) -> str:
        return f"Session(session_id={self._session_id}, start_time={self._start_time}, end_time={self._end_time}, ip_address={self._ip_address}, user_agent={self._user_agent}, data={self._data})"

    def __str__(self) -> str:
        return self.to_json()

    def to_json(self, exclude_keys: Optional[Set[str]] = None) -> str:
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)

        output_dict = {
            "session_id": self._session_id,
            "start_time": self._start_time,
            "end_time": self._end_time,
            "ip_address": self._ip_address,
            "user_agent": self._user_agent,
            **self._data,
        }

        if exclude_keys:
            for key in exclude_keys:
                output_dict.pop(key, None)

        logger.debug(f"Serialized session {self._session_id} to JSON")
        return json.dumps(output_dict, default=default_serializer)

    @classmethod
    def from_json(cls, json_str: str) -> "Session":
        session_dict = json.loads(json_str)
        session = cls(
            session_id=session_dict["session_id"],
            ip_address=session_dict.get("ip_address"),
            user_agent=session_dict.get("user_agent"),
        )
        if "start_time" in session_dict:
            session._start_time = datetime.fromisoformat(session_dict["start_time"])
        if "end_time" in session_dict and session_dict["end_time"]:
            session.end_time = datetime.fromisoformat(session_dict["end_time"])

        for key, value in session_dict.items():
            if key not in [
                "session_id",
                "start_time",
                "end_time",
                "ip_address",
                "user_agent",
            ]:
                session._data[key] = value

        logger.info(f"Created Session from JSON with id: {session.session_id}")
        return session

    def to_sqlite(self):
        logger.debug(f"Converted session {self._session_id} to SQLite format")
        return {
            "session_id": self._session_id,
            "start_time": self._start_time.isoformat(),
            "end_time": self._end_time.isoformat() if self._end_time else None,
            "ip_address": self._ip_address,
            "user_agent": self._user_agent,
            "data": pickle.dumps(
                self._data
            ),  # This is already bytes, compatible with BLOB
        }

    @classmethod
    def from_sqlite(cls, data):
        session = cls(data["session_id"], data["ip_address"], data["user_agent"])
        session._start_time = datetime.fromisoformat(data["start_time"])
        if data["end_time"]:
            session._end_time = datetime.fromisoformat(data["end_time"])
        session._data = pickle.loads(data["data"])  # Unpickle the BLOB data
        logger.info(f"Created Session from SQLite data with id: {session._session_id}")
        return session


class SessionRegistry:
    def __init__(self, db_path: str | None = None):
        if not db_path:
            db_path = str((SESSION_DB_FOLDER / DEFAULT_DB_NAME).resolve())
        self.db_path = db_path
        self._create_table()
        logger.info(f"Initialized SessionRegistry with database: {db_path}")

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    start_time TEXT,
                    end_time TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    data BLOB
                )
            """
            )
            conn.commit()
        logger.debug("Created sessions table if not exists")

    def insert_session(self, session: Session):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            session_data = session.to_sqlite()
            cursor.execute(
                """
                INSERT INTO sessions
                (session_id, start_time, end_time, ip_address, user_agent, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    session_data["session_id"],
                    session_data["start_time"],
                    session_data["end_time"],
                    session_data["ip_address"],
                    session_data["user_agent"],
                    session_data["data"],  # This is already bytes, compatible with BLOB
                ),
            )
            conn.commit()
        logger.info(f"Inserted session {session.session_id} into database")

    def update_session(self, session: Session):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            session_data = session.to_sqlite()
            cursor.execute(
                """
                UPDATE sessions
                SET start_time = ?, end_time = ?, ip_address = ?, user_agent = ?, data = ?
                WHERE session_id = ?
            """,
                (
                    session_data["start_time"],
                    session_data["end_time"],
                    session_data["ip_address"],
                    session_data["user_agent"],
                    session_data["data"],  # This is already bytes, compatible with BLOB
                    session_data["session_id"],
                ),
            )
            conn.commit()
        logger.info(f"Updated session {session.session_id} in database")

    def session_exists(self, session_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sessions WHERE session_id = ?", (session_id,))
            exists = cursor.fetchone() is not None
        logger.debug(
            f"Checked existence of session {session_id}: {'exists' if exists else 'does not exist'}"
        )
        return exists

    # If you need a method to load a session, you can add it like this:
    def load_session(self, session_id: str) -> Optional[Session]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                logger.info(f"Loaded session {session_id} from database")
                return Session.from_sqlite(
                    {
                        "session_id": row[0],
                        "start_time": row[1],
                        "end_time": row[2],
                        "ip_address": row[3],
                        "user_agent": row[4],
                        "data": row[5],  # This is BLOB data, which is bytes
                    }
                )
        logger.warning(f"Attempted to load non-existent session: {session_id}")
        return None
