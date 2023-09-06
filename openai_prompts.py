import json
import re
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    Language,
)
import os
from utils import get_repo
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory


# Define the prompt text for rating and improving code
rate_prompt = """
    Your task is to conduct an in-depth analysis of the naming conventions used in a given Python source code. 
    The aim is to evaluate the quality, appropriateness, and consistency of the names used for functions, classes, and variables.
    Ignore any kind of comments in your analysis.
    In this analysis, consider the following criteria:
    Descriptiveness: The names should be descriptive and relevant to their associated code. For example, a function meant to calculate an average could be named 'calculate_average', while 'calc_avg' might be somewhat less clear, and 'function1' would be vague and misleading.
    Length: Very short names (like 'a' or 'x') may not provide enough information about what they represent, while very long names can be cumbersome and may be a sign of trying to do too much with a single variable or function.
    Common Misuses: Names consisting of generic terms (like 'data', 'value') or Python reserved words should be avoided unless their usage is universally understood in the context of programming.
    Consistency: Check for consistency in naming conventions across the codebase. A name might be semantically correct in isolation but if it's not consistent with the rest of the codebase, it can be confusing for others reading the code.
    Abstraction: Avoid overly specific names if a more general naming would be appropriate.
    Clarity: Names should not only be descriptive but also intuitive and easily understood.
    Avoidance of Acronyms: Unless they are widely known or defined throughout the code.
    Domain-Specific Conventions: Depending on the purpose of the program, there may be specific naming conventions or practices that should be followed.
    Your analysis results should be formatted as a JSON object, following this schema:
    {
        "score": "<score>"
        "names_count" : "<names_count>"
    }
    Here, <score> represents the calculated score between 0.000 and 1.000 with up to 3 decimal places, expressed as a decimal number in string format with a granularity of 0.01. This score should reflect the overall quality of naming in the codebase, taking into account the factors mentioned above. As <names_count> you should return the total number of names that went into your rating. It is the value of the "score" and "names_count" key in the provided JSON schema. Ensure your evaluation is rigorous and critical to ensure code quality.
    """

improve_prompt = """Your task is to analyze a given Python source code and make corrections to the naming of variables, classes, functions, etc. to improve both semantic appropriateness and syntactic correctness. 
    The goal is to improve the quality, appropriateness, and consistency of the names used for functions, classes, and variables and to ensure that the code conforms to PEP 8 standards.
       
    Criteria:
    - Descriptive character: Suggest descriptive and relevant names. So the variables, classes, functions and constants should have names that also describe what they do or what they are.
   - Length: Provide concise and meaningful names.
    - Common misuse: avoid generic terms and reserved Python words.
    - Consistency: Ensure that naming is consistent throughout the code base.
    - Domain-specific conventions: Adhere to all domain-specific practices.
    - Syntactic correctness: Adhere to the PEP 8 guidelines for Python code.
    
    Your corrections should be returned in the form of the modified Python source code, which includes all semantic and syntactic name changes. Do not output any other text besides the code. \n\n"""


# Function to extract and validate score and names_count from JSON
def get_score(data):
    try:
        score = data.get("score")
        # Check if score is a valid float
        if score is not None:
            float(score)
        else:
            score = "N/A"  # Or some other default value
    except (AttributeError, ValueError):
        score = "N/A"  # Or some other default value

    try:
        names_count = data.get("names_count")

        if names_count is not None:
            float(names_count)

        else:
            names_count = "N/A"

    except (AttributeError, ValueError):
        names_count = "N/A"

    return score, names_count

# Function to extract JSON string from a larger text string
def extract_json_from_string(s):
    # Find the JSON string using a regex
    json_str = re.search(r"\{.*\}", s, flags=re.DOTALL)
    try:
        if json_str:
            # Load the JSON string as a Python dict
            json_obj = json.loads(json_str.group())
            return json_obj
        else:
            return None
    except json.decoder.JSONDecodeError:
        return None


