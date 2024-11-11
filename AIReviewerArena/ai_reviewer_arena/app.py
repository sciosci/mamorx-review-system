import logging
import random
from datetime import datetime
from pathlib import Path

import gradio as gr
import pandas as pd
from gradio_pdf import PDF

from ai_reviewer_arena.configs.app_cfg import (ACK_MD, APP_CSS,
                                               ARENA_LOGGING_LEVEL,
                                               ARENA_NOTICE_MD,
                                               ARENA_RATING_CHOICES, TOS_MD)
from ai_reviewer_arena.configs.logging_cfg import setup_logging
from ai_reviewer_arena.elo_system import EloSystem
from ai_reviewer_arena.papers import Paper, paper_registry
from ai_reviewer_arena.reviewers import model_registry
from ai_reviewer_arena.sessions import Session, SessionRegistry
from ai_reviewer_arena.utils import get_session_id
from ai_reviewer_arena.votes import Vote, VotesJSONL, VotesSqlite

PROJECT_HOME = Path(__file__).parent.parent
PDF_FOLDER = PROJECT_HOME / "arena_data/resources/pdfs"

ui_logger = logging.getLogger("UILogger")
setup_logging(log_level=ARENA_LOGGING_LEVEL)

NUM_COLUMNS = 2

MODEL_SHORT_NAME_LIST = model_registry.get_all_short_names()
MODEL_ID_LIST = model_registry.get_model_id_list()

# Create a SessionRegistry instance
session_registry = SessionRegistry()


# Function to save the session
def save_session(session_state):
    if session_state:
        # Update the end_time field
        session_state.end_time = datetime.now()

        # Check if the session exists and save/update accordingly
        if session_registry.session_exists(session_state.session_id):
            session_registry.update_session(session_state)
            ui_logger.info(f"Session updated for {session_state.session_id}")
        else:
            session_registry.insert_session(session_state)
            ui_logger.info(f"New session inserted for {session_state.session_id}")


def update_leaderboard(session: Session):
    elo_sys: EloSystem = session["elo_sys"]
    ratings_stats = elo_sys.get_ratings_stats()
    df = (
        pd.DataFrame.from_dict(ratings_stats, orient="index")
        .reset_index()
        .rename(columns={"index": "System"})
    )
    if len(df) == 0:
        gr.Warning("No comparisons yet, please start voting.")
        vote_counts_md = f"### Total \\#models: {len(MODEL_ID_LIST)},&nbsp;&nbsp;&nbsp;&nbsp;Total \\#votes: {0}"
        return [df, vote_counts_md]

    df["Arena Score"] = df["Arena Score"].round(2)
    df["Votes"] = df["Votes"].round(2)
    df["95% CI"] = df["95% CI"].apply(lambda x: (round(x[0], 2), round(x[1], 2)))
    df["95% CI"] = df["95% CI"].apply(lambda x: f"({x[0]:.2f}, {x[1]:.2f})")
    df = (
        df.sort_values(by="Arena Score", ascending=False)
        .reset_index()
        .rename(columns={"index": "Rank"})
    )
    df["Rank"] = df["Rank"] + 1
    vote_counts_md = f"### Total \\#models: {len(MODEL_ID_LIST)},&nbsp;&nbsp;&nbsp;&nbsp;Total \\#votes: {df['Votes'].sum()}"

    return [df.sort_values(by="Rank", ascending=True), vote_counts_md]


