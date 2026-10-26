# """
# Centralized config loading from environment variables (.env).
# Every other module should import `settings` from here rather than
# calling os.environ directly.
# """

# # TODO: use python-dotenv's load_dotenv() plus os.environ / pydantic
# # BaseSettings to load:
# #   GROQ_API_KEY, GROQ_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME,
# #   EMBEDDING_MODEL, DATABASE_URL, CONFIDENCE_THRESHOLD
# # Expose them as a `settings` object other modules can import.



"""
Centralized config loading from environment variables (.env).
Every other module should import `settings` from here rather than
calling os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    RELEVANCE_THRESHOLD: float = 10.0
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = ""

    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "ai_guidance_documents"

    EMBEDDING_MODEL: str = (
  
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )


    DATABASE_URL: str = ""

    CONFIDENCE_THRESHOLD: float = 10.0

    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_SESSION_MINUTES: int = 30

    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "qwen3:4b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5-nano"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()