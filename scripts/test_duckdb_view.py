import duckdb

DB_PATH = "data/duckdb/knowledge.duckdb"

conn = duckdb.connect(DB_PATH)

print("=" * 60)
print("DUCKDB DATABASE")
print("=" * 60)

print("\n[TABLES]")
tables = conn.execute("SHOW TABLES").fetchall()

for table in tables:
    print("-", table[0])

print("\n[ROW COUNTS]")

for table in tables:
    table_name = table[0]

    count = conn.execute(
        f'SELECT COUNT(*) FROM "{table_name}"'
    ).fetchone()[0]

    print(f"{table_name}: {count}")

print("\n[EMPLOYEE TEST]")

result = conn.execute("""
    SELECT *
    FROM employees
    WHERE employee_id = 'EMP-000001'
""").fetchall()

for row in result:
    print(row)

conn.close()