import json
import os
from bs4 import BeautifulSoup
import openai
import gensim.downloader as api
import psycopg2

word2vec_model = api.load('word2vec-google-news-300')

openai.api_key = 'sk-proj-kZwhxcdUcEQcryaE5PmUT3BlbkFJpNZ45ZGYzvqqA6BOXWW5'
# Function to categorize text using OpenAI


def split_compound_word(word):
    # Check if the compound word is present in the model's vocabulary
    if word in word2vec_model.key_to_index:
        return [word]  # If present, return the word as it is
    else:
        # Split the compound word into constituent words based on camel case or spaces
        constituent_words = []
        start_idx = 0
        for idx, char in enumerate(word):
            if char.isupper() or char == ' ' or char == '_':
                if start_idx != idx:
                    constituent_words.append(word[start_idx:idx])
                start_idx = idx
        # Add the last word
        constituent_words.append(word[start_idx:])
        return constituent_words


# Function to split multi-word labels into constituent words
def split_multi_word_label(label):
    return label.split()


# Precompute similarity scores between class names and labels
def precompute_similarities(class_names, labels):
    similarities_cache = {}
    for class_name in class_names:
        similarities_cache[class_name] = {}
        for label in labels:
            if all(word in word2vec_model.key_to_index for word in [class_name, label]):  # Check if both class name and label exist in the model's vocabulary
                # If label is a compound word, split it into constituent words
                label_words = split_multi_word_label(label)
                total_similarity = 0.0
                for word in label_words:
                    class_words = split_compound_word(class_name)
                    # Check if all class words exist in the model's vocabulary
                    if all(class_word in word2vec_model.key_to_index for class_word in class_words):
                        total_similarity += max([word2vec_model.similarity(word, class_word) for class_word in class_words])
                if total_similarity > 0:
                    similarity = total_similarity / len(label_words)  # Average similarity for constituent words
                else:
                    similarity = 0.0  # Assign a default similarity score if no word found in the model's vocabulary
                similarities_cache[class_name][label] = similarity
            else:
                similarities_cache[class_name][label] = 0.0  # Assign a default similarity score if class name or label not found
    return similarities_cache


def compute_similarity(class_name, labels):
    similarities_cache = {}
    for label in labels:
        if all(word in word2vec_model.key_to_index for word in [class_name, label]):  # Check if both class name and label exist in the model's vocabulary
            # If label is a compound word, split it into constituent words
            label_words = split_multi_word_label(label)
            total_similarity = 0.0
            for word in label_words:
                class_words = split_compound_word(class_name)
                # Check if all class words exist in the model's vocabulary
                if all(class_word in word2vec_model.key_to_index for class_word in class_words):
                    total_similarity += max([word2vec_model.similarity(word, class_word) for class_word in class_words])
            if total_similarity > 0:
                similarity = total_similarity / len(label_words)  # Average similarity for constituent words
            else:
                similarity = 0.0  # Assign a default similarity score if no word found in the model's vocabulary
            similarities_cache[label] = similarity
        else:
            similarities_cache[label] = 0.0  # Assign a default similarity score if class name or label not found
    return similarities_cache



def categorize_text(message):
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages= message,
        temperature=0.0,
    )
    return response.choices[0].message["content"]


delimiter= '#####'
system_messages = f''' You will be provided with a Java class name. 
The query will be limited with {delimiter} characters Then classify each class name in any of the 31 different types, 
it must be the best fit. Ensure that your response consists of only the one label, no other words. Types: 
Application, Application Performance Manager, Big Data, Cloud, Computer Graphics, Data Structure, Databases, 
Software Development and IT Operation, Error Handling, Event Handling, Geographic Information System Input-Output, 
Interpreter, Internationalization, Logic, Language, Logging, Machine Learning, Microservices/ Services, Multimedia, 
Multi-Thread, Natural Language Processing, Network, Operation System, Parser, Search, Security, Setup, 
User Interface, Utility, Test. '''
summary_messages = f'''You will be provided with a Java method and its description as noted in Java documentation, 
if the description is "not found" find the description for that method. The query will be limited with {delimiter} 
characters, 
summarize the description and output in the format of " 'method': 'summarized description'" '''

