# from app.security.pii import validate_question


# tests = [
#     "What is the leave policy?",
#     "   ",
#     "",
#     "My email is john@gmail.com",
#     "Call me at 9876543210",
#     "What is the policy " * 1001,
# ]


# for text in tests:
#     print("=" * 60)

#     valid, message = validate_question(text)

#     print("VALID:", valid)
#     print("MESSAGE:", message)


from app.security.pii import (
    sanitize_for_llm,
    restore_pii,
)


question = """
What is the salary of john@gmail.com?
"""

context = """
Employee contact email is john@gmail.com.
His phone number is +91 9876543210.
"""

pii_map = {}

sanitized_question, pii_map = sanitize_for_llm(
    question,
    pii_map,
)

sanitized_context, pii_map = sanitize_for_llm(
    context,
    pii_map,
)


print("=" * 60)
print("ORIGINAL QUESTION")
print(question)

print("=" * 60)
print("SANITIZED QUESTION")
print(sanitized_question)

print("=" * 60)
print("ORIGINAL CONTEXT")
print(context)

print("=" * 60)
print("SANITIZED CONTEXT")
print(sanitized_context)

print("=" * 60)
print("PII MAP")
print(pii_map)

# Simulate an LLM response
fake_llm_answer = (
    "The employee's email is "
    "<PII_EMAIL_ADDRESS_1> and their phone is "
    "<PII_PHONE_NUMBER_1>."
)

final_answer = restore_pii(
    fake_llm_answer,
    pii_map,
)

print("=" * 60)
print("FAKE LLM ANSWER")
print(fake_llm_answer)

print("=" * 60)
print("RESTORED ANSWER")
print(final_answer)

print("=" * 60)