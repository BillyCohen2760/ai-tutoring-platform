from flask import Flask, render_template, request
from services.gpt_service import GPT_response
from services.wa_service import WA_response
from utils import replace_underscores_with_spaces



app = Flask(__name__)

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

@app.route('/generate_problems/<problem_type>/<problem_topic>/', defaults={'num_problems': None})
@app.route('/generate_problems/<problem_type>/<problem_topic>/<num_problems>')
def generate_problems(problem_type, problem_topic, num_problems):
    if num_problems is None:
        num_problems = 3  # Default to 3 problems if num_problems is not specified

    prob_type = replace_underscores_with_spaces(problem_type) # get rid of underscores
    prob_topic = replace_underscores_with_spaces(problem_topic) # get rid of underscores
    # num_problems = request.form.get('num_problems')  # New field for number of problems
    # difficulty_level = request.form.get('difficulty_level')  # New field for difficulty level

    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = f"Please generate {num_problems} unique and new algebra problems. Please make sure the problems have not been used before. The topic is {prob_type} by {prob_topic}. The variable should be x. Do not use LaTex formatting, and do not enumerate the problems. Your response should ONLY be the math problems."
    
    GPT_output = GPT_response(system_msg, user_msg)
    problems = [problem.strip() for problem in GPT_output.splitlines() if problem.strip()]
    print(problems)


    solutions = []
    for problem in problems:
        prompt = f"Solve {problem}"
        WA_output = WA_response(prompt)
        solutions.append(WA_output)
    print(solutions)
    
    # Then, render the problems in a new template
    return render_template('practice_problems.html', problems=problems, solutions=solutions, prob_topic = prob_topic, problem_type=problem_type, problem_topic=problem_topic)


if __name__ == '__main__':
    app.run(debug=True)
