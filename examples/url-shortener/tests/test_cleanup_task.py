import importlib
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[3]
_PACKAGE = "url_shortener_example"

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _ensure_package(name: str, path: Path) -> None:
    package = types.ModuleType(name)
    package.__path__ = [str(path)]
    package.__package__ = name
    sys.modules[name] = package


_ensure_package(_PACKAGE, _ROOT)
for _subpackage in (
    "domain",
    "domain.dtos",
    "domain.protocols",
    "domain.services",
    "interface",
    "interface.server",
    "interface.server.schemas",
):
    _ensure_package(f"{_PACKAGE}.{_subpackage}", _ROOT / _subpackage.replace(".", "/"))

LinkDTO = importlib.import_module(f"{_PACKAGE}.domain.dtos.link_dto").LinkDTO
LinkService = importlib.import_module(
    f"{_PACKAGE}.domain.services.link_service"
).LinkService


class InMemoryLinkRepository:
    def __init__(self, links: list[LinkDTO]) -> None:
        self.links = {link.short_code: link for link in links}

    async def delete_expired(self, cutoff: datetime) -> int:
        expired_codes = [
            short_code
            for short_code, link in self.links.items()
            if link.expires_at is not None and link.expires_at < cutoff
        ]
        for short_code in expired_codes:
            self.links.pop(short_code)
        return len(expired_codes)


def make_link(short_code: str, expires_at: datetime | None) -> LinkDTO:
    now = datetime.now(UTC).replace(tzinfo=None)
    return LinkDTO(
        id=len(short_code),
        short_code=short_code,
        target_url=f"https://example.com/{short_code}",
        expires_at=expires_at,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_delete_expired_removes_only_expired_links() -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    repo = InMemoryLinkRepository(
        [
            make_link("old", now - timedelta(minutes=1)),
            make_link("fresh", now + timedelta(minutes=1)),
            make_link("permanent", None),
        ]
    )
    service = LinkService(link_repository=repo)

    deleted = await service.delete_expired(cutoff=now)

    assert deleted == 1  # noqa: S101
    assert "old" not in repo.links  # noqa: S101
    assert "fresh" in repo.links  # noqa: S101
    assert "permanent" in repo.links  # noqa: S101
