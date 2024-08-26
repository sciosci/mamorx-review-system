import gradio as gr
import random
from elo_system import EloSystem
from pdf_utils import get_pdf_page_image, get_pdf_page_count
from data_storage import papers, reviewers
from review_utils import get_reviews
from database import init_db, store_comparison

# Initialize the database
init_db()

# Initialize ELO system
elo_system = EloSystem()

# New global variables to store session data
session_data = {"email": "", "current_index": 0, "history": []}

# Add a new global variable for caching
page_cache = {}


# Function to get initial reviews
def get_initial_reviews():
    global session_data
    initial_paper = random.choice(papers)
    initial_reviewer_a, initial_reviewer_b = elo_system.get_fair_pair(
        [r["id"] for r in reviewers]
    )
    session_data = {
        "email": "",
        "current_index": 0,
        "history": [
            {
                "paper_id": initial_paper["id"],
                "reviewer_a": initial_reviewer_a,
                "reviewer_b": initial_reviewer_b,
                "comparisons": {},
                "elo_updated": False,
            }
        ],
    }
    elo_ratings = display_elo_ratings()
    elo_summary = get_elo_summary()  # Add this line

    # Check if the page is in the cache
    if (initial_paper["pdf_path"], 0) in page_cache:
        pdf_image = page_cache[(initial_paper["pdf_path"], 0)]
    else:
        pdf_image = get_pdf_page_image(initial_paper["pdf_path"], 0)
        # Add the page to the cache
        page_cache[(initial_paper["pdf_path"], 0)] = pdf_image

    reviews = get_reviews(initial_paper["id"])
    total_pages = get_pdf_page_count(initial_paper["pdf_path"])
    return (
        initial_paper["pdf_path"],
        0,  # Initial page index
        pdf_image,
        reviews.get(initial_reviewer_a, "No review available"),
        reviews.get(initial_reviewer_b, "No review available"),
        f"## {initial_paper['title']}",
        initial_paper["id"],
        session_data["email"],
        *[None] * len(dimensions),
        elo_ratings,
        f"Page 1 of {total_pages}",
        elo_summary,  # Add this line
    )


# Add a new function to get a summary of Elo ratings
def get_elo_summary():
    ratings = elo_system.get_ratings()
    sorted_reviewers = sorted(reviewers, key=lambda x: ratings[x["id"]], reverse=True)
    top_human = next((r for r in sorted_reviewers if r["type"] == "human"), None)
    top_ai = next((r for r in sorted_reviewers if r["type"] == "ai"), None)

    summary = "### Elo Rating Summary\n"
    if top_human:
        summary += f"Top Human: {top_human['name']} ({ratings[top_human['id']]:.2f})\n"
    if top_ai:
        summary += f"Top AI: {top_ai['name']} ({ratings[top_ai['id']]:.2f})\n"
    return summary


