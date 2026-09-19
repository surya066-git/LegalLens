import requests

BASE_URL = 'http://127.0.0.1:8000'
PDF_PATH = r'd:\LawAi\docs\demo_contract.pdf'

print('1. Uploading document...')
with open(PDF_PATH, 'rb') as f:
    files = {'file': ('demo_contract.pdf', f, 'application/pdf')}
    res = requests.post(f'{BASE_URL}/documents', files=files)
    
if res.status_code != 200:
    print(f'Upload failed: {res.text}')
    exit(1)

doc_id = res.json()['documentId']
print(f'Uploaded! Document ID: {doc_id}')

print('2. Processing document...')
res = requests.post(f'{BASE_URL}/documents/{doc_id}/process')
if res.status_code != 200:
    print(f'Process failed: {res.text}')
    exit(1)

process_data = res.json()
print(f'Processed! Found {process_data["clauseCount"]} clauses across {process_data["pageCount"]} pages.')

print('3. Asking question...')
payload = {'question': 'What is the base salary and notice period?'}
res = requests.post(f'{BASE_URL}/documents/{doc_id}/questions', json=payload)
if res.status_code != 200:
    print(f'Question failed: {res.text}')
    exit(1)

answer_data = res.json()
print('\n--- AI Response ---')
print(f'Answer: {answer_data["answer"]}')
print(f'Confidence: {answer_data["confidence"]}')
print(f'Citations: {len(answer_data["citations"])}')

print('\nEnd-to-End Test Passed!')
