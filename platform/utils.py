import re
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
        if any(word in item.lower() for word in ['add', 'addition', 'subtract', 'subtraction', 'multiply', 'multiplication', 'divide', 'division', 'calculate', 'compute', 'what', 'evaluate', 'solve', 'by', 'is', 'using', 'the', 'method', 'find', 'solution', 'determine', 'equation', 'expression', '?']) or item == '\[' or item == '\]' or item == '\(' or item == '\)':
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

# cleans gpt output to take away brackets, enumerations, etc.
def clean_gpt_output(gpt_output):
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