# Modified comparison function
def compare_reviews(user_email, paper_id, *comparison_inputs):
    # Update email in session data
    session_data["email"] = user_email

    # Check for missing inputs
    missing_fields = []
    if not user_email:
        missing_fields.append("email")
    for i, vote in enumerate(comparison_inputs):
        if vote is None:
            missing_fields.append(f"'{dimensions[i][0]}' comparison")

    # If there are missing fields, raise a specific error
    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        raise gr.Error(f"Please fill in the following fields: {missing_fields_str}")

    # Use only the dimension name (first element of the tuple) as the key
    comparisons = dict(zip([dim[0] for dim in dimensions], comparison_inputs))
    current_entry = session_data["history"][session_data["current_index"]]
    current_entry["comparisons"] = comparisons

    # Add comparison to EloSystem
    elo_system.add_comparison(
        current_entry["reviewer_a"], current_entry["reviewer_b"], comparisons
    )

    # Store comparison in the database
    store_comparison(
        user_email,
        current_entry["paper_id"],
        current_entry["reviewer_a"],
        current_entry["reviewer_b"],
        comparisons,
    )

    # Move to next comparison
    session_data["current_index"] += 1
    if session_data["current_index"] >= len(session_data["history"]):
        # Generate new comparison with fair pairing
        next_paper = random.choice(papers)
        next_reviewer_a, next_reviewer_b = elo_system.get_fair_pair(
            [r["id"] for r in reviewers]
        )
        session_data["history"].append(
            {
                "paper_id": next_paper["id"],
                "reviewer_a": next_reviewer_a,
                "reviewer_b": next_reviewer_b,
                "comparisons": {},
                "elo_updated": False,
            }
        )
    else:
        # Use existing comparison
        next_paper = next(
            p
            for p in papers
            if p["id"]
            == session_data["history"][session_data["current_index"]]["paper_id"]
        )

    current_entry = session_data["history"][session_data["current_index"]]

    # Check if the page is in the cache
    if (next_paper["pdf_path"], 0) in page_cache:
        pdf_image = page_cache[(next_paper["pdf_path"], 0)]
    else:
        pdf_image = get_pdf_page_image(next_paper["pdf_path"], 0)
        # Add the page to the cache
        page_cache[(next_paper["pdf_path"], 0)] = pdf_image

    total_pages = get_pdf_page_count(next_paper["pdf_path"])

    elo_summary = get_elo_summary()  # Add this line

    return (
        next_paper["pdf_path"],  # Return the new PDF path
        0,  # Reset to first page
        pdf_image,  # This is for the pdf_viewer
        get_reviews(current_entry["paper_id"])[current_entry["reviewer_a"]],
        get_reviews(current_entry["paper_id"])[current_entry["reviewer_b"]],
        f"## {next_paper['title']}",
        current_entry["paper_id"],
        user_email,
        *[None] * len(dimensions),
        f"Page 1 of {total_pages}",
        elo_summary,  # Add this line
    )


# Modify the navigate_pdf function to handle both file paths and image objects
def navigate_pdf(pdf_path_or_image, current_page, direction, total_pages):
    # Always get the current PDF path from session_data
    current_entry = session_data["history"][session_data["current_index"]]
    paper = next(p for p in papers if p["id"] == current_entry["paper_id"])
    pdf_path = paper["pdf_path"]

    total_pages = get_pdf_page_count(pdf_path)

    if direction == "next" and current_page < total_pages - 1:
        current_page += 1
    elif direction == "prev" and current_page > 0:
        current_page -= 1
    elif direction == "first":
        current_page = 0
    elif direction == "last":
        current_page = total_pages - 1

    # Check if the page is in the cache
    if (pdf_path, current_page) in page_cache:
        current_image = page_cache[(pdf_path, current_page)]
    else:
        current_image = get_pdf_page_image(pdf_path, current_page)
        # Add the page to the cache
        page_cache[(pdf_path, current_page)] = current_image

    return (
        current_image,
        current_page,
        gr.update(
            value=f"Page {current_page + 1} of {total_pages}", elem_id="page-info"
        ),
    )


# Add this function to navigate to a specific page
def go_to_page(pdf_path, page_number):
    total_pages = get_pdf_page_count(pdf_path)
    page_number = max(0, min(page_number, total_pages - 1))
    current_image = get_pdf_page_image(pdf_path, page_number)
    return (
        current_image,
        page_number,
        f"Page {page_number + 1} of {total_pages}",
    )


# Updated function to navigate to previous comparison
def go_to_previous():
    if session_data["current_index"] > 0:
        session_data["current_index"] -= 1
    current_entry = session_data["history"][session_data["current_index"]]
    paper = next(p for p in papers if p["id"] == current_entry["paper_id"])
    pdf_path = paper["pdf_path"]
    total_pages = get_pdf_page_count(pdf_path)
    current_image = get_pdf_page_image(pdf_path, 0)  # Get first page

    elo_summary = get_elo_summary()  # Add this line

    return (
        pdf_path,  # Return pdf_path instead of current_image
        0,  # Reset to first page
        current_image,  # This is for the pdf_viewer
        get_reviews(current_entry["paper_id"])[current_entry["reviewer_a"]],
        get_reviews(current_entry["paper_id"])[current_entry["reviewer_b"]],
        f"## {paper['title']}",
        current_entry["paper_id"],
        session_data["email"],
        *[current_entry["comparisons"].get(dim[0], None) for dim in dimensions],
        f"Page 1 of {total_pages}",
        elo_summary,  # Add this line
    )


