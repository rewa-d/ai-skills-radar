import os
import sqlite3
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read Adzuna credentials
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

# Search Australian jobs
COUNTRY = "au"

# SQLite database file
DB_NAME = "job_postings.db"

# Search terms to collect jobs for
SEARCH_TERMS = [
    "artificial intelligence",
    "data scientist",
    "machine learning engineer",
    "data analyst",
]


def create_table():
    """
    Create the postings table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS postings (
            id TEXT PRIMARY KEY,
            search_term TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary_min REAL,
            salary_max REAL,
            description TEXT,
            url TEXT,
            created TEXT,
            fetched_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def fetch_jobs(search_term):
    """
    Fetch jobs from Adzuna API.
    """

    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 25,
        "what": search_term,
        "content-type": "application/json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    # Raise an exception if API call fails
    response.raise_for_status()

    data = response.json()

    return data.get("results", [])


def save_jobs(search_term, jobs):
    """
    Save jobs into SQLite.
    INSERT OR IGNORE prevents duplicates.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    fetched_at = datetime.now(timezone.utc).isoformat()

    for job in jobs:
        cursor.execute("""
            INSERT OR IGNORE INTO postings (
                id,
                search_term,
                title,
                company,
                location,
                salary_min,
                salary_max,
                description,
                url,
                created,
                fetched_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(job.get("id")),
            search_term,
            job.get("title"),
            job.get("company", {}).get("display_name"),
            job.get("location", {}).get("display_name"),
            job.get("salary_min"),
            job.get("salary_max"),
            job.get("description"),
            job.get("redirect_url"),
            job.get("created"),
            fetched_at,
        ))

    conn.commit()
    conn.close()


def main():
    """
    Main workflow.
    """

    if not APP_ID or not APP_KEY:
        raise ValueError(
            "Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in .env file."
        )

    create_table()

    for term in SEARCH_TERMS:
        try:
            print(f"\nFetching jobs for: {term}")

            jobs = fetch_jobs(term)

            save_jobs(term, jobs)

            print(f"Saved {len(jobs)} jobs")

        except requests.exceptions.RequestException as e:
            print(f"API request failed for '{term}': {e}")

        except Exception as e:
            print(f"Unexpected error for '{term}': {e}")


if __name__ == "__main__":
    main()