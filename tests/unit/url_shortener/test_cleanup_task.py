import importlib.util
from pathlib import Path

_EXAMPLE_TEST = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "url-shortener"
    / "tests"
    / "test_cleanup_task.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "url_shortener_example_cleanup_test",
    _EXAMPLE_TEST,
)
assert _SPEC is not None
assert _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

test_delete_expired_removes_only_expired_links = (
    _MODULE.test_delete_expired_removes_only_expired_links
)
