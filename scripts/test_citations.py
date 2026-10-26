from app.generation.citations import format_sources
from app.retrieval.retriever import get_retriever


retriever = get_retriever(k=2)

query = "How many days of annual leave do employees get?"

documents = retriever.invoke(query)

sources = format_sources(documents)

print("\nQuestion:")
print(query)

print("\nSources:")

for source in sources:
    print(f"Source: {source['source']}")
    print(f"Page: {source['page']}")