function_labeled = f''' You will be provided with a Java function name. 
The query will be limited with {delimiter} characters
Then classify each class name in any of the 31 different types, it must be the best fit. 
Types: Application, Application Performance Manager, Big Data, Cloud, Computer Graphics, Data Structure,
Databases, Software Development and IT Operation, Error Handling, Event Handling, Geographic Information System
Input-Output, Interpreter, Internationalization, Logic, Language, Logging, Machine Learning, 
Microservices/ Services, Multimedia, Multi-Thread, Natural Language Processing, Network, 
Operation System, Parser, Search, Security, Setup, User Interface, Utility, Test. 
Only output the function label, no yapping '''

reserved_word_definitions = {
    "abstract": "Used to declare a class or method as incomplete and to be implemented by subclasses.",
    "assert": "Used to test an assumption in the code.",
    "boolean": "A data type that can have only one of two values: true or false.",
    "break": "Used to terminate the loop or switch statement and transfers control to the statement immediately "
             "following the loop or switch.",
    "byte": "A data type that represents 8-bit signed two's complement integers.",
    "case": "Used in switch statements to specify a block of code to be executed.",
    "catch": "Used to handle exceptions that are thrown by the try block.",
    "char": "A data type that represents a single 16-bit Unicode character.",
    "class": "Used to declare a class.",
    "const": "Not used in modern Java; reserved for future use.",
    "continue": "Used to skip the current iteration of a loop and proceed to the next iteration.",
    "default": "Used in switch statements to specify the default block of code to be executed.",
    "do": "Used to start a do-while loop.",
    "double": "A data type that represents double-precision 64-bit floating-point numbers.",
    "else": "Used to specify a block of code to be executed if the condition in the if statement is false.",
    "enum": "A data type that consists of a set of predefined constants.",
    "extends": "Used to indicate that a class is derived from another class or to indicate that an interface is "
               "derived from another interface.",
    "final": "Used to restrict the user from inheriting a class, overriding a method, or modifying a variable.",
    "finally": "Used to execute important code such as closing a file or releasing resources, whether an exception is "
               "thrown or not.",
    "float": "A data type that represents single-precision 32-bit floating-point numbers.",
    "for": "Used to create a loop that executes a block of code a specified number of times.",
    "if": "Used to execute a block of code if a specified condition is true.",
    "implements": "Used to declare that a class implements an interface.",
    "import": "Used to import a package, class, or interface.",
    "instanceof": "Used to test whether an object is an instance of a specified class or interface.",
    "int": "A data type that represents 32-bit signed integers.",
    "interface": "Used to declare an interface.",
    "long": "A data type that represents 64-bit signed integers.",
    "native": "Used to indicate that a method is implemented in native code using JNI (Java Native Interface).",
    "new": "Used to create new objects.",
    "null": "A special literal that represents a null reference, meaning that the object does not point to any memory "
            "location.",
    "package": "Used to declare a package.",
    "private": "Access modifier that restricts access to members of the same class.",
    "protected": "Access modifier that restricts access to members of the same class and its subclasses, "
                 "and to members of other classes in the same package.",
    "public": "Access modifier that allows unrestricted access to a class, method, or variable.",
    "return": "Used to exit from a method, with or without a value.",
    "short": "A data type that represents 16-bit signed integers.",
    "static": "Used to declare members (variables and methods) that belong to"
              " the class rather than to instances of the class.",
    "strictfp": "Used to restrict floating-point calculations to ensure portability across platforms.",
    "super": "Used to refer to the immediate superclass of a class.",
    "switch": "Used to specify multiple execution paths based on a variable's value.",
    "synchronized": "Used to control access to shared resources by multiple threads.",
    "this": "Used to refer to the current instance of the class.",
    "throw": "Used to explicitly throw an exception.",
    "throws": "Used to declare the exceptions that a method might throw.",
    "transient": "Used to indicate that a field should not be serialized.",
    "try": "Used to start a block of code that might throw an exception.",
    "void": "A data type that represents the absence of a value.",
    "volatile": "Used to indicate that a variable's value will be modified by different threads.",
    "while": "Used to create a loop that executes a block of code as long as a specified condition is true."
}


