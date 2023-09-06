from syntactic_metric import rate_repository_syntactic
from utils import delete_repo
import pandas as pd
import os
from openai_prompts import prompt_langchain


# Function to evaluate a single repository
def evaluate_repo(index, row, dataframe, is_improved=False):
    # Get the repository URL from the DataFrame row
    repo_url = row["Repository URL"]
    print(f"Evaluating repository: {repo_url}")

    # Extract the repository name from the URL
    repo_name = "/".join(repo_url.split("/")[-2:])
    # Determine the source of the repository (GitHub or improved)
    repo_source = 'improved' if is_improved else 'github'

    # Get syntactic and semantic scores for the repository
    syntactic_score = rate_repository_syntactic(repo_name, repo_source)
    semantic_score = prompt_langchain(repo_url if not is_improved else f"./improved_repos/{repo_name}", 'rate')

    # Combine both scores into a single dictionary
    score = {**syntactic_score, **semantic_score}
    print(f"der Score für das das Repo: {repo_url} ist: {score}")

    # Update the DataFrame with the new scores
    dataframe.at[index, "Semantic Rating"] = score["semantic_score"]
    dataframe.at[index, "Syntactic Rating"] = score["syntactic_score"]

    # Delete the repository if it's not improved
    if not is_improved:
        delete_repo(repo_url)

    return dataframe


if __name__ == "__main__":
    # Unused variables; consider removing if not needed.
    GITHUB_API_URL = "https://api.github.com"
    github_token = ""

    # Load repository data from CSV into a DataFrame
    repositories_df = pd.read_csv("repositories.csv")
    # Initialize columns for semantic and syntactic ratings
    repositories_df["Semantic Rating"] = None
    repositories_df["Syntactic Rating"] = None

    # Check if rates.csv already exists
    if not os.path.exists("rates.csv"):
        # Iterate through each repository to evaluate it
        for index, row in repositories_df.iterrows():
            # Evaluate and update DataFrame with new scores
            repositories_df = evaluate_repo(index, row, repositories_df)
            # Save updated DataFrame to rates.csv
            repositories_df.to_csv("rates.csv", index=False)
            print('\n\n\n')

    # Iterate through each repository to improve and evaluate it
    for index, row in repositories_df.iterrows():
        # Run code improvement for the repository
        prompt_langchain(row["Repository URL"], 'improve')
        # Evaluate and update DataFrame with new scores for the improved repository
        repositories_df = evaluate_repo(index, row, repositories_df, is_improved=True)
        # Save updated DataFrame to rates_improved.csv
        repositories_df.to_csv("rates_improved.csv", index=False)
        print('\n\n\n')
