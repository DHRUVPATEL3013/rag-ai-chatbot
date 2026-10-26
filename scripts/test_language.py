from app.ingestion.language_detect import detect_language


texts = [
    "Employees are entitled to 21 days of annual leave per year.",
    "Los empleados tienen derecho a 21 días de vacaciones al año.",
    "Les employés ont droit à 21 jours de congé annuel par an.",
    "Annual Leave",
    "",
]


for text in texts:
    print(f"Text: {text}")
    print(f"Language: {detect_language(text)}")
    print()