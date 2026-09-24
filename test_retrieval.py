import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'services', 'api')))

from app.services.retrieval import RetrievalService
from app.services.document_store import DocumentStore
from app.config import get_settings

store = DocumentStore(get_settings().document_storage_dir)
doc = store.load_metadata("doc_b802b58605054944b6aefef1f2144504")
service = RetrievalService()

for q in ["What is the notice period?", "what is post employment restriction"]:
    print(f"\n--- Q: {q} ---")
    chunks = service.retrieve_chunks(q, doc.chunks, top_k=15)
    print(f"Retrieved: {len(chunks)} chunks")
    for c in chunks[:3]:
        print(f"Chunk {c.chunk_id}, Clause {c.clause_number}: {c.source_text[:50]}...")
