from app.ingestion.duckdb_store import (
    excel_to_duckdb,
    get_connection,
)


excel_file = "data/uploads/large_non_sensitive_excel_test.xlsx"


# Build DuckDB tables
excel_to_duckdb(excel_file)


con = get_connection()

print("=" * 60)
print("[TEST] EMP-000001")
print("=" * 60)

result = con.execute("""
    SELECT
        employee_id,
        employee_name,
        department,
        salary
    FROM employees
    WHERE employee_id = 'EMP-000001'
""").fetchall()

for row in result:
    print(row)


print("=" * 60)
print("[TEST] Average salary")
print("=" * 60)

result = con.execute("""
    SELECT AVG(salary)
    FROM employees
""").fetchone()

print(result)


print("=" * 60)
print("[TEST] IT employees")
print("=" * 60)

result = con.execute("""
    SELECT COUNT(*)
    FROM employees
    WHERE department = 'IT'
""").fetchone()

print(result)


con.close()