# Function to index a given repository or file
def index_repo(repo_url):
    os.environ['OPENAI_API_KEY'] = ""

    contents = []
    fileextensions = [
        ".py", ]

    if bool(re.match(r'https://github\.com/[\w.-]+/[\w.-]+', repo_url)):
        repo_dir = get_repo(repo_url)

    else:
        repo_dir = repo_url

    text_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON, chunk_size=1000,
                                                                 chunk_overlap=0)

    all_splits = []
    for dirpath, dirnames, filenames in os.walk(repo_dir):
        for file in filenames:
            if file.endswith(tuple(fileextensions)):
                with open(os.path.join(dirpath, file), "r", encoding="utf-8") as f:
                    file_content = f.read()
                splits = text_splitter.create_documents([file_content])
                for split in splits:
                    split.metadata['file_name'] = file
                all_splits.extend(splits)
    return all_splits



# Function to run the language model chain for either rating or improving code

def prompt_langchain(repo_url, type):
    # Setting up environment variables
    os.environ['OPENAI_API_KEY'] = ""

    # Extract repository name from the URL
    repo_name = "/".join(repo_url.split("/")[-2:])

    # Index the repository and get code chunks
    codes = index_repo(repo_url)

    # Choose model based on operation type
    gpt_model = "gpt-3.5-turbo-16k-0613" if type != "rate" else "gpt-4"

    # Set up prompt based on operation type
    text = rate_prompt if type == "rate" else improve_prompt

    # Initialize model
    model = ChatOpenAI(temperature=0.1, model_name=gpt_model)
    # Initialize chain and memory based on operation type
    if type == "rate":
        # For rating, use a simple prompt
        prompt_template = PromptTemplate(template='{text}', input_variables=["text"])
        chain = LLMChain(llm=model, prompt=prompt_template, verbose=False)
    else:
        # For improving, use a more complex template and memory
        template = """ {text}
                {chat_history}
               """
        prompt_template = PromptTemplate(template=template, input_variables=["text", 'chat_history'])
        memory = ConversationBufferMemory(memory_key="chat_history")
        chain = LLMChain(llm=model, prompt=prompt_template, verbose=False, memory=memory)


    # Code for rating the repository
    if type == "rate":
        overall_score = []
        for code in codes:
            retries = 0
            max_retries = 3

            while retries < max_retries:

                result = chain.run(text=text + str(code.page_content))
                score_json = extract_json_from_string(result)

                if get_score(score_json) is None:
                    retries += 1
                    print(f"Invalid score for chunk: {code}. Retrying {retries}/{max_retries}...")
                else:
                    chunk_score, total_names = get_score(score_json)
                    if chunk_score == 'N/A' or total_names == 'N/A':
                        retries += 1
                        break
                    if total_names == '0':
                        chunk_score = '0'
                    chunk_score = {"score": chunk_score, "names_count": total_names}
                    overall_score.append(chunk_score)
                    break

        counter = 0
        divider = 0
        for score in overall_score:
            counter += float(score['score']) * float(score['names_count'])
            divider += float(score['names_count'])
        if divider == 0:
            final_score = 0
        else:
            final_score = counter / divider

        return {"semantic_score": final_score}

    # Code for improving the repository
    if type == 'improve':
        root_name = './improved_repos'

        if not os.path.exists(root_name):
            os.makedirs(root_name)

        previous_filename = None
        for idx, code in enumerate(codes):

            retries = 0
            max_retries = 3
            filename = code.metadata['file_name']

            if filename != previous_filename:
                memory.clear()
                previous_filename = filename

            while retries < max_retries:

                result = chain.run(text=text + filename + '\n\n' + str(code.page_content))
                code_blocks =result
                if code_blocks:
                    if not os.path.exists(os.path.join(root_name, repo_name)):
                        os.makedirs(os.path.join(root_name, repo_name))

                    file_path = os.path.join(root_name, repo_name, filename)

                    with open(file_path, 'a') as f:
                        f.write(code_blocks + '\n')

                    retries = max_retries
                else:
                    retries += 1
