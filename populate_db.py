import os
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "letschatbackend.settings.development")
import django

django.setup()

from lobbies.models import Question


def add_question(text):
    if Question.objects.filter(text=text).exists():
        print(f"Question '{text}' already exists, skipping...")
    else:
        Question.objects.create(text=text)
        print(f"Created question: '{text}'")


with open("questions.csv", "r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        question_text = row[0].strip()
        add_question(question_text)

print("Done!")
