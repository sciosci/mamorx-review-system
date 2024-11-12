from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Back, Style, init

init(autoreset=True)

SCALE = 400
BASE = 10
INIT_RATING = 1500
sample_weight = None


def compute_corrected_elo_mle_with_covariates(df, analysis_dimension="overall_quality"):
    # Initialize matrices for X (features) and Y (outcome)
    reviewers = sorted(set(df["reviewer_a"].unique()) | set(df["reviewer_b"].unique()))
    reviewer_to_index = {reviewer: i for i, reviewer in enumerate(reviewers)}
    p = len(reviewers)

    reviewer_feature_list = []
    covariate_feature_list = []
    Y = []
    sample_weights = []

    for _, row in df.iterrows():
        reviewer_a = row["reviewer_a"]
        reviewer_b = row["reviewer_b"]
        review_a_newlines = row["review_a_newlines"]
        review_b_newlines = row["review_b_newlines"]
        review_a_sections = row["review_a_sections"]
        review_b_sections = row["review_b_sections"]
        review_a_lists = row["review_a_lists"]
        review_b_lists = row["review_b_lists"]

        new_lines_diff = review_a_newlines - review_b_newlines
        sections_diff = review_a_sections - review_b_sections
        lists_diff = review_a_lists - review_b_lists

        if reviewer_a == reviewer_b:
            continue

        reviewer_vector = np.zeros(p)
        reviewer_vector[reviewer_to_index[reviewer_a]] = np.log(BASE)
        reviewer_vector[reviewer_to_index[reviewer_b]] = -np.log(BASE)

        covariate_vector = np.array([new_lines_diff, sections_diff, lists_diff])

        if row[analysis_dimension] == "👈  A is better":
            Y.append(1)
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            sample_weights.append(2)
        elif row[analysis_dimension] == "👉  B is better":
            Y.append(0)
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            sample_weights.append(2)
        elif row[analysis_dimension] == "🤝  Tie":
            Y.append(1)
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            sample_weights.append(1)
            # also add a lost
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            Y.append(0)
            sample_weights.append(1)

    X_reviewer = np.vstack(reviewer_feature_list)
    X_covariate = np.vstack(covariate_feature_list)

    # normalize the covariate features to be min max scaled
    X_covariate = (X_covariate - np.min(X_covariate)) / (
        np.max(X_covariate) - np.min(X_covariate)
    )

    X = np.hstack((X_reviewer, X_covariate))
    Y = np.array(Y)

    covariate_names = ["new_lines", "sections", "lists"]

    # Logistic regression model with no penalty
    lr_corrected = LogisticRegression(fit_intercept=False, penalty=None, tol=1e-6)
    lr_corrected.fit(X, Y, sample_weight=sample_weights)

    elo_scores_corrected = SCALE * lr_corrected.coef_[0][:p] + INIT_RATING
    final_elo_corrected = pd.Series(elo_scores_corrected, index=reviewers).sort_values(
        ascending=False
    )

    # remove the covariate part for the uncorrected elo
    lr_uncorrected = LogisticRegression(fit_intercept=False, penalty=None, tol=1e-6)
    lr_uncorrected.fit(X[:, :p], Y, sample_weight=sample_weights)
    elo_scores_uncorrected = SCALE * lr_uncorrected.coef_[0] + INIT_RATING
    final_elo = pd.Series(elo_scores_uncorrected, index=reviewers).sort_values(
        ascending=False
    )

    # only covariates
    lr_covariate = LogisticRegression(fit_intercept=False, penalty=None, tol=1e-6)
    lr_covariate.fit(X_covariate, Y, sample_weight=sample_weights)
    elo_scores_covariate = SCALE * lr_covariate.coef_[0] + INIT_RATING
    final_elo_covariate = pd.Series(
        elo_scores_covariate, index=covariate_names
    ).sort_values(ascending=False)

    # create a dataframe with the elo scores
    elo_df = pd.DataFrame(
        {
            "reviewer": reviewers,
            "elo_score": final_elo_corrected,
            "elo_score_uncorrected": final_elo,
        },
        index=reviewers,
    ).sort_values(by="elo_score", ascending=False)
    # create difference column
    # elo_df["elo_score_difference"] = (
    #     elo_df["elo_score"] - elo_df["elo_score_uncorrected"]
    # )
    return elo_df


def elo_win_probability(elo_a, elo_b):
    return 1 / (1 + BASE ** ((elo_b - elo_a) / SCALE))


