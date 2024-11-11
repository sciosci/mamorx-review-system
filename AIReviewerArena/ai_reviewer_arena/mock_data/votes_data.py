import random
import string
from collections import defaultdict

from ai_reviewer_arena.configs.app_cfg import ARENA_RATING_CHOICES
from ai_reviewer_arena.papers import Paper
from ai_reviewer_arena.utils import generate_short_uuid
from ai_reviewer_arena.votes import Vote, VotesJSONL, VotesSqlite


def generate_random_text(length=100):
    letters = string.ascii_letters + string.digits + string.punctuation + " "
    return "".join(random.choice(letters) for _ in range(length))


def generate_mock_votes(num_votes=100):
    reviewers = Paper.REVIEWER_FIELDS

    # Probability weights for A and B
    weights = [0.25, 0.25, 0.25, 0.25]

    votes = []
    for _ in range(num_votes):
        reviewer_a, reviewer_b = random.sample(reviewers, 2)
        vote = Vote(
            session_id=generate_short_uuid(),
            paper_id=generate_short_uuid(),  # New field added
            reviewer_a=reviewer_a,
            reviewer_b=reviewer_b,
            technical_quality=random.choices(ARENA_RATING_CHOICES, weights=weights)[0],
            constructiveness=random.choices(ARENA_RATING_CHOICES, weights=weights)[0],
            clarity=random.choices(ARENA_RATING_CHOICES, weights=weights)[0],
            overall_quality=random.choices(ARENA_RATING_CHOICES, weights=weights)[0],
            review_a=generate_random_text(100),  # Random text for review_a
            review_b=generate_random_text(100),  # Random text for review_b
        )
        votes.append(vote)

    return votes


def main():
    votes_storage_jsonl = VotesJSONL("mock_arena_votes.jsonl")
    votes_storage_db = VotesSqlite("mock_arena_votes.db")

    mock_votes = generate_mock_votes(1000)

    for vote in mock_votes:
        votes_storage_jsonl.store_vote(vote)
        votes_storage_db.store_vote(vote)

    print("Generated and stored 1000 mock votes in arena_votes.jsonl")

    # Verify the stored votes
    stored_votes = votes_storage_jsonl.get_all_votes()
    print(f"Retrieved {len(stored_votes)} votes from the file")

    # Print the first 5 votes as a sample
    for i, vote in enumerate(stored_votes[:5]):
        print(f"Vote {i+1}:")
        print(vote.model_dump_json())
        print()

    # Calculate and print the distribution of choices
    choice_counts = {
        "technical_quality": defaultdict(lambda: 0),
        "constructiveness": defaultdict(lambda: 0),
        "clarity": defaultdict(lambda: 0),
        "overall_quality": defaultdict(lambda: 0),
    }

    for vote in stored_votes:
        choice_counts["technical_quality"][vote.technical_quality] += 1
        choice_counts["constructiveness"][vote.constructiveness] += 1
        choice_counts["clarity"][vote.clarity] += 1
        choice_counts["overall_quality"][vote.overall_quality] += 1

    print("Distribution of choices:")
    for category, counts in choice_counts.items():
        total = sum(counts.values())
        print(f"{category}:")
        for choice, count in counts.items():
            percentage = (count / total) * 100
            print(f"  {choice}: {count} ({percentage:.2f}%)")


if __name__ == "__main__":
    main()
