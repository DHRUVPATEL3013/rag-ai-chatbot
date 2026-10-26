import re


EMPLOYEE_ID_PATTERN = r"\bemp-\d{6}\b"

EXCEL_PATTERNS = [
    # Strongest signal: actual employee ID
    EMPLOYEE_ID_PATTERN,

    # Explicit employee-data fields
    r"\bsalary\b",
    r"\bsalaries\b",
    r"\bearn\b",
    r"\bearnings\b",
    r"\bannual bonus\b",
    r"\bperformance rating\b",
    r"\byears of experience\b",
    r"\bemployment type\b",
    r"\bjoining year\b",

    # Explicit data operations
    r"\bhow many employees\b",
    r"\bcount of employees\b",
    r"\bnumber of employees\b",
    r"\baverage salary\b",
    r"\baverage salaries\b",
    r"\btotal salary\b",
    r"\btotal salaries\b",
    r"\bsum of salaries\b",
    r"\bhighest salary\b",
    r"\blowest salary\b",
    r"\bmaximum salary\b",
    r"\bminimum salary\b",
]


def classify_query(query: str) -> str:
    query_lower = query.lower().strip()

    for pattern in EXCEL_PATTERNS:
        if re.search(pattern, query_lower):
            print(
                f"[ROUTER] Excel query detected: {query}"
            )
            return "duckdb"

    print(
        f"[ROUTER] Normal knowledge query detected: {query}"
    )
    return "rag"