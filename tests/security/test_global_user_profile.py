import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "configure-user-settings.py"


def _module():
    spec = importlib.util.spec_from_file_location("wms_user_settings", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_probation_preserves_unrelated_settings_and_freezes_global():
    mod = _module()
    src = {"model": "sonnet", "env": {"KEEP_ME": "yes"}}
    out = mod.apply_mode(src, "probation")
    assert out["model"] == "sonnet"
    assert out["env"]["KEEP_ME"] == "yes"
    assert out["env"]["AUTOHARNESS_CARRIER"] == "bundle"
    assert out["env"]["AUTOHARNESS_ALLOW_GLOBAL_WRITES"] == "0"
    assert out["env"]["AUTOHARNESS_GRADUATION_SUSPENDED"] == "1"
    assert out["env"]["AUTOHARNESS_REFLECT_EVERY_N"] == "999999"
    assert out["env"]["AUTOHARNESS_CONSOLIDATE_EVERY_N"] == "999999"


def test_production_promotes_global_and_restores_default_cadence():
    mod = _module()
    prob = mod.apply_mode({}, "probation")
    out = mod.apply_mode(prob, "production")
    assert out["env"]["AUTOHARNESS_ALLOW_GLOBAL_WRITES"] == "1"
    assert out["env"]["AUTOHARNESS_GRADUATION_SUSPENDED"] == "0"
    assert "AUTOHARNESS_REFLECT_EVERY_N" not in out["env"]
    assert "AUTOHARNESS_CONSOLIDATE_EVERY_N" not in out["env"]


def test_production_does_not_delete_custom_cadence():
    mod = _module()
    src = {"env": {"AUTOHARNESS_REFLECT_EVERY_N": "75", "AUTOHARNESS_CONSOLIDATE_EVERY_N": "400"}}
    out = mod.apply_mode(src, "production")
    assert out["env"]["AUTOHARNESS_REFLECT_EVERY_N"] == "75"
    assert out["env"]["AUTOHARNESS_CONSOLIDATE_EVERY_N"] == "400"


def test_freeze_only_disables_global_writes():
    mod = _module()
    src = mod.apply_mode({}, "production")
    src["env"]["KEEP_ME"] = "yes"
    out = mod.apply_mode(src, "freeze")
    assert out["env"]["AUTOHARNESS_ALLOW_GLOBAL_WRITES"] == "0"
    assert out["env"]["AUTOHARNESS_GRADUATION_SUSPENDED"] == "0"
    assert out["env"]["KEEP_ME"] == "yes"
