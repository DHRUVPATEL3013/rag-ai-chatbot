from app.ingestion.embed_store import get_embedding_function


embedding_function = get_embedding_function()

text = "Employees are entitled to 21 days of annual leave per year."

vector = embedding_function.embed_query(text)

print("Vector type:", type(vector))
print("Vector dimensions:", len(vector))
print("First 10 values:", vector[:10])