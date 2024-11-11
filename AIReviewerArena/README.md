# AI Reviewer Arena

AI Reviewer Arena is a project designed to facilitate the evaluation of AI paper reviewers using the 
Elo grading system

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

## Installation

To get started with AI Reviewer Arena, clone the repository and install the required dependencies:

```bash
git clone https://github.com/tong-zeng/ai_reviewer_arena.git
cd ai_reviewer_arena
pip install -r requirements.txt
```


## Usage



### Importing Paper Reviews

You can import paper reviews from a JSONL file. The JSONL file should be in the following format:

```json
{
    "paper_id": "1",
    "title": "Paper Title",
    "pdf_path": "paper.pdf",
    "human_reviewer": ["review_1"],
    "barebones": ["review_2"],
    "liang_etal": ["review_3"],
    "multi_agent_without_knowledge": ["review_4"]
}
```
The default path to the paper reviews is `./arena_data/resources/papers/paper_reviews.jsonl`.

Then the `PaperRegistry` class can load the reviews from the JSONL file.


### Running the Application

To run the application, use the following command:

```bash
python ai_reviewer_arena/app.py
```

This will start the Gradio interface for the AI Reviewer Arena.


### Adding New Reviewers

We currently have 4 reviewers: `["human_reviewer", "barebones", "liang_etal", "multi_agent_without_knowledge"]`, If you want to add a new reviewer, you need to add a new field to the `Paper` class and the `ReviewerRegistry` class.

#### Adding New Reviewers to Paper Class

Add new fields to the `Paper` class and the `REVIEWER_FIELDS` class attribute.

```python
class Paper(BaseModel):
    paper_id: str
    title: str
    pdf_path: str
    human_reviewer: List[str]
    barebones: List[str]
    liang_etal: List[str]
    multi_agent_without_knowledge: List[str]

    # Class attribute listing all reviewer fields
    REVIEWER_FIELDS: ClassVar[List[str]] = [
        "human_reviewer",
        "barebones",
        "liang_etal",
        "multi_agent_without_knowledge"
    ]
```


#### Adding New Reviewers to ReviewerRegistry Class


You can register models using the `ModelRegistry` class. Here is an example of how to register a model:

```python
from ai_reviewer_arena.models import ModelRegistry
model_registry = ModelRegistry()
model_registry.register_model_info(
    id="human_reviewer",
    short_name="Human Reviewer",
    long_name="Human Reviewer",
    link="http://example.com/model_v1",
    description="These reviews are get from OpenView"
)
```


## Project Structure

The project structure is as follows:

```bash
Project_Root
./AIArena/
├── ai_reviewer_arena
│   ├── configs
│   │   ├── app_cfg.py
│   │   └──  logging_cfg.py
│   ├── mock_data
│   │   └── votes_data.py
│   ├── tests
│   │   ├── test_elo_system.py
│   │   ├── test_paper_registry.py
│   │   ├── test_review_eval_weights.py
│   │   ├── test_session.py
│   │   ├── test_session_registry.py
│   │   └── test_votes.py
│   ├── __init__.py
│   ├── app.py
│   ├── elo_system.py
│   ├── models.py
│   ├── papers.py
│   ├── sessions.py
│   ├── utils.py
│   └── votes.py
├── arena_data
│   ├── app_databases
│   │   ├── arena_votes.db
│   │   ├── arena_votes.jsonl
│   │   └── sessions.db
│   └── resources
│       ├── papers
│       │   └── paper_reviews.jsonl
│       └── pdfs
│           └── s10734-010-9390-y.pdf
├── logs
│   └── ai_reviewer_arena.log
├── README.md
└── requirements.txt
```

- `configs/`: Contains configuration files for the application.
- `mock_data/`: Contains mock data for testing.
- `tests/`: Contains unit tests for the project.
- `app.py`: Main application file to run the Gradio interface.
- `elo_system.py`: Contains the `EloSystem` class for managing the Elo rating system.
- `papers.py`: Contains the `PaperRegistry` class for managing paper reviews.
- `reviewers.py`: Contains the `ReviewerRegistry` class for managing reviewer information.
- `sessions.py`: Contains the `Session` and `SessionRegistry` classes for managing user sessions.
- `votes.py`: Contains the `Vote`, `VotesSqlite`, and `VotesJSONL` classes for managing votes.
- `utils.py`: Contains utility functions.
- `arena_data/`: Contains data for the application.
- `logs/`: Contains log files.

## Configuration

### Logging

You can use the enviroment variable `ARENA_LOGGING_LEVEL` to set the logging level. The logging level can be set to `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.

Or you can set the logging level with  constant variable `ARENA_LOGGING_LEVEL` in the `app_cfg.py` file.

### Application Configuration

All application configurations are in the `app_cfg.py` file.
