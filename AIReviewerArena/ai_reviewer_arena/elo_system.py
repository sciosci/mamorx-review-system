import logging
import math
import random
from collections import defaultdict
from typing import Annotated, ClassVar, Dict, List, Tuple

from pydantic import BaseModel, Field, model_validator

from ai_reviewer_arena.configs.app_cfg import ARENA_RATING_CHOICES
from ai_reviewer_arena.configs.logging_cfg import setup_logging
from ai_reviewer_arena.votes import Vote, VotesInterface

# Setup logging
setup_logging()
logger = logging.getLogger("EloSystem")


class ReviewEvalWeights(BaseModel):
    technical_quality: Annotated[float, Field(gt=0, lt=1)] = 0.2
    constructiveness: Annotated[float, Field(gt=0, lt=1)] = 0.2
    clarity: Annotated[float, Field(gt=0, lt=1)] = 0.2
    overall_quality: Annotated[float, Field(gt=0, lt=1)] = 0.4
    FIELDS: ClassVar[list] = [
        "technical_quality",
        "constructiveness",
        "clarity",
        "overall_quality",
    ]

    @model_validator(mode="after")
    def check_weights_sum_to_one(self):
        total = sum(getattr(self, field) for field in self.FIELDS)
        if abs(total - 1) > 1e-6:  # Allow for small floating-point errors
            raise ValueError(f"The sum of all weights must be 1, but it is {total}")
        return self


