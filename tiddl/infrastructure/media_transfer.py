"""Infrastructure helpers for downloading and atomically placing media files."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import AsyncIterator, Iterable

import aiofiles
import aiohttp

from tiddl.cli.const import APP_PATHS


ChunkCallback = Callable[[int], None]

CHUNK_SIZE = 1024**2


@dataclass(frozen=True)
class DownloadedFile:
    path: Path
    temp_path: Path


def _ensure_tmp_dir(tmp_dir: Path) -> None:
    tmp_dir.mkdir(parents=True, exist_ok=True)


class MediaTransferError(RuntimeError):
    pass


@asynccontextmanager
async def _session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession(trust_env=True) as session:
        yield session


async def _write_stream_to_tmp(
    session: aiohttp.ClientSession,
    urls: Iterable[str],
    tmp: Path,
    progress_callback: ChunkCallback | None = None,
) -> Path:
    async with aiofiles.open(tmp, "wb") as f:
        for url in urls:
            async with session.get(url) as resp:
                if resp.status >= 400:
                    raise MediaTransferError(
                        f"Bad response fetching {url}: {resp.status}"
                    )

                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    await f.write(chunk)
                    if progress_callback:
                        progress_callback(len(chunk))

    return tmp


def _cleanup_tmp(tmp_path: Path) -> None:
    if tmp_path.exists():
        tmp_path.unlink()


def _finalize_downloads(tmp_path: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        destination.unlink()

    tmp_path.replace(destination)

    try:
        destination.chmod(0o644)
    except OSError:
        pass

    return destination


async def transfer_media(
    urls: list[str],
    destination: Path,
    *,
    progress_callback: ChunkCallback | None = None,
    tmp_root: Path | None = None,
) -> DownloadedFile:
    target_tmp_dir = tmp_root or APP_PATHS.download_tmp_dir
    _ensure_tmp_dir(target_tmp_dir)

    with NamedTemporaryFile("wb", delete=False, dir=target_tmp_dir) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        async with _session() as session:
            await _write_stream_to_tmp(
                session=session,
                urls=urls,
                tmp=tmp_path,
                progress_callback=progress_callback,
            )

        final_path = _finalize_downloads(tmp_path, destination)
        return DownloadedFile(path=final_path, temp_path=tmp_path)
    except Exception as exc:
        _cleanup_tmp(tmp_path)
        raise MediaTransferError(f"Failed downloading to {destination}: {exc}") from exc


__all__ = ["DownloadedFile", "MediaTransferError", "transfer_media"]
