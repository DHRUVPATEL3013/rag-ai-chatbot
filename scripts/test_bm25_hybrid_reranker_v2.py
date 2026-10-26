import sys
import re
import time
from pathlib import Path
from collections import defaultdict

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


# ============================================================
# CONFIG
# ============================================================

RERANKER_MODEL = "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"

SEMANTIC_K = 30
BM25_K = 30
FINAL_K = 5

# Number of Chroma records loaded per DB request.
BATCH_SIZE = 500

# Existing RRF constant.
RRF_K = 60


QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How many unused annual leave days can be carried into the next year?",
    "How many weeks of parental leave are available to eligible employees?",
    "What is the standard notice period for confirmed employees?",
    "How many working days in advance should annual leave normally be requested?",
    "By what date must carried-over annual leave be used?",
    "How long is the standard probation period?",
    "How are travel expenses reimbursed?",
    "What is the process for sick leave?",
    "What are the rules for remote work?",
]


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text: str):
    """
    Simple lexical tokenizer.

    Keeps words and useful numeric tokens.
    """
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


# ============================================================
# QUESTION-SPECIFIC TERMS
# ============================================================

def extract_priority_terms(query: str):
    """
    Extract important policy phrases from the question.

    These are intentionally simple and transparent.
    They are NOT LLM-generated.
    """

    q = query.lower()

    phrases = [
        "annual leave",
        "carried-over annual leave",
        "carry-over annual leave",
        "unused annual leave",
        "parental leave",
        "notice period",
        "probation period",
        "travel expenses",
        "sick leave",
        "remote work",
        "remote working",
    ]

    found = []

    for phrase in phrases:
        if phrase in q:
            found.append(phrase)

    # Also preserve important numeric/question concepts.
    concepts = [
        "days",
        "weeks",
        "working days",
        "calendar days",
        "advance",
        "deadline",
        "date",
        "reimbursed",
        "reimbursement",
        "process",
        "rules",
        "eligible",
        "confirmed employees",
        "full-time employee",
    ]

    for concept in concepts:
        if concept in q:
            found.append(concept)

    return found


# ============================================================
# PRIORITY SCORE
# ============================================================

def lexical_priority_score(query: str, text: str):
    """
    Give a small deterministic boost when the candidate contains
    the important phrase from the question.

    This is deliberately much smaller than the CrossEncoder score.
    """

    q = query.lower()
    t = text.lower()

    priority_terms = extract_priority_terms(q)

    score = 0.0

    for term in priority_terms:

        # Strong boost for exact multi-word phrases.
        if " " in term and term in t:
            score += 0.20

        # Smaller boost for individual concepts.
        elif " " not in term and re.search(
            rf"\b{re.escape(term)}\b",
            t,
        ):
            score += 0.04

    # Exact numeric concepts.
    if "how many" in q:
        if re.search(r"\b\d+\b", t):
            score += 0.03

    return score


# ============================================================
# LOAD ALL CHROMA DOCUMENTS
# ============================================================

