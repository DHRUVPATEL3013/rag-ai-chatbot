import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.retriever import retrieve_with_scores
from app.retrieval.confidence import (
    filter_relevant_documents,
    is_low_confidence,
)


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
print("RETRIEVER + CONFIDENCE TEST")
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
        k=10,
    )

    relevant = filter_relevant_documents(
        results
    )

    low_confidence = is_low_confidence(
        relevant
    )

    print(f"Retrieved results : {len(results)}")
    print(f"Relevant results  : {len(relevant)}")
    print(f"Low confidence    : {low_confidence}")

    for rank, (document, distance) in enumerate(
        relevant[:5],
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
            [:250]
        )

        print(
            f"\nRank {rank}"
            f"\nDistance: {distance:.6f}"
            f"\nSource: {source}"
            f"\nPage: {page}"
            f"\nText: {text}"
        )


print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("LLM calls: 0")
print("API calls: 0")