# Add a function to display current ELO ratings
def display_elo_ratings():
    ratings = elo_system.get_ratings()
    sorted_reviewers = sorted(reviewers, key=lambda x: ratings[x["id"]], reverse=True)
    ratings_text = "### Current ELO Ratings\n\n"
    for reviewer in sorted_reviewers:
        ratings_text += f"{reviewer['name']} ({reviewer['type'].capitalize()}): {ratings[reviewer['id']]:.2f}\n"
    return ratings_text


# Modified error wrapper function
def error_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            elo_ratings = display_elo_ratings()
            return (
                [gr.update(visible=False)] * (len(dimensions) + 1)
                + list(result)
                + [elo_ratings]
            )
        except gr.Error as e:
            errors = str(e).split(", ")
            updates = []
            if "email" in str(e).lower():
                updates.append(
                    gr.update(
                        visible=True,
                        value="<span style='color: red;'>Please enter your email</span>",
                    )
                )
            else:
                updates.append(gr.update(visible=False))

            for dim in [dim[0] for dim in dimensions]:
                if any(err.startswith(f"'{dim}") for err in errors):
                    updates.append(
                        gr.update(
                            visible=True,
                            value=f"<span style='color: red;'>Please select an option</span>",
                        )
                    )
                else:
                    updates.append(gr.update(visible=False))

            # Return the correct number of outputs
            return (
                updates + [gr.update()] * 14
            )  # Adjust this number to match the total number of outputs

    return wrapper


