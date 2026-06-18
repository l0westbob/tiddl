import asyncio

import pytest

from tiddl.infrastructure.media_transfer import MediaTransferError, transfer_media


class _FakeContent:
    def __init__(self, chunks: list[bytes]):
        self._chunks = chunks

    async def iter_chunked(self, _size: int):
        for chunk in self._chunks:
            yield chunk


class _FakeResponse:
    def __init__(self, chunks: list[bytes], status: int = 200):
        self.status = status
        self.content = _FakeContent(chunks)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None


class _FakeSession:
    def __init__(self, responses: dict[str, tuple[int, list[bytes]]] | None = None):
        self.responses = responses or {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_args):
        return None

    def get(self, url: str):
        status, chunks = self.responses[url]
        return _FakeResponse(chunks=chunks, status=status)


@pytest.fixture
def fake_session_factory(monkeypatch: pytest.MonkeyPatch):
    def factory(urls_to_chunks: dict[str, tuple[int, list[bytes]]]):
        class _PatchedSession:
            def __init__(self, *args, **kwargs):
                self._session = _FakeSession(urls_to_chunks)

            async def __aenter__(self):
                return self._session

            async def __aexit__(self, *_args):
                return None

        monkeypatch.setattr(
            "tiddl.infrastructure.media_transfer.aiohttp.ClientSession",
            _PatchedSession,
        )

    return factory


def test_transfer_media_writes_all_chunks(tmp_path, fake_session_factory):
    fake_session_factory(
        {
            "https://example.test/a": (200, [b"hello "]),
            "https://example.test/b": (200, [b"world"]),
        }
    )

    dest = tmp_path / "artwork/track.flac"

    result = asyncio.run(
        transfer_media(
            ["https://example.test/a", "https://example.test/b"],
            destination=dest,
            tmp_root=tmp_path / "tmp",
        )
    )

    assert result.path == dest
    assert dest.read_text("utf-8") == "hello world"
    assert not any((tmp_path / "tmp").iterdir())


def test_transfer_media_cleans_temp_on_http_error(tmp_path, fake_session_factory):
    fake_session_factory(
        {
            "https://example.test/a": (404, [b"oops"]),
        }
    )

    with pytest.raises(MediaTransferError):
        asyncio.run(
            transfer_media(
                ["https://example.test/a"],
                destination=tmp_path / "track.m4a",
                tmp_root=tmp_path / "tmp",
            )
        )

    assert not any((tmp_path / "tmp").iterdir())
