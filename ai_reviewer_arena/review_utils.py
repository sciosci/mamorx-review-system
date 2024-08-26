from data_storage import mock_reviews, reviewers


def get_reviews(paper_id):
    if paper_id not in mock_reviews:
        print(f"Warning: No reviews found for paper {paper_id}")
        return {}

    reviews = {}
    for reviewer in reviewers:
        reviewer_id = reviewer["id"]
        review = mock_reviews[paper_id].get(reviewer_id, "No review available")
        reviews[reviewer_id] = review

    return reviews
