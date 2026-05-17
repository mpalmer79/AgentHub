"""Tests for structured JSON logging."""

import io
import json
import logging

from app.core.logging import JsonFormatter, configure_logging, get_logger


def test_formatter_emits_valid_json_with_extras():
    record = logging.LogRecord(
        name="agenthub.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="task_started",
        args=(),
        exc_info=None,
    )
    record.task_id = "t-123"
    record.agent_type = "bookkeeper"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["msg"] == "task_started"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "agenthub.test"
    assert payload["task_id"] == "t-123"
    assert payload["agent_type"] == "bookkeeper"
    assert payload["ts"].endswith("Z")


def test_configure_logging_is_idempotent():
    # pytest itself injects extra handlers (live-log, capture, etc.), so we
    # can't assert handler count. What we *can* assert is that calling twice
    # doesn't keep stacking our JsonFormatter handlers.
    import app.core.logging as logging_mod

    logging_mod._CONFIGURED = False
    configure_logging("INFO")
    json_after_first = [
        h for h in logging.getLogger().handlers if isinstance(h.formatter, JsonFormatter)
    ]
    configure_logging("DEBUG")
    json_after_second = [
        h for h in logging.getLogger().handlers if isinstance(h.formatter, JsonFormatter)
    ]
    assert len(json_after_first) == 1
    assert len(json_after_second) == 1


def test_get_logger_returns_adapter_with_service_field():
    log = get_logger("agenthub.x")
    assert log.extra.get("service") == "agenthub-api"
