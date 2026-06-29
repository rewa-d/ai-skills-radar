import json
import re
import sqlite3
import time

from ollama import chat

DB_NAME = "job_postings.db"
MODEL_NAME = "qwen2.5:7b"

SKILL_DICTIONARY = [
    # Programming Languages
    "Python", "SQL", "R", "Java", "JavaScript", "TypeScript",
    "C", "C++", "C#", "Go", "Rust", "Scala", "Kotlin",
    "Bash", "PowerShell", "PL/SQL", "T-SQL",

    # Web / APIs
    "React", "Node.js", "FastAPI", "REST API", "GraphQL",

    # Cloud
    "AWS", "Azure", "GCP",
    "Amazon EC2", "Amazon S3", "AWS Lambda",
    "Amazon Redshift", "AWS Glue", "Amazon SageMaker",
    "Azure Data Factory", "Azure Databricks",
    "Azure Synapse", "Azure Machine Learning",
    "Microsoft Fabric",
    "BigQuery", "Cloud Run", "Dataflow", "Vertex AI",

    # Machine Learning Frameworks
    "TensorFlow",
    "PyTorch",
    "scikit-learn",
    "Keras",
    "XGBoost",
    "LightGBM",
    "CatBoost",

    # LLM Ecosystem
    "Hugging Face",
    "Transformers",
    "LangChain",
    "LlamaIndex",
    "OpenAI API",

    # NLP / CV Libraries
    "spaCy",
    "NLTK",
    "OpenCV",

    # MLOps
    "MLflow",
    "Kubeflow",

    # Data Libraries
    "Pandas",
    "NumPy",
    "SciPy",
    "PySpark",
    "Apache Spark",
    "Databricks",
    "Snowflake",
    "dbt",
    "Apache Airflow",
    "Apache Kafka",
    "Apache Flink",
    "Apache Beam",
    "Hadoop",
    "Hive",
    "Presto",
    "Trino",
    "Delta Lake",
    "DuckDB",
    "Polars",
    "Dask",
    "Prefect",

    # BI
    "Power BI",
    "Tableau",
    "Looker",
    "Looker Studio",
    "Excel",
    "Qlik",
    "Qlik Sense",
    "Alteryx",
    "SAP BusinessObjects",

    # Visualization
    "Jupyter",
    "Jupyter Notebook",
    "Plotly",
    "Matplotlib",
    "Seaborn",

    # Databases
    "PostgreSQL",
    "MySQL",
    "MariaDB",
    "SQL Server",
    "Oracle",
    "SQLite",
    "MongoDB",
    "DynamoDB",
    "Cassandra",
    "Redis",
    "Elasticsearch",
    "OpenSearch",
    "Neo4j",
    "Teradata",
    "Bigtable",
    "Cosmos DB",
    "Pinecone",
    "Weaviate",
    "Milvus",
    "FAISS",

    # DevOps
    "Docker",
    "Kubernetes",
    "Git",
    "GitHub",
    "GitLab",
    "Bitbucket",
    "CI/CD",
    "Jenkins",
    "GitHub Actions",
    "GitLab CI",
    "Terraform",
    "Ansible",
    "Helm",
    "Argo CD",
    "Prometheus",
    "Grafana",
    "Datadog",
    "Linux",
    "Unix",
    "Microservices",
]

DOMAIN_TERMS = [
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "AI",
    "Generative AI",
    "Natural Language Processing",
    "Computer Vision",
    "Large Language Models",
    "Prompt Engineering",
    "Feature Engineering",
    "RAG",
    "Model Monitoring",
    "MLOps",
    "Vector Database",
    "Vector Databases",
    "ETL",
    "ELT",
]


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


def match_dictionary_skills(description, dictionary):
    """
    Return dictionary skills explicitly present as whole words or phrases.
    """

    text = description or ""
    candidates = []

    for index, skill in enumerate(dictionary):
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"

        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidates.append({
                "index": index,
                "start": match.start(),
                "end": match.end()
            })

    candidates.sort(
        key=lambda item: (
            -(item["end"] - item["start"]),
            item["index"]
        )
    )

    occupied_spans = []
    matched_indexes = set()

    for candidate in candidates:
        overlaps = any(
            candidate["start"] < end
            and candidate["end"] > start
            for start, end in occupied_spans
        )

        if not overlaps:
            matched_indexes.add(candidate["index"])
            occupied_spans.append((
                candidate["start"],
                candidate["end"]
            ))

    return [
        skill
        for index, skill in enumerate(dictionary)
        if index in matched_indexes
    ]