def select_new_paper(session: Session, new_paper_pos: int, attempts: int = 0) -> tuple:
    paper_registry_size = paper_registry.get_paper_count()
    if attempts >= paper_registry_size:
        ui_logger.error(
            f"No paper with a fair pair of reviewers found after {attempts} attempts."
        )
        raise ValueError(
            "No paper with a fair pair of reviewers found in the entire registry."
        )

    new_paper_pos = (
        new_paper_pos % paper_registry_size
    )  # Ensure we wrap around if we go past the end
    session["cur_paper_pos"] = new_paper_pos
    cur_sampled_paper: Paper = paper_registry.get_paper_at_position(new_paper_pos)

    # Get the path of the paper PDF
    pdf_path = cur_sampled_paper.pdf_path
    pdf_path_full = str(PDF_FOLDER / pdf_path)

    # Get the fair pair of reviewers
    elo_sys: EloSystem = session["elo_sys"]
    valid_reviewer_ids = set(cur_sampled_paper.get_all_valid_reviewer_ids())
    fair_pair = elo_sys.get_fair_pair(
        candidates_a=valid_reviewer_ids, candidates_b=valid_reviewer_ids
    )

    if fair_pair is None:
        ui_logger.warning(
            f"No fair pair found for paper with paper_id: {cur_sampled_paper.paper_id}, at paper registry position: {new_paper_pos}. Attempting next paper at position: {new_paper_pos + 1}."
        )
        return select_new_paper(session, new_paper_pos + 1, attempts + 1)

    reviewer_a, reviewer_b = fair_pair
    ui_logger.info(
        f"Selected fair pair: {reviewer_a} and {reviewer_b} for paper with: position {new_paper_pos}, paper_id: {cur_sampled_paper.paper_id}, paper_title: {cur_sampled_paper.title}"
    )

    # Sample one review from the review list specified by `reviewer_a` from the sampled `Paper`
    reviewer_a_review_list = getattr(cur_sampled_paper, reviewer_a, [])
    assert len(reviewer_a_review_list) > 0
    reviewer_a_sampled_review = random.choice(reviewer_a_review_list)

    # Sample one review from the review list specified by `reviewer_b` from the sampled `Paper`
    reviewer_b_review_list = getattr(cur_sampled_paper, reviewer_b, [])
    assert len(reviewer_b_review_list) > 0
    reviewer_b_sampled_review = random.choice(reviewer_b_review_list)

    # Update session variables
    session["reviewer_a"] = reviewer_a
    session["reviewer_b"] = reviewer_b
    session["reviewer_a_review"] = reviewer_a_sampled_review
    session["reviewer_b_review"] = reviewer_b_sampled_review
    session["paper_id"] = cur_sampled_paper.paper_id  # New field added

    # Reset voted pair of reviews for the new paper
    session["voted_pair_of_reviews"] = set()

    return pdf_path_full, reviewer_a_sampled_review, reviewer_b_sampled_review, session


def next_paper(session_state, pdf_viewer):
    cur_paper_pos = session_state["cur_paper_pos"]
    new_paper_pos = (cur_paper_pos + 1) % paper_registry.get_paper_count()
    pdf_path_full, reviewer_a_review, reviewer_b_review, updated_session = (
        select_new_paper(session_state, new_paper_pos)
    )

    # Save the session after moving to the next paper
    save_session(session_state)

    return [pdf_path_full, reviewer_a_review, reviewer_b_review, updated_session]


def prev_paper(session_state, pdf_viewer):
    cur_paper_pos = session_state["cur_paper_pos"]
    new_paper_pos = (cur_paper_pos - 1) % paper_registry.get_paper_count()
    pdf_path_full, reviewer_a_review, reviewer_b_review, updated_session = (
        select_new_paper(session_state, new_paper_pos)
    )

    # Save the session after moving to the previous paper
    save_session(session_state)

    return [pdf_path_full, reviewer_a_review, reviewer_b_review, updated_session]


def init_demo(request: gr.Request):
    # Create a session
    assert request
    session = Session(
        session_id=get_session_id(request),
        ip_address=request.client.host,
        user_agent=request.headers["user-agent"],
    )
    ui_logger.info(f"New session initialized: {session.session_id}")

    # Create the VotesSqlite and VotesJSONL object
    votes_sqlite = VotesSqlite()
    votes_jsonl = VotesJSONL()

    # Assert the two votes databases are identical
    assert votes_sqlite.get_all_votes() == votes_jsonl.get_all_votes()

    # Create an EloSystem
    elo_sys = EloSystem(votes_sqlite)

    # Store the variables in the session
    session["votes_sqlite"] = votes_sqlite
    session["votes_jsonl"] = votes_jsonl
    session["elo_sys"] = elo_sys

    # Initialize new session variables
    session["voted_pair_of_reviews"] = set()

    # Select a random paper to start with
    cur_paper_pos: int = paper_registry.sample_paper_position()
    (
        pdf_path_full,
        reviewer_a_sampled_review,
        reviewer_b_sampled_review,
        updated_session,
    ) = select_new_paper(session, cur_paper_pos)

    # Save the initial session
    save_session(session)

    return (
        updated_session,
        pdf_path_full,
        reviewer_a_sampled_review,
        reviewer_b_sampled_review,
    )


