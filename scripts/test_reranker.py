from app.retrieval.retriever import retrieve_with_scores
from sentence_transformers import CrossEncoder
import time

query = "What is the annual leave entitlement?"

print("Retrieving documents...")
results = retrieve_with_scores(query, k=15)

print("Retrieved:", len(results))

model = CrossEncoder(
    "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"
)

pairs = [
    (query, doc.page_content)
    for doc, dist in results
]

start = time.perf_counter()

scores = model.predict(pairs)

elapsed = time.perf_counter() - start

ranked = sorted(
    zip(scores, results),
    key=lambda x: x[0],
    reverse=True,
)

print()
print("=" * 100)
print("RERANKED RESULTS")
print("=" * 100)
print("Reranking time:", round(elapsed, 3), "seconds")
print()

for i, (score, (doc, dist)) in enumerate(ranked):
    print(
        f"RANK {i + 1} | "
        f"RERANKER={score:.6f} | "
        f"CHROMA_DISTANCE={dist:.6f} | "
        f"SOURCE={doc.metadata.get('source')} | "
        f"PAGE={doc.metadata.get('page')}"
    )

    print(doc.page_content[:500].replace("\n", " "))
    print("-" * 100)