import re # Regular Expressions Documentation used (https://www.w3schools.com/python/python_regex.asp)
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP
from categories import *
from services.gpt_service import GPT_response


# For clarity in code
def replace_underscores_with_spaces(input_string):
    return input_string.replace('_', ' ')

# helper for clean_gpt_output, used for testing
def categorize_output(output_list):
    categories = {
        "Equations Only": [],
        "Includes Instructions": [] #,
        # "Extra Lines": []
    }
    
    for item in output_list:        
        # Check if the item contains any instructional words and process the entire line
        if any(word in item.lower() for word in ['add', 'addition', 'subtract', 'subtraction', 'multiply', 'multiplication', 'divide', 'division', 'calculate', 'compute', 'for', 'what', 'evaluate', 'by', 'is', 'using', 'the', 'method', 'find', 'solution', 'determine', 'equation', 'expression', '?']) or item == '\[' or item == '\]' or item == '\(' or item == '\)':
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



# Filter out "BAD" problems according to user customizations
def find_BAD_problems(problem, customizations):
    temp_problem = str(problem)
    print('temp_problem', temp_problem)

        
    # if customizations['problem_topic'] == 'Combining_Like_Terms':
    #     print("CLT")
    #     if '.' in temp_problem:
    #         print("DECIMAL FOUND")
    #         return 'BAD'
    
    # Make sure a, b, c, values are correct.
    if customizations['problem_type'] == 'Solving_Quadratic_Equations':
        a, b, c = extract_coefficients(temp_problem)
        print("a, b, c", a, b, c)

        if 'a = 1' in customizations['abc'] and a != 1:
            return 'BAD'
        
        if 'b = 0' in customizations['abc'] and b != 0:
            return 'BAD'
        
        if 'c = 0' in customizations['abc'] and c != 0:
            return 'BAD'
        
    # Make sure the signs of the problems match the name (i.e. no division in multiplciation problems)
    if customizations['problem_type'] == 'Evaluating_Fractions' or customizations['problem_type'] == 'Evaluating_Decimals':
        if customizations['problem_topic'] == 'Using_Addition':
            print("EVALUATING FRACTIONS", temp_problem)
            if (' - ' in temp_problem and '(-' not in temp_problem) or 'times' in temp_problem or 'div' in temp_problem:
                return 'BAD'
        if customizations['problem_topic'] == 'Using_Subtraction':
            print("EVALUATING FRACTIONS", temp_problem)
            if '+' in temp_problem or 'times' in temp_problem or 'div' in temp_problem:
                return 'BAD'
        if customizations['problem_topic'] == 'Using_Multiplication':
            print("EVALUATING FRACTIONS", temp_problem)
            if (' - ' in temp_problem and '(-' not in temp_problem) or '+' in temp_problem or 'div' in temp_problem:
                return 'BAD'
        if customizations['problem_topic'] == 'Using_Division':
            print("EVALUATING FRACTIONS", temp_problem)
            if (' - ' in temp_problem and '(-' not in temp_problem) or 'times' in temp_problem or '+' in temp_problem:
                return 'BAD'
            
    # Check number of terms
    if customizations['problem_topic'] in num_terms_problems or customizations['problem_type'] in num_terms_problems:
        print("CHECK NUM TERMS")
        if count_terms(temp_problem) != customizations['num_terms']:
            return 'BAD'
        
    # if all good, then return the problem.
    return problem

# Validate problems to ensure they don't violate user customizations. If they do, they are discarded
def validate_problems(problems, customizations):
    problems_filtered = []
    # problems.append('''\\frac{4}{10} - \\frac{3}{10}''') TEST!!!!
    for problem in problems:
        print("PROBLEM", problem)
        problem = find_BAD_problems(problem, customizations)
        print("PROBLEM:", problem)
        if problem != 'BAD':
            problems_filtered.append(problem)
    
    # problems_filtered = [problem for problem in problems if problem != 'BAD']
    print("FILTERED PROBLEMS:", problems_filtered)
    return problems_filtered







