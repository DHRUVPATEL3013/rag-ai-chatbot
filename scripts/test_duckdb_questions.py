import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.chat.query_router import classify_query
from app.chat.query_intent import detect_simple_intent
from app.chat.duckdb_query import execute_structured_query

DUCKDB_QUESTIONS = [

    # =========================
    # SALARY
    # =========================

    "What is the salary of EMP-000001?",
    "What is the salary of EMP-000002?",
    "What is the salary of EMP-040054?",
    "How much does EMP-000001 earn?",
    "How much does EMP-000002 earn?",
    "How much does EMP-040054 earn?",
    "What are the earnings of EMP-000001?",
    "What are the earnings of EMP-000002?",
    "What is the annual salary of EMP-000001?",
    "What is the annual salary of EMP-040054?",
    "Give me the salary of EMP-000001.",
    "Tell me how much EMP-000002 earns.",
    "Show the salary for EMP-040054.",
    "Find the salary of EMP-000001.",
    "Look up EMP-000002's salary.",
    "How much is EMP-000001 paid?",
    "What does EMP-000001 make annually?",
    "What does EMP-000002 earn?",
    "What does EMP-040054 earn?",
    "Give me EMP-000001's salary information.",

    # =========================
    # MULTIPLE EMPLOYEES
    # =========================

    "What do EMP-000001 and EMP-000002 earn?",
    "What do EMP-000001 and EMP-040054 earn in total?",
    "What is the combined salary of EMP-000001 and EMP-000002?",
    "What is the total salary of EMP-000001 and EMP-040054?",
    "Add the salaries of EMP-000001 and EMP-000002.",
    "What is the sum of the salaries of EMP-000001 and EMP-040054?",
    "Compare the salaries of EMP-000001 and EMP-000002.",
    "Which employee earns more, EMP-000001 or EMP-000002?",
    "Which has the higher salary, EMP-000001 or EMP-040054?",
    "Show me the salaries of EMP-000001 and EMP-040054.",
    "Give me the salary details for EMP-000001 and EMP-000002.",
    "What is the difference between the salaries of EMP-000001 and EMP-000002?",
    "How much more does EMP-000002 earn than EMP-000001?",
    "What is the combined earnings of EMP-000001 and EMP-040054?",
    "Calculate the total earnings of EMP-000001 and EMP-000002.",

    # =========================
    # DEPARTMENT
    # =========================

    "What department is EMP-000001 in?",
    "Which department does EMP-000002 belong to?",
    "Find the department of EMP-040054.",
    "What is EMP-000001's department?",
    "Tell me the department for EMP-000002.",
    "Which department is EMP-000001 assigned to?",
    "Show me EMP-000001's department.",
    "Look up the department of EMP-040054.",
    "Where does EMP-000002 work?",
    "What department is employee EMP-000001 assigned to?",

    # =========================
    # LOCATION
    # =========================

    "Where is EMP-000001 located?",
    "What is the location of EMP-000002?",
    "Find the location of EMP-040054.",
    "Which location is EMP-000001 assigned to?",
    "Where is employee EMP-000002 based?",
    "What location does EMP-000001 have?",
    "Tell me EMP-040054's location.",
    "Show the location for EMP-000001.",
    "Which office is EMP-000002 assigned to?",
    "What is the work location of EMP-000001?",

    # =========================
    # EMPLOYMENT TYPE
    # =========================

    "What is the employment type of EMP-000001?",
    "Is EMP-000002 full-time or part-time?",
    "What type of employment does EMP-040054 have?",
    "Find the employment type for EMP-000001.",
    "What is EMP-000002's employment type?",
    "Is EMP-000001 a full-time employee?",
    "What employment category is EMP-040054 in?",
    "Show EMP-000001's employment type.",
    "Tell me whether EMP-000002 is full-time.",
    "Look up the employment type of EMP-040054.",

    # =========================
    # PERFORMANCE
    # =========================

    "What is the performance rating of EMP-000001?",
    "What is EMP-000002's performance rating?",
    "Find the performance rating for EMP-040054.",
    "Show the performance rating of EMP-000001.",
    "What performance rating does EMP-000002 have?",
    "Give me EMP-000001's performance rating.",
    "Look up the performance rating for EMP-040054.",
    "What is the rating of EMP-000002?",
    "What performance score does EMP-000001 have?",
    "Tell me the performance rating of EMP-040054.",

    # =========================
    # BONUS
    # =========================

    "What is the bonus of EMP-000001?",
    "What bonus does EMP-000002 receive?",
    "Find EMP-040054's bonus.",
    "What is EMP-000001's annual bonus?",
    "How much bonus does EMP-000002 get?",
    "Show me the bonus for EMP-000001.",
    "What is the annual bonus of EMP-040054?",
    "Look up EMP-000002's bonus.",
    "Give me the bonus amount for EMP-000001.",
    "How much is EMP-040054's bonus?",

    # =========================
    # EXPERIENCE
    # =========================

    "How many years of experience does EMP-000001 have?",
    "What is EMP-000002's years of experience?",
    "Find the experience of EMP-040054.",
    "How experienced is EMP-000001?",
    "How many years has EMP-000002 been working?",
    "Show the years of experience for EMP-000001.",
    "What is the experience level of EMP-040054?",
    "Tell me how many years of experience EMP-000002 has.",
    "Look up EMP-000001's years of experience.",
    "How many years of experience are recorded for EMP-040054?",

    # =========================
    # JOINING YEAR
    # =========================

    "What year did EMP-000001 join?",
    "What is the joining year of EMP-000002?",
    "When did EMP-040054 join?",
    "Find the joining year for EMP-000001.",
    "What year was EMP-000002 hired?",
    "When was EMP-040054 hired?",
    "Show the joining year of EMP-000001.",
    "Tell me when EMP-000002 joined.",
    "Look up EMP-040054's joining year.",
    "What is EMP-000001's joining year?",

    # =========================
    # COUNT
    # =========================

    "How many employees are in Finance?",
    "How many employees are in Support?",
    "How many employees are in HR?",
    "How many employees are in Engineering?",
    "What is the count of employees in Finance?",
    "What is the number of employees in Support?",
    "Count the employees in Finance.",
    "Give me the total number of employees in HR.",
    "How many employees work in Engineering?",
    "How many employees are in the Finance department?",

    # =========================
    # AGGREGATIONS
    # =========================

    "What is the average salary?",
    "What is the average salary of employees?",
    "What is the total salary of all employees?",
    "What is the sum of all salaries?",
    "What is the highest salary?",
    "What is the lowest salary?",
    "What is the maximum salary?",
    "What is the minimum salary?",
    "What is the average employee salary?",
    "What is the total of all employee salaries?",

    # =========================
    # MORE EMPLOYEE LOOKUPS
    # =========================

    "Give me all information about EMP-000001.",
    "Give me all information about EMP-000002.",
    "Show all details for EMP-040054.",
    "Look up EMP-000001.",
    "Look up EMP-000002.",
    "Find EMP-040054.",
    "Show employee EMP-000001.",
    "Show employee EMP-000002.",
    "Get the details of EMP-040054.",
    "What information do we have for EMP-000001?",

    # =========================
    # COMBINED STRUCTURED QUESTIONS
    # =========================

    "What is the salary and department of EMP-000001?",
    "What is the salary and location of EMP-000002?",
    "Give me the department and salary of EMP-040054.",
    "What is EMP-000001's salary and performance rating?",
    "Give me EMP-000002's bonus and salary.",
    "What are EMP-040054's salary and years of experience?",
    "Show the department and location of EMP-000001.",
    "Give me the employment type and department of EMP-000002.",
    "What are the salary and bonus of EMP-000001?",
    "Show me the joining year and experience of EMP-040054.",
]


