import duckdb
from pathlib import Path
import pandas as pd


DUCKDB_DIR = Path("data/duckdb")
DUCKDB_DIR.mkdir(parents=True, exist_ok=True)

DUCKDB_PATH = DUCKDB_DIR / "knowledge.duckdb"


def get_connection():
    return duckdb.connect(str(DUCKDB_PATH))


def excel_to_duckdb(file_path: str):
    """
    Load every Excel sheet into a DuckDB table.
    """

    print("=" * 60)
    print("[DUCKDB] Loading Excel:", file_path)
    print("=" * 60)

    excel_file = pd.ExcelFile(file_path)

    con = get_connection()

    tables = []

    for sheet_name in excel_file.sheet_names:

        print(f"[DUCKDB] Processing sheet: {sheet_name}")

        df = pd.read_excel(
            file_path,
            sheet_name=sheet_name,
        )

        # Convert sheet name into a safe table name
        table_name = (
            sheet_name
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        print(
            f"[DUCKDB] Sheet: {sheet_name} | "
            f"Rows: {len(df)} | Columns: {len(df.columns)}"
        )

        con.register("temp_df", df)

        con.execute(
            f'''
            CREATE OR REPLACE TABLE "{table_name}" AS
            SELECT * FROM temp_df
            '''
        )

        tables.append(table_name)

    con.close()

    print("-" * 60)
    print("[DUCKDB] Tables created:")

    for table in tables:
        print(f"  - {table}")

    print("=" * 60)

    return tables