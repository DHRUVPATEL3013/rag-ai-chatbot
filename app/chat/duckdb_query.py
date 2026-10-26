# # import re

# # from app.ingestion.duckdb_store import get_connection


# # EMPLOYEE_ID_PATTERN = r"\bEMP-\d{6}\b"


# # def query_duckdb(question: str):
# #     """
# #     Execute supported analytical queries against DuckDB.

# #     Supports:
# #     - employee salary
# #     - employee department
# #     - average salary
# #     - employee count by department
# #     - total salary of multiple employees
# #     """

# #     q = question.lower().strip()

# #     con = get_connection()

# #     try:

# #         # --------------------------------------------------
# #         # Extract ALL employee IDs
# #         # --------------------------------------------------

# #         employee_ids = re.findall(
# #             EMPLOYEE_ID_PATTERN,
# #             question,
# #             re.IGNORECASE,
# #         )

# #         employee_ids = list(
# #             dict.fromkeys(
# #                 employee_id.upper()
# #                 for employee_id in employee_ids
# #             )
# #         )

# #         # --------------------------------------------------
# #         # Multiple employee salary aggregation
# #         # --------------------------------------------------

# #         if (
# #             len(employee_ids) >= 2
# #             and "salary" in q
# #             and any(
# #                 word in q
# #                 for word in [
# #                     "total",
# #                     "sum",
# #                     "combined",
# #                     "together",
# #                 ]
# #             )
# #         ):

# #             placeholders = ", ".join(
# #                 "?" for _ in employee_ids
# #             )

# #             result = con.execute(
# #                 f"""
# #                 SELECT
# #                     SUM(salary),
# #                     COUNT(*)
# #                 FROM employees
# #                 WHERE employee_id IN ({placeholders})
# #                 """,
# #                 employee_ids,
# #             ).fetchone()

# #             total_salary = result[0]
# #             found_count = result[1]

# #             if found_count == 0:
# #                 return (
# #                     "None of the specified employees "
# #                     "were found."
# #                 )

# #             if found_count != len(employee_ids):
# #                 return (
# #                     f"Found {found_count} of "
# #                     f"{len(employee_ids)} specified employees."
# #                 )

# #             employee_text = " and ".join(
# #                 employee_ids
# #             )

# #             return (
# #                 f"The total salary of "
# #                 f"{employee_text} is "
# #                 f"₹{total_salary:,.0f}."
# #             )

# #         # --------------------------------------------------
# #         # Compare / average salary of multiple employees
# #         # --------------------------------------------------

# #         if (
# #             len(employee_ids) >= 2
# #             and "salary" in q
# #             and "average" in q
# #         ):

# #             placeholders = ", ".join(
# #                 "?" for _ in employee_ids
# #             )

# #             result = con.execute(
# #                 f"""
# #                 SELECT AVG(salary)
# #                 FROM employees
# #                 WHERE employee_id IN ({placeholders})
# #                 """,
# #                 employee_ids,
# #             ).fetchone()

# #             if result[0] is None:
# #                 return (
# #                     "None of the specified employees "
# #                     "were found."
# #                 )

# #             return (
# #                 f"The average salary of the specified "
# #                 f"employees is ₹{result[0]:,.2f}."
# #             )

# #         # --------------------------------------------------
# #         # Employee ID lookup
# #         # --------------------------------------------------

# #         if len(employee_ids) == 1:

# #             employee_id = employee_ids[0]

# #             # --------------------------------------------------
# #             # Salary
# #             # --------------------------------------------------

# #             if "salary" in q:

# #                 result = con.execute(
# #                     """
# #                     SELECT salary
# #                     FROM employees
# #                     WHERE employee_id = ?
# #                     """,
# #                     [employee_id],
# #                 ).fetchone()

# #                 if not result:
# #                     return (
# #                         f"No employee found for "
# #                         f"{employee_id}."
# #                     )

# #                 return (
# #                     f"The salary of {employee_id} "
# #                     f"is ₹{result[0]:,.0f}."
# #                 )

# #             # --------------------------------------------------
# #             # Department
# #             # --------------------------------------------------

# #             if "department" in q:

# #                 result = con.execute(
# #                     """
# #                     SELECT department
# #                     FROM employees
# #                     WHERE employee_id = ?
# #                     """,
# #                     [employee_id],
# #                 ).fetchone()

# #                 if not result:
# #                     return (
# #                         f"No employee found for "
# #                         f"{employee_id}."
# #                     )

# #                 return (
# #                     f"{employee_id} belongs to the "
# #                     f"{result[0]} department."
# #                 )

# #         # --------------------------------------------------
# #         # Average salary
# #         # --------------------------------------------------

# #         if (
# #             "average salary" in q
# #             or "average salary of all employees" in q
# #         ):

