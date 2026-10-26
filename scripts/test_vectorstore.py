from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()

print("Vector store created successfully.")
print("Collection:", vectorstore._collection.name)