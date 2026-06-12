"""Protocol for cross-domain access to the author repository.

The post domain depends on this protocol, NOT on the concrete
AuthorRepository from the author domain. This keeps the two domains
independently deployable — the only coupling is this abstract contract.
"""

from typing import Protocol

from examples.blog.author.domain.dtos.author_dto import AuthorDTO
from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol


class AuthorRepositoryProtocol(BaseRepositoryProtocol[AuthorDTO], Protocol):
    pass
