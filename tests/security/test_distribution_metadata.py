import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_wms_plugin_manifest_identity():
    data = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert data["name"] == "autoharness"  # preserve plugin/MCP namespace
    assert data["displayName"] == "AutoHarness WMS"
    assert data["version"] == "0.5.4-wms.2"
    assert "ghadfield32/autoharness-wms" in data["homepage"]


def test_wms_marketplace_identity_and_source():
    data = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert data["name"] == "autoharness-wms"
    assert data["plugins"][0]["name"] == "autoharness"
    assert data["plugins"][0]["source"] == "./"


def test_background_spawn_source_never_reintroduces_bypass_permissions():
    source = (ROOT / "src" / "autoharness" / "hook" / "spawn.py").read_text(encoding="utf-8")
    assert "--dangerously-skip-permissions" not in source
    assert '"dontAsk"' in source
    assert '"--permission-prompts", "none"' in source
