import json
import sqlite3
import pandas as pd

import os

DB_NAME = (
    "job_postings.db"
    if os.path.exists("job_postings.db")
    else "sample_job_postings.db"
)


def load_postings():
    """
    Load all postings from SQLite.
    """

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM postings",
        conn
    )

    conn.close()

    return df


def expand_skills(df):
    """
    Convert JSON skill lists into a normalized dataframe.

    Example:
    [{"skill": "Python", "source": "dictionary"}]

    becomes

    job_id | skill_name | source
    ---------------------------------
    123    | Python     | dictionary

    Legacy flat string lists remain readable, with a null source.
    """

    rows = []

    for _, row in df.iterrows():

        skills_text = row.get(
            "extracted_skills"
        )

        if pd.isna(skills_text):
            continue

        if skills_text == "":
            continue

        try:
            skills = json.loads(skills_text)

        except Exception:
            continue

        for skill_entry in skills:
            if isinstance(skill_entry, dict):
                skill_name = str(
                    skill_entry.get("skill", "")
                ).strip()
                source = skill_entry.get("source")
            else:
                skill_name = str(skill_entry).strip()
                source = None

            if not skill_name:
                continue

            rows.append({
                "job_id": row["id"],
                "skill_name": skill_name,
                "source": source
            })

    return pd.DataFrame(
        rows,
        columns=["job_id", "skill_name", "source"]
    )


def get_summary_stats(df):
    total_jobs = len(df)

    relevant_jobs = len(df[df["is_relevant"] == 1])
    irrelevant_jobs = len(df[df["is_relevant"] == 0])

    extraction_failures = len(
        df[df["seniority"] == "extraction_failed"]
    )

    skills_df = expand_skills(
        df[df["is_relevant"] == 1]
    )

    unique_skills = (
        skills_df["skill_name"].nunique()
        if not skills_df.empty
        else 0
    )

    return {
        "total_jobs": total_jobs,
        "relevant_jobs": relevant_jobs,
        "irrelevant_jobs": irrelevant_jobs,
        "extraction_failures": extraction_failures,
        "unique_skills": unique_skills
    }


def get_top_skills(df, limit=20):
    """
    Most common skills.
    """

    relevant_df = df[
        df["is_relevant"] == 1
    ]

    skills_df = expand_skills(
        relevant_df
    )

    if skills_df.empty:

        return pd.DataFrame(
            columns=[
                "skill",
                "frequency",
                "percentage"
            ]
        )

    top_skills = (
        skills_df
        .groupby("skill_name")
        .size()
        .reset_index(name="frequency")
        .sort_values(
            "frequency",
            ascending=False
        )
        .head(limit)
    )

    relevant_count = len(
        relevant_df
    )

    top_skills["percentage"] = (
        top_skills["frequency"]
        / relevant_count
        * 100
    ).round(1)

    top_skills.rename(
        columns={
            "skill_name": "skill"
        },
        inplace=True
    )

    top_skills.rename(
        columns={
            "percentage": "% of Relevant Jobs"
        },
        inplace=True
    )

    return top_skills


def get_seniority_breakdown(df):
    clean_df = df[
        df["seniority"] != "extraction_failed"
    ]

    result = (
        clean_df["seniority"]
        .fillna("unclear")
        .value_counts()
        .reset_index()
    )

    result.columns = ["seniority", "count"]

    return result


def get_skill_source_breakdown(df):
    """
    Counts of skills found by dictionary matching versus the LLM.
    """

    skills_df = expand_skills(
        df[df["is_relevant"] == 1]
    )

    if skills_df.empty:
        return pd.DataFrame(
            columns=["source", "count"]
        )

    result = (
        skills_df[
            skills_df["source"].isin([
                "dictionary",
                "llm_inferred"
            ])
        ]
        .groupby("source")
        .size()
        .reset_index(name="count")
    )

    result = result.sort_values(
        "count",
        ascending=False
    )

    return result


def get_search_term_breakdown(df):
    """
    Search term counts.
    """

    result = (
        df["search_term"]
        .fillna("unknown")
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "search_term",
        "count"
    ]

    return result


def get_relevance_breakdown(df):
    """
    Relevant vs irrelevant counts.
    """

    temp = df.copy()

    temp["relevance"] = (
        temp["is_relevant"]
        .map({
            1: "Relevant",
            0: "Irrelevant"
        })
        .fillna("Unknown")
    )

    result = (
        temp["relevance"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "relevance",
        "count"
    ]

    return result

def load_skill_snapshots():
    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        """
        SELECT
            snapshot_date,
            skill,
            frequency,
            percentage
        FROM skill_snapshots
        ORDER BY snapshot_date ASC, frequency DESC
        """,
        conn
    )

    conn.close()

    return df

def get_top_companies(df, limit=10):
    clean_df = df[
        (df["is_relevant"] == 1) &
        (df["company"].notna())
    ]

    result = (
        clean_df["company"]
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = ["company", "count"]
    return result


def get_top_locations(df, limit=10):
    clean_df = df[
        (df["is_relevant"] == 1) &
        (df["location"].notna())
    ]

    result = (
        clean_df["location"]
        .value_counts()
        .head(limit)
        .reset_index()
    )

    result.columns = ["location", "count"]
    return result


def get_salary_by_search_term(df):
    salary_df = df[
        (df["is_relevant"] == 1) &
        (
            df["salary_min"].notna() |
            df["salary_max"].notna()
        )
    ].copy()

    if salary_df.empty:
        return salary_df

    salary_df["avg_salary"] = salary_df[
        ["salary_min", "salary_max"]
    ].mean(axis=1)

    result = (
        salary_df
        .groupby("search_term")["avg_salary"]
        .mean()
        .round(0)
        .reset_index()
    )

    return result
