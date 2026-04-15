import os
import subprocess
from datetime import datetime, timezone

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/app/dog_tracker_telemetry_dbt")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "/app/dog_tracker_telemetry_dbt")

def run_dbt() -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    print(f"[{started_at}] Running dbt tests only")

    result = subprocess.run(
        [
            "dbt",
            "test",
            "--project-dir",
            DBT_PROJECT_DIR,
            "--profiles-dir",
            DBT_PROFILES_DIR,
        ],
        check=False,
    )

    finished_at = datetime.now(timezone.utc).isoformat()
    print(
        f"[{finished_at}] dbt test finished with exit_code={result.returncode}"
    )
    return result.returncode

if __name__ == "__main__":
    run_dbt()
