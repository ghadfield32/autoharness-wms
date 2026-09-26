"""Global-mode admission tests for the WMS AutoHarness fork."""
from autoharness import config
from autoharness.lib import validate
from autoharness.stage_skill import server


VALID_BODY = """---
name: verify-before-claiming
description: Use when declaring an engineering task complete.
category: engineering
---
Verify the relevant implementation layers and tests before claiming completion.
"""


def _create(level):
    return {
        "action": "create",
        "name": "verify-before-claiming",
        "level": level,
        "body": VALID_BODY,
        "reason": "durable workflow rule",
        "evidence": "verify it completely before saying it is done",
    }


def test_global_create_rejected_when_global_writes_disabled(monkeypatch):
    monkeypatch.setattr(config, "ALLOW_GLOBAL_WRITES", False)
    findings = server._schema_errors(_create("global"))
    assert any(family == "global_disabled" for family, _ in findings)


def test_project_create_still_allowed_when_global_writes_disabled(monkeypatch):
    monkeypatch.setattr(config, "ALLOW_GLOBAL_WRITES", False)
    findings = server._schema_errors(_create("project"))
    assert not any(family == "global_disabled" for family, _ in findings)


def test_global_create_allowed_when_enabled(monkeypatch):
    monkeypatch.setattr(config, "ALLOW_GLOBAL_WRITES", True)
    findings = server._schema_errors(_create("global"))
    assert not findings


def test_global_validation_rejects_repo_name():
    intent = _create("global")
    body = VALID_BODY + "\nUse betts_basketball conventions.\n"
    verdict = validate.validate(intent, body, repo_name="betts_basketball")
    assert any(family == "global_repo_agnostic" for family, _ in verdict["findings"])


def test_global_validation_rejects_absolute_path():
    intent = _create("global")
    body = VALID_BODY + "\nRead C:\\Users\\ghadf\\repo\\config.json first.\n"
    verdict = validate.validate(intent, body)
    assert any(family == "global_repo_agnostic" for family, _ in verdict["findings"])


def test_global_validation_accepts_repo_agnostic_rule():
    intent = _create("global")
    verdict = validate.validate(intent, VALID_BODY)
    assert verdict["ok"], verdict["findings"]
