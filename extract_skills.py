import json
import re
import sqlite3
import time

from ollama import chat

DB_NAME = "job_postings.db"
MODEL_NAME = "qwen2.5:7b"


def add_extraction_columns():
    """
    Add extraction columns to existing postings table.
    If columns already exist, skip them safely.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    columns = [
        ("extracted_skills", "TEXT"),
        ("seniority", "TEXT"),
        ("is_relevant", "INTEGER")
    ]

    for column_name, column_type in columns:
        try:
            cursor.execute(
                f"ALTER TABLE postings ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added column: {column_name}")

        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column already exists: {column_name}")
            else:
                raise e

    conn.commit()
    conn.close()


def clean_json(text):
    """
    Remove markdown/code fences and keep only the JSON object.
    """

    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model response")

    return text[start:end + 1]


def get_unprocessed_rows():
    """
    Select rows that still need extraction.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            search_term,
            title,
            company,
            location,
            description
        FROM postings
        WHERE extracted_skills IS NULL
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def build_prompt(row):
    """
    Build prompt for one job posting.
    """

    job_id, search_term, title, company, location, description = row

    return f"""
Return ONLY valid JSON.
Do not use markdown.
Do not explain anything.

Analyze this job posting.

Job ID: {job_id}
Search term used: {search_term}
Title: {title}
Company: {company}
Location: {location}

Description:
{description}

Return exactly this JSON format:

{{
  "technical_skills": [],
  "seniority_level": "",
  "is_relevant_ai_data_role": false
}}

Rules:
- Extract only technical skills explicitly mentioned in the title or description.
- Include programming languages, databases, cloud platforms, BI tools, ML frameworks, Python libraries, deployment tools, and technical platforms.
- Do NOT include soft skills.
- Do NOT include generic words like "AI", "artificial intelligence", "data", "analytics", "technology", "software", "enterprise architecture", or "digital".
- Normalize common skill names:
  Python, SQL, R, Excel, Power BI, Tableau, AWS, Azure, GCP, TensorFlow, PyTorch, scikit-learn, Pandas, NumPy, Spark, Docker, Kubernetes, Git.
- If no clear technical skills are mentioned, return an empty list.
- seniority_level must be one of: junior, mid, senior, unclear.
- junior means graduate, intern, junior, entry-level, associate.
- senior means senior, lead, principal, manager, architect, head, professor, lecturer, 5+ years.
- mid means analyst, consultant, developer, engineer, specialist, 2-5 years, with no junior/senior wording.
- unclear means not enough information.
- is_relevant_ai_data_role should be true only for technical AI, machine learning, data science, data analytics, BI, data engineering, or technical software/data roles.
- is_relevant_ai_data_role should be false for sales, marketing, recruitment, account management, policy, legal, general business, training-only, or non-technical roles.
"""


def call_ollama(prompt):
    """
    Call local Ollama model.
    """

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        }
    )

    raw_text = response["message"]["content"]
    cleaned = clean_json(raw_text)

    return json.loads(cleaned)


def update_posting(row_id, result):
    """
    Save extraction result back into postings table.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    skills_json = json.dumps(
        result.get("technical_skills", [])
    )

    seniority = result.get(
        "seniority_level",
        "unclear"
    )

    is_relevant = int(
        result.get(
            "is_relevant_ai_data_role",
            False
        )
    )

    cursor.execute("""
        UPDATE postings
        SET
            extracted_skills = ?,
            seniority = ?,
            is_relevant = ?
        WHERE id = ?
    """, (
        skills_json,
        seniority,
        is_relevant,
        row_id
    ))

    conn.commit()
    conn.close()


def main():
    add_extraction_columns()

    rows = get_unprocessed_rows()
    total = len(rows)

    print(f"Found {total} rows to process")

    for index, row in enumerate(rows, start=1):
        row_id = row[0]
        title = row[2]

        try:
            print(f"\nProcessing {index}/{total}: {title}")

            prompt = build_prompt(row)
            result = call_ollama(prompt)

            update_posting(row_id, result)

            print("Saved:", result)

            time.sleep(0.5)

        except Exception as e:
            print(f"Failed row {row_id}: {e}")
            continue

    print("\nExtraction complete")


if __name__ == "__main__":
    main()