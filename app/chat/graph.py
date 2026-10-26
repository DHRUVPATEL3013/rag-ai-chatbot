"""
LangGraph state machine tying retrieval + generation + fallback together
— Phase 4.

This is what makes the "low confidence -> fallback" branch declarative
instead of a pile of if/else in chain.py.
"""


def build_graph():
    """
    TODO: Define a langgraph.graph.StateGraph with nodes:
      - "retrieve"  — runs retrieval + confidence check
      - "generate"  — internal-knowledge answer (chat.chain)
      - "fallback"  — chat.fallback.call_external_ai + log_unanswered
    Add a conditional edge after "retrieve": low confidence -> "fallback",
    otherwise -> "generate". Compile and return the graph.
    """
    raise NotImplementedError
