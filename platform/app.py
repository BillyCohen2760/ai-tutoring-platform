from flask import Flask, render_template
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


@app.route('/generate_problems/<problem_type>/<problem_topic>')
def generate_problems(problem_type, problem_topic):

    prob_type = replace_underscores_with_spaces(problem_type) # get rid of underscores
    prob_topic = replace_underscores_with_spaces(problem_topic) # get rid of underscores

    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = f"Please generate 3 unique and new algebra problems. Please make sure the problems have not been used before. The topic is {prob_type} by {prob_topic}. The variable should be x. Do not use LaTex formatting, and do not enumerate the problems. The answer should be in the following format: [math problem]"
    
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
    return render_template('practice_problems.html', problems=problems, solutions=solutions, prob_topic = prob_topic)


if __name__ == '__main__':
    app.run(debug=True)
