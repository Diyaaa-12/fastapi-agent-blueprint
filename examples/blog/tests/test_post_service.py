"""Test PostService with a mock AuthorRepositoryProtocol.

Demonstrates that the post domain can be tested without any author
infrastructure — only the protocol contract matters.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from examples.blog.author.domain.dtos.author_dto import AuthorDTO
from examples.blog.post.domain.services.post_service import PostService


@pytest.fixture
def mock_post_repository():
    return AsyncMock()


@pytest.fixture
def mock_author_repository():
    return AsyncMock()


@pytest.fixture
def post_service(mock_post_repository, mock_author_repository):
    return PostService(
        post_repository=mock_post_repository,
        author_repository=mock_author_repository,
    )


@pytest.mark.asyncio
async def test_get_author_display_name(post_service, mock_author_repository):
    mock_author_repository.find_by_id.return_value = AuthorDTO(
        id=1,
        display_name="Alice",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    name = await post_service.get_author_display_name(author_id=1)

    assert name == "Alice"
    mock_author_repository.find_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_author_display_name_unknown(post_service, mock_author_repository):
    mock_author_repository.find_by_id.return_value = None

    name = await post_service.get_author_display_name(author_id=999)

    assert name == "Unknown"
