import os
import sqlite3
import unittest
from datetime import datetime

from ai_reviewer_arena.sessions import Session, SessionRegistry


class TestSessionRegistry(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_sessions.db"
        self.registry = SessionRegistry(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_table(self):
        # Check if the table was created
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
            )
            self.assertIsNotNone(cursor.fetchone())

    def test_insert_session(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        session["key1"] = "value1"
        self.registry.insert_session(session)

        # Check if the session was inserted
        self.assertTrue(self.registry.session_exists("test_id"))

    def test_update_session(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        self.registry.insert_session(session)

        # Update the session
        session["key2"] = "value2"
        session.end_time = datetime.now()
        self.registry.update_session(session)

        # Load the session and check if it was updated
        updated_session = self.registry.load_session("test_id")
        self.assertIsNotNone(updated_session, "Session should exist")
        if updated_session:  # Type narrowing
            self.assertEqual(updated_session["key2"], "value2")
            self.assertIsNotNone(updated_session.end_time)
        else:
            self.fail("Session was not loaded successfully")

    def test_session_exists(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        self.registry.insert_session(session)

        self.assertTrue(self.registry.session_exists("test_id"))
        self.assertFalse(self.registry.session_exists("non_existent_id"))

    def test_load_session(self):
        original_session = Session("test_id", "127.0.0.1", "test_agent")
        original_session["key1"] = "value1"
        self.registry.insert_session(original_session)

        loaded_session = self.registry.load_session("test_id")
        self.assertIsNotNone(loaded_session, "Session should exist")
        if loaded_session:
            self.assertEqual(loaded_session.session_id, "test_id")
            self.assertEqual(loaded_session.ip_address, "127.0.0.1")
            self.assertEqual(loaded_session.user_agent, "test_agent")
            self.assertEqual(loaded_session["key1"], "value1")
        else:
            self.fail("Session was not loaded successfully")

    def test_load_non_existent_session(self):
        self.assertIsNone(self.registry.load_session("non_existent_id"))

    def test_multiple_sessions(self):
        session1 = Session("id1", "127.0.0.1", "agent1")
        session2 = Session("id2", "127.0.0.2", "agent2")
        self.registry.insert_session(session1)
        self.registry.insert_session(session2)

        self.assertTrue(self.registry.session_exists("id1"))
        self.assertTrue(self.registry.session_exists("id2"))

    def test_update_non_existent_session(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        # This should not raise an exception, but the session won't be in the database
        self.registry.update_session(session)
        self.assertFalse(self.registry.session_exists("test_id"))

    def test_insert_duplicate_session(self):
        session1 = Session("test_id", "127.0.0.1", "agent1")
        session2 = Session("test_id", "127.0.0.2", "agent2")
        self.registry.insert_session(session1)

        # This should raise an exception due to duplicate primary key
        with self.assertRaises(sqlite3.IntegrityError):
            self.registry.insert_session(session2)

    def test_session_with_complex_data(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        session["list"] = [1, 2, 3]
        session["dict"] = {"a": 1, "b": 2}
        session["set"] = {1, 2, 3}
        self.registry.insert_session(session)

        loaded_session = self.registry.load_session("test_id")
        self.assertIsNotNone(loaded_session, "Session should exist")
        if loaded_session:
            self.assertEqual(loaded_session["list"], [1, 2, 3])
            self.assertEqual(loaded_session["dict"], {"a": 1, "b": 2})
            self.assertEqual(loaded_session["set"], {1, 2, 3})
        else:
            self.fail("Session was not loaded successfully")

    def test_session_with_datetime(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        now = datetime.now()
        session["datetime"] = now
        self.registry.insert_session(session)

        loaded_session = self.registry.load_session("test_id")
        self.assertIsNotNone(loaded_session, "Session should exist")
        if loaded_session:
            self.assertEqual(loaded_session["datetime"], now)
        else:
            self.fail("Session was not loaded successfully")

    def test_large_data(self):
        session = Session("test_id", "127.0.0.1", "test_agent")
        large_data = "x" * 1000000  # 1MB of data
        session["large_data"] = large_data
        self.registry.insert_session(session)

        loaded_session = self.registry.load_session("test_id")
        self.assertIsNotNone(loaded_session, "Session should exist")
        if loaded_session:
            self.assertEqual(loaded_session["large_data"], large_data)
        else:
            self.fail("Session was not loaded successfully")


if __name__ == "__main__":
    unittest.main()