def load_all_documents(vectorstore):

    print("=" * 80)
    print("LOADING ALL CHROMA DOCUMENTS")
    print("=" * 80)

    collection = vectorstore._collection

    total = collection.count()

    print(f"Total Chroma chunks: {total}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    documents = []

    start = time.time()

    for offset in range(0, total, BATCH_SIZE):

        end = min(offset + BATCH_SIZE, total)

        print(f"Loading {offset + 1}-{end} of {total}")

        batch = collection.get(
            limit=BATCH_SIZE,
            offset=offset,
            include=[
                "documents",
                "metadatas",
            ],
        )

        ids = batch.get("ids", [])
        texts = batch.get("documents", [])
        metadatas = batch.get("metadatas", [])

        for i, text in enumerate(texts):

            metadata = (
                metadatas[i]
                if i < len(metadatas)
                else {}
            )

            doc_id = (
                ids[i]
                if i < len(ids)
                else None
            )

            documents.append({
                "id": doc_id,
                "text": text or "",
                "metadata": metadata or {},
            })

    elapsed = time.time() - start

    print()
    print(f"Loaded documents: {len(documents)}")
    print(f"Loading time: {elapsed:.2f}s")
    print("=" * 80)

    return documents


# ============================================================
# RRF
# ============================================================

def reciprocal_rank(rank):
    return 1.0 / (RRF_K + rank)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 80)
    print("BM25 + SEMANTIC + PRIORITY TERMS + CROSSENCODER TEST")
    print("=" * 80)

    print()
    print("LLM calls: 0")
    print("LLM/API tokens used: 0")
    print()

    # --------------------------------------------------------
    # Load Chroma
    # --------------------------------------------------------

    vectorstore = get_vectorstore()

    # --------------------------------------------------------
    # Load documents
    # --------------------------------------------------------

    documents = load_all_documents(vectorstore)

    # --------------------------------------------------------
    # Build BM25
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("BUILDING BM25 INDEX")
    print("=" * 80)

    start = time.time()

    tokenized_docs = [
        tokenize(doc["text"])
        for doc in documents
    ]

    bm25 = BM25Okapi(tokenized_docs)

    elapsed = time.time() - start

    print(f"BM25 index built in {elapsed:.2f}s")

    # --------------------------------------------------------
    # Load CrossEncoder
    # --------------------------------------------------------

    print()
    print("=" * 80)
    print("LOADING CROSSENCODER")
    print("=" * 80)

    start = time.time()

    reranker = CrossEncoder(
        RERANKER_MODEL,
        max_length=512,
    )

    elapsed = time.time() - start

    print(f"Reranker loaded in {elapsed:.2f}s")

    # --------------------------------------------------------
    # QUESTIONS
    # --------------------------------------------------------

    for question_number, query in enumerate(QUESTIONS, start=1):

        print()
        print("=" * 100)
        print(f"QUESTION {question_number}")
        print("=" * 100)
        print(query)

        priority_terms = extract_priority_terms(query)

        print()
        print("Priority terms:")
        print(priority_terms)

        # ====================================================
        # SEMANTIC SEARCH
        # ====================================================

        print()
        print("Running semantic search...")

        start = time.time()

        semantic_results = vectorstore.similarity_search_with_score(
            query,
            k=SEMANTIC_K,
        )

        semantic_time = time.time() - start

        print(f"Semantic search: {semantic_time:.3f}s")

        # Map document IDs to semantic rank.
        semantic_rank = {}

        semantic_distance = {}

        semantic_docs = {}

        for rank, (doc, distance) in enumerate(
            semantic_results,
            start=1,
        ):

            text = doc.page_content or ""

            metadata = doc.metadata or {}

            key = (
                metadata.get("id")
                or metadata.get("chunk_id")
                or (
                    metadata.get("filename"),
                    metadata.get("page"),
                    text[:200],
                )
            )

            semantic_rank[key] = rank
            semantic_distance[key] = float(distance)
            semantic_docs[key] = {
                "text": text,
                "metadata": metadata,
            }

        # ====================================================
        # BM25 SEARCH
        # ====================================================

        print("Running BM25 search...")

        start = time.time()

        query_tokens = tokenize(query)

        bm25_scores = bm25.get_scores(query_tokens)

        top_bm25_indexes = sorted(
            range(len(bm25_scores)),
            key=lambda i: bm25_scores[i],
            reverse=True,
        )[:BM25_K]

        bm25_time = time.time() - start

        print(f"BM25 search: {bm25_time:.3f}s")

        bm25_rank = {}

        bm25_score_map = {}

        bm25_docs = {}

        for rank, index in enumerate(
            top_bm25_indexes,
            start=1,
        ):

            doc = documents[index]

            key = (
                doc["id"]
                or (
                    doc["metadata"].get("filename"),
                    doc["metadata"].get("page"),
                    doc["text"][:200],
                )
            )

            bm25_rank[key] = rank
            bm25_score_map[key] = float(
                bm25_scores[index]
            )
            bm25_docs[key] = doc

        # ====================================================
        # UNION CANDIDATES
        # ====================================================

        candidate_keys = set(
            semantic_rank.keys()
        ) | set(
            bm25_rank.keys()
        )

        candidates = []

        for key in candidate_keys:

            if key in semantic_docs:

                base = {
                    "key": key,
                    "text": semantic_docs[key]["text"],
                    "metadata": semantic_docs[key]["metadata"],
                }

            else:

                base = {
                    "key": key,
                    "text": bm25_docs[key]["text"],
                    "metadata": bm25_docs[key]["metadata"],
                }

            srank = semantic_rank.get(key)
            brank = bm25_rank.get(key)

            rrf = 0.0

            if srank is not None:
                rrf += reciprocal_rank(srank)

            if brank is not None:
                rrf += reciprocal_rank(brank)

            priority = lexical_priority_score(
                query,
                base["text"],
            )

            base.update({
                "semantic_rank": srank,
                "bm25_rank": brank,
                "semantic_distance": semantic_distance.get(key),
                "bm25_score": bm25_score_map.get(key),
                "rrf_score": rrf,
                "priority_score": priority,
            })

            candidates.append(base)

        # ====================================================
        # FIRST STAGE: RRF + PRIORITY
        # ====================================================

        candidates.sort(
            key=lambda x: (
                x["rrf_score"] + x["priority_score"]
            ),
            reverse=True,
        )

        # Keep a reasonable reranking pool.
        rerank_candidates = candidates[:15]

        print()
        print(
            f"Candidates before reranking: "
            f"{len(candidates)}"
        )
        print(
            f"Candidates sent to CrossEncoder: "
            f"{len(rerank_candidates)}"
        )

        # ====================================================
        # CROSSENCODER
        # ====================================================

        print("Running CrossEncoder...")

        pairs = [
            (
                query,
                candidate["text"],
            )
            for candidate in rerank_candidates
        ]

        start = time.time()

        scores = reranker.predict(
            pairs,
            show_progress_bar=False,
        )

        rerank_time = time.time() - start

        for candidate, score in zip(
            rerank_candidates,
            scores,
        ):
            candidate["reranker_score"] = float(score)

        # ====================================================
        # FINAL SCORE
        # ====================================================

        for candidate in rerank_candidates:

            reranker_score = candidate.get(
                "reranker_score",
                0.0,
            )

            priority = candidate.get(
                "priority_score",
                0.0,
            )

            # CrossEncoder is dominant.
            # Priority terms are only a small deterministic tie-breaker.
            candidate["final_score"] = (
                reranker_score
                + priority
            )

        rerank_candidates.sort(
            key=lambda x: x["final_score"],
            reverse=True,
        )

        # ====================================================
        # DISPLAY
        # ====================================================

        print()
        print("=" * 100)
        print("FINAL RESULTS")
        print("=" * 100)

        print(
            f"CrossEncoder reranking time: "
            f"{rerank_time:.3f}s"
        )

        for rank, candidate in enumerate(
            rerank_candidates[:FINAL_K],
            start=1,
        ):

            metadata = candidate["metadata"]

            filename = (
                metadata.get("filename")
                or metadata.get("source")
                or "UNKNOWN"
            )

            page = metadata.get(
                "page",
                metadata.get("page_number", "?"),
            )

            text = candidate["text"].replace(
                "\n",
                " ",
            )

            if len(text) > 500:
                text = text[:500] + "..."

            print()
            print("-" * 100)
            print(f"RANK: {rank}")
            print(
                f"Final score: "
                f"{candidate['final_score']:.6f}"
            )
            print(
                f"CrossEncoder: "
                f"{candidate.get('reranker_score', 0):.6f}"
            )
            print(
                f"Priority score: "
                f"{candidate['priority_score']:.6f}"
            )
            print(
                f"RRF score: "
                f"{candidate['rrf_score']:.6f}"
            )
            print(
                f"Semantic rank: "
                f"{candidate.get('semantic_rank')}"
            )
            print(
                f"BM25 rank: "
                f"{candidate.get('bm25_rank')}"
            )
            print(
                f"Semantic distance: "
                f"{candidate.get('semantic_distance')}"
            )
            print(
                f"BM25 score: "
                f"{candidate.get('bm25_score')}"
            )
            print(f"Source: {filename}")
            print(f"Page: {page}")
            print(f"Text: {text}")

    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("LLM calls: 0")
    print("LLM/API tokens used: 0")
    print("=" * 80)


if __name__ == "__main__":
    main()