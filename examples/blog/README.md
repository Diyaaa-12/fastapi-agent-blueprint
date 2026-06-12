# Blog Example — Protocol-based Cross-Domain DIP

Two domains (`author`, `post`) where `post` depends on `author` **via
`AuthorRepositoryProtocol`, not via a direct import**. This keeps the
domains independently deployable — the only coupling point is the DI
container that wires the protocol to the concrete implementation.

## Domains

### Author
Standard CRUD domain with minimal fields (`id`, `display_name`).

### Post
Standard CRUD domain (`id`, `author_id`, `title`, `body`). The
`PostService` receives an `AuthorRepositoryProtocol` via DI and uses it
to resolve the author's `display_name` when returning post responses.

## Key File: Protocol Boundary

`post/domain/protocols/author_repository_protocol.py` — the post domain
defines its **own** protocol for what it needs from the author domain.
The concrete `AuthorRepository` from `author/infrastructure/` is wired
to this protocol in `post/infrastructure/di/post_container.py`.

## Endpoints

### Author
| Method | Path               | Description   |
|--------|--------------------|---------------|
| POST   | `/v1/author`       | Create author |
| GET    | `/v1/authors`      | List authors  |
| GET    | `/v1/author/{id}`  | Get author    |
| PUT    | `/v1/author/{id}`  | Update author |
| DELETE | `/v1/author/{id}`  | Delete author |

### Post
| Method | Path             | Description |
|--------|------------------|-------------|
| POST   | `/v1/post`       | Create post |
| GET    | `/v1/posts`      | List posts  |
| GET    | `/v1/post/{id}`  | Get post    |
| PUT    | `/v1/post/{id}`  | Update post |
| DELETE | `/v1/post/{id}`  | Delete post |

## Verification

```bash
# 1. Copy domains into src/
cp -r examples/blog/author/ src/author/
cp -r examples/blog/post/ src/post/

# 2. Start the server
make quickstart

# 3. Create an author
curl -X POST http://localhost:8000/v1/author \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Alice"}'

# 4. Create a post referencing the author
curl -X POST http://localhost:8000/v1/post \
  -H "Content-Type: application/json" \
  -d '{"author_id": 1, "title": "Hello World", "body": "First post!"}'

# 5. Get the post — response includes author_display_name
curl http://localhost:8000/v1/post/1

# 6. Run tests
pytest examples/blog/tests/ -v
```
