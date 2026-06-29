import sqlite3
from datetime import date

from analytics import load_postings, get_top_skills
from extract_skills import normalize_skill

DB_NAME = "job_postings.db"


def create_snapshot_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT NOT NULL,
            skill TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            percentage REAL NOT NULL,
            UNIQUE(snapshot_date, skill)
        )
    """)

    conn.commit()
    conn.close()


def save_today_snapshot():
    snapshot_date = date.today().isoformat()

    df = load_postings()
    top_skills = get_top_skills(df, limit=100)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    saved_count = 0

    for _, row in top_skills.iterrows():
        normalized_skill = normalize_skill(row["skill"])

        if normalized_skill is None:
            continue

        cursor.execute("""
            INSERT OR REPLACE INTO skill_snapshots (
                snapshot_date,
                skill,
                frequency,
                percentage
            )
            VALUES (?, ?, ?, ?)
        """, (
            snapshot_date,
            normalized_skill,
            int(row["frequency"]),
            float(row["% of Relevant Jobs"])
        ))

        saved_count += 1

    conn.commit()
    conn.close()

    print(f"Saved {saved_count} skill snapshots for {snapshot_date}")


def main():
    create_snapshot_table()
    save_today_snapshot()


if __name__ == "__main__":
    main()