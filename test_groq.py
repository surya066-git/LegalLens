import requests
from dotenv import load_dotenv
import os

load_dotenv(".env")
key = os.getenv("GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama3-8b-8192",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! What is 2+2? Respond ONLY in JSON matching {'answer': 'string'}."}
    ],
    "response_format": {"type": "json_object"},
    "temperature": 0.0
}

r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
print(r.status_code)
print(r.text)
