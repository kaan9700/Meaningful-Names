from utils import check_github_api_credentials
import sys
import pandas as pd
import requests
import tiktoken
import base64

# Function to count the number of tokens in a string using tiktoken
def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

# Function to fetch the default branch of a GitHub repository
def get_default_branch(repo_full_name, github_token):
    api_url = f"https://api.github.com/repos/{repo_full_name}"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        return response.json().get("default_branch", "main")
    else:
        print(f"Problem beim Abrufen des Standardbranches von {repo_full_name}")
        return "main"

# Function to get the content of a specific file in a GitHub repository
def get_file_content(repo_full_name, filename, github_token):
    api_url = f"https://api.github.com/repos/{repo_full_name}/contents/{filename}"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(api_url, headers=headers)
    try:
        content_decoded = base64.b64decode(response.json()["content"]).decode("utf-8")
    except UnicodeDecodeError:
        return 'x' * 10000
    if response.status_code == 200:
        return content_decoded
    else:
        return None

# Function to count the number of Python tokens in a GitHub repository
def count_python_tokens(repo_full_name, github_token, max_tokens):
    default_branch = get_default_branch(repo_full_name, github_token)
    api_url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{default_branch}?recursive=1"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        tree = response.json()["tree"]
        total_tokens = 0
        for item in tree:
            if item["path"].endswith(".py"):
                file_content = get_file_content(repo_full_name, item["path"], github_token)
                if file_content:
                    total_tokens += num_tokens_from_string(file_content, "gpt-3.5-turbo")
        return total_tokens <= int(max_tokens)
    else:
        print(f"Problem beim Abrufen des Inhalts von {repo_full_name}")
        return False

# Main function to search for GitHub repositories based on various criteria
def search_repositories(language, num_repos, year, max_tokens, query_terms, github_token):
    num_repos = int(num_repos)
    api_url = "https://api.github.com/search/repositories"
    query = f"language:{language} created:{year} {query_terms}"

    params = {
        "q": query,
        "sort": "stars",
        "order": "asc",
        "per_page": 100,
    }
    headers = {"Authorization": f"token {github_token}"}
    filtered_repos = []
    page_num = 1

    while len(filtered_repos) < num_repos:
        params["page"] = page_num
        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Fehlercode: {response.status_code}")
            print("Es gab ein Problem beim Abrufen der Repositories.")
            return None

        repos = response.json()["items"]
        if not repos:
            break

        for repo in repos:
            if len(filtered_repos) >= num_repos:
                break
            py_files_count = count_python_tokens(repo["full_name"], github_token, max_tokens)
            if py_files_count:
                filtered_repos.append(repo)

        page_num += 1

    df = pd.DataFrame([repo["html_url"] for repo in filtered_repos], columns=["Repository URL"])
    df.to_csv("repositories.csv", index=False)

    print("Die Repositories wurden erfolgreich in der Datei 'repositories.csv' gespeichert.")
    return df

# Entry point of the script
if __name__ == "__main__":
    if not check_github_api_credentials("https://api.github.com", ""):
        sys.exit()

    # Initialize parameters
    language = "Python"
    num_repos = '10'
    max_tokens = '5000'
    year = '2022'
    search_terms = ['test', 'example']
    query_terms = " OR ".join(search_terms)

    df = search_repositories(language, num_repos, year, max_tokens, query_terms, "")
    print(df)
