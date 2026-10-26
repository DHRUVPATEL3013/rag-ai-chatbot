# import asyncio

# from app.db.session import engine
# from app.db.models import Base

# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# asyncio.run(create_tables())

from .ingestion.embed_store import get_vectorstore

vectorstore = get_vectorstore() 

print("Collection name:", vectorstore._collection.name)
print("Total chunks:", vectorstore._collection.count())

results = vectorstore.similarity_search_with_score(
    "By what time should employees arrive at the office?",
    k=5,
)

for i, (doc, distance) in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("Distance:", distance)
    print("Metadata:", doc.metadata)
    print("Text:", doc.page_content[:500])



