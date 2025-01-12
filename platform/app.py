from flask import Flask, render_template, request, jsonify
from services.gpt_service import GPT_response
from services.wa_service import WA_response
from utils import *
from categories import *
from dotenv import load_dotenv
import os




app = Flask(__name__)

load_dotenv()
app.config['OPEN_AI_KEY'] = os.getenv('OPEN_AI_KEY')

# Highlight steps in Walkthrough
@app.template_filter('highlight_steps')
def highlight_steps(text):
    # Regular expression to find "### Step x: ______" and "### Final Step: ______"
    step_pattern = r"(### (Step \d+:|Final Step: | Final Answer:))"
    
    # Replace the step titles with a styled span
    styled_text = re.sub(step_pattern, r'<span class="step-title">\1</span>', text)
    
    # Return the modified text
    return styled_text

app.jinja_env.filters['highlight_steps'] = highlight_steps


# Mathematical Equivalence Check
@app.route('/api/simplify_expression', methods=['POST'])
def simplify_expression():
    # Get the expression from the request
    data = request.get_json()
    expr = data.get('expression', '')
    prob_topic = data.get('probTopic', '')

    print("data", data)
    print("expr", expr)
    print("probTopic", prob_topic)

    if expr.isnumeric():
        return expr
   
    if prob_topic == 'Slope_Intercept_Form':
        prompt = create_prompt(expr, 'Slope Intercept Form')
    elif prob_topic == 'Standard_Form':
        prompt = create_prompt(expr, 'Standard Form')
    
    else: 
        prompt = create_prompt(expr, 'Expand:') # MIGHT WANT TO DO EXPAND...

    # Use the WA_response function to simplify the expression
    result = WA_response(prompt)
    # verdict = equal_or_not(result)
    print('EXPANDED:', result, result[0])

    # Ensure the response is correctly formatted as JSON
    if result:
        if result[0] == 'No results found.':
            prompt2 = create_prompt(expr, 'Simplify:')
            result2 = WA_response(prompt2)
            if result2:
                print('SIMPLIFIED', result2, result2[0])
                if result2[0] == 'No results found.':
                    return jsonify({"result": expr.replace(" ", "")}), 200 # error handling logic recommended by ChatGPT

                else: return jsonify({"result": result2[0].replace(" ", "")}), 200 # error handling logic recommended by ChatGPT
            else: return jsonify({"result": expanded.replace(" ", "")}), 200 # error handling logic recommended by ChatGPT


        else: 
            expanded = result[0]
            prompt2 = create_prompt(expanded, 'Simplify:')
            result2 = WA_response(prompt2)
            print('SIMPLIFIED', result2, result2[0])

            if result2:
                if result2[0] == 'No results found.':
                    print("returning", expanded.replace(" ", ""))
                    return jsonify({"result": expanded.replace(" ", "")}), 200
                else: return jsonify({"result": result2[0].replace(" ", "")}), 200
                
            else: return jsonify({"result": expanded.replace(" ", "")}), 200
    
    else:
        return jsonify({"error": "Failed to simplify the expression"}), 500 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html') 

# Choose Problem Type and Solving Method
@app.route('/practice_landing')
def practice_landing():
    return render_template('practice_landing.html')

# Create a generic settings page -- can specify further down the line

# Make Additional Problem and Solution Customizations
@app.route('/practice_settings', methods=['POST'])
def practice_settings():
    problem_type = request.form.get('problem_type')  # Get problem type from form data
    prob_type = replace_underscores_with_spaces(problem_type)
    problem_topic = request.form.get('problem_topic')  # Get problem topic from form data
    prob_topic = replace_underscores_with_spaces(problem_topic)

    return render_template('practice_settings.html', problem_type=problem_type, prob_type=prob_type, prob_topic=prob_topic, problem_topic=problem_topic)

