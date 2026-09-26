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


def _global_skill(tmp_path):
    from autoharness.lib import skill_store
    groot, proot = tmp_path / "g", tmp_path / "p"
    from autoharness.lib import sidecar
    skill_store.write_body("global", "verify-before-claiming", VALID_BODY, groot)
    sidecar.create("global", "verify-before-claiming", 0, groot)  # agent-created, so modify intents are admissible
    return {"global": groot, "project": proot}


def test_unfrozen_global_update_lands(monkeypatch, tmp_path):
    from autoharness.hook import promoter
    from autoharness.lib import skill_store
    roots = _global_skill(tmp_path)
    monkeypatch.setattr(config, "ALLOW_GLOBAL_WRITES", True)
    new = VALID_BODY + "\nAlso run the full gate.\n"
    out = promoter.promote({"action": "update", "name": "verify-before-claiming", "reason": "r",
                            "evidence": "e", "body": new}, roots=roots)
    assert skill_store.read_body("global", "verify-before-claiming", roots["global"]) != VALID_BODY, out


def test_frozen_global_blocks_every_modify_action(monkeypatch, tmp_path):
    from autoharness.hook import promoter
    from autoharness.lib import skill_store
    roots = _global_skill(tmp_path)
    monkeypatch.setattr(config, "ALLOW_GLOBAL_WRITES", False)
    base = {"name": "verify-before-claiming", "reason": "r", "evidence": "e"}
    for intent in ({**base, "action": "update", "body": VALID_BODY + "\nextra\n"},
                   {**base, "action": "patch", "old_string": "Verify", "new_string": "Check"},
                   {**base, "action": "delete"}):
        out = promoter.promote(intent, roots=roots)
        assert "global_disabled" in str(out), (intent["action"], out)
        assert skill_store.read_body("global", "verify-before-claiming", roots["global"]) == VALID_BODY, intent["action"]
