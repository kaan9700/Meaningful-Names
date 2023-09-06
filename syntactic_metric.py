from preprocessing_syntactic import analyze_repository
from syntactic_analysis import is_name_conformant



# Function to calculate metrics based on the conformity of naming in the code
def calc_metrik(names_dict):
    total_names = 0  # Counter for the total number of names
    total_conformant_names = 0  # Counter for the total number of conformant names
    # Dictionary to hold non-conformant names categorized by their type
    non_conformant_names = {
        "function": [],
        "class": [],
        "variable": [],
        "constant": []
    }

    # Loop through each name type (function, class, variable, constant)
    for name_type, names in names_dict.items():
        total_names += len(names)  # Add the count of names to total_names
        # Check each name's conformity and categorize accordingly
        for name in names:
            if is_name_conformant(name, name_type):
                total_conformant_names += 1
            else:
                non_conformant_names[name_type].append(name)

    # Calculate the metric for conformant names
    metric = total_conformant_names / total_names if total_names > 0 else 0
    return metric, non_conformant_names

# Function to summarize the results from multiple analyses into a single result
def summarize_results(results):
    # Dictionary to hold all the names categorized by their type
    all_names = {
        "function": [],
        "class": [],
        "variable": [],
        "constant": []
    }
    # Loop through each result to extend the lists in the all_names dictionary
    for result in results:
        for name_type in all_names.keys():
            all_names[name_type].extend(result.get(name_type, []))
    return all_names

# Function to rate the repository's syntactic naming conformity
def rate_repository_syntactic(repo_name, type):
    # Analyze the repository and get initial results
    results = analyze_repository(repo_name, type)
    # Summarize the results into a single result set
    summary = summarize_results(results)
    # Calculate the metric and get non-conformant names
    metric, non_conformant_names = calc_metrik(summary)
    return {'syntactic_score': metric}  # Return the syntactic score as a dictionary

