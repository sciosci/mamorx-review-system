# Review Comparison System

This project implements a Review Comparison System using Gradio, allowing users to compare and evaluate reviews of academic papers. The system uses an Elo rating algorithm to rank reviewers based on the quality of their reviews.

## Features

- Display academic paper PDFs
- Show reviews from different reviewers (both human and AI)
- Allow users to compare reviews across multiple dimensions
- Implement an Elo rating system to rank reviewers
- Store comparison data in a SQLite database

## Requirements

- Python 3.7+
- Gradio
- PyMuPDF (fitz)
- Pillow
- SQLite3

1. Create a virtual environment

```
python -m venv venv
```

2. Activate the virtual environment

```
source venv/bin/activate
```

3. Install the required packages using:

```
pip install -r requirements.txt
```

4. Run the application

```
python review_comparison_app.py
```