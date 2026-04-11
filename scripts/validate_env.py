# scripts/validate_env.py
from src.core.settings import Settings
import sys

try:
    Settings()   # type: ignore
    print("Environment validation passed.")
except Exception as e:
    print("Environment validation failed:")
    print(e)
    sys.exit(1)