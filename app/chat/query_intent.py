"""
Natural-language query -> structured employee database intent.

The LLM determines WHAT the user wants.
Python/DuckDB determines HOW to execute it.
"""

import json

from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq

# from app.config import settings
from app.llm import get_llm


# def get_llm():
#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You convert natural-language questions about the employee
database into structured JSON.

Available table:

employees

Available columns:

employee_id
employee_name
department
location
employment_type
status
performance_rating
salary
years_experience
joining_year
annual_bonus

Supported operations:

1. lookup
2. sum
3. average
4. count

Rules:

1. Return ONLY valid JSON.
2. Never return SQL.
3. Never answer the question.
4. Never invent employee IDs.
5. Preserve employee IDs exactly.
6. For salary questions use field "salary".
7. For bonus questions use field "annual_bonus".
8. For employee count questions use operation "count".
9. For total/combined/together/sum/add/earn in total/
   make combined or equivalent wording, use operation "sum".
10. For average questions use operation "average".
11. For a single employee attribute question use operation "lookup".
12. If a department is mentioned in a count query,
    put it under filters.department.
13. If multiple employee IDs are mentioned in a sum query,
    put all of them into employee_ids.
14. If the query cannot be represented using the supported
    operations, return:
    {{"operation": "unsupported"}}

Examples:

Question:
What is the salary of EMP-000001?

JSON:
{{
  "operation": "lookup",
  "field": "salary",
  "employee_id": "EMP-000001"
}}

Question:
Which department does EMP-000001 belong to?

JSON:
{{
  "operation": "lookup",
  "field": "department",
  "employee_id": "EMP-000001"
}}

Question:
What do EMP-000001 and EMP-040054 earn in total?

JSON:
{{
  "operation": "sum",
  "field": "salary",
  "employee_ids": [
    "EMP-000001",
    "EMP-040054"
  ]
}}

Question:
Add the salaries of EMP-000001 and EMP-000002.

JSON:
{{
  "operation": "sum",
  "field": "salary",
  "employee_ids": [
    "EMP-000001",
    "EMP-000002"
  ]
}}

Question:
Give me the employee count in the Finance department.

JSON:
{{
  "operation": "count",
  "filters": {{
    "department": "Finance"
  }}
}}

Question:
How many people work in the Finance department?

JSON:
{{
  "operation": "count",
  "filters": {{
    "department": "Finance"
  }}
}}

Question:
What is the average salary?

JSON:
{{
  "operation": "average",
  "field": "salary"
}}

Question:
What is the company's remote work policy?

JSON:
{{
  "operation": "unsupported"
}}

Return ONLY JSON.
""",
        ),
        (
            "human",
            """
Question:

{question}
""",
        ),
    ]
)

import re


def detect_simple_intent(question: str) -> dict:
    """
    Detect simple employee database queries without using an LLM.

    This handles deterministic patterns such as:
    - salary of EMP-000001
    - bonus of EMP-000001
    - department of EMP-000001
    - total salary of two employees
    - average salary
    - employee count
    """

    question_lower = question.lower()

    # --------------------------------------------------
    # Find employee IDs
    # --------------------------------------------------

    employee_ids = re.findall(
        r"\bEMP-\d{6}\b",
        question.upper()
    )

    # --------------------------------------------------
    # Detect field
    # --------------------------------------------------

    field = None

    if (
        "salary" in question_lower
        or "salaries" in question_lower
        or "earn" in question_lower
        or "earning" in question_lower
        or "earnings" in question_lower
    ):
        field = "salary"

    elif (
        "bonus" in question_lower
        or "bonuses" in question_lower
        or "annual bonus" in question_lower
    ):
        field = "annual_bonus"

    elif "department" in question_lower:
        field = "department"

    elif "location" in question_lower:
        field = "location"

    elif "employment type" in question_lower:
        field = "employment_type"

    elif "status" in question_lower:
        field = "status"

    elif "performance rating" in question_lower:
        field = "performance_rating"

    elif "years of experience" in question_lower:
        field = "years_experience"

    elif "joining year" in question_lower:
        field = "joining_year"

    # --------------------------------------------------
    # COUNT
    # --------------------------------------------------

    if (
        "how many employees" in question_lower
        or "how many people" in question_lower
        or "employee count" in question_lower
        or "count of employees" in question_lower
        or "number of employees" in question_lower
    ):
        result = {
            "operation": "count"
        }

        # Department filter
        departments = [
            "finance",
            "engineering",
            "hr",
            "human resources",
            "marketing",
            "sales",
            "operations",
            "it",
            "legal",
        ]

        for department in departments:
            if department in question_lower:
                if department == "human resources":
                    department = "HR"

                result["filters"] = {
                    "department": department.title()
                    if department != "it"
                    else "IT"
                }
                break

        return result

    # --------------------------------------------------
    # AVERAGE
    # --------------------------------------------------

    if "average" in question_lower and field:
        return {
            "operation": "average",
            "field": field
        }

    # --------------------------------------------------
    # SUM
    # --------------------------------------------------

    sum_words = [
        "total",
        "combined",
        "together",
        "sum",
        "add",
        "in total",
    ]

    is_sum = any(
        word in question_lower
        for word in sum_words
    )

    if is_sum and field and len(employee_ids) >= 2:
        return {
            "operation": "sum",
            "field": field,
            "employee_ids": employee_ids,
        }

    # --------------------------------------------------
    # LOOKUP
    # --------------------------------------------------

    if len(employee_ids) == 1 and field:
        return {
            "operation": "lookup",
            "field": field,
            "employee_id": employee_ids[0],
        }

    # --------------------------------------------------
    # Nothing deterministic found
    # --------------------------------------------------

    return {}


# def extract_query_intent(question: str) -> dict:
#     """
#     Convert a natural-language question into a structured
#     database intent.
#     """

