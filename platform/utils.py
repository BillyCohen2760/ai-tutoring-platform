import re
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP
from categories import *



def replace_underscores_with_spaces(input_string):
    return input_string.replace('_', ' ')

# Example usage:
# input_str = "This_is_an_example_string"
# output_str = replace_underscores_with_spaces(input_str)
# print(output_str)  # Output: "This is an example string"

# helper for clean_gpt_output
def categorize_output(output_list):
    categories = {
        "Equations Only": [],
        "Includes Instructions": [] #,
        # "Extra Lines": []
    }
    
    for item in output_list:        
        # Check if the item contains any instructional words and process the entire line
        if any(word in item.lower() for word in ['add', 'addition', 'subtract', 'subtraction', 'multiply', 'multiplication', 'divide', 'division', 'calculate', 'compute', 'what', 'evaluate', 'by', 'is', 'using', 'the', 'method', 'find', 'solution', 'determine', 'equation', 'expression', '?']) or item == '\[' or item == '\]' or item == '\(' or item == '\)':
            categories["Includes Instructions"].append(item)
        else:
            categories["Equations Only"].append(item)

        
    # categories['Extra Lines'].append((len(categories["Equations Only"]) + len(categories['Includes Instructions'])) - tot_iters*3)
    return categories

# helper for clean_gpt_output
def extract_math_expressions(text):
    # Regular expression to capture both inline and display LaTeX math expressions
    pattern = r'\\\((.*?)\\\)|\\\[(.*?)\\\]'
    
    # Find all LaTeX matches in the text
    matches = re.findall(pattern, text)

    # Collecting all math expressions; only one of the groups will have a match
    math_expressions = []
    for match in matches:
        #  Catch case where x is alone (e.g. solve for 'x' in this equation: _______)
        if ((match[0] == ' x ' or match[0] == 'x') and match[1] == '') or ((match[1] == ' x ' or match[1] == 'x') and match[0] == ''):
            continue
        # Append the non-empty group (either inline or display)
        math_expressions.append(match[0] or match[1])  

    return [expr.strip() for expr in math_expressions]

# helper for clean_gpt_output
def clean(final_equations):
    cleaned_equations = []
    
    for eq in final_equations:
        # print(eq)
        # Replace all instances of backslash followed by specific characters
        eq = eq.replace(r'\[', '').replace(r'\]', '').replace(r'\(', '').replace(r'\)', '')
        # print(eq)
        # Replace all instances of simplify:, solve: with space
        eq = re.sub(r'(?i)(simplify:|simplify|solve:|solve)', '', eq).strip()

        # Remove leading enumerations like '1.' or '2.' but NOT '3.2'
        eq = re.sub(r'^\d+\.\s+', '', eq)
        # print(eq)

        # get rid of whitespace
        eq = eq.strip()
        # print(eq)
        
        # Add the cleaned equation to the list if it's not empty after cleaning
        if eq:
            cleaned_equations.append(eq)
    
    return cleaned_equations   

def find_BAD_answers(problem, solution, customizations):
    temp_solution = str(solution)
    print('temp_solution', temp_solution)


    # print()
    # print()
    # print("find_BAD_answers", temp_solution, customizations['sqrt'])

    if customizations['sqrt'] == 'false':
        if re.search(r'sqrt\([^)]*\)', temp_solution) != None:
            print("SQRT FOUND!")
            return 'BAD'
        
    if customizations['i'] == 'false':
        if 'i' in temp_solution:
            print("IMAGINARY FOUND!")
            return 'BAD'
        
    if temp_solution == '[\'No results found.\']' or temp_solution == '[\'(no solutions exist)\']':
        return 'BAD'

    return solution

def validate(problems, solutions, customizations):
    for i, (problem, solution) in enumerate(zip(problems, solutions)):
        solutions[i] = find_BAD_answers(problem, solution, customizations)
        
    # print("bad Problems:", problems)
    # print("bad Solutions:", solutions)


    # filter out bad answers
    problems_filtered = [problem for problem, solution in zip(problems, solutions) if solution != 'BAD']
    solutions_filtered = [solution for solution in solutions if solution != 'BAD']

    # Print the filtered arrays
    print("Filtered Problems:", problems_filtered)
    print("Filtered Solutions:", solutions_filtered)

    return problems_filtered, solutions_filtered

