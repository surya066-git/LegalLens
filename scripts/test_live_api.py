import requests
import sys
import time

API_BASE = "http://127.0.0.1:8000"

def test_workflow():
    print("Testing health...")
    res = requests.get(f"{API_BASE}/health")
    if res.status_code != 200:
        print(f"Health check failed: {res.text}")
        sys.exit(1)
    print("Health check OK.")

    print("\nUploading document...")
    with open("docs/demo_contract.pdf", "rb") as f:
        res = requests.post(f"{API_BASE}/documents", files={"file": ("demo_contract.pdf", f, "application/pdf")})
    
    if res.status_code != 200:
        print(f"Upload failed: {res.text}")
        sys.exit(1)
    
    doc_id = res.json()["documentId"]
    print(f"Upload OK. Document ID: {doc_id}")

    print("\nProcessing document...")
    res = requests.post(f"{API_BASE}/documents/{doc_id}/process")
    if res.status_code != 200:
        print(f"Process failed: {res.text}")
        sys.exit(1)
    print("Process OK.")
    
    print("\nGetting pages...")
    res = requests.get(f"{API_BASE}/documents/{doc_id}/pages")
    if res.status_code != 200:
        print(f"Get pages failed: {res.text}")
        sys.exit(1)
    print("Get pages OK.")

    print("\nAsking a question...")
    res = requests.post(
        f"{API_BASE}/documents/{doc_id}/questions",
        json={"question": "What is the notice period?"}
    )
    if res.status_code != 200:
        print(f"Ask question failed: {res.status_code} {res.text}")
        sys.exit(1)
    
    data = res.json()
    print("Ask question OK.")
    print("Answer:")
    print(data["answer"])
    
    print("\nAll live tests passed successfully!")

if __name__ == "__main__":
    test_workflow()