# Gradio interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Review Comparison System")

    elo_summary_display = gr.Markdown()  # Add this line

    with gr.Row():
        with gr.Column(scale=3):
            user_email = gr.Textbox(label="Your Email", placeholder="Enter your email")
        with gr.Column(scale=1):
            email_error = gr.HTML(visible=False)

    with gr.Row():
        paper_title = gr.Markdown(elem_id="paper_title")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                page_info = gr.Markdown("Page 1 of X", elem_id="page-info")
            with gr.Row():
                first_page_btn = gr.Button("⏮️ First", size="sm")
                prev_page_btn = gr.Button("◀️ Previous", size="sm")
                next_page_btn = gr.Button("▶️ Next", size="sm")
                last_page_btn = gr.Button("⏭️ Last", size="sm")
            pdf_viewer = gr.Image(
                label="Paper",
                height=1400,
                width="100%",
            )
            current_page = gr.State(0)

    gr.Markdown("---")
    with gr.Row():
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### Review A")
            review_a = gr.Markdown()
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### Review B")
            review_b = gr.Markdown()

    # Add space between the reviews and the comparisons
    gr.Markdown("---")

    # add header for the comparisons
    gr.Markdown("# Comparisons")

    paper_id = gr.State()
    pdf_path = gr.State()  # Add this line to store the PDF file path

    dimensions = [
        (
            "Technical Quality",
            "Thoroughness and accuracy in assessing the study's methods, analysis, and scientific rigor.",
        ),
        (
            "Constructiveness",
            "Helpfulness and actionability of the feedback and suggestions for improvement.",
        ),
        (
            "Clarity",
            "How well-structured, organized, and clearly communicated the review is.",
        ),
        (
            "Overall Quality",
            "Holistic assessment of the review's effectiveness and value.",
        ),
    ]
    comparison_inputs = {}
    dimension_errors = {}
    with gr.Column(scale=1):
        for dim, explanation in dimensions:
            with gr.Row():
                gr.Markdown(f"### {dim}\n{explanation}")
            with gr.Row():
                comparison_inputs[dim] = gr.Radio(
                    [
                        "👈 A is better",
                        "👉 B is better",
                        "🤝 Tie",
                        "👎 Both are bad",
                    ],
                    label=f"Comparison: {dim}",
                    container=False,
                )
            with gr.Row():
                dimension_errors[dim] = gr.HTML(visible=False)

    with gr.Row():
        prev_btn = gr.Button("Previous", variant="secondary", size="lg")
        submit_btn = gr.Button("Submit and Next", variant="primary", size="lg")

    elo_ratings_display = gr.Markdown()

    submit_btn.click(
        error_wrapper(compare_reviews),
        inputs=[user_email, paper_id] + list(comparison_inputs.values()),
        outputs=[
            email_error,
            *[dimension_errors[dim[0]] for dim in dimensions],
            pdf_path,
            current_page,
            pdf_viewer,
            review_a,
            review_b,
            paper_title,
            paper_id,
            user_email,
            *comparison_inputs.values(),
            elo_ratings_display,
            page_info,
            elo_summary_display,  # Add this line
        ],
    )

    prev_btn.click(
        go_to_previous,
        outputs=[
            pdf_path,
            current_page,
            pdf_viewer,
            review_a,
            review_b,
            paper_title,
            paper_id,
            user_email,
            *comparison_inputs.values(),
            page_info,
            elo_summary_display,  # Add this line
        ],
    )

    def get_current_pdf_path():
        try:
            current_entry = session_data["history"][session_data["current_index"]]
            paper = next(p for p in papers if p["id"] == current_entry["paper_id"])
            return paper["pdf_path"]
        except (IndexError, KeyError, StopIteration):
            # If there's any error, return the path of the first paper as a fallback
            return papers[0]["pdf_path"] if papers else None

    first_page_btn.click(
        navigate_pdf,
        inputs=[
            gr.State(get_current_pdf_path),
            current_page,
            gr.State("first"),
            gr.State(lambda: get_pdf_page_count(get_current_pdf_path() or "")),
        ],
        outputs=[pdf_viewer, current_page, page_info],
    )

    prev_page_btn.click(
        navigate_pdf,
        inputs=[
            gr.State(get_current_pdf_path),
            current_page,
            gr.State("prev"),
            gr.State(lambda: get_pdf_page_count(get_current_pdf_path() or "")),
        ],
        outputs=[pdf_viewer, current_page, page_info],
    )

    next_page_btn.click(
        navigate_pdf,
        inputs=[
            gr.State(get_current_pdf_path),
            current_page,
            gr.State("next"),
            gr.State(lambda: get_pdf_page_count(get_current_pdf_path() or "")),
        ],
        outputs=[pdf_viewer, current_page, page_info],
    )

    last_page_btn.click(
        navigate_pdf,
        inputs=[
            gr.State(get_current_pdf_path),
            current_page,
            gr.State("last"),
            gr.State(lambda: get_pdf_page_count(get_current_pdf_path() or "")),
        ],
        outputs=[pdf_viewer, current_page, page_info],
    )

    demo.load(
        get_initial_reviews,
        outputs=[
            pdf_path,
            current_page,
            pdf_viewer,
            review_a,
            review_b,
            paper_title,
            paper_id,
            user_email,
            *comparison_inputs.values(),
            elo_ratings_display,
            page_info,
            elo_summary_display,  # Add this line
        ],
    )

    # Add some CSS to stabilize the layout and style the buttons
    demo.load(
        lambda: gr.update(
            value="""
        <style>
        #page-info {
            height: 1.5em;
            margin-bottom: 0.5em;
        }
        .gradio-radio {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        .gradio-radio label {
            flex-grow: 1;
            text-align: center;
        }
        </style>
    """
        ),
        outputs=gr.HTML(),
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
