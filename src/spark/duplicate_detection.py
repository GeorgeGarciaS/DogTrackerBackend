from pyspark.sql import DataFrame, functions as F
from pyspark.sql.window import Window


DUPLICATE_GROUP_COLUMNS = [
    "dog_id",
    "event_ts",
    "latitude",
    "longitude",
    "cumulative_steps",
    "heart_rate",
    "battery",
    "signal_strength",
]


def find_duplicate_rows(raw_df: DataFrame) -> DataFrame:
    """
        Returns rows from telemetry_raw that are duplicates and should be invalidated.
        Keeps the first row per duplicate group and marks the rest as duplicates.
    """
    window_spec = Window.partitionBy(*DUPLICATE_GROUP_COLUMNS).orderBy(
        F.col("ingested_at").asc(),
        F.col("event_id").asc(),
    )

    ranked_df = raw_df.withColumn("row_num", F.row_number().over(window_spec))

    duplicates_df = ranked_df.filter(F.col("row_num") > 1).drop("row_num")

    return duplicates_df


def build_duplicate_issues_df(duplicates_df: DataFrame) -> DataFrame:
    return duplicates_df.select(
        "event_id",
        "dog_id",
        F.lit("DUPLICATE_EVENT").alias("issue_type"),
        F.lit("Validation failed: duplicate event").alias("issue_reason"),
    )