"""Backward-compatible ffmpeg utilities.

The actual implementation now lives in infrastructure adapters.
"""

from tiddl.infrastructure.ffmpeg import (
    FFmpegError,
    convert_to_mp4,
    extract_flac,
    is_ffmpeg_installed,
    run,
)

__all__ = [
    "FFmpegError",
    "convert_to_mp4",
    "extract_flac",
    "is_ffmpeg_installed",
    "run",
]
