import sys
import re
import hashlib
import time
from pathlib import Path

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


# ============================================================
# CONFIG
# ============================================================

SEMANTIC_K = 30
BM25_K = 30
RRF_K = 60
RERANK_K = 15
FINAL_K = 5

RERANKER_MODEL = (
    "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"
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


# ============================================================
# HELPERS
# ============================================================

def normalize_text(text):
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def stable_key(doc):
    metadata = doc.metadata or {}

    chunk_id = (
        metadata.get("id")
        or metadata.get("chunk_id")
        or metadata.get("document_id")
    )

    if chunk_id:
        return f"id:{chunk_id}"

    source = (
        metadata.get("filename")
        or metadata.get("source")
        or ""
    )

    page = (
        metadata.get("page")
        or metadata.get("page_number")
        or ""
    )

    text = normalize_text(doc.page_content)

    raw = f"{source}|{page}|{text}"

    return "hash:" + hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()


def tokenize(text):
    return re.findall(r"\w+", normalize_text(text))


def get_source(doc):
    metadata = doc.metadata or {}

    return (
        metadata.get("filename")
        or metadata.get("source")
        or "unknown"
    )


def get_page(doc):
    metadata = doc.metadata or {}

    return (
        metadata.get("page")
        or metadata.get("page_number")
        or "-"
    )


def print_result(rank, item):
    doc = item["document"]

    print(
        f"\n  Rank {rank}"
        f"\n  Reranker score : {item['reranker_score']:.6f}"
        f"\n  RRF score      : {item['rrf_score']:.6f}"
        f"\n  Semantic rank  : {item['semantic_rank']}"
        f"\n  BM25 rank      : {item['bm25_rank']}"
        f"\n  Source         : {get_source(doc)}"
        f"\n  Page           : {get_page(doc)}"
        f"\n  Text           : "
        f"{doc.page_content[:500].replace(chr(10), ' ')}"
    )


# ============================================================
# LOAD CHROMA
# ============================================================

print("=" * 80)
print("V3 HYBRID + CROSSENCODER TEST")
print("=" * 80)

print("\nLLM calls      : 0")
print("API calls      : 0")
print("Production code changed : NO")

print("\nLoading Chroma documents...")

vectorstore = get_vectorstore()
collection = vectorstore._collection

total = collection.count()

print(f"Total Chroma chunks: {total:,}")

all_docs = []

BATCH_SIZE = 500

start = time.time()

for offset in range(0, total, BATCH_SIZE):

    batch = collection.get(
        include=["documents", "metadatas"],
        limit=BATCH_SIZE,
        offset=offset,
    )

    documents = batch["documents"]
    metadatas = batch["metadatas"]

    for text, metadata in zip(documents, metadatas):
        from langchain_core.documents import Document

        all_docs.append(
            Document(
                page_content=text,
                metadata=metadata or {},
            )
        )

    print(
        f"Loaded {min(offset + BATCH_SIZE, total):,}/{total:,}",
        end="\r",
    )

print()

print(
    f"Document loading time: "
    f"{time.time() - start:.2f}s"
)


# ============================================================
# BUILD BM25
# ============================================================

print("\nBuilding BM25 index...")

start = time.time()

corpus_tokens = [
    tokenize(doc.page_content)
    for doc in all_docs
]

bm25 = BM25Okapi(corpus_tokens)

print(
    f"BM25 build time: "
    f"{time.time() - start:.2f}s"
)


# ============================================================
# LOAD RERANKER
# ============================================================

print("\nLoading CrossEncoder...")

start = time.time()

reranker = CrossEncoder(RERANKER_MODEL)

print(
    f"Reranker load time: "
    f"{time.time() - start:.2f}s"
)


# ============================================================
# TEST QUESTIONS
# ============================================================

for q_index, query in enumerate(QUESTIONS, 1):

    print("\n")
    print("=" * 80)
    print(f"QUESTION {q_index}: {query}")
    print("=" * 80)

    # --------------------------------------------------------
    # SEMANTIC
    # --------------------------------------------------------

    start = time.time()

    semantic_results = vectorstore.similarity_search_with_score(
        query,
        k=SEMANTIC_K,
    )

    semantic_time = time.time() - start

    semantic_map = {}

    for rank, (doc, distance) in enumerate(
        semantic_results,
        start=1,
    ):
        key = stable_key(doc)

        semantic_map[key] = {
            "document": doc,
            "semantic_rank": rank,
            "semantic_distance": distance,
            "bm25_rank": None,
            "bm25_score": None,
        }

    # --------------------------------------------------------
    # BM25
    # --------------------------------------------------------

    start = time.time()

    bm25_scores = bm25.get_scores(
        tokenize(query)
    )

    ranked_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True,
    )[:BM25_K]

    bm25_time = time.time() - start

    bm25_map = {}

    for rank, index in enumerate(
        ranked_indices,
        start=1,
    ):
        doc = all_docs[index]
        key = stable_key(doc)

        bm25_map[key] = {
            "document": doc,
            "bm25_rank": rank,
            "bm25_score": float(bm25_scores[index]),
        }

    # --------------------------------------------------------
    # MERGE + DEDUPLICATE
    # --------------------------------------------------------

    merged = {}

    for key, item in semantic_map.items():

        merged[key] = {
            "document": item["document"],
            "semantic_rank": item["semantic_rank"],
            "semantic_distance": item["semantic_distance"],
            "bm25_rank": None,
            "bm25_score": None,
        }

    for key, item in bm25_map.items():

        if key not in merged:

            merged[key] = {
                "document": item["document"],
                "semantic_rank": None,
                "semantic_distance": None,
                "bm25_rank": item["bm25_rank"],
                "bm25_score": item["bm25_score"],
            }

        else:

            merged[key]["bm25_rank"] = item["bm25_rank"]
            merged[key]["bm25_score"] = item["bm25_score"]

    # --------------------------------------------------------
    # RRF
    # --------------------------------------------------------

    for item in merged.values():

        rrf = 0.0

        if item["semantic_rank"] is not None:
            rrf += 1.0 / (
                RRF_K + item["semantic_rank"]
            )

        if item["bm25_rank"] is not None:
            rrf += 1.0 / (
                RRF_K + item["bm25_rank"]
            )

        item["rrf_score"] = rrf

    candidates = sorted(
        merged.values(),
        key=lambda x: x["rrf_score"],
        reverse=True,
    )[:RERANK_K]

    print(
        f"\nSemantic time : {semantic_time:.3f}s"
        f"\nBM25 time     : {bm25_time:.3f}s"
        f"\nCandidates    : {len(candidates)}"
    )

    # --------------------------------------------------------
    # CROSSENCODER
    # --------------------------------------------------------

    pairs = [
        (
            query,
            item["document"].page_content,
        )
        for item in candidates
    ]

    start = time.time()

    scores = reranker.predict(pairs)

    rerank_time = time.time() - start

    for item, score in zip(candidates, scores):
        item["reranker_score"] = float(score)

    final_results = sorted(
        candidates,
        key=lambda x: x["reranker_score"],
        reverse=True,
    )[:FINAL_K]

    print(
        f"Rerank time   : {rerank_time:.3f}s"
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    for rank, item in enumerate(
        final_results,
        start=1,
    ):
        print_result(rank, item)


print("\n")
print("=" * 80)
print("V3 TEST COMPLETE")
print("=" * 80)
print("LLM calls : 0")
print("API calls : 0")
print("Production code changed : NO")