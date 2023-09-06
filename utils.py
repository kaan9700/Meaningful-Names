import glob
from github import Github
import requests
import openai
import os
import shutil
from git import Repo

# Function to clone a GitHub repository to a local directory
def get_repo(repoURL):
    name = repoURL.split("/")
    repo_path = "./repos/" + name[-2] + "/" + name[-1]

    # Create 'repos' folder if it doesn't exist
    if not os.path.exists("./repos/"):
        print("Creating repos folder")
        os.makedirs("./repos/")

    # Check if the repo is already cloned
    if os.path.exists(repo_path):
        print(f"The repo {name[-1]} has already been cloned. Exiting.")
        return str(repo_path)

    # Clone the repository to the 'repos' folder
    Repo.clone_from(repoURL, repo_path)
    print(f"Cloned repo {name[-1]} to repos folder")
    return str(repo_path)

# Function to validate the OpenAI API key
def check_openai_key(api_key):
    openai.api_key = api_key
    try:
        # Try to list available OpenAI models
        openai.Model.list()
        print("Der OpenAI-API-Schlüssel ist gültig.")
    except openai.OpenAIError:
        print("Der OpenAI-API-Schlüssel ist ungültig.")

# Function to clone a GitHub repository and list all Python files in it
def clone_repo(repo_link, github_token):
    repo_name = "/".join(repo_link.split("/")[-2:])
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    repo_dir = os.path.abspath(f'./repos/{repo_name}')

    # Check if the repo is already cloned
    if os.path.exists(repo_dir):
        print(f"Repository {repo_name} already exists. Using existing repo.")
    else:
        print(f"Cloning repository {repo_name}.")
        Repo.clone_from(repo_link, repo_dir)

    # List all Python files in the repository
    python_files = glob.glob(os.path.join(repo_dir, '**/*.py'), recursive=True)
    return python_files, repo_dir

# Function to delete a cloned GitHub repository from the local machine
def delete_repo(repo_link):
    repo_name = "/".join(repo_link.split("/")[-2:])
    repo_dir = os.path.abspath(f'./repos/{repo_name}')

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
        print(f"Repository {repo_name} deleted.")
    else:
        print(f"Repository {repo_name} does not exist.")

# Function to check if the provided GitHub API token is valid
def check_github_api_credentials(api_url, token):
    headers = {"Authorization": f"token {token}"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        print("Die angegebene GitHub API-URL und/oder der Token sind nicht korrekt.")
        print(response.status_code)
        return False
