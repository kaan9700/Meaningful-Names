# Summary

The project aims to conduct an in-depth analysis of the naming conventions used in a given Python source code. The analysis evaluates the quality, appropriateness, and consistency of the names used for functions, classes, and variables. It considers criteria such as descriptiveness, length, common misuses, consistency, abstraction, clarity, avoidance of acronyms, and domain-specific conventions. The analysis results are presented as a JSON object, including a score representing the overall quality of naming in the codebase and the total number of names evaluated. The project also provides the ability to make corrections to the naming of variables, classes, functions, etc. to improve both semantic appropriateness and syntactic correctness, following PEP 8 standards.

## Dependencies

The project does not have any specified dependencies.

# Setup

To set up the project, follow these instructions:

1. Clone the repository to your local machine.
2. Install the required dependencies by running the command `pip install -r requirements.txt`.
3. Set up the necessary environment variables, such as API keys or configuration files.
4. Run the unit tests to ensure everything is functioning correctly. Use the command `python -m unittest` to run the tests.

Once you have completed these steps, the project will be ready to use.

## Installation

To install the project, follow these steps:

1. Clone the repository to your local machine:

   ```
   git clone [repository URL]
   ```

2. Navigate to the project directory:

   ```
   cd [project directory]
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run the project:
   ```
   python main.py
   ```

Make sure you have Python and pip installed on your machine before proceeding with the installation.

## Examples

Here are some code examples from the project:

1. Parsing a Python source code file:

```python
try:
    with open(file_path, "r") as source:
        code_str = source.read()
        tree = ast.parse(code_str)
except SyntaxError:
    modified_code_str = code_str.replace("print ", "print(") + ")"
    try:
        tree = ast.parse(modified_code_str)
    except Exception as er:
        # Return an empty dictionary if the code cannot be parsed
        return {
            "function": [],
            "class": [],
            "variable": [],
            "constant": []
        }
```

2. Analyzing naming conventions in Python source code:

```python
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
```

3. Cloning a GitHub repository:

```python
def clone_repo(repo_link, github_token):
    # Get repo name from the link
    repo_name = "/".join(repo_link.split("/")[-2:])

    # Initialize Github instance with your token
    g = Github(github_token)

    # Get repo instance
    repo = g.get_repo(repo_name)

    # Define repo directory
    repo_dir = os.path.abspath(f'./repos/{repo_name}')

    # Clone the repo to the specified directory
    Repo.clone_from(repo_link, repo_dir)

    print(f"Cloned repo {repo_name} to repos folder")
    return str(repo_dir)
```

These are just a few examples from the project. For more code examples and documentation, please refer to the project's source code and documentation files.

# Usage

To use the project, follow these instructions:

1. Clone the repository using the command `git clone [repository-url]`.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Run the main script using the command `python main.py`.
4. Follow the prompts and provide the necessary input.
5. The project will perform the specified analysis or improvements based on the provided input.
6. Review the results and any generated output files or logs.

Note: Make sure to replace `[repository-url]` with the actual URL of the repository.

# Functions

1. `analyze_code(file_path)`: This function takes a file path as input and analyzes the Python source code in the file. It reads the code from the file, parses it using the `ast` module, and then extracts information about functions, classes, variables, and constants. The analysis results are returned as a dictionary.

2. `is_name_conformant(name, name_type)`: This function checks if a given name conforms to the PEP 8 naming conventions for a specific type (function, class, variable, or constant). It uses regular expressions to match the name against the appropriate convention pattern.

3. `rate_repository_syntactic(repo_name, type)`: This function rates the syntactic quality of a given repository. It takes the repository name and the type of rating (either "rate" or "improved") as input. It uses the `is_name_conformant` function to check the conformity of function, class, variable, and constant names in the repository. The results are returned as a dictionary containing the names that do not conform to the conventions.

4. `summarize_results(results)`: This function takes a list of results dictionaries as input and summarizes the results by combining the names from all dictionaries into a single dictionary. It returns the summarized dictionary.

5. `prompt_langchain(repo_url, type)`: This function prompts the language model to perform a specific task on a given repository. It takes the repository URL and the type of task (either "rate" or "improve") as input. It sets up the OpenAI API credentials, initializes the language model, and generates prompts based on the specified task. The function returns the generated prompts.

Note: The code documentation only includes the documentation for each function. For a more comprehensive documentation of the entire project, including class descriptions, variable explanations, and code examples, please refer to the complete project documentation.