def submit_vote(
    session_state,
    pdf_path_full,
    review_display_a,
    review_display_b,
    technical_quality,
    constructiveness,
    clarity,
    overall_quality,
):
    # Check if all radio buttons are selected
    if any(
        x is None
        for x in [technical_quality, constructiveness, clarity, overall_quality]
    ):
        ui_logger.warning(
            f"Incomplete vote submission attempt for session {session_state['session_id']}"
        )
        missing_fields = []
        if technical_quality is None:
            missing_fields.append("Technical Quality")
        if constructiveness is None:
            missing_fields.append("Constructiveness")
        if clarity is None:
            missing_fields.append("Clarity")
        if overall_quality is None:
            missing_fields.append("Overall Quality")

        error_message = f"Please select a rating for: {', '.join(missing_fields)}"
        gr.Warning(error_message, duration=5)
        return [
            pdf_path_full,
            review_display_a,
            review_display_b,
            None,  # technical_quality_radio
            None,  # constructiveness_radio
            None,  # clarity_radio
            None,  # overall_quality_radio
            session_state,
            session_state["reviewer_a"],  # New return value for model_selector_a
            session_state["reviewer_b"],  # New return value for model_selector_b
        ]
    # Create a Vote object
    vote = Vote(
        session_id=session_state["session_id"],
        paper_id=session_state["paper_id"],  # New field added
        reviewer_a=session_state["reviewer_a"],
        reviewer_b=session_state["reviewer_b"],
        technical_quality=technical_quality,
        constructiveness=constructiveness,
        clarity=clarity,
        overall_quality=overall_quality,
        review_a=session_state["reviewer_a_review"],  # New field added
        review_b=session_state["reviewer_b_review"],  # New field added
    )

    # Save the vote to both databases
    session_state["votes_sqlite"].store_vote(vote)
    session_state["votes_jsonl"].store_vote(vote)

    # Add vote record to the Elo system and update the Elo ratings
    session_state["elo_sys"].add_vote_then_update_ratings(vote)

    # Record the voted pair of reviews
    session_state["voted_pair_of_reviews"].add(
        (session_state["reviewer_a_review"], session_state["reviewer_b_review"])
    )

    # Get the current paper
    cur_paper_pos = session_state["cur_paper_pos"]
    cur_sampled_paper = paper_registry.get_paper_at_position(cur_paper_pos)

    # Function to sample a new pair of reviews
    def sample_new_reviews(paper: Paper, reviewer_a, reviewer_b):
        reviewer_a_review_list = getattr(paper, reviewer_a, [])
        reviewer_b_review_list = getattr(paper, reviewer_b, [])

        available_pairs = [
            (a, b)
            for a in reviewer_a_review_list
            for b in reviewer_b_review_list
            if (a, b) not in session_state["voted_pair_of_reviews"]
            and len(a.strip()) > 0
            and len(b.strip()) > 0
        ]

        if available_pairs:
            return random.choice(available_pairs)
        else:
            ui_logger.warning(
                f"No valid review pairs found for paper {paper.paper_id}, reviewers {reviewer_a} and {reviewer_b}, the number of voted_pair_of_reviews is: {len(session_state['voted_pair_of_reviews'])}"
            )
            return None

    # Try to get a new fair pair and sample reviews
    MAX_ATTEMPTS = 10  # Maximum number of attempts to find a new pair
    for attempt in range(MAX_ATTEMPTS):
        elo_sys: EloSystem = session_state["elo_sys"]
        valid_reviewer_ids = set(cur_sampled_paper.get_all_valid_reviewer_ids())
        fair_pair = elo_sys.get_fair_pair(
            candidates_a=valid_reviewer_ids, candidates_b=valid_reviewer_ids
        )

        if fair_pair is None:
            ui_logger.debug(
                f"Sampling new reviews for paper with paper_id: {cur_sampled_paper.paper_id}, title: {cur_sampled_paper.title}, However, No fair pair found on attempt: {attempt + 1}, max attempts: {MAX_ATTEMPTS}"
            )
            continue

        reviewer_a, reviewer_b = fair_pair

        new_reviews = sample_new_reviews(cur_sampled_paper, reviewer_a, reviewer_b)

        if new_reviews:
            ui_logger.info(
                f"Sampling new reviews for paper with paper_id: {cur_sampled_paper.paper_id}, title: {cur_sampled_paper.title}, New reviews sampled from {reviewer_a} and {reviewer_b} after {attempt + 1} attempts"
            )
            reviewer_a_sampled_review, reviewer_b_sampled_review = new_reviews
            break
    else:
        ui_logger.warning(
            f"Sampling new reviews for paper with paper_id: {cur_sampled_paper.paper_id}, title: {cur_sampled_paper.title}, However, failed to find new reviews after {MAX_ATTEMPTS} attempts. It seems we've exhausted all combinations for this paper at position: {cur_paper_pos}. Moving to next paper at position: {cur_paper_pos + 1}."
        )
        # If we've exhausted all combinations for this paper or reached max attempts, move to the next paper
        cur_paper_pos = (cur_paper_pos + 1) % paper_registry.get_paper_count()
        (
            pdf_path_full,
            reviewer_a_sampled_review,
            reviewer_b_sampled_review,
            session_state,
        ) = select_new_paper(session_state, cur_paper_pos)
        reviewer_a, reviewer_b = (
            session_state["reviewer_a"],
            session_state["reviewer_b"],
        )

    session_state["reviewer_a"] = reviewer_a
    session_state["reviewer_b"] = reviewer_b
    session_state["reviewer_a_review"] = reviewer_a_sampled_review
    session_state["reviewer_b_review"] = reviewer_b_sampled_review

    # Update the leaderboard
    # leaderboard_df, vote_counts_md = update_leaderboard(session_state)

    # Save the session after submitting a vote
    save_session(session_state)

    ui_logger.info(f"Vote submitted for session {session_state['session_id']}: {vote}")

    return [
        pdf_path_full,
        reviewer_a_sampled_review,
        reviewer_b_sampled_review,
        None,  # technical_quality_radio
        None,  # constructiveness_radio
        None,  # clarity_radio
        None,  # overall_quality_radio
        session_state,
        reviewer_a,  # New return value for model_selector_a
        reviewer_b,  # New return value for model_selector_b
    ]


