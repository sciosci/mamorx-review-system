from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
import math
from tabulate import tabulate
from colorama import Fore, Back, Style, init

init(autoreset=True)

SCALE = 400
BASE = 10
INIT_RATING = 1500
sample_weight = None


def compute_corrected_elo_mle_with_covariates(df):
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

        if row["overall_quality"] == "👈  A is better":
            Y.append(1)
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            sample_weights.append(2)
        elif row["overall_quality"] == "👉  B is better":
            Y.append(0)
            reviewer_feature_list.append(reviewer_vector)
            covariate_feature_list.append(covariate_vector)
            sample_weights.append(2)
        elif row["overall_quality"] == "🤝  Tie":
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
    X_covariate += 1
    X_covariate /= 3
    X_covariate = np.log(X_covariate)

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
    # print how much in Elo the covariates added (for each covariate)
    for i, covariate in enumerate(covariate_names):
        print(f"{covariate}: {(lr_corrected.coef_[0][len(reviewers) + i] ):.1f} Elo")
    print(lr_corrected.coef_[0])
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
    for i, covariate in enumerate(covariate_names):
        print(f"{covariate}: {lr_covariate.coef_[0][i]:.1f} Elo")

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
    elo_df["elo_score_difference"] = (
        elo_df["elo_score"] - elo_df["elo_score_uncorrected"]
    )
    return elo_df


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

elo_scores = compute_corrected_elo_mle_with_covariates(df)

# Prepare data for tabulate
data = []
for _, row in elo_scores.iterrows():
    difference = row["elo_score"] - row["elo_score_uncorrected"]
    if difference > 0:
        change = f"{Fore.GREEN}▲ {difference:.1f}{Style.RESET_ALL}"
    elif difference < 0:
        change = f"{Fore.RED}▼ {abs(difference):.1f}{Style.RESET_ALL}"
    else:
        change = f"{Fore.YELLOW}━{Style.RESET_ALL}"

    data.append(
        [
            row["reviewer"],
            f"{row['elo_score']:.1f}",
            f"{row['elo_score_uncorrected']:.1f}",
            change,
        ]
    )

# Create a colorful table
headers = [
    f"{Fore.CYAN}Reviewer{Style.RESET_ALL}",
    f"{Fore.GREEN}Corrected ELO{Style.RESET_ALL}",
    f"{Fore.YELLOW}Uncorrected ELO{Style.RESET_ALL}",
    f"{Fore.MAGENTA}Change{Style.RESET_ALL}",
]

table = tabulate(data, headers=headers, tablefmt="fancy_grid")

# Add a title
title = f"{Fore.MAGENTA}{Style.BRIGHT}ELO Scores Comparison{Style.RESET_ALL}"
print(f"\n{title:^{len(table.splitlines()[0])}}\n")

# Print the table
print(table)

# Add a legend
print(f"\n{Fore.CYAN}Legend:{Style.RESET_ALL}")
print(f"{Fore.GREEN}Corrected ELO: Scores adjusted for covariates{Style.RESET_ALL}")
print(
    f"{Fore.YELLOW}Uncorrected ELO: Raw scores without covariate adjustment{Style.RESET_ALL}"
)
print(
    f"{Fore.MAGENTA}Change: Difference between Corrected and Uncorrected ELO{Style.RESET_ALL}"
)
print(f"  {Fore.GREEN}▲: Increase{Style.RESET_ALL}")
print(f"  {Fore.RED}▼: Decrease{Style.RESET_ALL}")
print(f"  {Fore.YELLOW}━: No change{Style.RESET_ALL}")


# Calculate probability matrices
def calculate_win_probability(elo_i, elo_j):
    return 1 / (1 + 10 ** ((elo_j - elo_i) / 400))


reviewers = elo_scores["reviewer"].tolist()
n = len(reviewers)

corrected_probs = np.zeros((n, n))
uncorrected_probs = np.zeros((n, n))

for i in range(n):
    for j in range(n):
        elo_i = elo_scores.iloc[i]
        elo_j = elo_scores.iloc[j]
        corrected_probs[i, j] = calculate_win_probability(
            elo_i["elo_score"], elo_j["elo_score"]
        )
        uncorrected_probs[i, j] = calculate_win_probability(
            elo_i["elo_score_uncorrected"], elo_j["elo_score_uncorrected"]
        )


# Display probability matrices
def display_probability_matrix(matrix, title):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    max_reviewer_length = max(len(reviewer) for reviewer in reviewers)
    column_width = max(max_reviewer_length, 10)

    print(f"{Fore.YELLOW}{'':{column_width}}", end="")
    for reviewer in reviewers:
        print(f"{reviewer:>{column_width}}", end="")
    print(Style.RESET_ALL)

    for i, row in enumerate(matrix):
        print(f"{Fore.YELLOW}{reviewers[i]:{column_width}}{Style.RESET_ALL}", end="")
        for prob in row:
            color = Fore.GREEN if prob > 0.5 else Fore.RED if prob < 0.5 else Fore.WHITE
            print(f"{color}{prob:{column_width}.2f}{Style.RESET_ALL}", end="")
        print()


display_probability_matrix(corrected_probs, "Corrected ELO Win Probabilities")
display_probability_matrix(uncorrected_probs, "Uncorrected ELO Win Probabilities")

print(f"\n{Fore.CYAN}Legend:{Style.RESET_ALL}")
print(f"{Fore.GREEN}>0.50: Higher probability of winning{Style.RESET_ALL}")
print(f"{Fore.RED}<0.50: Lower probability of winning{Style.RESET_ALL}")
print(f"{Fore.WHITE}=0.50: Equal probability{Style.RESET_ALL}")