def iterate_json(json_data):
    # create stack to keep track of position

    stack = [(json_data, [], None)]

    # list for typeSpec case and package/import case
    concat_typeSpec = []
    concat_package = []
    # list for

    # loop until stack is empty
    while stack:
        current_node, path, parent = stack.pop()

        # go through dictionary
        if isinstance(current_node, dict):
            for key, value in current_node.items():
                stack.append((value, path + [key], current_node))

        # go through list
        elif isinstance(current_node, list):
            for index, item in enumerate(current_node):
                stack.append((item, path + [index], current_node))

        else:
            if "text" in path:
                text_list.insert(0, current_node)

            # get the first text from nodes in our dictionary
            path_length = len(path)
            if (path[path_length - 3] in node_dictionary and path[path_length - 2] == 0 and path[
                    path_length - 1] == 'text'):

                # add word to dictionary if its not already in there
                if current_node not in reserved_word_dictionary:
                    definition = reserved_word_definitions.get(current_node, "Definition not available")
                    reserved_word_dictionary[current_node] = definition

            # concat all text within typeSpec
            elif "typeSpec" in path:

                if "text" in path:
                    concat_typeSpec.append(current_node)

            # get identifiers
            elif "variableDeclaratorId" in path and "text" in path:
                identifier_dictionary[current_node] = None

            # get package names
            elif "TypeName" and "importDeclaration" in path or "packageDeclaration" in path:
                if "text" in path:
                    concat_package.append(current_node)

            else:

                # print if typeSpec is not empty and typeSpec is no longer i path
                if concat_typeSpec:
                    to_string = ''.join(concat_typeSpec[::-1])

                    # add to dictionary in not already in there
                    if to_string not in reserved_word_dictionary:
                        definition = reserved_word_definitions.get(to_string, "Definition not available")
                        reserved_word_dictionary[to_string] = definition
                if concat_package:
                    to_string = ''.join(concat_package[::-1])
                    curr_string = ''
                    for i in range(len(to_string)):
                        if to_string[i] == ';':
                            if curr_string not in import_dictionary:
                                import_dictionary[curr_string] = None
                            curr_string = ""
                        else:
                            curr_string += to_string[i]
                            if curr_string == ("import" or "package"):
                                curr_string = ""

                concat_package = []
                concat_typeSpec = []
    if concat_package:
        to_string = ''.join(concat_package[::-1])
        curr_string = ''
        for i in range(len(to_string)):
            if to_string[i] == ';':
                if curr_string not in import_dictionary:
                    import_dictionary[curr_string] = None
                curr_string = ""
            else:
                curr_string += to_string[i]
                if curr_string == ("import" or "package"):
                    curr_string = ""


def get_package_summary(partial_package_path, folders):
    target_file = ".html"
    for folder in folders:
        full_package_path = folder + partial_package_path + target_file
        if os.path.exists(full_package_path):
            return full_package_path


def get_folder_names(directory):
    folder_names = []

    # List items in directory
    items = os.listdir(directory)

    # append folder name if path exists
    for item in items:
        path = directory + "/" + item + "/"
        if os.path.isdir(path):
            folder_names.append(path)

    return folder_names


def to_path(package_name):
    # convert file name to path
    path = package_name.replace(".", "/")
    return path


def parse_html(file_path):
    # read html
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")  # use BeatifulSoup to parse html

    # Initialize an empty string to store parsed text
    parsed_text = ""

    # Find all text elements
    for text in soup.stripped_strings:
        count = 0

        parsed_text += text + " "  # Add space between text elements

        # Check if the keyword "Since" is in the parsed text
        if "Since" in parsed_text:
            return parsed_text.strip()  # If found, stop parsing
        elif "Related Packages" in parsed_text:
            count = count + 1
            if count == 3:
                return parsed_text.strip()  # If found, stop parsing
        elif "All Classes and Interfaces" in parsed_text:
            return parsed_text.strip()  # If found, stop parsing

    return parsed_text.strip()  # Return parsed text, removing leading/trailing spaces


