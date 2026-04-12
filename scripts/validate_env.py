# scripts/validate_env.py
import sys

from src.core.settings import Settings

try:
    Settings()   # type: ignore
    print("Environment validation passed.")
except Exception as e:
    print("Environment validation failed:")
    print(e)
    sys.exit(1)