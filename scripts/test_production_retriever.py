import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.retriever import retrieve_with_scores


QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How many unused annual leave days can be carried into the next year?",
    "How many weeks of parental leave are available to eligible employees?",
    "What is the standard notice period for confirmed employees?",
    "How many working days in advance should annual leave normally be requested?",
    "By what date must carried-over annual leave be used?",
    "What is the probation period for employees?",
    "How are travel expenses reimbursed?",
    "What is the process for taking sick leave?",
    "What are the main obligations for remote work?",
]


print("=" * 80)
print("PRODUCTION RETRIEVER TEST")
print("=" * 80)
print("LLM calls: 0")
print("API calls: 0")
print()


for number, query in enumerate(QUESTIONS, 1):

    print("=" * 80)
    print(f"Q{number}: {query}")
    print("=" * 80)

    results = retrieve_with_scores(
        query,
        k=5,
    )

    for rank, (document, distance) in enumerate(
        results,
        start=1,
    ):

        metadata = document.metadata or {}

        source = (
            metadata.get("source")
            or metadata.get("filename")
            or "unknown"
        )

        page = (
            metadata.get("page")
            or metadata.get("page_number")
            or "-"
        )

        text = (
            document.page_content
            .replace("\n", " ")
            [:350]
        )

        print(f"\nRank {rank}")
        print(f"Distance: {distance}")
        print(f"Source: {source}")
        print(f"Page: {page}")
        print(f"Text: {text}")


print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("LLM calls: 0")
print("API calls: 0")