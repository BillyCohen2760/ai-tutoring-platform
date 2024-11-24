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
    details = request.form.get('details', '')  # Default to an empty string if not provided
    if details != "In the problem, ":
        details = details + "."

    # Log received values
    print("Details received (POST):", details)
    print("Number of problems received (POST):", num_problems)

    if num_problems is None:
        num_problems = 3  # Default to 3 problems if num_problems is not specified

    prob_type = replace_underscores_with_spaces(problem_type)
    prob_topic = replace_underscores_with_spaces(problem_topic)

    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = f"Please generate {int(num_problems) + 2} unique and new algebra problems. DO NOT REPEAT PROBLEMS. Please make sure the problems have not been used before. The topic is {prob_type} by {prob_topic}. {details} The variable should be x. Change the coefficients from last iteration. Please use LaTex formatting."
    print(user_msg)
    GPT_output = GPT_response(system_msg, user_msg)
    problems = clean_gpt_output(GPT_output)
    problems = problems[:int(num_problems)]
    print(problems)

    solutions = []
    for problem in problems:
        prompt = f"Solve {problem}"
        WA_output = WA_response(prompt)
        solutions.append(WA_output)
    print(solutions)

    return render_template(
        'practice_problems.html',
        problems=problems,
        solutions=solutions,
        prob_topic=prob_topic,
        problem_type=problem_type,
        problem_topic=problem_topic
    )

if __name__ == '__main__':
    app.run(debug=True)
