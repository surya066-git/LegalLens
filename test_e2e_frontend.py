import requests

BASE_URL = 'http://127.0.0.1:3000/api'
PDF_PATH = r'd:\LawAi\docs\demo_contract.pdf'

print('1. Uploading document through Next.js...')
with open(PDF_PATH, 'rb') as f:
    files = {'file': ('demo_contract.pdf', f, 'application/pdf')}
    res = requests.post(f'{BASE_URL}/documents', files=files)
    
if res.status_code != 200:
    print(f'Upload failed: {res.text}')
    exit(1)

doc_id = res.json()['documentId']
print(f'Uploaded! Document ID: {doc_id}')
