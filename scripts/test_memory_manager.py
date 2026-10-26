from app.memory.manager import should_update_summary


test_counts = [1, 4, 5, 6, 9, 10, 11, 19, 20, 21, 29, 30, 31]

for count in test_counts:
    print(
        f"Messages: {count:2} -> "
        f"Update summary: {should_update_summary(count)}"
    )