# #             result = con.execute(
# #                 """
# #                 SELECT AVG(salary)
# #                 FROM employees
# #                 """
# #             ).fetchone()

# #             return (
# #                 f"The average salary is "
# #                 f"₹{result[0]:,.2f}."
# #             )

# #         # --------------------------------------------------
# #         # Employee count by department
# #         # --------------------------------------------------

# #         department_match = re.search(
# #             r"in the\s+(\w+)\s+department",
# #             q,
# #         )

# #         if (
# #             "how many employees" in q
# #             and department_match
# #         ):

# #             department = department_match.group(1)

# #             result = con.execute(
# #                 """
# #                 SELECT COUNT(*)
# #                 FROM employees
# #                 WHERE LOWER(department) = LOWER(?)
# #                 """,
# #                 [department],
# #             ).fetchone()

# #             return (
# #                 f"There are {result[0]} employees "
# #                 f"in the {department} department."
# #             )

# #         # --------------------------------------------------
# #         # Unsupported DuckDB query
# #         # --------------------------------------------------

# #         return None

# #     finally:
# #         con.close()





# # ------------kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk

# import re

# from app.ingestion.duckdb_store import get_connection


# EMPLOYEE_ID_PATTERN = r"\bEMP-\d{6}\b"


# def extract_employee_ids(value: str) -> list[str]:
#     return list(
#         dict.fromkeys(
#             match.upper()
#             for match in re.findall(
#                 EMPLOYEE_ID_PATTERN,
#                 value,
#                 re.IGNORECASE,
#             )
#         )
#     )


# def execute_structured_query(query: dict):
#     operation = query.get("operation")
#     field = query.get("field")
#     employee_ids = query.get("employee_ids", [])
#     filters = query.get("filters", {})

#     con = get_connection()

#     try:

#         # ==================================================
#         # EMPLOYEE LOOKUP
#         # ==================================================

#         if operation == "lookup":

#             employee_id = query.get("employee_id")

#             if not employee_id:
#                 return None

#             if field not in {
#                 "salary",
#                 "department",
#                 "employee_name",
#                 "location",
#                 "employment_type",
#                 "status",
#                 "performance_rating",
#                 "years_experience",
#                 "joining_year",
#                 "annual_bonus",
#             }:
#                 return None

#             sql = f"""
#                 SELECT {field}
#                 FROM employees
#                 WHERE employee_id = ?
#             """

#             result = con.execute(
#                 sql,
#                 [employee_id],
#             ).fetchone()

#             if not result:
#                 return {
#                     "found": False,
#                     "employee_id": employee_id,
#                 }

#             return {
#                 "found": True,
#                 "employee_id": employee_id,
#                 "field": field,
#                 "value": result[0],
#             }

#         # ==================================================
#         # SUM
#         # ==================================================

#         if operation == "sum":

#             if field not in {
#                 "salary",
#                 "annual_bonus",
#             }:
#                 return None

#             if not employee_ids:
#                 return None

#             placeholders = ", ".join(
#                 ["?"] * len(employee_ids)
#             )

#             sql = f"""
#                 SELECT SUM({field})
#                 FROM employees
#                 WHERE employee_id IN ({placeholders})
#             """

#             result = con.execute(
#                 sql,
#                 employee_ids,
#             ).fetchone()

#             return {
#                 "operation": "sum",
#                 "field": field,
#                 "employee_ids": employee_ids,
#                 "value": result[0] if result else None,
#             }

#         # ==================================================
#         # AVERAGE
#         # ==================================================

#         if operation == "average":

#             if field not in {
#                 "salary",
#                 "annual_bonus",
#             }:
#                 return None

#             sql = f"""
#                 SELECT AVG({field})
#                 FROM employees
#             """

#             result = con.execute(sql).fetchone()

#             return {
#                 "operation": "average",
#                 "field": field,
#                 "value": result[0] if result else None,
#             }

#         # ==================================================
#         # COUNT
#         # ==================================================

#         if operation == "count":

#             department = filters.get("department")

#             if department:

#                 sql = """
#                     SELECT COUNT(*)
#                     FROM employees
#                     WHERE LOWER(department) = LOWER(?)
#                 """

#                 result = con.execute(
#                     sql,
#                     [department],
#                 ).fetchone()

#             else:

#                 sql = """
#                     SELECT COUNT(*)
#                     FROM employees
#                 """

#                 result = con.execute(sql).fetchone()

#             return {
#                 "operation": "count",
#                 "department": department,
#                 "value": result[0] if result else 0,
#             }

#         return None

#     finally:
#         con.close()


# def query_duckdb(question: str):
#     """
#     Backward-compatible wrapper.

#     Converts a simple natural-language query into the
#     structured DuckDB execution flow.
#     """