# Generate problems receives the problem settings and generates problems, solutions, walkthroughs
@app.route('/generate_problems/<problem_type>/<problem_topic>/', methods=['GET', 'POST'])
# @app.route('/generate_problems/<problem_type>/<problem_topic>/<num_problems>', methods=['GET', 'POST'])
def generate_problems(problem_type, problem_topic): #, num_problems):
    prob_type = replace_underscores_with_spaces(problem_type)
    prob_topic = replace_underscores_with_spaces(problem_topic)

    # Retrieve num_problems and details from POST form data
    num_problems = request.form.get('num_problems', '3')  # Default to 3 if not provided
    allow_square_roots = request.form.get('allow_square_roots', '')  # Default to None if not provided
    allow_imaginary_numbers = request.form.get('allow_imaginary_numbers', '')  # Default to None if not provided
    allow_negative_answers = request.form.get('allow_negative_answers', '')  # Default to None if not provided
    details = request.form.get('details', '')  # Default to an empty string if not provided

    customizations = {}
    # NEED TO ADD NUMBER OF TERMS CHECK!!
    customizations['problem_type'] = problem_type
    customizations['problem_topic'] = problem_topic
    if allow_square_roots != '':
        customizations['sqrt'] = allow_square_roots
    if allow_imaginary_numbers != '':
        customizations['i'] = allow_imaginary_numbers
    if allow_negative_answers != '':
        customizations['negative'] = allow_negative_answers


    # Log received values
    print("Details received (POST):", details)
    print("Number of problems received (POST):", num_problems)
    print("Allow Square Roots received (POST):", allow_square_roots)
    print("Allow Imaginary Numbers received (POST):", allow_imaginary_numbers)
    print("Allow Negative Numbers received (POST):", allow_negative_answers)

    print(problem_type, problem_topic)
    num_decimal_places = 0
    if problem_type == "Evaluating_Decimals":
        num_decimal_places = request.form.get('num_decimal_places', '0') # Default to 0 if not provided
        num_decimal_places = int(num_decimal_places)
        print("Number of Decimal Places received (POST):", num_decimal_places)

    
        num_terms = request.form.get('num_terms', '0') # Default to 0 if not provided
        customizations['num_terms'] = int(num_terms)
        print("Number of Terms received (POST):", num_terms)

    if problem_type == "Evaluating_Fractions":
        num_terms = request.form.get('num_terms', '0') # Default to 0 if not provided
        customizations['num_terms'] = int(num_terms)
        print("Number of Terms received (POST):", num_terms)

    if problem_topic == "Combining_Like_Terms":
        num_terms = request.form.get('num_terms', '0') # Default to 0 if not provided
        customizations['num_terms'] = int(num_terms)
        print("Number of Terms received (POST):", num_terms)


    if problem_type == "Solving_Quadratic_Equations":
        abc = request.form.get('abc', '') # Default to 0 if not provided
        # num_decimal_places = int(num_decimal_places)
        print("abc", abc)
        customizations['abc'] = abc



    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = f"Please generate {int(num_problems) + 5} unique and new algebra problems. DO NOT REPEAT PROBLEMS. Please make sure the problems have not been used before. The topic is {prob_type} by {prob_topic}. {details}. Please use LaTex formatting."
    print(user_msg)
    GPT_output = GPT_response(system_msg, user_msg)
    # GPT_output = 'simplify 4x + 3y - 2x + 5y' # test for simplify and Try Again button
    print(prob_type, prob_topic)
    problems = clean_gpt_output(GPT_output, customizations)
    # problems = problems[:int(num_problems)] # temporarily commenting out because want to handle this after finding solution
    # problems
    # Ensure problems adhere to user customizations
    problems = validate_problems(problems, customizations)
    # problems = ['x^2 - 5x - 14 = 0']
    print(problems)

    solutions = []
    for problem in problems:
        if prob_type == 'Equations Of A Line':
            prompt = create_prompt(problem, prob_topic)
        else:
            prompt = create_prompt(problem, prob_type)
        print("WA Prompt", prompt)
        WA_output = WA_response(prompt)
        print(WA_output)
        solution = format_answer(WA_output, prob_type, num_decimal_places)
        solutions.append(solution)
    print(solutions)

    print('problems', problems)
    print('solutions', solutions)

    problems, solutions = validate_solutions(problems, solutions, customizations)
    # print('problems', problems)
    # print('solutions', solutions)

    message = 'None'
    if len(problems) < int(num_problems) and len(problems) != 0:
        print(len(problems))
        if (len(problems)) == 1:
            message = f"Sorry, only " + str(len(problems)) + " problem was created. "
        else:
            message = f"Sorry, only " + str(len(problems)) + " problems were created. "

        if str(num_problems) == '1':
            message += "If you want " + str(num_problems) + " problem, please click the Try Again button"
        else:
            message += "If you want " + str(num_problems) + " problems, please click the Try Again button"


    # only save num_problems number of problems
    problems = problems[:int(num_problems) + 1] # plus 1 for Practice One More Functionality
    solutions = solutions[:int(num_problems) + 1] # plus 1 for Practice One More Functionality
    print('problems', problems)
    print('solutions', solutions)

    explanation = get_explanations(problems, solutions, prob_topic, prob_type, num_decimal_places)
# Test Explanation
#     explanation = ['''
#     Sure! Let's solve the quadratic equation \( x^2 + 4x + 3 = 0 \) using the factoring method step-by-step.

# ### Step 1: Write the equation in standard form
# The equation is already in standard form:
# \[
# x^2 + 4x + 3 = 0.
# \]

# ### Step 2: Factor the quadratic
# We want to factor the quadratic expression \( x^2 + 4x + 3 \). To do this, we're looking for two numbers that multiply to the constant term (which is 3) and add up to the coefficient of the \( x \) term (which is 4).

# The numbers that fit these criteria are:
# - \( 1 \) and \( 3 \) (since \( 1 \times 3 = 3 \) and \( 1 + 3 = 4 \)).

# ### Step 3: Write the factored form
# Using these numbers, we can rewrite the quadratic as:
# \[
# (x + 1)(x + 3) = 0.
# \]

# ### Step 4: Apply the Zero Product Property
# The Zero Product Property states that if the product of two factors equals zero, then at least one of the factors must be equal to zero. Therefore, we can set each factor equal to zero:
# \[
# x + 1 = 0 \quad \text{or} \quad x + 3 = 0.
# \]

# ### Step 5: Solve for \( x \)
# Now we will solve each equation separately.

# 1. For the first equation:
#    \[
#    x + 1 = 0
#    \]
#    Subtracting 1 from both sides gives us:
#    \[
#    x = -1.
#    \]

# 2. For the second equation:
#    \[
#    x + 3 = 0
#    \]
#    Subtracting 3 from both sides gives us:
#    \[
#    x = -3.
#    \]

# ### Conclusion
# Therefore, the solutions to the quadratic equation \( x^2 + 4x + 3 = 0 \) are:
# \[
# x = -1 \quad \text{and} \quad x = -3.
# \]

# We can summarize the answers:
# \[
# \text{The solutions are } x = -1 \text{ and } x = -3.
# \]
# ''']

    return render_template(
        'practice_problems.html',
        problems=problems,
        solutions=solutions,
        prob_topic=prob_topic,
        prob_type=prob_type,
        problem_type=problem_type,
        problem_topic=problem_topic,
        message = message,
        explanation = explanation,
        allow_square_roots = allow_square_roots,
        allow_imaginary_numbers = allow_imaginary_numbers,
        allow_negative_answers = allow_negative_answers,
        num_decimal_places = num_decimal_places
    )

if __name__ == '__main__':
    app.run(debug=True)