#     chain = PROMPT | get_llm()

#     response = chain.invoke(
#         {
#             "question": question,
#         }
#     )

#     content = response.content.strip()

#     # -----------------------------------------------
#     # Remove accidental markdown code fences
#     # -----------------------------------------------

#     if content.startswith("```"):
#         content = content.replace("```json", "")
#         content = content.replace("```", "")
#         content = content.strip()

#     # -----------------------------------------------
#     # Parse JSON
#     # -----------------------------------------------

#     try:
#         result = json.loads(content)

#     except json.JSONDecodeError:

#         print("=" * 60)
#         print("[QUERY INTENT ERROR]")
#         print("Question :", question)
#         print("LLM output:", content)
#         print("=" * 60)

#         return {}

#     # -----------------------------------------------
#     # Validate basic structure
#     # -----------------------------------------------

#     if not isinstance(result, dict):
#         return {}

#     print("=" * 60)
#     print("[QUERY INTENT]")
#     print("Question :", question)
#     print("Intent   :", result)
#     print("=" * 60)

#     return result

def extract_query_intent(question: str) -> dict:
    """
    Convert a natural-language question into a structured
    database intent.

    Simple queries are handled deterministically.
    The LLM is used only when Python cannot confidently
    determine the intent.
    """

    # ==================================================
    # STEP 1: Deterministic detection
    # ==================================================

    simple_intent = detect_simple_intent(question)

    if simple_intent:
        print("=" * 60)
        print("[QUERY INTENT - PYTHON]")
        print("Question :", question)
        print("Intent   :", simple_intent)
        print("=" * 60)

        return simple_intent

    # ==================================================
    # STEP 2: LLM fallback
    # ==================================================

    print("=" * 60)
    print("[QUERY INTENT - LLM FALLBACK]")
    print("Question :", question)
    print("=" * 60)

    chain = PROMPT | get_llm()

    response = chain.invoke(
        {
            "question": question,
        }
    )

    content = response.content.strip()

    # --------------------------------------------------
    # Remove accidental markdown code fences
    # --------------------------------------------------

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    # --------------------------------------------------
    # Parse JSON
    # --------------------------------------------------

    try:
        result = json.loads(content)

    except json.JSONDecodeError:
        print("=" * 60)
        print("[QUERY INTENT ERROR]")
        print("Question :", question)
        print("LLM output:", content)
        print("=" * 60)
        return {}

    # --------------------------------------------------
    # Validate basic structure
    # --------------------------------------------------

    if not isinstance(result, dict):
        return {}

    print("=" * 60)
    print("[QUERY INTENT - LLM]")
    print("Question :", question)
    print("Intent   :", result)
    print("=" * 60)

    return result