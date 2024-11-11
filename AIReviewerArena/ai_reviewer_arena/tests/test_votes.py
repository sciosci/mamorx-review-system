import os
import unittest

from ai_reviewer_arena.votes import Vote, VotesJSONL, VotesSqlite


class TestVotesSqlite(unittest.TestCase):
    def setUp(self):
        self.test_db_name = "test_votes_sqlite.db"
        self.votes_storage = VotesSqlite(self.test_db_name)

    def tearDown(self):
        if os.path.exists(self.test_db_name):
            os.remove(self.test_db_name)

    def test_init_storage(self):
        # Check if the table is created
        with self.votes_storage.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='comparisons'"
            )
            result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "comparisons")

    def test_store_and_retrieve_comparison(self):
        test_vote = Vote(
            session_id="session123",
            paper_id="paper123",
            reviewer_a="reviewer1",
            reviewer_b="reviewer2",
            technical_quality="A",
            constructiveness="B",
            clarity="A",
            overall_quality="B",
            review_a="This is review A",
            review_b="This is review B",
        )
        self.votes_storage.store_vote(test_vote)

        # Retrieve and verify the stored data
        comparisons = self.votes_storage.get_all_votes()
        self.assertEqual(len(comparisons), 1)
        stored_vote = comparisons[0]
        self.assertEqual(stored_vote, test_vote)

    def test_get_all_votes(self):
        # Store multiple comparisons
        test_votes = [
            Vote(
                session_id=f"session{i}",
                paper_id=f"paper{i}",
                reviewer_a=f"reviewer{i}a",
                reviewer_b=f"reviewer{i}b",
                technical_quality="A",
                constructiveness="B",
                clarity="A",
                overall_quality="B",
                review_a=f"This is review {i}A",
                review_b=f"This is review {i}B",
            )
            for i in range(3)
        ]
        for vote in test_votes:
            self.votes_storage.store_vote(vote)

        # Retrieve and verify all stored data
        comparisons = self.votes_storage.get_all_votes()
        self.assertEqual(len(comparisons), 3)
        for stored_vote, test_vote in zip(comparisons, test_votes):
            self.assertEqual(stored_vote, test_vote)


class TestVotesJSONL(unittest.TestCase):
    def setUp(self):
        self.test_file_name = "test_votes_jsonl.jsonl"
        self.votes_storage = VotesJSONL(self.test_file_name)

    def tearDown(self):
        if os.path.exists(self.test_file_name):
            os.remove(self.test_file_name)

    def test_init_storage(self):
        # Check if the file is created
        self.assertTrue(os.path.exists(self.test_file_name))

    def test_store_and_retrieve_comparison(self):
        test_vote = Vote(
            session_id="session123",
            paper_id="paper123",
            reviewer_a="reviewer1",
            reviewer_b="reviewer2",
            technical_quality="A",
            constructiveness="B",
            clarity="A",
            overall_quality="B",
            review_a="This is review A",
            review_b="This is review B",
        )
        self.votes_storage.store_vote(test_vote)

        # Retrieve and verify the stored data
        comparisons = self.votes_storage.get_all_votes()
        self.assertEqual(len(comparisons), 1)
        stored_vote = comparisons[0]
        self.assertEqual(stored_vote, test_vote)

    def test_get_all_votes(self):
        # Store multiple comparisons
        test_votes = [
            Vote(
                session_id=f"session{i}",
                paper_id=f"paper{i}",
                reviewer_a=f"reviewer{i}a",
                reviewer_b=f"reviewer{i}b",
                technical_quality="A",
                constructiveness="B",
                clarity="A",
                overall_quality="B",
                review_a=f"This is review {i}A",
                review_b=f"This is review {i}B",
            )
            for i in range(3)
        ]
        for vote in test_votes:
            self.votes_storage.store_vote(vote)

        # Retrieve and verify all stored data
        comparisons = self.votes_storage.get_all_votes()
        self.assertEqual(len(comparisons), 3)
        for stored_vote, test_vote in zip(comparisons, test_votes):
            self.assertEqual(stored_vote, test_vote)


if __name__ == "__main__":
    unittest.main()