# find coefficients and constants in ax^2 + bx + c for validation
def extract_coefficients(equation):
    # Remove spaces for consistent processing
    equation = equation.replace(" ", "")
    
    # Remove the "= 0" part, if present
    if "=" in equation:
        equation = equation.split("=")[0]
    
    # Regular expressions to match coefficients
    a_match = re.search(r"([+-]?\d*)x\^2", equation)
    b_match = re.search(r"([+-]?\d*)x(?!\^)", equation)
    c_match = re.search(r"([+-]?\d+)$", equation)  # Match the constant at the end of the string
    
    # Extract and convert coefficients to integers
    # a coefficient (x^2 term)
    a = int(a_match.group(1)) if a_match and a_match.group(1) not in ["", "+", "-"] else (1 if "x^2" in equation and (not a_match.group(1) or a_match.group(1) == "+") else -1)
    
    # b coefficient (x term)
    b = int(b_match.group(1)) if b_match and b_match.group(1) not in ["", "+", "-"] else (0 if b_match is None else (1 if b_match.group(1) == "+" else -1))
    
    # c coefficient (constant term)
    c = int(c_match.group(1)) if c_match else 0
    
    return a, b, c


# Count number of terms in problem (to ensure they are as many as specified by the user)
def count_terms(temp_problem):
    # Regular expression to match terms in LaTeX expressions.
    # This includes numbers, fractions, and anything between operators.
    terms = re.findall(r'(?:[+-]?\d*\.?\d+|\\frac\{[^}]+\}\{[^}]+\}|\{[^}]+\})', temp_problem)
    
    # Filter out empty strings that may occur due to malformed LaTeX or extraneous spaces.
    terms = [term for term in terms if term.strip()]

    print('TERMS:', terms, len(terms))
    
    return len(terms)







# Filter out "BAD" answers according to user customizations
def find_BAD_answers(problem, solution, customizations):
    temp_solution = str(solution)
    temp_problem = str(problem)
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
        
    if customizations['negative'] == 'false':
        if '-' in temp_solution: 
            print("NEGATIVE FOUND!")
            return 'BAD'
        
    if customizations['problem_topic'] == 'Combining_Like_Terms':
        print("CLT")
        if '.' in temp_problem:
            print("DECIMAL FOUND")
            return 'BAD'

    if temp_solution == '[\'No results found.\']' or temp_solution == '[\'(no solutions exist)\']':
        return 'BAD'
    
    if customizations['problem_type'] == 'Solving_Quadratic_Equations':
        a, b, c = extract_coefficients(temp_problem)
        print("a, b, c", a, b, c)

        if 'a = 1' in customizations['abc'] and a != 1:
            return 'BAD'
        
        if 'b = 0' in customizations['abc'] and b != 0:
            return 'BAD'
        
        if 'c = 0' in customizations['abc'] and c != 0:
            return 'BAD'
        
    # if customizations['problem_type'] == 'Evaluating_Fractions' or customizations['problem_type'] == 'Evaluating_Decimals':
    #     if customizations['problem_topic'] == 'Using_Addition':
    #         print("EVALUATING FRACTIONS", temp_problem)
    #         if '-' in temp_problem or 'times' in temp_problem or 'div' in temp_problem:
    #             return 'BAD'
    #     if customizations['problem_topic'] == 'Using_Subtraction':
    #         print("EVALUATING FRACTIONS", temp_problem)
    #         if '+' in temp_problem or 'times' in temp_problem or 'div' in temp_problem:
    #             return 'BAD'
    #     if customizations['problem_topic'] == 'Using_Multiplication':
    #         print("EVALUATING FRACTIONS", temp_problem)
    #         if '-' in temp_problem or '+' in temp_problem or 'div' in temp_problem:
    #             return 'BAD'
    #     if customizations['problem_topic'] == 'Using_Division':
    #         print("EVALUATING FRACTIONS", temp_problem)
    #         if '-' in temp_problem or 'times' in temp_problem or '+' in temp_problem:
    #             return 'BAD'
            
    # Check number of terms
    if customizations['problem_topic'] in num_terms_problems or customizations['problem_type'] in num_terms_problems:
        print("CHECK NUM TERMS")
        if count_terms(temp_problem) != customizations['num_terms']:
            return 'BAD'



    print('final_solution', solution)
    return solution

# Validate solution to ensure they don't violate user customizations. If they do, both the problems and solutions are discarded
def validate_solutions(problems, solutions, customizations):
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

# cleans gpt output to take away words, brackets, enumerations, etc.
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

# For slope problems
def answer_to_coordinates(answer):
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

