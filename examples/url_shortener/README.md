# URL Shortener Example

A focused CRUD + worker example that demonstrates one domain service shared by
two interfaces. The HTTP router creates, reads, and deletes links by short code;
the Taskiq cleanup worker calls the same `LinkService` to delete expired rows.

> **Note:** Reference code only. Not auto-wired from `examples/`. To run it,
> copy this folder into `src/url_shortener/` so domain auto-discovery picks
> it up on server and worker startup.

## What It Teaches

- A small CRUD domain shaped like [`examples/todo/`](../todo/).
- A Taskiq task that reuses domain logic instead of duplicating cleanup rules.
- The zero-config worker path with `BROKER_TYPE=inmemory`.

Compare with [`src/user/interface/worker/`](../../src/user/interface/worker/)
for the minimal worker task pattern and
[`src/docs/interface/worker/`](../../src/docs/interface/worker/) for a router
that enqueues work with `.kiq(...)`.

## Install The Example

```bash
cp -r examples/url_shortener src/url_shortener
rm -f ./quickstart.db
make quickstart
```

`discover_domains()` expects `src/url_shortener/infrastructure/di/url_shortener_container.py`
and picks up the domain on server and worker startup.

## Endpoints

- `POST /v1/link` — Create a link
- `GET /v1/link/{short_code}` — Get a link by short code
- `DELETE /v1/link/{short_code}` — Delete a link by short code

## Try It With Curl

`expiresAt` values in the examples below are naive UTC datetimes (no timezone
offset). Match that format when creating links locally.

Create a link that expires in the future:

```bash
curl -sS -X POST http://127.0.0.1:8001/v1/link \
  -H "Content-Type: application/json" \
  -d '{
    "shortCode": "docs",
    "targetUrl": "https://fastapi.tiangolo.com/",
    "expiresAt": "2099-01-01T00:00:00"
  }'
```

Fetch it:

```bash
curl -sS http://127.0.0.1:8001/v1/link/docs
```

Delete it:

```bash
curl -sS -X DELETE http://127.0.0.1:8001/v1/link/docs
```

## Enqueue Cleanup With InMemory Broker

`make quickstart` loads `_env/quickstart.env`, which sets:

```env
BROKER_TYPE=inmemory
```

With the in-memory broker, the task runs in the same process — no separate
worker is needed.

Create an already-expired link:

```bash
curl -sS -X POST http://127.0.0.1:8001/v1/link \
  -H "Content-Type: application/json" \
  -d '{
    "shortCode": "expired",
    "targetUrl": "https://example.com/expired",
    "expiresAt": "2000-01-01T00:00:00"
  }'
```

Then enqueue the cleanup task from a Python REPL or tiny script:

```bash
uv run python - <<'PY'
import asyncio

from src.url_shortener.interface.worker.tasks.cleanup_expired_links_task import (
    cleanup_expired_links_task,
)


async def main() -> None:
    result = await cleanup_expired_links_task.kiq()
    await result.wait_result()


asyncio.run(main())
PY
```

Confirm the expired row is gone:

```bash
curl -sS http://127.0.0.1:8001/v1/link/expired
```

The response should be a not-found error after the worker processes the task.
