import importlib.abc
import importlib.machinery
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path


# ---------------------------------------------------------------------------
# MetaPathFinder to redirect ``src.simple_chatbot`` to the example folder
# so tests can be run inside ``examples/simple-chatbot/tests/`` directly.
# ---------------------------------------------------------------------------
class SimpleChatbotFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "src.simple_chatbot" or fullname.startswith(
            "src.simple_chatbot."
        ):
            parts = fullname.split(".")[2:]
            base_dir = Path(__file__).parent.parent
            target_path = base_dir.joinpath(*parts)

            if target_path.is_dir():
                init_file = target_path / "__init__.py"
                if init_file.exists():
                    loader = SourceFileLoader(fullname, str(init_file))
                    spec = importlib.machinery.ModuleSpec(
                        fullname, loader, origin=str(init_file), is_package=True
                    )
                    spec.submodule_search_locations = [str(target_path)]
                    return spec
            else:
                py_file = target_path.with_suffix(".py")
                if py_file.exists():
                    loader = SourceFileLoader(fullname, str(py_file))
                    return importlib.machinery.ModuleSpec(
                        fullname, loader, origin=str(py_file), is_package=False
                    )
        return None


sys.meta_path.insert(0, SimpleChatbotFinder())


import pytest
import pytest_asyncio

# Force registration of chatbot model onto Base.metadata
from src.simple_chatbot.infrastructure.database.models.chatbot_model import (  # noqa: E402
    ChatMessageModel,
)

from src._core.infrastructure.persistence.rdb.config import DatabaseConfig  # noqa: E402
from src._core.infrastructure.persistence.rdb.database import (  # noqa: E402
    Base,
    Database,
)


def _build_test_database() -> Database:
    config = DatabaseConfig(echo=False)
    return Database(
        database_engine="sqlite",
        database_user="",
        database_password="",
        database_host="",
        database_port=0,
        database_name=":memory:",
        config=config,
    )


@pytest_asyncio.fixture(scope="module")
async def test_db():
    db = _build_test_database()
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield db
    async with db.async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db.dispose()


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"