# Convert ± into separate positive and negative values
def expand_pm(answer):
    # Extract the string from the list
    input_str = answer[0]
    
    # Check if the string contains the '±' symbol
    if '±' in input_str:
        print("BEFORE", input_str)
        # Split the string into the part before and after the '±'
        before_pm, after_pm = input_str.split('±')
        print("SPLIT", before_pm, after_pm)
        before_pm = before_pm.strip()
        after_pm = after_pm.strip()
        print("SPLIT", before_pm, after_pm)

        
        # Check if the part before ± is just "x =" or has more
        if before_pm.endswith('=') or before_pm.endswith('= '): # endswith() was a neat trick Chat GPT recommended
            print("OK>>>>>")
            print([f"{before_pm} {after_pm}", f"{before_pm} -{after_pm}"])
            # If it ends with "=", drop the "+"
            return [f"{before_pm} {after_pm}", f"{before_pm} -{after_pm}"]
        else:
            # Otherwise, include "+" and "-" for the ±
            return [f"{before_pm} + {after_pm}", f"{before_pm} - {after_pm}"]
    else:
        # If no '±', return the input as-is
        return answer

# Format answers according to decimal rounding or coordinates
def format_answer(answer, prob_type, num_decimal_places):
    print("Initial answer:", answer)
    
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
                rounded_numbers.append(str(decimal_value.quantize(precision, rounding=ROUND_HALF_UP))) # quantize() was a Chat GPT recommendation
            except Exception as e:
                # Handle any conversion errors
                print(f"Error processing '{num}': {e}") # ChatGPT error handling recommendation
                rounded_numbers.append('Invalid number')
        solution = rounded_numbers

    else:
        solution = answer

    if prob_type in simplifying_expressions:
        solution = solution[0]
        solution = [solution]
    print("Final solution:", solution)

    # Replace ± with two solutions
    # Do this +/- search last
    if "±" in str(solution):
        print("FOUND")
        solution =  expand_pm(solution)

    return solution

# Create the prompt based on type of problem. Will be solve, simplify, or expand based on type of problem
def create_prompt(problem, prob_type):
   
    if prob_type == 'Slope Intercept Form':
        prompt = f"Slope Intercept Form {problem}"

    elif prob_type == 'Standard Form':
        prompt = f"Convert {problem} to Standard Form"

    elif prob_type in simplifying_expressions or prob_type == 'Simplify:':
        prompt = f"Simplify {problem}"
        print(prompt)

    elif prob_type == 'Expand:':
        prompt = f"Expand {problem}"
        print(prompt)

    # elif prob_type == 'Equivalence_Test':
    #     prompt = f"Does {problem[0]} = {problem[1]}"

    else:
        prompt = f"Solve {problem}"
    return prompt

# function to check if WA response for two equations indicate that they are equal
def equal_or_not(result):
    if "true" in result:
        return True
    return False

# Get an explanation for each solution.
def get_explanations(problems, solutions, prob_topic, prob_type, num_decimal_places):
    details = ""
    if prob_type == "Evaluating Decimals":
        if num_decimal_places == 1:
            details += f"Please round the solution to {num_decimal_places} decimal place"
        else:
            details += f"Please round the solution to {num_decimal_places} decimal places"


    explanations = []
    for problem, solution in zip(problems, solutions):
        
        system_msg = "You are a math teacher. You excel at thoroughly explaining the steps you took to reach the correct answer."
        user_msg = f"Please walk me through how the answer to the question 'Solve {problem}' is {solution}. Please do this by {prob_topic}. {details}. Please use LaTex formatting. Make sure text inside math formulas are wrapped in '\\text', and organize steps in this format: '### Step x: Title. '\\[  \\] Details...'. Every step should be separated by '\\[ ... \\]', which will either contain a step or be blank. In the final step, please box the final answer (\\boxed)"
        print(user_msg)
        GPT_output = GPT_response(system_msg, user_msg)
        print(GPT_output)
        explanation = clean_explanation(GPT_output)
        explanations.append(explanation)

    return explanations

# Clean explanation by fixing some common LaTeX mistakes
def clean_explanation(explanation):
    # print("INITIAL EXPLANATION", explanation)
    replacements = {
        "\times": "\\times",
        "\text": "\\text"
    }
    newline = "\\[ \\]"

    # Get rid of text before the actual explanation
    start_index = explanation.find("###")
    if start_index != -1:
        explanation = explanation[start_index:]  # Slice from the first occurrence of '###'

    # Replace subsequent occurrences of ### with newline + ###
    explanation = explanation.replace("###", newline + "###")  
    explanation = explanation.replace("- \\(", "\\quad - \\(") 
    explanation = explanation.replace("- \\[", "\\quad - \\[") 
    # Perform other replacements
    for target, replacement in replacements.items():
        explanation = explanation.replace(target, replacement)

    # print("FINAL EXPLANATION", explanation)
    return explanation