def build_prompt(row, dictionary_matches):
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
- Here are the skills already found by keyword matching: {json.dumps(dictionary_matches)}.
- Read the title and description and suggest ONLY additional technical skills
  that are clearly mentioned but NOT already in this list.
- If there are no additional skills, return an empty list.
- Do not repeat anything already found by keyword matching.
- Extract only technical skills explicitly mentioned in the title or description.
- Include programming languages, databases, cloud platforms, BI tools, ML frameworks, Python libraries, deployment tools, and technical platforms.
- Do NOT include soft skills.
- Do NOT include generic words like "AI", "artificial intelligence", "data", "analytics", "technology", "software", "enterprise architecture", or "digital".
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


def merge_skill_sources(dictionary_matches, llm_skills):
    """
    Merge dictionary and LLM skills with source metadata and no duplicates.
    """

    merged = []
    seen = set()

    for skill in dictionary_matches:
        normalized = skill.strip()
        key = normalized.casefold()

        if normalized and key not in seen:
            merged.append({
                "skill": normalized,
                "source": "dictionary"
            })
            seen.add(key)

    for skill in llm_skills:
        if not isinstance(skill, str):
            continue

        normalized = skill.strip()
        key = normalized.casefold()

        if normalized and key not in seen:
            merged.append({
                "skill": normalized,
                "source": "llm_inferred"
            })
            seen.add(key)

    return merged


def extract_row(row):
    """
    Run dictionary matching and ask the LLM for additional skills.
    If JSON parsing fails, retry once. If it still fails, return extraction_failed.
    """

    title = row[2] or ""
    description = row[5] or ""

    dictionary_matches = match_dictionary_skills(
        f"{title}\n{description}",
        SKILL_DICTIONARY
    )

    prompt = build_prompt(row, dictionary_matches)

    try:
        result = call_ollama(prompt)
        result["_retry_used"] = False

    except (json.JSONDecodeError, ValueError) as first_error:
        print(f"JSON parsing failed once: {first_error}")
        print("Retrying same row once...")

        try:
            result = call_ollama(prompt)
            result["_retry_used"] = True

        except (json.JSONDecodeError, ValueError) as second_error:
            print(f"JSON parsing failed twice: {second_error}")

            return {
                "technical_skills": [],
                "seniority_level": "extraction_failed",
                "is_relevant_ai_data_role": None,
                "_retry_used": True,
                "_failed_after_retry": True
            }

    result["technical_skills"] = merge_skill_sources(
        dictionary_matches,
        result.get("technical_skills", [])
    )

    result["_failed_after_retry"] = False

    return result


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

    if seniority in ["principal", "staff", "lead", "head", "manager", "architect"]:
        seniority = "senior"

    if seniority not in ["junior", "mid", "senior", "unclear", "extraction_failed"]:
        seniority = "unclear"

    raw_relevance = result.get("is_relevant_ai_data_role")

    if raw_relevance is None:
        is_relevant = None
    else:
        is_relevant = int(raw_relevance)

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

    succeeded_first_try = 0
    succeeded_after_retry = 0
    failed_after_retry = 0

    print(f"Found {total} rows to process")

    for index, row in enumerate(rows, start=1):
        row_id = row[0]
        title = row[2]

        print(f"\nProcessing {index}/{total}: {title}")

        try:
            result = extract_row(row)
            update_posting(row_id, result)

            if result.get("_failed_after_retry"):
                failed_after_retry += 1
            elif result.get("_retry_used"):
                succeeded_after_retry += 1
            else:
                succeeded_first_try += 1

            result.pop("_retry_used", None)
            result.pop("_failed_after_retry", None)

            print("Saved:", result)

        except Exception as e:
            print(f"Unexpected failure for row {row_id}: {e}")

            failed_result = {
                "technical_skills": [],
                "seniority_level": "extraction_failed",
                "is_relevant_ai_data_role": None
            }

            update_posting(row_id, failed_result)
            failed_after_retry += 1

        time.sleep(0.5)

    print("\nExtraction complete")
    print(f"Total rows processed: {total}")
    print(f"Succeeded first try: {succeeded_first_try}")
    print(f"Succeeded after retry: {succeeded_after_retry}")
    print(f"Failed after retry: {failed_after_retry}")


if __name__ == "__main__":
    main()
