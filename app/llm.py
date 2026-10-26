# from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
from app.config import settings


def get_llm():
    provider = getattr(settings, "LLM_PROVIDER", "groq").lower()

    # =========================================================
    # OLLAMA - currently not used
    # =========================================================
    # if provider == "ollama":
    #     return ChatOllama(
    #         model=getattr(settings, "OLLAMA_MODEL", "qwen3:4b"),
    #         base_url=getattr(
    #             settings,
    #             "OLLAMA_BASE_URL",
    #             "http://localhost:11434",
    #         ),
    #         temperature=0,
    #     )

    # =========================================================
    # GROQ - CURRENTLY USED
    # =========================================================
    if provider == "groq": 
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0,
        )

    # =========================================================
    # OPENAI - currently not used
    # =========================================================
    # if provider == "openai":
    #     return ChatOpenAI(
    #         model=getattr(settings, "OPENAI_MODEL", "gpt-5.6-luna"),
    #         api_key=settings.OPENAI_API_KEY,
    #         temperature=0,
    #     )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


 