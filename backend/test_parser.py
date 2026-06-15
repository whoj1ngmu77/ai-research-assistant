from app.services.embedder import embed_text
from app.services.vector_store import search
from app.services.generator import generate_answer

question = "What is the capital of France?"

print(f"Question: {question}\n")

query_embedding = embed_text(question, task_type="RETRIEVAL_QUERY")
chunks = search(query_embedding, top_k=3)

print(f"Retrieved {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"  [{i+1}] Page {chunk['page_number']}, distance {chunk['distance']:.4f}")

answer = generate_answer(question, chunks)

print(f"\n--- ANSWER ---")
print(answer)