#     from app.chat.query_intent import extract_query_intent

#     intent = extract_query_intent(question)

#     if not intent:
#         return None

#     result = execute_structured_query(intent)

#     if result is None:
#         return None

#     # --------------------------------------------------
#     # Format result for existing /chat endpoint
#     # --------------------------------------------------

#     if result.get("found") is False:
#         employee_id = result.get("employee_id")
#         return f"No employee found for {employee_id}."

#     operation = result.get("operation")
#     field = result.get("field")
#     value = result.get("value")

#     if operation == "lookup":

#         employee_id = result["employee_id"]

#         if field == "salary":
#             return (
#                 f"The salary of {employee_id} "
#                 f"is ₹{value:,.0f}."
#             )

#         if field == "department":
#             return (
#                 f"{employee_id} belongs to the "
#                 f"{value} department."
#             )

#         return f"The {field} of {employee_id} is {value}."

#     if operation == "sum":

#         employee_ids = result.get(
#             "employee_ids",
#             [],
#         )

#         if value is None:
#             return (
#                 "I couldn't calculate the requested total."
#             )

#         if field == "salary":
#             return (
#                 f"The total salary of "
#                 f"{' and '.join(employee_ids)} "
#                 f"is ₹{value:,.0f}."
#             )

#         if field == "annual_bonus":
#             return (
#                 f"The total annual bonus of "
#                 f"{' and '.join(employee_ids)} "
#                 f"is ₹{value:,.0f}."
#             )

#     if operation == "average":

#         if value is None:
#             return (
#                 "I couldn't calculate the requested average."
#             )

#         if field == "salary":
#             return (
#                 f"The average salary is "
#                 f"₹{value:,.2f}."
#             )

#         if field == "annual_bonus":
#             return (
#                 f"The average annual bonus is "
#                 f"₹{value:,.2f}."
#             )

#     if operation == "count":

#         department = result.get("department")

#         if department:
#             return (
#                 f"There are {value} employees "
#                 f"in the {department} department."
#             )

#         return f"There are {value} employees."

#     return None



import re

from app.ingestion.duckdb_store import get_connection


EMPLOYEE_ID_PATTERN = r"\bEMP-\d{6}\b"


def extract_employee_ids(value: str) -> list[str]:
    return list(
        dict.fromkeys(
            match.upper()
            for match in re.findall(
                EMPLOYEE_ID_PATTERN,
                value,
                re.IGNORECASE,
            )
        )
    )


def execute_structured_query(query: dict):
    operation = str(query.get("operation", "")).strip().lower()
    field = str(query.get("field", "")).strip().lower()
    employee_ids = [str(x).strip().upper() for x in query.get("employee_ids", [])]
    filters = query.get("filters", {}) or {}

    # Normalize a single employee_id too, because lookup intents use
    # employee_id while aggregation intents may use employee_ids.
    single_employee_id = str(query.get("employee_id", "")).strip().upper()
    if single_employee_id and not employee_ids:
        employee_ids = [single_employee_id]

    con = get_connection()

    try:

        # ==================================================
        # EMPLOYEE LOOKUP
        # ==================================================

        if operation == "lookup":

            employee_id = single_employee_id or (employee_ids[0] if employee_ids else "")

            if not employee_id:
                return None

            if field not in {
                "salary",
                "department",
                "employee_name",
                "location",
                "employment_type",
                "status",
                "performance_rating",
                "years_experience",
                "joining_year",
                "annual_bonus",
            }:
                return None

            sql = f"""
                SELECT {field}
                FROM employees
                WHERE employee_id = ?
            """

            result = con.execute(
                sql,
                [employee_id],
            ).fetchone()

            if not result:
                return {
                    "found": False,
                    "employee_id": employee_id,
                }

            return {
                "found": True,
                "employee_id": employee_id,
                "field": field,
                "value": result[0],
            }

        # ==================================================
        # SUM
        # ==================================================

        if operation == "sum":

            if field not in {
                "salary",
                "annual_bonus",
            }:
                return None

            if not employee_ids:
                return None

            placeholders = ", ".join(
                ["?"] * len(employee_ids)
            )

            sql = f"""
                SELECT SUM({field})
                FROM employees
                WHERE employee_id IN ({placeholders})
            """

            result = con.execute(
                sql,
                employee_ids,
            ).fetchone()

            return {
                "operation": "sum",
                "field": field,
                "employee_ids": employee_ids,
                "value": result[0] if result else None,
            }

        # ==================================================
        # AVERAGE
        # ==================================================

        if operation == "average":

            if field not in {
                "salary",
                "annual_bonus",
            }:
                return None

            sql = f"""
                SELECT AVG({field})
                FROM employees
            """

            result = con.execute(sql).fetchone()

            return {
                "operation": "average",
                "field": field,
                "value": result[0] if result else None,
            }

        # ==================================================
        # COUNT
        # ==================================================

        if operation == "count":

            department = filters.get("department")

            if department:

                sql = """
                    SELECT COUNT(*)
                    FROM employees
                    WHERE LOWER(department) = LOWER(?)
                """

                result = con.execute(
                    sql,
                    [department],
                ).fetchone()

            else:

                sql = """
                    SELECT COUNT(*)
                    FROM employees
                """

                result = con.execute(sql).fetchone()

            return {
                "operation": "count",
                "department": department,
                "value": result[0] if result else 0,
            }

        return None

    finally:
        con.close()


