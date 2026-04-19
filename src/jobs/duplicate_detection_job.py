import os
from typing import List

import psycopg2
from psycopg2.extras import execute_values
from pyspark.sql import DataFrame

from src.spark.session import create_spark_session
from src.spark.duplicate_detection import (
    build_duplicate_issues_df,
    find_duplicate_rows,
)


def get_db_config() -> dict[str, str]:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME", "your_db"),
        "user": os.getenv("DB_USER", "your_user"),
        "password": os.getenv("DB_PASSWORD", "your_password"),
    }


def get_jdbc_url() -> str:
    cfg = get_db_config()
    return f"jdbc:postgresql://{cfg['host']}:{cfg['port']}/{cfg['dbname']}"


def get_jdbc_properties() -> dict[str, str]:
    cfg = get_db_config()
    return {
        "user": cfg["user"],
        "password": cfg["password"],
        "driver": "org.postgresql.Driver",
    }


def read_telemetry_raw() -> DataFrame:
    spark = create_spark_session("telemetry-duplicate-detection")
    return spark.read.jdbc(
        url=get_jdbc_url(),
        table="telemetry_raw",
        properties=get_jdbc_properties(),
    )


def write_data_quality_issues(issues_df: DataFrame) -> None:
    if issues_df.rdd.isEmpty():
        return

    issues_df.write.jdbc(
        url=get_jdbc_url(),
        table="data_quality_issue",
        mode="append",
        properties=get_jdbc_properties(),
    )


def invalidate_clean_rows(event_ids: List[str]) -> None:
    if not event_ids:
        return

    cfg = get_db_config()
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
    )

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE telemetry_clean
                    SET is_valid = false,
                        invalid_reason = 'DUPLICATE_EVENT',
                        invalidated_at = NOW()
                    WHERE event_id = ANY(%s)
                    """,
                    (event_ids,),
                )
    finally:
        conn.close()


def fetch_duplicate_event_ids(duplicates_df: DataFrame) -> List[str]:
    rows = duplicates_df.select("event_id").distinct().collect()
    return [row["event_id"] for row in rows]


def main() -> None:
    raw_df = read_telemetry_raw()

    duplicates_df = find_duplicate_rows(raw_df)
    issues_df = build_duplicate_issues_df(duplicates_df)

    write_data_quality_issues(issues_df)

    duplicate_event_ids = fetch_duplicate_event_ids(duplicates_df)
    invalidate_clean_rows(duplicate_event_ids)

    print(f"Processed duplicate detection. Invalidated {len(duplicate_event_ids)} clean rows.")


if __name__ == "__main__":
    main()