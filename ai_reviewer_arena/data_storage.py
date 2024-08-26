import json

# Mock data storage
papers = [
    {
        "id": "paper1",
        "title": "Sample Paper 1",
        "pdf_path": "example_pdfs/s10734-010-9390-y.pdf",
    },
    {
        "id": "paper2",
        "title": "Sample Paper 2",
        "pdf_path": "example_pdfs/12874_2019_Article_688.pdf",
    },
    {
        "id": "paper3",
        "title": "Sample Paper 3",
        "pdf_path": "example_pdfs/science.ado4166.pdf",
    },
]

reviewers = [
    {
        "id": 1,
        "name": "Human Reviewer",
        "type": "human",
        "expertise": "Machine Learning",
    },
    {"id": 2, "name": "AI System 1", "type": "ai", "expertise": "Quantum Computing"},
    {"id": 3, "name": "AI System 2", "type": "ai", "expertise": "Ethics in AI"},
    {"id": 4, "name": "AI System 3", "type": "ai", "expertise": "Neural Networks"},
    {"id": 5, "name": "AI System 4", "type": "ai", "expertise": "General AI"},
]

# Mock reviews in Markdown format
mock_reviews = {
    "paper1": {
        1: "# Review\n\nThe paper presents innovative ideas...",
        2: "# Review\n\nA comprehensive overview of recent advancements...",
        3: "# Review\n\nWhile the technical aspects are sound...",
        4: "# Review\n\nThe methodology is well-explained...",
        5: "# Review\n\nAn interesting read with potential real-world applications...",
    },
    "paper2": {
        1: "# Review\n\nThe paper offers a clear explanation...",
        2: "# Review\n\nA well-structured overview of quantum computing...",
        3: "# Review\n\nThe authors present a balanced view...",
        4: "# Review\n\nThe paper effectively bridges the gap...",
        5: "# Review\n\nA comprehensive review of quantum computing progress...",
    },
    "paper3": {
        1: "# Review\n\nThe paper raises important ethical considerations...",
        2: "# Review\n\nA thorough examination of ethical challenges in AI...",
        3: "# Review\n\nThe authors present a nuanced view of AI ethics...",
        4: "# Review\n\nWhile the ethical framework is well-constructed...",
        5: "# Review\n\nAn insightful analysis of ethical AI challenges...",
    },
}


def store_comparison(user_email, paper_id, reviewer_a, reviewer_b, comparisons):
    pass
    # print(f"Stored: User {user_email}, Paper {paper_id}, {reviewer_a} vs {reviewer_b}")
    # print(f"Comparisons: {json.dumps(comparisons, indent=2)}")
