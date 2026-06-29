import sqlite3
import time

from extract_skills import DB_NAME, extract_row, update_posting


def get_rows_to_reextract():
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
        WHERE extracted_skills = '[]'
           OR seniority = 'extraction_failed'
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def main():
    rows = get_rows_to_reextract()
    total = len(rows)

    updated = 0
    failed = 0

    print(f"Found {total} rows to re-extract")

    for index, row in enumerate(rows, start=1):
        row_id = row[0]
        title = row[2]

        print(f"\nProcessing {index}/{total}: {title}")

        try:
            result = extract_row(row)
            update_posting(row_id, result)

            updated += 1
            print("Updated:", result)

        except Exception as e:
            failed += 1
            print(f"Failed row {row_id}: {e}")

        time.sleep(0.5)

    print("\nRe-extraction complete")
    print(f"Total checked: {total}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    main()