def main():

    # Display the computed Elo scores
    df = pd.read_csv("arena_votes.csv")

    import re

    # Define functions to calculate covariates for new lines, sections, and lists
    def count_new_lines(text):
        return text.count("\n")

    def count_sections(text):
        return len(re.findall(r"\w+:", text))

    def count_lists(text):
        return len(re.findall(r"(\d+\.\s|\-\s|\*\s)", text))

    # Apply these functions to both review_a and review_b columns
    df["review_a_newlines"] = df["review_a"].apply(count_new_lines)
    df["review_b_newlines"] = df["review_b"].apply(count_new_lines)

    df["review_a_sections"] = df["review_a"].apply(count_sections)
    df["review_b_sections"] = df["review_b"].apply(count_sections)

    df["review_a_lists"] = df["review_a"].apply(count_lists)
    df["review_b_lists"] = df["review_b"].apply(count_lists)

    comparison_combination = [
        {"use_covariates": False, "analysis_dimension": "technical_quality"},
        {"use_covariates": False, "analysis_dimension": "constructiveness"},
        {"use_covariates": False, "analysis_dimension": "clarity"},
        {"use_covariates": False, "analysis_dimension": "overall_quality"},
        {"use_covariates": True, "analysis_dimension": "overall_quality"},
    ]

    all_elo_scores = pd.DataFrame()
    for combination in comparison_combination:
        elo_scores = compute_corrected_elo_mle_with_covariates(
            df, analysis_dimension=combination["analysis_dimension"]
        )
        if combination["use_covariates"]:
            elo_scores.rename(
                columns={
                    "elo_score": f"{combination['analysis_dimension']}_elo_corrected"
                },
                inplace=True,
            )
            if all_elo_scores.empty:
                all_elo_scores = elo_scores[
                    ["reviewer", f"{combination['analysis_dimension']}_elo_corrected"]
                ]
            else:
                all_elo_scores = pd.merge(
                    all_elo_scores,
                    elo_scores[
                        [
                            "reviewer",
                            f"{combination['analysis_dimension']}_elo_corrected",
                        ]
                    ],
                    on="reviewer",
                    how="outer",
                )
        else:
            elo_scores.rename(
                columns={
                    "elo_score_uncorrected": f"{combination['analysis_dimension']}_elo_uncorrected"
                },
                inplace=True,
            )
            if all_elo_scores.empty:
                all_elo_scores = elo_scores[
                    ["reviewer", f"{combination['analysis_dimension']}_elo_uncorrected"]
                ]
            else:
                all_elo_scores = pd.merge(
                    all_elo_scores,
                    elo_scores[
                        [
                            "reviewer",
                            f"{combination['analysis_dimension']}_elo_uncorrected",
                        ]
                    ],
                    on="reviewer",
                    how="outer",
                )
    all_elo_scores.reset_index(drop=True, inplace=True)

    # Define the desired order of reviewers
    reviewer_order = [
        "human_reviewer",
        "barebones",
        "liang_etal",
        "multi_agent_without_knowledge",
        "multi_agent_with_knowledge",
    ]

    # Reorder the DataFrame according to the specified order
    all_elo_scores = (
        all_elo_scores.set_index("reviewer").loc[reviewer_order].reset_index()
    )
    print(tabulate(all_elo_scores, headers="keys", tablefmt="grid", showindex=False))

    # Calculate and display the probability of reviewer A being better than reviewer B
    # using the uncorrected elo scores for overall quality

    # Extract uncorrected elo scores for overall quality and reviewer names
    uncorrected_elo_scores = all_elo_scores["overall_quality_elo_uncorrected"]
    # set the index to be the reviewer names
    uncorrected_elo_scores.index = all_elo_scores["reviewer"]
    reviewer_names = all_elo_scores["reviewer"]

    # Calculate the probability of reviewer A being better than reviewer B
    # using the formula: 1 / (1 + 10^(elo_score_B - elo_score_A / 400))
    probabilities = pd.DataFrame(
        data=np.zeros((len(reviewer_names), len(reviewer_names))),
        index=reviewer_order,  # Use the ordered list here
        columns=reviewer_order,  # And here
    )
    for reviewer_a in reviewer_names:
        for reviewer_b in reviewer_names:
            elo_score_a = uncorrected_elo_scores.loc[reviewer_a]
            elo_score_b = uncorrected_elo_scores.loc[reviewer_b]
            probability = elo_win_probability(elo_score_a, elo_score_b)
            probabilities.loc[reviewer_a, reviewer_b] = probability * 100

    # round to 2 decimal places
    probabilities = probabilities.round(2)
    print()
    # Display the probabilities in a table with reviewer names as headers and indices
    print(tabulate(probabilities, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()
