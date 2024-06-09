set -e
uvicorn survin.app:app --host 0.0.0.0 --reload --reload-include survin