def main():

    total = len(DUCKDB_QUESTIONS)

    duckdb_passed = 0
    rag_routed = []
    errors = []

    print("=" * 80)
    print(f"Testing {total} DuckDB questions")
    print("=" * 80)

    for i, question in enumerate(DUCKDB_QUESTIONS, start=1):

        print("\n" + "-" * 80)
        print(f"[{i}/{total}] {question}")

        try:
            route = classify_query(question)

            print(f"ROUTE: {route}")

            # IMPORTANT:
            # Do NOT call RAG.
            # If router sends it to RAG, just record it and continue.
            if route != "duckdb":
                print("SKIPPED: Router selected RAG")
                rag_routed.append(question)
                continue

            try:
                intent = detect_simple_intent(question)

                if not intent:
                    print("SKIPPED: Python intent detector could not handle this question")
                    print("         LLM fallback intentionally disabled")
                    continue

                print(f"PYTHON INTENT: {intent}")

                try:
                    result = execute_structured_query(intent)

                    print("DUCKDB RESULT:")
                    print(result)

                    if result is not None:
                        duckdb_passed += 1
                    else:
                        errors.append((question, "DuckDB returned None"))

                except Exception as e:
                    print(f"DUCKDB ERROR: {e}")
                    errors.append((question, str(e)))

            except Exception as e:
                print(f"DUCKDB ERROR: {e}")
                errors.append((question, str(e)))

        except Exception as e:
            print(f"ROUTER ERROR: {e}")
            errors.append((question, str(e)))


    print("\n")
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    print(f"Total questions       : {total}")
    print(f"DuckDB executed       : {duckdb_passed}")
    print(f"Routed to RAG         : {len(rag_routed)}")
    print(f"Errors                : {len(errors)}")

    if rag_routed:

        print("\n")
        print("=" * 80)
        print("QUESTIONS ROUTED TO RAG")
        print("=" * 80)

        for question in rag_routed:
            print(f"- {question}")

    if errors:

        print("\n")
        print("=" * 80)
        print("DUCKDB ERRORS")
        print("=" * 80)

        for question, error in errors:
            print(f"\nQuestion: {question}")
            print(f"Error: {error}")


if __name__ == "__main__":
    main()