def get_package_descriptions(packages):
    # get root directory and folder names within directory
    directory = "packages"
    folders = get_folder_names(directory)

    # find the summary of each package in the dictionary
    for key in packages:

        package = key
        partial_path = to_path(package)  # convert package name to path
        package_summary_path = get_package_summary(partial_path, folders)  # get full path of summary
        last_part = key.split(".")[-1]
        if "slf4j" in key:
            package_summary_path = directory + "/slf4j/" + last_part + ".html"
        if last_part not in class_names:
            class_names[last_part] = package_summary_path

        if package_summary_path is not None:
            packages[key] = parse_html(package_summary_path)

    return packages


def get_function_description(path_and_fragment):
    path = path_and_fragment[0]
    fragment = path_and_fragment[1]

    # Read the HTML content from the file
    with open(path, "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the element corresponding to the fragment identifier "#nextInt()"
    element = soup.find(id=fragment)

    # Extract and print the text content of the element
    if element:
        fragment_text = element.get_text()

        # Find the index of the first occurrence of two consecutive newline characters
        empty_line_index = fragment_text.find('\n\n')

        # If two consecutive newline characters are found, extract the substring up to that index
        if empty_line_index != -1:
            output_string = fragment_text[:empty_line_index]
        else:
            # If two consecutive newline characters are not found, output the entire input string
            output_string = fragment_text

        return output_string
    else:
        return "not found"


def print_dict_keys(my_dict):
    """Prints the keys of a dictionary."""
    for key in my_dict.keys():
        print(key)


def print_dict(my_dict):
    for key, value in my_dict.items():
        print("key:", key, "value:", value )


def find_full_import(class_name):
    for key in import_dictionary:
        if key.split('.')[-1] == class_name:
            return key


def get_functions(text_list):
    class_identifiers = {}
    functions = {}
    for i in range(len(text_list)):
        if text_list[i] in class_names:
            if text_list[i + 2] == "=":
                class_identifiers[text_list[i + 1]] = find_full_import(text_list[i])

            elif text_list[i + 1] == ".":
                functions[text_list[i + 2]] = find_full_import(text_list[i])

            elif text_list[i + 1] == "<":
                class_identifiers[text_list[i + 4]] = find_full_import(text_list[i])

            else:
                class_identifiers[text_list[i + 1]] = find_full_import(text_list[i])

        if text_list[i] in class_identifiers:
            if text_list[i + 1] == ".":
                functions[text_list[i+2]] = class_identifiers[text_list[i]]
    print("class identifiers:", print(class_identifiers))
    return functions


def populate_api_table(api_dictionary, cursor):

    insert_api_query = '''
    INSERT INTO _API (api_name, api_context, llm_expert, sim_expert)
    VALUES (%s, %s, %s, %s)
    '''
    for key, value in api_dictionary.items():
        # context chat sim
        values = (key, value[0], value[1], value[2])
        cursor.execute(insert_api_query, values)


def populate_function_table(function_dictionary, cursor):

    insert_function_query = '''
    INSERT INTO function (function_name, function_topic, llm_expert, sim_expert)
    VALUES (%s, %s, %s, %s)
    '''

    for key, value in function_dictionary.items():
        values = (key, value[0], value[1], value[2])
        cursor.execute(insert_function_query, values)


def populate_api_specific_table(api_specific_dictionary, cursor):

    insert_api_function_query = '''
    INSERT INTO API_function (api_name_fk, function_name_fk)
    VALUES (%s, %s)
    '''

    for key, value in api_specific_dictionary.items():
        values = (value, key)
        cursor.execute(insert_api_function_query, values)

# Function to parse .env file
def parse_env_file():
    env_vars = {}
    with open("env", "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def connect_to_database():
    # Load environment variables from .env file
    env_vars = parse_env_file()

    # Get database credentials from environment variables
    db_name = env_vars["DB_NAME"]
    db_user = env_vars["DB_USER"]
    db_password = env_vars["DB_PASSWORD"]
    db_host = env_vars["DB_HOST"]
    db_port = env_vars["DB_PORT"]

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    return conn


# create dictionary of nodes of interest
node_dictionary = {'packageDeclaration': None, 'importDeclaration': None, 'classOrInterfaceModifier': None,
                   'expression': None, 'switchLabel': None, 'classDeclaration': None, 'methodDeclaration': None,
                   'statement': None}

# dictionary to store imports
import_dictionary = {}

# dictionary to store class names and path to html
class_names = {}

# dictionary to store identifiers
identifier_dictionary = {}

# dictionary to store reserved words
reserved_word_dictionary = {}

# create a list to store text
text_list = []

# Assuming you have labels 'database' and 'big data'
labels = [
    'Application',
    'Application Performance Manager',
    'Big Data',
    'Cloud',
    'Computer Graphics',
    'Data Structure',
    'Databases',
    'Software Development and Information Technology Operations',
    'Error Handling',
    'Event Handling',
    'Geographic Information System',
    'Input Output',
    'Interpreter',
    'Internationalization',
    'Logic',
    'Language',
    'Logging',
    'Machine Learning',
    'Microservices Services',
    'Multimedia',
    'Multi Thread',
    'Natural Language and Processing',
    'Network',
    'Operating System',
    'Parser',
    'Search',
    'Security',
    'Setup',
    'User Interface',
    'Utility',
    'Test'
]

api_table = {}
function_table = {}
api_function_table = {}

file_path = "input.json"
# Read the JSON file
with open(file_path, "r") as json_file:
    data = json.load(json_file)

# Extract the list of JSON file paths
json_files = data.get("json_files", [])

for json_file in json_files:

    with open(json_file, 'r') as file:
        # Load the JSON data from the file
        data = json.load(file)

    # parse json
    iterate_json(data)

    import_dictionary = get_package_descriptions(import_dictionary)
    print("--------imports-------")
    for key, value in import_dictionary.items():
        if key not in api_table:
            class_name = key.split(".")[-1]

            if class_name in word2vec_model.key_to_index:
                # Compute similarity scores using cached results
                similarities = compute_similarity(class_name, labels)
                # Choose the label with the highest similarity score
                most_similar_label = max(similarities, key=similarities.get)
            else:
                most_similar_label = "word does not exist in word2vec model"

            result_string = ""
            result_string += f"{key}: {value}\n"
            message = [
                {'role': 'system',
                 'content': system_messages},
                {'role': 'user',
                 'content': f'{delimiter}{class_name}{delimiter}'}
            ]
            response = categorize_text(message)
            api_table[key] = [value, response, most_similar_label]

    functions = get_functions(text_list)

    print("--------functions-------")
    for key, value in functions.items():
        if key not in api_function_table:
            api_function_table[key] = value
        if key not in function_table:
            result_string = ""
            result_string += f"{key}: {value}\n"
            summary_message = [
                {'role': 'system',
                 'content': summary_messages},
                {'role': 'user',
                 'content': f'{delimiter}{result_string}{delimiter}'}
            ]

            description = categorize_text(summary_message)

            result_string = ""
            result_string += f"{key}: {value}\n"
            summary_message = [
                {'role': 'system',
                 'content': function_labeled},
                {'role': 'user',
                 'content': f'{delimiter}{result_string}{delimiter}'}
            ]
            llm_label = categorize_text(summary_message)

            # Compute similarity scores using cached results
            similarities = compute_similarity(class_name, labels)
            # Choose the label with the highest similarity score
            most_similar_label = max(similarities, key=similarities.get)

            function_table[key] = [description, llm_label, most_similar_label]
    # dictionary to store imports
    import_dictionary = {}

    # dictionary to store class names and path to html
    class_names = {}

    # create a list to store text
    text_list = []

print("------api table------")
print_dict(api_table)
print("------function table------")
print_dict(function_table)
print("-----api function specific------")
print_dict(api_function_table)

conn = connect_to_database()
cursor = conn.cursor()

populate_api_table(api_table, cursor)
populate_function_table(function_table, cursor)
populate_api_specific_table(api_function_table, cursor)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cursor.close()
conn.close()