class EloSystem:
    """
    A class representing an Elo rating system for reviewers.
    See https://en.wikipedia.org/wiki/Elo_rating_system for more information.
    """

    def __init__(
        self,
        votes_db: VotesInterface,
        k_factor: float = 32,
        initial_rating: float = 1500.0,
        weights: ReviewEvalWeights | None = None,
    ):
        """
        Initialize the EloSystem.

        :param votes_db: The database interface for storing and retrieving votes
        :param k_factor: The maximum rating change per comparison (default: 32)
        :param initial_rating: The starting rating for new reviewers (default: 1500)
        :param weights: A ReviewEvalWeights object with weights for each dimension (default: None)
        """
        self.votes_db = votes_db
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.weights = weights or ReviewEvalWeights()
        self._ratings: Dict[str, float] = defaultdict(self._default_rating)
        self.votes: List[Vote] = []
        self.vote_counts: Dict[str, float] = defaultdict(float)
        self.initialize_ratings()
        logger.info(
            "EloSystem initialized with k_factor=%s, initial_rating=%s",
            k_factor,
            initial_rating,
        )

    def initialize_ratings(self):
        """
        Initialize ratings based on stored comparisons.
        """
        self.votes = self.votes_db.get_all_votes()
        self.compute_ratings()
        logger.info("Ratings initialized from stored votes")

    def compute_ratings(self):
        """
        Compute the Elo ratings for all reviewers based on the stored comparisons.
        """
        self._ratings = defaultdict(self._default_rating)
        for vote in self.votes:
            self.update_ratings(vote)
        logger.info("Ratings computed for all reviewers")

    def _default_rating(self):
        return self.initial_rating

    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate the expected score for a reviewer based on ratings.

        :param rating_a: The rating of the first reviewer
        :param rating_b: The rating of the second reviewer
        :return: The expected score for the first reviewer
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

    def update_ratings(self, vote: Vote):
        """
        Update the Elo ratings for two reviewers based on their comparison.

        :param vote: The Vote object containing comparison results
        """
        comparisons = {
            "technical_quality": vote.technical_quality,
            "constructiveness": vote.constructiveness,
            "clarity": vote.clarity,
            "overall_quality": vote.overall_quality,
        }

        total_score = 0
        for dimension, result in comparisons.items():
            if result == ARENA_RATING_CHOICES[0]:  # "👈  A is better"
                score = 1.0
            elif result == ARENA_RATING_CHOICES[1]:  # "👉  B is better"
                score = 0.0
            elif result == ARENA_RATING_CHOICES[2]:  # "🤝  Tie"
                score = 0.5
            else:  # "👎  Both are bad"
                # " Both are bad, it's essentially a Tie"
                score = 0.5

            total_score += getattr(self.weights, dimension) * score

        total_weight = sum(self.weights.model_dump().values())
        normalized_score = total_score / total_weight

        rating_a = self._ratings[vote.reviewer_a]
        rating_b = self._ratings[vote.reviewer_b]

        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1 - expected_a

        self._ratings[vote.reviewer_a] += self.k_factor * (
            normalized_score - expected_a
        )
        self._ratings[vote.reviewer_b] += self.k_factor * (
            (1 - normalized_score) - expected_b
        )

        # Update vote counts
        self.vote_counts[vote.reviewer_a] += normalized_score
        self.vote_counts[vote.reviewer_b] += 1 - normalized_score

        logger.debug(
            "Updated ratings: %s (new rating: %s), %s (new rating: %s)",
            vote.reviewer_a,
            self._ratings[vote.reviewer_a],
            vote.reviewer_b,
            self._ratings[vote.reviewer_b],
        )

    def add_vote(self, vote: Vote):
        """
        Add a new vote to the system.

        :param vote: The Vote object containing comparison results
        """
        self.votes.append(vote)
        logger.info("Added vote: %s vs %s", vote.reviewer_a, vote.reviewer_b)

    def add_vote_then_update_ratings(self, vote: Vote):
        """
        Add a new vote to the system and update the Elo ratings.

        :param vote: The Vote object containing comparison results
        """
        self.add_vote(vote)
        self.update_ratings(vote)
        logger.info(
            "Added vote and update ratings: %s vs %s", vote.reviewer_a, vote.reviewer_b
        )

    def get_fair_pair(
        self,
        fair_match_diff_step: float = 10.0,
        exclude_pairs: set[tuple[str, str]] = set(),
        candidates_a: set[str] | None = None,
        candidates_b: set[str] | None = None,
    ) -> tuple[str, str] | None:
        all_reviewers = set(self._ratings.keys())

        # Use all_reviewers only if candidates are None, not if they're empty sets
        candidates_a = candidates_a if candidates_a is not None else all_reviewers
        candidates_b = candidates_b if candidates_b is not None else all_reviewers

        if len(candidates_a) < 1 or len(candidates_b) < 1:
            return None

        # If all_reviewers is empty, randomly sample a pair from candidates_a and candidates_b
        if not all_reviewers:
            reviewer_a = random.choice(list(candidates_a))
            reviewer_b = random.choice(list(candidates_b - {reviewer_a}))
            logger.info("Selected fair pair: %s vs %s", reviewer_a, reviewer_b)
            return reviewer_a, reviewer_b

        max_rating = max(self._ratings.values())
        min_rating = min(self._ratings.values())

        max_attempts = 100  # Prevent infinite loop
        for _ in range(max_attempts):
            reviewer_a = random.choice(list(candidates_a))
            base_rating = self._ratings[reviewer_a]

            max_possible_diff = max(max_rating - base_rating, base_rating - min_rating)
            max_possible_diff = (
                math.ceil(max_possible_diff / fair_match_diff_step)
                * fair_match_diff_step
            )

            # Starting from 0, in case all the scores are the same
            current_diff = 0.0

            while current_diff <= max_possible_diff:
                eligible_reviewers = [
                    r
                    for r in candidates_b
                    if r != reviewer_a
                    and abs(self._ratings[r] - base_rating) <= current_diff
                    and (reviewer_a, r) not in exclude_pairs
                    and (r, reviewer_a) not in exclude_pairs
                ]

                if eligible_reviewers:
                    reviewer_b = random.choice(eligible_reviewers)
                    logger.info("Selected fair pair: %s vs %s", reviewer_a, reviewer_b)
                    return reviewer_a, reviewer_b

                current_diff += fair_match_diff_step

        logger.warning("No valid pair found after maximum attempts")
        return None  # No valid pair found after maximum attempts

    def get_ratings(self) -> Dict[str, float]:
        """
        Get the current ratings for all reviewers.

        :return: A dictionary of reviewer IDs and their corresponding ratings
        """
        return dict(self._ratings)

    def get_ratings_stats(self) -> Dict[str, Dict[str, float | Tuple[float, float]]]:
        """
        Get the current ratings, 95% confidence intervals, and number of votes for all reviewers.

        :return: A dictionary of reviewer IDs and their corresponding stats
        """
        stats: Dict[str, Dict[str, float | Tuple[float, float]]] = {}

        for reviewer_id, rating in self._ratings.items():
            vote_count = self.vote_counts[reviewer_id]
            ci: Tuple[float, float] = self._calculate_confidence_interval(
                rating, vote_count
            )
            stats[reviewer_id] = {
                "Arena Score": rating,
                "95% CI": ci,
                "Votes": vote_count,
            }

        return stats

    def _calculate_confidence_interval(
        self, rating: float, vote_count: float
    ) -> Tuple[float, float]:
        """
        Calculate the 95% confidence interval for a given rating and vote count.

        :param rating: The Elo rating
        :param vote_count: The cumulative vote count for the reviewer
        :return: A tuple of (lower_bound, upper_bound) for the 95% CI
        """
        if vote_count == 0:
            return (rating, rating)

        # Standard deviation of the rating
        std_dev = self.k_factor / math.sqrt(vote_count)

        # 95% CI is approximately 1.96 standard deviations from the mean
        margin = 1.96 * std_dev

        lower_bound = rating - margin
        upper_bound = rating + margin

        return (lower_bound, upper_bound)
