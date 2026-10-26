    # # """
    # # RAG answer generation using Groq.
    # # """

    # # from langchain_core.prompts import ChatPromptTemplate
    # # from langchain_groq import ChatGroq

    # # from app.config import settings


    # # def get_llm():
    # #     """Create and return the configured Groq chat model."""

    # #     return ChatGroq(
    # #         model=settings.GROQ_MODEL,
    # #         api_key=settings.GROQ_API_KEY,
    # #         temperature=0,
    # #     )


    # # def generate_answer(query: str, documents: list) -> str:
    # #     """Generate an answer using only the retrieved documents."""

    # #     if not documents:
    # #         return (
    # #             "I couldn't find enough information in the available "
    # #             "documents to answer that question."
    # #         )

    # #     context = "\n\n---\n\n".join(
    # #         document.page_content
    # #         for document in documents
    # #     )

    # #     prompt = ChatPromptTemplate.from_messages(
    # #         [
    # #             (
    # #                 "system",
    # #                 """You are an AI guidance assistant.

    # # Answer the user's question using ONLY the provided context.

    # # Rules:
    # # 1. Do not use information that is not present in the context.
    # # 2. Do not make up or assume facts.
    # # 3. If the context does not contain enough information to answer,
    # #    clearly say that the information is not available in the
    # #    provided documents.
    # # 4. Keep the answer concise and clear.
    # # """,
    # #             ),
    # #             (
    # #                 "human",
    # #                 """Context:

    # # {context}

    # # Question:
    # # {question}

    # # Answer:""",
    # #             ),
    # #         ]
    # #     )

    # #     chain = prompt | get_llm()

    # #     response = chain.invoke(
    # #         {
    # #             "context": context,
    # #             "question": query,
    # #         }
    # #     )

    # #     return response.content
























    # # ===============================================================


    # """
    # RAG answer generation using Groq.
    # """

    # from langchain_core.prompts import ChatPromptTemplate
    # from langchain_groq import ChatGroq

    # from app.config import settings
    # from app.generation.citations import format_sources
    # from app.retrieval.confidence import is_low_confidence
    # from app.retrieval.confidence import (
    #     is_low_confidence,
    #     filter_relevant_documents,
    # )
    # from app.ingestion.embed_store import get_vectorstore


    # def get_llm():
    #     """Create and return the configured Groq chat model."""

    #     return ChatGroq(
    #         model=settings.GROQ_MODEL,
    #         api_key=settings.GROQ_API_KEY,
    #         temperature=0,
    #     )


    # def generate_answer(
    #     query: str,
    #     retrieved_docs_with_scores: list,
    # ) -> str:
    #     """Generate an answer using confident retrieved documents."""

    #     if not retrieved_docs_with_scores:
    #         return {
    #             "answer": (
    #                 "I couldn't find enough information in the available "
    #                 "documents to answer that question."
    #             ),
    #             "sources": [],
    #         }

    #     if is_low_confidence(retrieved_docs_with_scores):
    #         return {
    #             "answer": (
    #                 "I couldn't find enough information in the available "
    #                 "documents to answer that question."
    #             ),
    #             "sources": [],
    #         }

    #     documents = [
    #         document
    #         for document, score in retrieved_docs_with_scores
    #     ]

    #     context = "\n\n---\n\n".join(
    #         document.page_content
    #         for document in documents
    #     )

    #     prompt = ChatPromptTemplate.from_messages(
    #         [
    #             (
    #                 "system",
    #                 """You are an AI guidance assistant.

    # Answer the user's question using ONLY the provided context.

    # Rules:
    # 1. Do not use information that is not present in the context.
    # 2. Do not make up or assume facts.
    # 3. If the context does not contain enough information to answer,
    #    clearly say that the information is not available in the
    #    provided documents.
    # 4. Keep the answer concise and clear.
    # """,
    #             ),
    #             (
    #                 "human",
    #                 """Context:

    # {context}

    # Question:
    # {question}

    # Answer:""",
    #             ),
    #         ]
    #     )

    #     chain = prompt | get_llm()

    #     response = chain.invoke(
    #         {
    #             "context": context,
    #             "question": query,
    #         }
    #     )

    #     # return response.content
    #     return {
    #         "answer": response.content,
    #         "sources": format_sources(documents),
    #     }




    # from app.retrieval.confidence import is_low_confidence
    # from app.retrieval.retriever import retrieve_with_scores

    # def generate_rag_answer(query: str, k: int = 10):
    #     """Retrieve documents, filter irrelevant results, then generate an answer."""

    #     results = retrieve_with_scores(query, k=k)

    #     # if is_low_confidence(results):
    #     #     return {
    #     #         "answer": (
    #     #             "I couldn't find enough information in the available "
    #     #             "documents to answer that question."
    #     #         ),
    #     #         "sources": [],
    #     #     }

    #     # relevant_results = filter_relevant_documents(results)
    #     relevant_results = filter_relevant_documents(results)

    #     if is_low_confidence(relevant_results):
    #         return {
    #             "answer": (
    #                 "I couldn't find enough information in the available "
    #                 "documents to answer that question."
    #             ),
    #             "sources": [],
    #         }

    #     if not relevant_results:
    #         return {
    #             "answer": (
    #                 "I couldn't find enough information in the available "
    #                 "documents to answer that question."
    #             ),
    #             "sources": [],
    #         }

    #     return generate_answer(
    #         query=query,
    #         retrieved_docs_with_scores=relevant_results,
    #     )














































