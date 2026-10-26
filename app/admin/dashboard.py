"""
Streamlit admin dashboard — Phase 5.

Run with: streamlit run app/admin/dashboard.py
"""

# TODO:
#   - Query pending ReviewQueueItem rows from Postgres (db/session.py)
#   - Display each question + the logged AI answer
#   - Approve button -> call the same logic as the
#     POST /admin/review-queue/{id}/approve endpoint (consider sharing
#     the function so the API and dashboard don't duplicate logic)
#   - Reject button -> mark rejected
