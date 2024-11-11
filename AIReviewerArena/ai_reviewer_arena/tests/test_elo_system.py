import os
import unittest
from datetime import datetime
from typing import Tuple

from ai_reviewer_arena.elo_system import EloSystem, ReviewEvalWeights
from ai_reviewer_arena.votes import Vote, VotesSqlite


class TestEloSystem(unittest.TestCase):
    def setUp(self):
        # self.test_file = "test_votes.jsonl"
        # self.votes_db = VotesJSONL(self.test_file)

        self.test_file = "test_votes.db"
        self.votes_db = VotesSqlite(self.test_file)

        self.elo_system = EloSystem(self.votes_db)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_initialization(self):
        self.assertEqual(self.elo_system.k_factor, 32)
        self.assertEqual(self.elo_system.initial_rating, 1500)
        self.assertIsInstance(self.elo_system.weights, ReviewEvalWeights)

    def test_expected_score(self):
        self.assertAlmostEqual(self.elo_system.expected_score(1500, 1500), 0.5)
        self.assertAlmostEqual(
            self.elo_system.expected_score(1600.5, 1400.5), 0.76, places=2
        )
        self.assertAlmostEqual(
            self.elo_system.expected_score(1400.5, 1600.5), 0.24, places=2
        )

    def test_update_ratings_win(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",  # New required field
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👈  A is better",
            clarity="👈  A is better",
            overall_quality="👈  A is better",
            review_a="Review A content",  # New required field
            review_b="Review B content",  # New required field
            vote_time=datetime.now(),
        )
        # New assertions for the added fields
        self.assertEqual(vote.paper_id, "paper1")
        self.assertEqual(vote.review_a, "Review A content")
        self.assertEqual(vote.review_b, "Review B content")
        self.elo_system.update_ratings(vote)
        self.assertGreater(self.elo_system._ratings["A"], 1500)
        self.assertLess(self.elo_system._ratings["B"], 1500)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_update_ratings_loss(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👉  B is better",
            constructiveness="👉  B is better",
            clarity="👉  B is better",
            overall_quality="👉  B is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        # New assertions for the added fields
        self.assertEqual(vote.paper_id, "paper1")
        self.assertEqual(vote.review_a, "Review A content")
        self.assertEqual(vote.review_b, "Review B content")

        self.elo_system.update_ratings(vote)
        self.assertLess(self.elo_system._ratings["A"], 1500)
        self.assertGreater(self.elo_system._ratings["B"], 1500)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_update_ratings_tie(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="🤝  Tie",
            constructiveness="🤝  Tie",
            clarity="🤝  Tie",
            overall_quality="🤝  Tie",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        self.elo_system.update_ratings(vote)
        self.assertAlmostEqual(self.elo_system._ratings["A"], 1500, places=2)
        self.assertAlmostEqual(self.elo_system._ratings["B"], 1500, places=2)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_update_ratings_both_bad(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👎  Both are bad",
            constructiveness="👎  Both are bad",
            clarity="👎  Both are bad",
            overall_quality="👎  Both are bad",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        self.elo_system.update_ratings(vote)
        self.assertAlmostEqual(self.elo_system._ratings["A"], 1500, places=2)
        self.assertAlmostEqual(self.elo_system._ratings["B"], 1500, places=2)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_update_ratings_mixed(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👉  B is better",
            clarity="🤝  Tie",
            overall_quality="👎  Both are bad",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        initial_rating_a = self.elo_system._ratings["A"]
        initial_rating_b = self.elo_system._ratings["B"]
        self.elo_system.update_ratings(vote)
        self.assertEqual(self.elo_system._ratings["A"], initial_rating_a)
        self.assertEqual(self.elo_system._ratings["B"], initial_rating_b)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_add_vote_then_update_ratings(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👈  A is better",
            clarity="👈  A is better",
            overall_quality="👈  A is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        # New assertions for the added fields
        self.assertEqual(vote.paper_id, "paper1")
        self.assertEqual(vote.review_a, "Review A content")
        self.assertEqual(vote.review_b, "Review B content")

        self.elo_system.add_vote_then_update_ratings(vote)
        self.assertEqual(len(self.elo_system.votes), 1)
        self.assertGreater(self.elo_system._ratings["A"], 1500)
        self.assertLess(self.elo_system._ratings["B"], 1500)
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_get_fair_pair_default_diff(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1550.25,
            "C": 1500.0,
            "D": 1450.75,
            "E": 1400.5,
        }
        pair = self.elo_system.get_fair_pair()
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], self.elo_system._ratings.keys())  # type: ignore
        self.assertIn(pair[1], self.elo_system._ratings.keys())  # type: ignore
        self.assertLessEqual(abs(self.elo_system._ratings[pair[0]] - self.elo_system._ratings[pair[1]]), 200.0)  # type: ignore

    def test_get_fair_pair_custom_diff(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1550.25,
            "C": 1500.0,
            "D": 1450.75,
            "E": 1400.5,
        }
        pair = self.elo_system.get_fair_pair(fair_match_diff_step=100.0)
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], self.elo_system._ratings.keys())  # type: ignore
        self.assertIn(pair[1], self.elo_system._ratings.keys())  # type: ignore
        self.assertLessEqual(abs(self.elo_system._ratings[pair[0]] - self.elo_system._ratings[pair[1]]), 200.0)  # type: ignore

    def test_get_fair_pair_exclude_pairs(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1550.25,
            "C": 1500.0,
            "D": 1450.75,
            "E": 1400.5,
        }
        exclude_pairs = {("A", "B"), ("B", "C"), ("C", "D")}
        pair = self.elo_system.get_fair_pair(exclude_pairs=exclude_pairs)
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], self.elo_system._ratings.keys())  # type: ignore
        self.assertIn(pair[1], self.elo_system._ratings.keys())  # type: ignore
        self.assertNotIn(pair, exclude_pairs)
        self.assertNotIn((pair[1], pair[0]), exclude_pairs)  # type: ignore

    def test_get_fair_pair_candidates(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1550.25,
            "C": 1500.0,
            "D": 1450.75,
            "E": 1400.5,
        }
        candidates_a = {"A", "B", "C"}
        candidates_b = {"C", "D", "E"}
        pair = self.elo_system.get_fair_pair(
            candidates_a=candidates_a, candidates_b=candidates_b
        )
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], candidates_a)  # type: ignore
        self.assertIn(pair[1], candidates_b)  # type: ignore

    def test_get_fair_pair_no_valid_pair(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1550.25,
        }
        exclude_pairs = {("A", "B"), ("B", "A")}
        pair = self.elo_system.get_fair_pair(exclude_pairs=exclude_pairs)
        self.assertIsNone(pair)

    def test_get_fair_pair_increasing_diff(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1500.0,
            "C": 1400.5,
        }
        pair = self.elo_system.get_fair_pair(fair_match_diff_step=10.0)
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], self.elo_system._ratings.keys())  # type: ignore
        self.assertIn(pair[1], self.elo_system._ratings.keys())  # type: ignore
        self.assertLessEqual(abs(self.elo_system._ratings[pair[0]] - self.elo_system._ratings[pair[1]]), 200.0)  # type: ignore

    def test_get_fair_pair_edge_case(self):
        self.elo_system._ratings = {
            "A": 1600.5,
            "B": 1000.0,
        }
        pair = self.elo_system.get_fair_pair()
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertEqual(set(pair), set(["A", "B"]))  # type: ignore

    def test_get_fair_pair_not_enough_reviewers(self):
        self.elo_system._ratings = {"A": 1500.0}
        pair = self.elo_system.get_fair_pair()
        self.assertIsNone(pair)

    def test_get_fair_pair_all_same_rating(self):
        self.elo_system._ratings = {"A": 1500, "B": 1500, "C": 1500, "D": 1500}
        pair = self.elo_system.get_fair_pair()
        self.assertIsNotNone(pair)
        self.assertIsInstance(pair, tuple)
        self.assertEqual(len(pair), 2)  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore
        self.assertIn(pair[0], self.elo_system._ratings.keys())  # type: ignore
        self.assertIn(pair[1], self.elo_system._ratings.keys())  # type: ignore

    def test_get_fair_pair_no_candidates(self):
        self.elo_system._ratings = {"A": 1500, "B": 1600, "C": 1400}
        # Test when candidates_a is empty
        pair = self.elo_system.get_fair_pair(
            candidates_a=set(), candidates_b={"B", "C"}
        )
        self.assertIsNone(pair)

        # Test when candidates_b is empty
        pair = self.elo_system.get_fair_pair(candidates_a={"A"}, candidates_b=set())
        self.assertIsNone(pair)

        # Test when both candidate sets are provided
        pair = self.elo_system.get_fair_pair(
            candidates_a={"A"}, candidates_b={"B", "C"}
        )
        if pair is not None:
            self.assertEqual(pair[0], "A")
            self.assertIn(pair[1], ["B", "C"])
        else:
            # If no pair is returned, it might be because the rating difference is too large
            self.assertTrue(
                abs(self.elo_system._ratings["A"] - self.elo_system._ratings["B"]) > 200
                and abs(self.elo_system._ratings["A"] - self.elo_system._ratings["C"])
                > 200
            )

        # Test when candidates_a and candidates_b are not provided (should use all reviewers)
        pair = self.elo_system.get_fair_pair()
        self.assertIsNotNone(pair)
        self.assertIn(pair[0], ["A", "B", "C"])  # type: ignore
        self.assertIn(pair[1], ["A", "B", "C"])  # type: ignore
        self.assertNotEqual(pair[0], pair[1])  # type: ignore

    # Add a new test to check if the method respects the fair_match_diff parameter
    def test_get_fair_pair_respects_fair_match_diff(self):
        self.elo_system._ratings = {"A": 1500, "B": 1550, "C": 1600, "D": 1650}
        pair = self.elo_system.get_fair_pair(fair_match_diff_step=60)
        if pair is not None:
            self.assertLessEqual(
                abs(
                    self.elo_system._ratings[pair[0]]
                    - self.elo_system._ratings[pair[1]]
                ),
                60,
            )

    def test_get_ratings(self):
        self.elo_system._ratings = {"A": 1600.5, "B": 1550.25, "C": 1500.0}
        ratings = self.elo_system.get_ratings()
        self.assertEqual(ratings, {"A": 1600.5, "B": 1550.25, "C": 1500.0})
        for rating in ratings.values():
            self.assertIsInstance(rating, float)

    def test_initialize_ratings(self):
        vote1 = Vote(
            session_id="test1",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👈  A is better",
            clarity="👈  A is better",
            overall_quality="👈  A is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        vote2 = Vote(
            session_id="test2",
            paper_id="paper2",
            reviewer_a="B",
            reviewer_b="C",
            technical_quality="👉  B is better",
            constructiveness="👉  B is better",
            clarity="👉  B is better",
            overall_quality="👉  B is better",
            review_a="Review B content",
            review_b="Review C content",
            vote_time=datetime.now(),
        )
        # New assertions for the added fields
        self.assertEqual(vote1.paper_id, "paper1")
        self.assertEqual(vote1.review_a, "Review A content")
        self.assertEqual(vote1.review_b, "Review B content")
        self.assertEqual(vote2.paper_id, "paper2")
        self.assertEqual(vote2.review_a, "Review B content")
        self.assertEqual(vote2.review_b, "Review C content")

        self.elo_system.add_vote_then_update_ratings(vote1)
        self.elo_system.add_vote_then_update_ratings(vote2)

        self.assertEqual(len(self.elo_system.votes), 2)
        self.assertEqual(len(self.elo_system._ratings), 3)
        self.assertGreater(self.elo_system._ratings["A"], self.elo_system._ratings["B"])
        self.assertGreater(self.elo_system._ratings["C"], self.elo_system._ratings["B"])
        self.assertGreater(self.elo_system._ratings["A"], self.elo_system._ratings["C"])

        self.assertEqual(
            sum(self.elo_system.get_ratings().values()),
            self.elo_system.initial_rating * 3,
        )

        for rating in self.elo_system._ratings.values():
            self.assertIsInstance(rating, float)

    def test_custom_weights(self):
        custom_weights = ReviewEvalWeights(
            technical_quality=0.4,
            constructiveness=0.3,
            clarity=0.2,
            overall_quality=0.1,
        )
        elo_system = EloSystem(self.votes_db, weights=custom_weights)
        vote = Vote(
            session_id="test",
            paper_id="paper3",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👉  B is better",
            clarity="👉  B is better",
            overall_quality="👉  B is better",
            review_a="Review A content for paper 3",
            review_b="Review B content for paper 3",
            vote_time=datetime.now(),
        )
        # New assertions for the added fields
        self.assertEqual(vote.paper_id, "paper3")
        self.assertEqual(vote.review_a, "Review A content for paper 3")
        self.assertEqual(vote.review_b, "Review B content for paper 3")

        initial_rating_a = elo_system._ratings["A"]
        initial_rating_b = elo_system._ratings["B"]
        elo_system.update_ratings(vote)
        self.assertNotEqual(elo_system._ratings["A"], initial_rating_a)
        self.assertNotEqual(elo_system._ratings["B"], initial_rating_b)
        self.assertIsInstance(elo_system._ratings["A"], float)
        self.assertIsInstance(elo_system._ratings["B"], float)

    def test_edge_case_very_high_rating_difference(self):
        self.elo_system._ratings["A"] = 2400.75
        self.elo_system._ratings["B"] = 1600.25
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👉  B is better",
            constructiveness="👉  B is better",
            clarity="👉  B is better",
            overall_quality="👉  B is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        self.elo_system.update_ratings(vote)
        self.assertLess(self.elo_system._ratings["A"], 2400.75)
        self.assertGreater(self.elo_system._ratings["B"], 1600.25)
        self.assertGreater(self.elo_system._ratings["A"], self.elo_system._ratings["B"])
        self.assertIsInstance(self.elo_system._ratings["A"], float)
        self.assertIsInstance(self.elo_system._ratings["B"], float)

    def test_invalid_weights(self):
        with self.assertRaises(ValueError):
            ReviewEvalWeights(
                technical_quality=0.3,
                constructiveness=0.3,
                clarity=0.3,
                overall_quality=0.3,
            )

    def test_update_ratings_extreme_case(self):
        self.elo_system._ratings["A"] = 100
        self.elo_system._ratings["B"] = 3000
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="A",
            reviewer_b="B",
            technical_quality="👈  A is better",
            constructiveness="👈  A is better",
            clarity="👈  A is better",
            overall_quality="👈  A is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )
        self.elo_system.update_ratings(vote)
        self.assertGreater(self.elo_system._ratings["A"], 100)
        self.assertLess(self.elo_system._ratings["B"], 3000)
        self.assertLess(self.elo_system._ratings["A"], self.elo_system._ratings["B"])

    def test_compute_ratings_multiple_votes(self):
        votes = [
            Vote(
                session_id="1",
                paper_id="paper1",
                reviewer_a="A",
                reviewer_b="B",
                technical_quality="👈  A is better",
                constructiveness="👈  A is better",
                clarity="👈  A is better",
                overall_quality="👈  A is better",
                review_a="Review A content",
                review_b="Review B content",
                vote_time=datetime.now(),
            ),
            Vote(
                session_id="2",
                paper_id="paper2",
                reviewer_a="B",
                reviewer_b="C",
                technical_quality="👉  B is better",
                constructiveness="👉  B is better",
                clarity="👉  B is better",
                overall_quality="👉  B is better",
                review_a="Review A content",
                review_b="Review B content",
                vote_time=datetime.now(),
            ),
            Vote(
                session_id="3",
                paper_id="paper3",
                reviewer_a="C",
                reviewer_b="A",
                technical_quality="🤝  Tie",
                constructiveness="🤝  Tie",
                clarity="🤝  Tie",
                overall_quality="🤝  Tie",
                review_a="Review A content",
                review_b="Review B content",
                vote_time=datetime.now(),
            ),
        ]
        self.elo_system.votes = votes
        self.elo_system.compute_ratings()
        self.assertGreater(self.elo_system._ratings["A"], self.elo_system._ratings["C"])
        self.assertGreater(self.elo_system._ratings["C"], self.elo_system._ratings["B"])
        self.assertNotEqual(
            self.elo_system._ratings["A"], self.elo_system.initial_rating
        )
        self.assertNotEqual(
            self.elo_system._ratings["B"], self.elo_system.initial_rating
        )
        self.assertNotEqual(
            self.elo_system._ratings["C"], self.elo_system.initial_rating
        )

    def test_get_ratings_stats_with_reviewers(self):
        # Simulate some ratings and votes
        self.elo_system._ratings = {"reviewer1": 1550.0, "reviewer2": 1450.0}
        self.elo_system.vote_counts = {"reviewer1": 10.0, "reviewer2": 5.0}

        stats = self.elo_system.get_ratings_stats()

        self.assertIn("reviewer1", stats)
        self.assertIn("reviewer2", stats)

        for reviewer in ["reviewer1", "reviewer2"]:
            self.assertIn("Arena Score", stats[reviewer])
            self.assertIn("95% CI", stats[reviewer])
            self.assertIn("Votes", stats[reviewer])

            self.assertIsInstance(stats[reviewer]["Arena Score"], float)
            ci: Tuple[float, float] = stats[reviewer]["95% CI"]  # type: ignore
            self.assertIsInstance(ci, tuple)
            self.assertIsInstance(ci[0], float)
            self.assertIsInstance(ci[1], float)
            self.assertEqual(len(ci), 2)
            self.assertIsInstance(stats[reviewer]["Votes"], float)

    def test_calculate_confidence_interval(self):
        # Test with no votes
        ci = self.elo_system._calculate_confidence_interval(1500, 0)
        self.assertEqual(ci, (1500, 1500))

        # Test with some votes
        ci = self.elo_system._calculate_confidence_interval(1500, 10)
        self.assertLess(ci[0], 1500)
        self.assertGreater(ci[1], 1500)

    def test_update_ratings_updates_vote_counts(self):
        vote = Vote(
            session_id="test",
            paper_id="paper1",
            reviewer_a="reviewer1",
            reviewer_b="reviewer2",
            technical_quality="👈  A is better",
            constructiveness="👉  B is better",
            clarity="🤝  Tie",
            overall_quality="👈  A is better",
            review_a="Review A content",
            review_b="Review B content",
            vote_time=datetime.now(),
        )

        self.elo_system.update_ratings(vote)

        self.assertGreater(self.elo_system.vote_counts["reviewer1"], 0)
        self.assertGreater(self.elo_system.vote_counts["reviewer2"], 0)
        self.assertAlmostEqual(
            self.elo_system.vote_counts["reviewer1"]
            + self.elo_system.vote_counts["reviewer2"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