"""
RAG answer generation using Groq.
"""

from app.retrieval.query_context import build_retrieval_query
from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq
from app.retrieval.ambiguity import is_ambiguous_query
from app.llm import get_llm
# from app.config import settings
from app.generation.citations import format_sources
from app.retrieval.confidence import (
    is_low_confidence,
    filter_relevant_documents,
)
from app.retrieval.retriever import retrieve_with_scores
from app.retrieval.query_normalizer import normalize_query
from app.generation.query_rewriter import rewrite_query

from app.security.pii import (
    sanitize_for_llm,
    restore_pii,
)

# def get_llm():
#     """Create and return the configured Groq chat model."""

#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


def generate_answer(
    query: str,
    retrieved_docs_with_scores: list,
    conversation_history: list | None = None,
):
    """
    Generate an answer using:
    - retrieved internal documents
    - recent conversation history
    """

    if not retrieved_docs_with_scores:
        print("the three")

        return {
            "answer": (
                "I couldn't find enough information in the available "
                "documents to answer that question."
            ),
            "sources": [],
            "source": "Internal Knowledge",
        }

    if is_low_confidence(retrieved_docs_with_scores):
        print("the four")

        return {
            "answer": (
                "I couldn't find enough information in the available "
                "documents to answer that question."
            ),
            "sources": [],
            "source": "Internal Knowledge",
        }

    documents = [
        document
        for document, score in retrieved_docs_with_scores
    ]

    context = "\n\n---\n\n".join(
        document.page_content
        for document in documents
    )
    
    # ---------------------------------------------------------
    # PII protection before sending anything to the LLM
    # ---------------------------------------------------------

    # ONE shared map for the entire LLM request.
    pii_map = {}

    # Sanitize the question.
    sanitized_query, pii_map = sanitize_for_llm(
        query,
        pii_map,
    )

    # Sanitize retrieved context.
    sanitized_context, pii_map = sanitize_for_llm(
        context,
        pii_map,
    )

    # Sanitize conversation history.
    if conversation_history:
        sanitized_history_parts = []

        for message in conversation_history:
            role = message["role"].capitalize()
            content = message["content"]

            sanitized_content, pii_map = sanitize_for_llm(
                content,
                pii_map,
            )

            sanitized_history_parts.append(
                f"{role}: {sanitized_content}"
            )

        sanitized_history_text = "\n".join(
            sanitized_history_parts
        )
    else:
        sanitized_history_text = "No previous conversation."

    # ---------------------------------------------------------
    # Debug security check
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("[PII] LLM SANITIZATION")
    print("=" * 60)

    print("[PII] Detected tokens:", list(pii_map.keys()))

    print("\n[PII] Sanitized question:")
    print(sanitized_query)

    print("\n[PII] Sanitized context:")
    print(sanitized_context[:3000])

    print("\n[PII] Sanitized history:")
    print(sanitized_history_text[:2000])

    print("=" * 60)

    # ---------------------------------------------------------
    # Prompt
    # ---------------------------------------------------------

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an AI guidance assistant.

        Answer the user's question using ONLY the provided internal
        knowledge context.

        Use the conversation history only to understand references,
        follow-up questions, and context.

        Important:
        Sensitive values may appear as placeholders such as
        <PII_EMAIL_ADDRESS_1> or <PII_PHONE_NUMBER_1>.
        Treat these placeholders as real values and preserve them
        exactly when they are needed in your answer.

        Rules:

        1. Do not use information that is not present in the provided
        internal knowledge context.

        2. Do not make up or assume facts.

        3. If the internal context does not contain enough information
        to answer the question, clearly say that the information is
        not available in the provided documents.

        4. Maintain the language of the user's current question.

        5. Keep the answer concise and clear.

        6. If the user asks a follow-up question such as:
        "What about casual leave?"
        use the conversation history to understand what they are
        referring to, but answer using only the internal knowledge
        context.

        7. Never attempt to guess, reconstruct, or expose the original
        value behind a PII placeholder.

        Conversation history:

        {history}

        Internal knowledge context:

        {context}
        """,
                    ),
                    (
                        "human",
                        """Current question:

        {question}

        Answer:""",
                    ),
                ]
            )

    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "history": sanitized_history_text,
            "context": sanitized_context,
            "question": sanitized_query,
        }
    )

    # ---------------------------------------------------------
    # Restore PII after LLM generation
    # ---------------------------------------------------------

    final_answer = restore_pii(
        response.content,
        pii_map,
    )


    return {
        # "answer": response.content,
        "answer": final_answer,
        "sources": format_sources(documents),
        "source": "Internal Knowledge",
    }


def generate_rag_answer(
    query: str,
    k: int = 10,
    conversation_history: list | None = None,
    conversation_summary: str | None = None,
):
    """
    Retrieve documents, filter irrelevant results,
    and generate an answer using conversation history.
    """

    retrieval_query = build_retrieval_query(
    query=query,
    conversation_history=conversation_history,
    conversation_summary=conversation_summary,
)


    print("\n" + "=" * 60)
    print("ORIGINAL QUERY:", query)
    print("CONVERSATION SUMMARY:", conversation_summary)
    print("REWRITTEN QUERY:", retrieval_query)
    print("=" * 60)


    retrieval_query = normalize_query(retrieval_query)

    results = retrieve_with_scores(
        retrieval_query,
        k=k,
    )
    # -----------------------------------------------------
    # No Documents Found 
    # -----------------------------------------------------
    print("0000000") 
    if not results:
        print("hello====================0000000")
        return {
        "answer": (
            "I couldn't find any documents to answer your question."
            "Please upload documents and try againn."
        ),
        "sources": [],
    }

    print("[DEBUG] Results before filtering:", len(results))

    for i, item in enumerate(results):
        doc, score = item
        print(f"[DEBUG] Result {i + 1}")
        print("Score/distance:", score)
        print("Text:", doc.page_content[:300])

    relevant_results = filter_relevant_documents(
        results
    )
    print("[DEBUG] Results after filtering:", len(results))

    # -----------------------------------------------------
    # No useful documents found
    # -----------------------------------------------------

    if not relevant_results:
        print("the one")

        if is_ambiguous_query(retrieval_query):
            return {
                "answer": (
                    "Could you clarify what you would like to know? "
                    "For example, you can ask about the number of "
                    "annual leave days, eligibility, or the leave "
                    "application process."
                ),
                "sources": [],
                "source": "Clarification",
            }

        return {
            "answer": (
                "I couldn't find enough information in the available "
                "documents to answer that question."
            ),
            "sources": [],
            "source": "Internal Knowledge",
        }

    # -----------------------------------------------------
    # Confidence check
    # -----------------------------------------------------

    if is_low_confidence(relevant_results):
        print("the two")

        return {
            "answer": (
                "I couldn't find enough information in the available "
                "documents to answer that question."
            ),
            "sources": [],
            "source": "Internal Knowledge",
        }

    # # -----------------------------------------------------
    # # Generate answer
    # # -----------------------------------------------------

    return generate_answer(
        query=query,
        # retrieved_docs_with_scores=relevant_results,
        retrieved_docs_with_scores=results,
        conversation_history=conversation_history,
    )