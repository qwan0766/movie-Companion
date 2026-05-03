"""Local backend runner for desktop testing."""

from pathlib import Path
import traceback

import uvicorn


LOG_PATH = Path(__file__).with_name("backend_local.log")


def main() -> None:
    try:
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write("Starting backend on http://127.0.0.1:8015\n")
        uvicorn.run(
            "api.routes:app",
            host="127.0.0.1",
            port=8015,
            reload=False,
            log_level="info",
        )
    except Exception:
        with LOG_PATH.open("a", encoding="utf-8") as log:
            log.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
