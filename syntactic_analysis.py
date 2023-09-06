import re
import unittest
from nltk.corpus import words
from wordsegment import load, segment
from nltk.stem import WordNetLemmatizer

# Create a set of English words for later use
english_words = set(words.words())
load()
lemmatizer = WordNetLemmatizer()
# Function to split a compound word into its constituents
def split_compound_word(word):
    word = word.lower()

    word = lemmatizer.lemmatize(word)
    split_words = segment(word)
    return split_words

# Define the PEP 8 naming conventions for different types of identifiers
pep8_naming_conventions = {
    "function": r"^[a-z_][a-z0-9_]{0,30}$",
    "class": r"^[A-Z][a-zA-Z0-9]{0,30}$",
    "variable": r"^[a-z_][a-z0-9_]{0,30}$",
    "constant": r"^[A-Z_][A-Z0-9_]{0,30}$",
}

# Function to check if a given name is conformant with a given type of PEP 8 naming convention
def is_name_conformant(name, name_type):
    pattern = pep8_naming_conventions.get(name_type)
    if not pattern:
        raise ValueError(f"Invalid name type: {name_type}")
    if not re.match(pattern, name):
        return False
    # Special case for function names, variable names, and constant names: check if the name is a compound word
    if name_type in ["function", "variable", "constant"]:
        parts = name.split('_')
        for part in parts:
            if len(split_compound_word(part)) > 1 and len(part) >= 7:
                return False
    return True


# Define a set of unit tests to check the correctness of the is_name_conformant function
class TestPep8Conventions(unittest.TestCase):
    # Test cases for class names
    def test_class_name(self):
        self.assertTrue(is_name_conformant("MyClass", "class"))
        self.assertTrue(is_name_conformant("Names", "class"))
        self.assertFalse(is_name_conformant("my_class", "class"))
        self.assertFalse(is_name_conformant("myclass", "class"))
        self.assertFalse(is_name_conformant("My_Class", "class"))
        self.assertFalse(is_name_conformant("myClass", "class"))
        self.assertFalse(is_name_conformant("my_Class", "class"))

    # Test cases for function names
    def test_function_name(self):
        self.assertTrue(is_name_conformant("parse_streams", "function"))
        self.assertTrue(is_name_conformant("streams", "function"))
        self.assertFalse(is_name_conformant("myFunction", "function"))
        self.assertFalse(is_name_conformant("MyFunction", "function"))
        self.assertFalse(is_name_conformant("my-function", "function"))
        self.assertFalse(is_name_conformant("myfunction", "function"))
        self.assertFalse((is_name_conformant("my_functiontwo", "function")))
        self.assertFalse((is_name_conformant("My_Functiontwo", "function")))

    # Test cases for variable names
    def test_variable_name(self):
        self.assertTrue(is_name_conformant("my_variable", "variable"))
        self.assertTrue(is_name_conformant("req", "variable"))
        self.assertFalse(is_name_conformant("HTTP_message", "variable"))
        self.assertFalse(is_name_conformant("myVariable", "variable"))
        self.assertFalse(is_name_conformant("MyVariable", "variable"))
        self.assertFalse(is_name_conformant("my-variable", "variable"))
        self.assertFalse(is_name_conformant("myvariable", "variable"))

    # Test cases for constant names
    def test_constant_name(self):
        self.assertTrue(is_name_conformant("MY_CONSTANT", "constant"))
        self.assertFalse(is_name_conformant("my_constant", "constant"))
        self.assertFalse(is_name_conformant("MyConstant", "constant"))
        self.assertFalse(is_name_conformant("MY-CONSTANT", "constant"))
        self.assertFalse(is_name_conformant("MYCONSTANT", "constant"))
        self.assertFalse(is_name_conformant("MY_constant", "constant"))



# Run the unit tests
if __name__ == "__main__":
    unittest.main()

