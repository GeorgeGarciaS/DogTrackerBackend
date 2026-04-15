import os
import subprocess
import time
from datetime import datetime, timezone

DBT_SELECT = os.getenv("DBT_SELECT", "analytics_signal_zones")
DBT_INTERVAL_SECONDS = float(os.getenv("DBT_INTERVAL_SECONDS", "10"))
DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/app/dog_tracker_telemetry_dbt")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", "/app/dog_tracker_telemetry_dbt")


def run_dbt() -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    print(f"[{started_at}] Running dbt for select={DBT_SELECT}")

    result = subprocess.run(
        [
            "dbt",
            "run",
            "--project-dir",
            DBT_PROJECT_DIR,
            "--profiles-dir",
            DBT_PROFILES_DIR,
        ],
        check=False,
    )

    finished_at = datetime.now(timezone.utc).isoformat()
    print(f"[{finished_at}] dbt finished with exit_code={result.returncode}")
    return result.returncode


def main() -> None:
    while True:
        loop_start = time.monotonic()
        try:
            run_dbt()
        except Exception as exc:
            print(f"dbt runner failed: {exc}")

        elapsed = time.monotonic() - loop_start
        time.sleep(max(0.0, DBT_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    main()