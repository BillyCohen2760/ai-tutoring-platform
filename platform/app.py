from flask import Flask, render_template, request
from services.gpt_service import GPT_response
from services.wa_service import WA_response
from utils import *
from dotenv import load_dotenv
import os




app = Flask(__name__)

load_dotenv()
app.config['OPEN_AI_KEY'] = os.getenv('OPEN_AI_KEY')

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

@app.route('/practice_landing')
def practice_landing():
    return render_template('practice_landing.html')

# Create a generic settings page -- can specify further down the line

@app.route('/practice_settings', methods=['POST'])
def practice_settings():
    problem_type = request.form.get('problem_type')  # Get problem type from form data
    prob_type = replace_underscores_with_spaces(problem_type)
    problem_topic = request.form.get('problem_topic')  # Get problem topic from form data
    prob_topic = replace_underscores_with_spaces(problem_topic)

    return render_template('practice_settings.html', problem_type=problem_type, prob_type=prob_type, prob_topic=prob_topic, problem_topic=problem_topic)

@app.route('/generate_problems/<problem_type>/<problem_topic>/', methods=['GET', 'POST'])
# @app.route('/generate_problems/<problem_type>/<problem_topic>/<num_problems>', methods=['GET', 'POST'])
def generate_problems(problem_type, problem_topic): #, num_problems):
    # Retrieve num_problems and details from POST form data
    num_problems = request.form.get('num_problems', None)  # Default to None if not provided
    allow_square_roots = request.form.get('allow_square_roots', '')  # Default to None if not provided
    allow_imaginary_numbers = request.form.get('allow_imaginary_numbers', '')  # Default to None if not provided
    details = request.form.get('details', '')  # Default to an empty string if not provided

    customizations = {}
    if allow_square_roots != '':
        customizations['sqrt'] = allow_square_roots
        customizations['i'] = allow_imaginary_numbers


    # Log received values
    print("Details received (POST):", details)
    print("Number of problems received (POST):", num_problems)
    print("Allow Square Roots received (POST):", allow_square_roots)

    if num_problems is None:
        num_problems = 3  # Default to 3 problems if num_problems is not specified

    prob_type = replace_underscores_with_spaces(problem_type)
    prob_topic = replace_underscores_with_spaces(problem_topic)

    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = f"Please generate {int(num_problems) + 5} unique and new algebra problems. DO NOT REPEAT PROBLEMS. Please make sure the problems have not been used before. The topic is {prob_type} by {prob_topic}. {details}. Please use LaTex formatting."
    print(user_msg)
    GPT_output = GPT_response(system_msg, user_msg)
    print(prob_type, prob_topic)
    problems = clean_gpt_output(GPT_output, customizations)
    # problems = problems[:int(num_problems)] # temporarily commenting out because want to handle this after finding solution
    print(problems)

    solutions = []
    for problem in problems:
        prompt = f"Solve {problem}"
        WA_output = WA_response(prompt)
        print(WA_output)
        solution = format_answer(WA_output, prob_type)
        solutions.append(solution)
    print(solutions)

    print('problems', problems)
    print('solutions', solutions)

    problems, solutions = validate(problems, solutions, customizations)
    # print('problems', problems)
    # print('solutions', solutions)

    message = 'None'
    if len(problems) >= int(num_problems):
        if str(len(problems)) == 1:
            message = f"Sorry, only " + str(len(problems)) + " problem was created. "
        else:
            message = f"Sorry, only " + str(len(problems)) + " problems were created. "

        if str(num_problems) == 1:
            message += "If you want " + str(num_problems) + " problem, please click the Try Again button"
        else:
            message += "If you want " + str(num_problems) + " problems, please click the Try Again button"


    # only save num_problems number of problems
    problems = problems[:int(num_problems)]
    solutions = solutions[:int(num_problems)]
    print('problems', problems)
    print('solutions', solutions)


    return render_template(
        'practice_problems.html',
        problems=problems,
        solutions=solutions,
        prob_topic=prob_topic,
        problem_type=problem_type,
        problem_topic=problem_topic,
        message = message
    )

if __name__ == '__main__':
    app.run(debug=True)
