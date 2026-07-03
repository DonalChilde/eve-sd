from logging import basicConfig, getLogger
from pathlib import Path
from time import perf_counter_ns

from eve_sd.db.helpers import (
    create_read_write_connection,
)
from eve_sd.db.load_datasets import import_jsonl_sde_to_db

basicConfig(level="INFO")
logger = getLogger(__name__)

project_root = Path(__file__).parent.parent.parent.parent
build_number = 3393779
jsonl_sde_path = project_root / "dev-data" / "sde" / "jsonl" / f"{build_number}"
jsonl_db_path = (
    project_root / "dev-data" / "db" / "jsonl" / f"sde_jsonl_{build_number}.db"
)


def main() -> None:
    connection = create_read_write_connection(str(jsonl_db_path.resolve()))
    import_jsonl_sde_to_db(jsonl_sde_path, connection=connection)


if __name__ == "__main__":
    start = perf_counter_ns()
    logger.info(f"Project root: {project_root}")
    logger.info(f"JSONL SDE path: {jsonl_sde_path}")
    logger.info(f"JSONL DB path: {jsonl_db_path}")
    main()
    end = perf_counter_ns()
    # output the elapsed time in seconds with millisecond precision
    elapsed_seconds = (end - start) / 1_000_000_000
    logger.info(f"Elapsed time: {elapsed_seconds:.3f} seconds")