def query_duckdb(question: str):
    """
    Convert a natural-language question into a structured query,
    execute it against DuckDB, and return a user-friendly answer.
    """

    from app.chat.query_intent import extract_query_intent

    # --------------------------------------------------
    # 1. Extract structured intent
    # --------------------------------------------------

    intent = extract_query_intent(question)

    if not intent:
        return None

    print("=" * 60)
    print("[DUCKDB QUERY]")
    print("Question :", question)
    print("Intent   :", intent)
    print("=" * 60)

    # --------------------------------------------------
    # 2. Execute structured query
    # --------------------------------------------------

    result = execute_structured_query(intent)

    print("[DUCKDB RESULT]")
    print(result)
    print("=" * 60)

    if result is None:
        return None

    # --------------------------------------------------
    # 3. Employee not found
    # --------------------------------------------------

    if result.get("found") is False:
        employee_id = result.get("employee_id")

        return f"No employee found for {employee_id}."

    # --------------------------------------------------
    # 4. Lookup
    # --------------------------------------------------

    operation = result.get("operation")

    # IMPORTANT:
    # execute_structured_query() currently does not include
    # "operation" in lookup results, so detect lookup using
    # the presence of "employee_id" + "field".
    if (
        result.get("employee_id")
        and result.get("field")
        and "value" in result
    ):

        employee_id = result["employee_id"]
        field = result["field"]
        value = result["value"]

        if field == "salary":
            return (
                f"The salary of {employee_id} "
                f"is ₹{value:,.0f}."
            )

        if field == "department":
            return (
                f"{employee_id} belongs to the "
                f"{value} department."
            )

        if field == "employee_name":
            return (
                f"The name of {employee_id} "
                f"is {value}."
            )

        if field == "location":
            return (
                f"{employee_id} is located in {value}."
            )

        if field == "employment_type":
            return (
                f"{employee_id} has employment type "
                f"{value}."
            )

        if field == "status":
            return (
                f"The status of {employee_id} "
                f"is {value}."
            )

        if field == "performance_rating":
            return (
                f"The performance rating of {employee_id} "
                f"is {value}."
            )

        if field == "years_experience":
            return (
                f"{employee_id} has {value} years of experience."
            )

        if field == "joining_year":
            return (
                f"{employee_id} joined in {value}."
            )

        if field == "annual_bonus":
            return (
                f"The annual bonus of {employee_id} "
                f"is ₹{value:,.0f}."
            )

        return f"The {field} of {employee_id} is {value}."

    # --------------------------------------------------
    # 5. SUM
    # --------------------------------------------------

    if operation == "sum":

        employee_ids = result.get("employee_ids", [])
        field = result.get("field")
        value = result.get("value")

        if value is None:
            return "I couldn't calculate the requested total."

        employee_text = " and ".join(employee_ids)

        if field == "salary":
            return (
                f"The total salary of {employee_text} "
                f"is ₹{value:,.0f}."
            )

        if field == "annual_bonus":
            return (
                f"The total annual bonus of {employee_text} "
                f"is ₹{value:,.0f}."
            )

        return (
            f"The total {field} of {employee_text} "
            f"is {value}."
        )

    # --------------------------------------------------
    # 6. AVERAGE
    # --------------------------------------------------

    if operation == "average":

        field = result.get("field")
        value = result.get("value")

        if value is None:
            return "I couldn't calculate the requested average."

        if field == "salary":
            return f"The average salary is ₹{value:,.2f}."

        if field == "annual_bonus":
            return (
                f"The average annual bonus is "
                f"₹{value:,.2f}."
            )

        return f"The average {field} is {value:,.2f}."

    # --------------------------------------------------
    # 7. COUNT
    # --------------------------------------------------

    if operation == "count":

        department = result.get("department")
        value = result.get("value", 0)

        if department:
            return (
                f"There are {value} employees "
                f"in the {department} department."
            )

        return f"There are {value} employees."

    # --------------------------------------------------
    # 8. Unsupported result
    # --------------------------------------------------

    return None