# cleans gpt output to take away brackets, enumerations, etc.
def clean_gpt_output(gpt_output, customizations):
    all_outputs = []
    output_list = [line.strip() for line in gpt_output.split('\n') if line.strip() != '']
    all_outputs.extend(output_list)

    categories = categorize_output(all_outputs)

    # for category in categories:
    #     print(category, ":", len(categories[category])) #, category.size())

    # print('Extra Lines:', (len(categories['Equations Only']) + len(categories['Includes Instructions'])) - 3*tot_iters)


    # print()
    # print('Final Equations:', categories['Equations Only'])
    # print('Equations to remedy:', categories['Includes Instructions'])
    updated_eqs = []
    for eq in categories['Includes Instructions']:
        extracted_equation = extract_math_expressions(eq)
        # undo if there is no equation
        # print('extracted_equation', extracted_equation)
        if (extracted_equation == []):
            # print(eq)
            updated_eqs.append(eq)
        updated_eqs.extend(extracted_equation)
        # print(extracted_equation)
        

    # print('updated equations:', updated_eqs)

    # print()
    # print("UPDATED CATEGORIES")
    categories_remedy = categorize_output(updated_eqs)

    # for category in categories_remedy:
    #     print(category, ":", len(categories_remedy[category])) #, category.size())
        # print(categories_remedy[category])
    
        

    final_equations = []

    final_equations.extend(categories['Equations Only'])
    final_equations.extend(categories_remedy['Equations Only'])
    # print(final_equations)
    final_equations = clean(final_equations) # FOCUS ON THIS!!!!!!!!    
    
    # print(final_equations)
    # print()
    # print("FINAL EQUATIONS")
    for equation in final_equations:
        print(equation)

    # print(final_equations)

    print(final_equations)
    print(list(set(final_equations)))
    return list(set(final_equations))

def answer_to_coordinates(answer):
    """
    Extracts numerical values for x and y from a list containing a string in the format 
    'x = <value> and y = <value>', where <value> can be an integer or a fraction, 
    and returns a list with the coordinates as a string "(x, y)".
    """
    # Initialize an empty list to store the results
    result_list = []
    
    # Assume the list contains one string element.
    answer_str = answer[0]  # Extract the string from the list
    
    # Split the input string by " and " to separate the x and y parts
    parts = answer_str.split(' and ')
    
    # Extract x and y values by splitting each part by "=" and stripping extra spaces
    x_value = parts[0].split('=')[1].strip()
    y_value = parts[1].split('=')[1].strip()

    # Format the result and append it to the list
    result_list.append(f"({x_value}, {y_value})")
    
    # Return the list containing the result
    return result_list

def string_to_normal(solution):
    return tuple(solution)

def expand_pm(answer):
    """
    Expands expressions with '±' into separate positive and negative values.
    
    Parameters:
        expression (list): A list containing a string with a '±' symbol.
        
    Returns:
        list: A list of strings with separate positive and negative values.
    """
    # Extract the string from the list
    input_str = answer[0]
    
    # Check if the string contains the '±' symbol
    if '±' in input_str:
        # Split the string into the part before and after the '±'
        before_pm, after_pm = input_str.split('±')
        before_pm = before_pm.strip()
        after_pm = after_pm.strip()
        
        # Check if the part before ± is just "x =" or has more
        if before_pm.endswith('='):
            # If it ends with "=", drop the "+"
            return [f"{before_pm} {after_pm}", f"{before_pm} -{after_pm}"]
        else:
            # Otherwise, include "+" and "-" for the ±
            return [f"{before_pm} + {after_pm}", f"{before_pm} - {after_pm}"]
    else:
        # If no '±', return the input as-is
        return answer

def format_answer(answer, prob_type, num_decimal_places):
    print("Initial answer:", answer)

    if "±" in str(answer):
        solution =  expand_pm(answer)
    
    if prob_type == "System Of Equations":
        solution = answer_to_coordinates(answer)
        # answer = string_to_normal(answer)
        # print(answer)

    elif prob_type == "Evaluating Decimals":
        rounded_numbers = []

        for num in answer:
            try:
                # Convert to Decimal
                decimal_value = Decimal(num)
                
                # Define the rounding precision
                precision = Decimal('1.' + '0' * num_decimal_places)
                
                # Round the value and append to the result
                rounded_numbers.append(str(decimal_value.quantize(precision, rounding=ROUND_HALF_UP)))
            except Exception as e:
                # Handle any conversion errors
                print(f"Error processing '{num}': {e}")
                rounded_numbers.append('Invalid number')
        solution = rounded_numbers

    else:
        solution = answer

    if prob_type in simplifying_expressions:
        solution = solution[0]
        solution = [solution]
    print("Final solution:", solution)
    return solution

# Create the prompt based on type of problem. Will eb solve or simply type of problem
def create_prompt(problem, prob_type):
    if prob_type in simplifying_expressions:
        prompt = f"Simplify {problem}"
    else:
        prompt = f"Solve {problem}"
    return prompt

