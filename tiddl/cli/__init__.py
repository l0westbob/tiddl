import logging

from tiddl.cli.const import APP_PATHS

APP_PATHS.logs_dir.mkdir(parents=True, exist_ok=True)

try:
    file_handler = logging.FileHandler(
        APP_PATHS.logs_dir / "latest.log", encoding="utf-8", mode="w"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s\t[%(name)s.%(funcName)s] %(message)s"
        )
    )
    handler = file_handler
except (PermissionError, OSError):
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(levelname)s\t%(message)s"))

log = logging.getLogger("tiddl")
log.setLevel(logging.DEBUG)
log.addHandler(handler)
