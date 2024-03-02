import json
import os
from bs4 import BeautifulSoup

reserved_word_definitions = {
    "abstract": "Used to declare a class or method as incomplete and to be implemented by subclasses.",
    "assert": "Used to test an assumption in the code.",
    "boolean": "A data type that can have only one of two values: true or false.",
    "break": "Used to terminate the loop or switch statement and transfers control to the statement immediately following the loop or switch.",
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
    "extends": "Used to indicate that a class is derived from another class or to indicate that an interface is derived from another interface.",
    "final": "Used to restrict the user from inheriting a class, overriding a method, or modifying a variable.",
    "finally": "Used to execute important code such as closing a file or releasing resources, whether an exception is thrown or not.",
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
    "null": "A special literal that represents a null reference, meaning that the object does not point to any memory location.",
    "package": "Used to declare a package.",
    "private": "Access modifier that restricts access to members of the same class.",
    "protected": "Access modifier that restricts access to members of the same class and its subclasses, and to members of other classes in the same package.",
    "public": "Access modifier that allows unrestricted access to a class, method, or variable.",
    "return": "Used to exit from a method, with or without a value.",
    "short": "A data type that represents 16-bit signed integers.",
    "static": "Used to declare members (variables and methods) that belong to the class rather than to instances of the class.",
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
    #list for

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

            #get identifiers
            elif "variableDeclaratorId" in path and "text" in path:
                identifier_dictionary[current_node] = None

            # get package names
            elif "qualifiedName" in path and "text in path":
                if "text" in path:
                    concat_package.append(current_node)

            else:

                # print if typeSpec is not empty and typeSpec is no longer i path
                if concat_typeSpec:
                    to_string = ''.join(concat_typeSpec[::-1])


                    #add to dictionary in not already in there
                    if to_string not in reserved_word_dictionary:

                        definition = reserved_word_definitions.get(to_string, "Definition not available")
                        reserved_word_dictionary[to_string] = definition
                if concat_package:
                    to_string = ''.join(concat_package[::-1])


                    #add to dictionary in not already in there
                    if to_string not in import_dictionary:
                        import_dictionary[to_string] = None

                concat_package = []
                concat_typeSpec = []


def get_package_summary(partial_package_path, folders):
    target_file = "/package-summary.html"
    target_file2 = ".html"
    for folder in folders:
        full_package_path = folder + partial_package_path + target_file
        full_package_path2 = folder + partial_package_path + target_file2
        if os.path.exists(full_package_path):
            return full_package_path
        elif os.path.exists(full_package_path2):
            return full_package_path2
def get_folder_names (directory):
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

    #convert file name to path
    path = package_name.replace("." , "/")
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
        partial_path = to_path(package) # convert package name to path
        package_summary_path = get_package_summary(partial_path, folders) # get full path of summary

        if package_summary_path is not None:
            packages[key] = parse_html(package_summary_path)

    return packages


# Open the JSON file
with open("/Users/Kevin/IdeaProjects/AST/output.json", 'r') as file:
    # Load the JSON data from the file
    data = json.load(file)

# create dictionary of nodes of interest
node_dictionary = {'packageDeclaration': None, 'importDeclaration': None, 'classOrInterfaceModifier': None,
                   'expression': None, 'switchLabel': None, 'classDeclaration': None, 'methodDeclaration': None,
                   'statement': None}

#dictionary to store imports
import_dictionary ={}

#dictionary to store identifiers
identifier_dictionary = {}

# dictionary to store reserved words
reserved_word_dictionary = {}





# parse json
iterate_json(data)

#print dictionarys

print("--------reserved words-------")
for key, value in reserved_word_dictionary.items():
    print(f"{key}: {value}")

print("--------identifiers-------")
for key, value in identifier_dictionary.items():
    print(f"{key}: {value}")

import_dictionary = get_package_descriptions(import_dictionary)
print("--------imports-------")
for key, value in import_dictionary.items():
    print(f"{key}: {value}")