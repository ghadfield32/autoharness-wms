"""Every persisted byte (skill body, subfiles, evidence) is redacted; the child tool wall holds."""
import pytest

from autoharness.hook import dispatch, promoter

SECRET = "sk-ant-api03-PERSISTENCECANARYPERSISTENCECANARY"


def test_promoter_redacts_body_files_and_evidence(tmp_path, monkeypatch):
    calls = {}
    monkeypatch.setattr(promoter.skill_store, "write_body", lambda lv, n, body, r: calls.setdefault("body", body))
    monkeypatch.setattr(promoter.sidecar, "create", lambda *a, **k: None)
    monkeypatch.setattr(promoter.counters, "request_count", lambda *a, **k: 0)
    monkeypatch.setattr(promoter.ledger, "append", lambda lv, n, e, r: calls.setdefault("led", e))
    written = {}
    monkeypatch.setattr(promoter.atomic, "write_text", lambda p, t: written.__setitem__(str(p), t))
    monkeypatch.setattr(promoter.layer, "symbol_dir", lambda lv, n, r: tmp_path)
    monkeypatch.setattr(promoter.layer, "subfile_path", lambda lv, n, rel, r: tmp_path / rel)
    intent = {"action": "create", "reason": "r", "evidence": f"user said {SECRET}",
              "files": {"references/notes.md": f"key {SECRET}"}}
    promoter._land("create", intent, f"# skill\nuse {SECRET}\n", "project", "s", tmp_path)
    blob = calls["body"] + "".join(written.values()) + str(calls["led"])
    assert SECRET not in blob and "[REDACTED:secret:" in blob


def _pre(tool, tool_input=None):
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input or {},
            "agent_type": "autoharness:reflector"}


@pytest.mark.parametrize("tool", ["Bash", "Write", "Edit", "MultiEdit", "NotebookEdit", "WebFetch",
                                  "WebSearch", "Agent", "mcp__railway__deploy", "mcp__github__merge"])
def test_child_disallowed_tools_denied(tool, tmp_path):
    assert dispatch.dispatch(_pre(tool), roots={"project": tmp_path, "global": tmp_path}).get("deny")


@pytest.mark.parametrize("path", [".env", r"C:\repo\.env.local", "/home/u/.ssh/id_rsa", r"C:\Users\u\.aws\credentials",
                                  r"C:\Users\u\.codex\config.toml", "certs/server.pem", "~/.git-credentials"])
def test_child_credential_reads_denied(path, tmp_path):
    assert dispatch.dispatch(_pre("Read", {"file_path": path}), roots={"project": tmp_path, "global": tmp_path}).get("deny")


@pytest.mark.parametrize("tool,inp", [("Read", {"file_path": "src/app.py"}), ("Grep", {"pattern": "def main"}),
                                      ("Glob", {"pattern": "**/*.md"}),
                                      ("mcp__plugin_autoharness_stage_skill__stage_skill", {})])
def test_child_allowed_tools_pass(tool, inp, tmp_path):
    assert not dispatch.dispatch(_pre(tool, inp), roots={"project": tmp_path, "global": tmp_path}).get("deny")


def test_main_session_unaffected(tmp_path):
    ev = _pre("Bash")
    ev.pop("agent_type")
    assert not dispatch.dispatch(ev, roots={"project": tmp_path, "global": tmp_path}).get("deny")


@pytest.mark.parametrize("rel", ["../../src/app.py", "references/../../x.md", r"C:\Users\u\x.md",
                                 "/etc/passwd", r"scripts\..\x", "notes.md", "src/app.py"])
def test_stage_subfile_traversal_rejected(rel):
    from autoharness.lib import layer
    with pytest.raises(ValueError):
        layer.check_subfile(rel)
