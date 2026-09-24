import requests
import json

base_url = "http://127.0.0.1:8000"
doc_id = "doc_b802b58605054944b6aefef1f2144504"

def ask(q):
    print(f"\n--- Q: {q} ---")
    resp = requests.post(f"{base_url}/documents/{doc_id}/questions", json={"question": q})
    try:
        print(json.dumps(resp.json(), indent=2))
    except:
        print(resp.text)

ask("What is the notice period?")
ask("Does the agreement provide health insurance?")
ask("Who is the Prime Minister of India?")
ask("what is post employment restriction")
