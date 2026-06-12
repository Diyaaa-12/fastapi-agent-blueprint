from examples.blog.post.domain.dtos.post_dto import PostDTO
from examples.blog.post.domain.protocols.author_repository_protocol import (
    AuthorRepositoryProtocol,
)
from examples.blog.post.domain.protocols.post_repository_protocol import (
    PostRepositoryProtocol,
)
from examples.blog.post.interface.server.schemas.post_schema import (
    CreatePostRequest,
    UpdatePostRequest,
)
from src._core.domain.services.base_service import BaseService


class PostService(BaseService[CreatePostRequest, UpdatePostRequest, PostDTO]):
    def __init__(
        self,
        post_repository: PostRepositoryProtocol,
        author_repository: AuthorRepositoryProtocol,
    ) -> None:
        super().__init__(repository=post_repository)
        self._author_repository = author_repository

    async def get_author_display_name(self, author_id: int) -> str:
        author = await self._author_repository.find_by_id(author_id)
        return author.display_name if author else "Unknown"
