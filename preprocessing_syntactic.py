import ast
import os
from utils import get_repo


# Function to analyze Python code for function, class, variable, and constant names
def analyze_code(file_path):
    try:
        # Read the source code file and parse it into an AST
        with open(file_path, "r") as source:
            code_str = source.read()
            tree = ast.parse(code_str)
    except SyntaxError:
        # Attempt to handle Python 2-specific constructs (e.g., old-style print)
        modified_code_str = code_str.replace("print ", "print(") + ")"
        try:
            tree = ast.parse(modified_code_str)
        except Exception as er:
            # Return an empty dictionary if the code still can't be parsed
            return {
                "function": [],
                "class": [],
                "variable": [],
                "constant": []
            }

    # Initialize sets to store the names of functions, classes, constants, and variables
    function_names = set()
    class_names = set()
    constant_names = set()
    variable_names = set()

    # Traverse the AST to collect names
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and not (node.name.startswith('__') and node.name.endswith('__')):
            function_names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            class_names.add(node.name)
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id.isupper():
                constant_names.add(node.targets[0].id)
            elif not (node.targets[0].id.startswith('__') and node.targets[0].id.endswith('__')):
                variable_names.add(node.targets[0].id)

    # Remove names that are both in variable and constant sets
    variable_names -= constant_names

    return {
        "function": list(function_names),
        "class": list(class_names),
        "variable": list(variable_names),
        "constant": list(constant_names)
    }


# Function to analyze an entire repository for function, class, variable, and constant names
def analyze_repository(repo_name, type):
    results = []
    if type == 'github':
        repo_url = f'https://github.com/{repo_name}'
        repo_dir = os.path.abspath(f'./repos/{repo_name}')

        # Clone the repo if it does not exist locally
        if not os.path.exists(repo_dir):
            if repo_url:
                print(f"Repo {repo_name} does not exist, cloning it now.")
                get_repo(repo_url)
            else:
                print(f"Repo {repo_name} does not exist and no repoURL provided to clone.")
                return []

    else:
        repo_dir = './improved_repos/' + repo_name

    # Iterate through all Python files in the repository directory
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    results.append(analyze_code(file_path))
                except Exception as e:
                    print(f"Failed to analyze file {file_path}: {e}")

    return results