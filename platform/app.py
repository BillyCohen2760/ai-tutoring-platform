from flask import Flask, render_template
from services.gpt_service import GPT_response
from services.wa_service import WA_response


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

@app.route('/practice')
def practice():
    system_msg = "You are a math teacher. You answer the question directly without any extra words or responses."
    user_msg = "Please generate 3 unique and new algebra problems. Please make sure the problems have not been used before. The topic is solving quadratic equations by factoring. The variable should be x. Do not use LaTex formatting, and do not enumerate the problems."

    # Get problems from GPT
    GPT_output = GPT_response(system_msg, user_msg)
    problems = [problem.strip() for problem in GPT_output.splitlines() if problem.strip()]
    print(problems)

    # Use Wolfram Alpha to solve each problem and collect solutions
    solutions = []
    for problem in problems:
        WA_output = WA_response(problem)
        solutions.append(WA_output)
    print(solutions)

    # Pass the problems and solutions to the template
    return render_template('practice.html', problems=problems, solutions=solutions)


if __name__ == '__main__':
    app.run(debug=True)