def build_arena_ui():
    text_size = gr.themes.sizes.text_lg
    with gr.Blocks(
        title="Scientific Paper Review with Large Language Models",
        theme=gr.themes.Default(text_size=text_size),
        css=APP_CSS,
    ) as demo:
        session_state = gr.State()

        with gr.Tab("⚔️ Arena (battle)"):
            gr.Markdown(ARENA_NOTICE_MD)
            with gr.Row():
                pdf_viewer = PDF(
                    value=None,
                    label="Document",
                    starting_page=1,
                    scale=1,
                    container=True,
                    min_width=1200,
                    height=1600,
                    interactive=False,
                )

            with gr.Row():
                gr.Markdown(
                    "## 👇 Compare the reviews generated by two matched models based on their Elo ratings"
                )

            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        model_selector_a = gr.Dropdown(
                            choices=list(zip(MODEL_SHORT_NAME_LIST, MODEL_ID_LIST)),
                            value=MODEL_ID_LIST[0] if MODEL_ID_LIST else "",
                            interactive=False,
                            show_label=False,
                            container=False,
                            visible=True,
                        )
                    with gr.Column():
                        model_selector_b = gr.Dropdown(
                            choices=list(zip(MODEL_SHORT_NAME_LIST, MODEL_ID_LIST)),
                            value=MODEL_ID_LIST[1] if len(MODEL_ID_LIST) > 1 else "",
                            interactive=False,
                            show_label=False,
                            container=False,
                            visible=True,
                        )

                with gr.Row():
                    with gr.Accordion(
                        f"🔍 Expand to see the descriptions of {len(MODEL_ID_LIST)} models",
                        open=False,
                        visible=True,
                    ):
                        model_description_md = model_registry.get_model_description_md()
                        gr.Markdown(
                            model_description_md, elem_id="model_description_markdown"
                        )

                with gr.Row():
                    with gr.Column():
                        review_display_a = gr.TextArea(
                            label="Model A",
                            elem_id="review_display_a",
                            lines=16,
                            show_copy_button=True,
                            interactive=False,
                            show_label=True,
                            container=True,
                        )
                    with gr.Column():
                        review_display_b = gr.TextArea(
                            label="Model B",
                            elem_id="review_display_b",
                            lines=16,
                            show_copy_button=True,
                            interactive=False,
                            show_label=True,
                            container=True,
                        )

            with gr.Group():
                with gr.Row():
                    with gr.Column(scale=6):
                        technical_quality_radio = gr.Radio(
                            choices=ARENA_RATING_CHOICES,
                            label="Technical Quality:",
                            container=True,
                            show_label=True,
                            elem_classes=["grading_radio"],
                            # info="Thoroughness and accuracy in assessing the study's methods, analysis, and scientific rigor."
                        )
                    with gr.Column(scale=6):
                        constructiveness_radio = gr.Radio(
                            choices=ARENA_RATING_CHOICES,
                            label="Constructiveness:",
                            container=True,
                            show_label=True,
                            elem_classes=["grading_radio"],
                            # info="Helpfulness and actionability of the feedback and suggestions for improvement."
                        )
                with gr.Row():
                    with gr.Column(scale=6):
                        clarity_radio = gr.Radio(
                            choices=ARENA_RATING_CHOICES,
                            label="Clarity:",
                            container=True,
                            show_label=True,
                            elem_classes=["grading_radio"],
                            # info="How well-structured, organized, and clearly communicated the review is."
                        )
                    with gr.Column(scale=6):
                        overall_quality_radio = gr.Radio(
                            choices=ARENA_RATING_CHOICES,
                            label="Overall Quality:",
                            container=True,
                            show_label=True,
                            elem_classes=["grading_radio"],
                            # info="Holistic assessment of the review's effectiveness and value.",
                        )

            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        prev_btn = gr.Button(
                            "Previous Paper", variant="secondary", size="lg"
                        )
                        next_btn = gr.Button(
                            "Next Paper", variant="secondary", size="lg"
                        )
                with gr.Column():
                    submit_btn = gr.Button(
                        "Submit and Next Battle", variant="primary", size="lg"
                    )
            with gr.Row(equal_height=True, elem_id="tos_md"):
                gr.Markdown(TOS_MD)

            with gr.Row(equal_height=True, elem_id="ack_md"):
                gr.Markdown(ACK_MD)

        with gr.Tab("🏆 Leaderboard") as leadboard_tab:
            LEADERBOARD_NOTICE_MD = """
# 🏆  AI Review System Leaderboard
 [GitHub](https://github.com/) | [Paper](https://arxiv.org/abs/) | [Dataset](https://github.com/) | [Code](https://github.com/)

The leaderboard is ranked according to the Elo rating, voted by human anonymously.

"""
            gr.Markdown(LEADERBOARD_NOTICE_MD, elem_id="leaderboard_stat_md")
            vote_counts_md = gr.Markdown(
                f"### Total #models: {len(MODEL_ID_LIST)}    Total #votes: 0"
            )
            leadboard_df = gr.Dataframe(type="pandas")

            with gr.Row(equal_height=True, elem_id="tos_md"):
                gr.Markdown(TOS_MD)

            with gr.Row(equal_height=True, elem_id="ack_md"):
                gr.Markdown(ACK_MD)

        with gr.Tab("ℹ️ About Us"):
            gr.Markdown("## SOS+CD")

        demo.load(
            init_demo,
            [],
            [session_state, pdf_viewer, review_display_a, review_display_b],
        )

        leadboard_tab.select(
            update_leaderboard, [session_state], [leadboard_df, vote_counts_md]
        )

        submit_btn.click(
            submit_vote,
            inputs=[
                session_state,
                pdf_viewer,
                review_display_a,
                review_display_b,
                technical_quality_radio,
                constructiveness_radio,
                clarity_radio,
                overall_quality_radio,
            ],
            outputs=[
                pdf_viewer,
                review_display_a,
                review_display_b,
                technical_quality_radio,
                constructiveness_radio,
                clarity_radio,
                overall_quality_radio,
                session_state,
                model_selector_a,  # Add this output
                model_selector_b,  # Add this output
            ],
        )

        next_btn.click(
            next_paper,
            inputs=[session_state, pdf_viewer],
            outputs=[pdf_viewer, review_display_a, review_display_b, session_state],
        )

        prev_btn.click(
            prev_paper,
            inputs=[session_state, pdf_viewer],
            outputs=[pdf_viewer, review_display_a, review_display_b, session_state],
        )

        # Update model selectors when session state changes
        # session_state.change(
        #     lambda s: (s['reviewer_a'], s['reviewer_b']),
        #     inputs=[session_state],
        #     outputs=[model_selector_a, model_selector_b]
        # )

        # Update review displays when model selectors change
        model_selector_a.change(
            lambda s, m: s["reviewer_a_review"] if s["reviewer_a"] == m else "",
            inputs=[session_state, model_selector_a],
            outputs=[review_display_a],
        )

        model_selector_b.change(
            lambda s, m: s["reviewer_b_review"] if s["reviewer_b"] == m else "",
            inputs=[session_state, model_selector_b],
            outputs=[review_display_b],
        )

        demo.unload(lambda: print("====================="))

    return demo


demo = build_arena_ui()

if __name__ == "__main__":
    demo.launch()
