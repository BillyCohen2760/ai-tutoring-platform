# services/gpt_service.py
from openai import OpenAI

client = OpenAI()

def GPT_response(system_message, user_message):
    """
    Generate a response from the OpenAI API based on the provided system message and user message.
    
    Parameters:
    - system_message: str - The content for the system role to set the assistant's behavior.
    - user_message: str - The content for the user role as the prompt.
    
    Returns:
    - str: Formatted response from the assistant.
    """
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )

    return completion.choices[0].message.content
