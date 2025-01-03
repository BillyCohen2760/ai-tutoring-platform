from celery import Celery
from utils import get_explanations

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Redis URL
    backend='redis://localhost:6379/0'
)

@celery_app.task
def async_get_explanations(problems, solutions, prob_topic, prob_type, num_decimal_places):
    explanations = []
    for problem, solution in zip(problems, solutions):
        explanation = get_explanations(problem, solution, prob_topic, prob_type, num_decimal_places)
        explanations.append(explanation)
    return explanations
