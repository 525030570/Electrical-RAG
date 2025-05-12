from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(
        api_key=os.getenv("online_model_API_KEY"),
        base_url=os.getenv("online_model_API_URL"),
    )      

def online_model_chat(history, history_round, prompt_template, temperature, max_tokens):          
    system_message = {'role': 'system', 'content': 'You are a helpful assistant.'}
    messages = []
    history_round = min(len(history),history_round)
    for i in range(history_round):
        messages.append({'role': 'user', 'content': history[-history_round+i][0]})
        messages.append({'role': 'assistant', 'content': history[-history_round+i][1]})
    messages.append({'role': 'user', 'content': prompt_template})
    messages = [system_message] + messages
    completion = client.chat.completions.create(
        model=os.getenv("online_chat_model_name"),
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
        )
    return completion

