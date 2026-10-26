"""
Core RAG chain — Phase 3.
"""


def build_rag_chain():
    """
    TODO: Using LangChain Expression Language (LCEL), wire together:
      retriever -> prompt (instruct the model to answer in the query's
      language and to cite the retrieved source metadata) -> ChatGroq
      -> output parser.
    Return the runnable chain.
    """
    raise NotImplementedError


def answer_question(query: str, language: str, category: str = None) -> dict:
    """
    TODO:
      1. Retrieve chunks via retrieval.retriever.get_retriever()
      2. Check confidence via retrieval.confidence.is_low_confidence()
      3. If confident: run build_rag_chain() and return
         {"answer": ..., "source": "Internal Knowledge",
          "citations": [{"document": ..., "page": ..., "section": ...}]}
      4. If not confident: delegate to chat.fallback.call_external_ai()
    """
    raise NotImplementedError
