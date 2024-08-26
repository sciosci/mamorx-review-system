import math
import random
from collections import defaultdict
from database import get_all_comparisons


class EloSystem:
    """
    A class representing an Elo rating system for reviewers.
    See https://en.wikipedia.org/wiki/Elo_rating_system for more information.
    """

    def __init__(self, k_factor=32, initial_rating=1500, weights=None):
        """
        Initialize the EloSystem.

        :param k_factor: The maximum rating change per comparison (default: 32)
        :param initial_rating: The starting rating for new reviewers (default: 1500)
        :param weights: A dictionary of weights for each dimension (default: None)
        """
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.weights = weights or {
            "Technical Quality": 0.2,
            "Constructiveness": 0.2,
            "Clarity": 0.2,
            "Overall Quality": 0.6,
        }
        self.ratings = defaultdict(lambda: self.initial_rating)
        self.comparisons = []
        self.initialize_ratings()

    def initialize_ratings(self):
        """
        Initialize ratings based on stored comparisons.
        """
        self.comparisons = get_all_comparisons()
        self.compute_ratings()

    def compute_ratings(self):
        """
        Compute the Elo ratings for all reviewers based on the stored comparisons.
        """
        self.ratings = defaultdict(lambda: self.initial_rating)
        for comparison in self.comparisons:
            self.update_ratings(
                comparison["reviewer_a"],
                comparison["reviewer_b"],
                {
                    "Technical Quality": comparison["technical_quality"],
                    "Constructiveness": comparison["constructiveness"],
                    "Clarity": comparison["clarity"],
                    "Overall Quality": comparison["overall_quality"],
                },
            )

    def expected_score(self, rating_a, rating_b):
        """
        Calculate the expected score for a reviewer based on ratings.

        :param rating_a: The rating of the first reviewer
        :param rating_b: The rating of the second reviewer
        :return: The expected score for the first reviewer
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def update_ratings(self, reviewer_a, reviewer_b, comparisons):
        """
        Update the Elo ratings for two reviewers based on their comparisons.

        :param reviewer_a: The ID of the first reviewer
        :param reviewer_b: The ID of the second reviewer
        :param comparisons: A dictionary of comparison results for each dimension
        """
        total_score = 0
        for dimension, result in comparisons.items():
            if result == "👈 A is better":
                score = 1
            elif result == "👉 B is better":
                score = 0
            elif result == "🤝 Tie":
                score = 0.5
            else:  # " Both are bad"
                continue  # Skip this dimension if both are bad

            total_score += self.weights[dimension] * score

        total_weight = sum(self.weights.values())
        normalized_score = total_score / total_weight

        rating_a = self.ratings[reviewer_a]
        rating_b = self.ratings[reviewer_b]

        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a

        self.ratings[reviewer_a] += self.k_factor * (normalized_score - expected_a)
        self.ratings[reviewer_b] += self.k_factor * (
            (1 - normalized_score) - expected_b
        )

    def add_comparison(self, reviewer_a, reviewer_b, comparisons):
        """
        Add a new comparison to the system and update the Elo ratings.

        :param reviewer_a: The ID of the first reviewer
        :param reviewer_b: The ID of the second reviewer
        :param comparisons: A dictionary of comparison results for each dimension
        """
        self.comparisons.append(
            {
                "reviewer_a": reviewer_a,
                "reviewer_b": reviewer_b,
                "technical_quality": comparisons["Technical Quality"],
                "constructiveness": comparisons["Constructiveness"],
                "clarity": comparisons["Clarity"],
                "overall_quality": comparisons["Overall Quality"],
            }
        )
        self.update_ratings(reviewer_a, reviewer_b, comparisons)

    def get_fair_pair(self, reviewer_ids):
        """
        Select a fair pair of reviewers for comparison.

        :param reviewer_ids: A list of all reviewer IDs
        :return: A tuple of two reviewer IDs (reviewer_a, reviewer_b)
        """
        # Ensure all reviewer_ids are in the ratings
        for reviewer_id in reviewer_ids:
            if reviewer_id not in self.ratings:
                self.ratings[reviewer_id] = self.initial_rating

        sorted_reviewers = sorted(reviewer_ids, key=lambda x: self.ratings[x])
        mid = len(sorted_reviewers) // 2
        group1 = sorted_reviewers[:mid]
        group2 = sorted_reviewers[mid:]
        return random.choice(group1), random.choice(group2)

    def get_ratings(self):
        """
        Get the current ratings for all reviewers.

        :return: A dictionary of reviewer IDs and their corresponding ratings
        """
        return dict(self.ratings)
