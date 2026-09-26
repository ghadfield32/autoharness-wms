#!/usr/bin/env python3
"""Configure the user-scope AutoHarness WMS profile without clobbering other Claude settings."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

COMMON = {
    "AUTOHARNESS_CARRIER": "bundle",
    "AUTOHARNESS_INDEX_SUSPENDED": "0",
    "AUTOHARNESS_MATURITY_GLOBAL": "300",
    "AUTOHARNESS_CAPACITY_GLOBAL": "20",
    "AUTOHARNESS_MATURITY_PROJECT": "100",
    "AUTOHARNESS_CAPACITY_PROJECT": "50",
    "AUTOHARNESS_SNAPSHOT_KEEP": "5",
}
WMS_KEYS = set(COMMON) | {
    "AUTOHARNESS_ALLOW_GLOBAL_WRITES",
    "AUTOHARNESS_GRADUATION_SUSPENDED",
    "AUTOHARNESS_REFLECT_EVERY_N",
    "AUTOHARNESS_CONSOLIDATE_EVERY_N",
}


def apply_mode(settings: dict, mode: str) -> dict:
    out = dict(settings)
    env = dict(out.get("env") or {})
    env.update(COMMON)

    if mode == "probation":
        env.update({
            "AUTOHARNESS_ALLOW_GLOBAL_WRITES": "0",
            "AUTOHARNESS_GRADUATION_SUSPENDED": "1",
            "AUTOHARNESS_REFLECT_EVERY_N": "999999",
            "AUTOHARNESS_CONSOLIDATE_EVERY_N": "999999",
        })
    elif mode == "production":
        env.update({
            "AUTOHARNESS_ALLOW_GLOBAL_WRITES": "1",
            "AUTOHARNESS_GRADUATION_SUSPENDED": "0",
        })
        for key in ("AUTOHARNESS_REFLECT_EVERY_N", "AUTOHARNESS_CONSOLIDATE_EVERY_N"):
            if env.get(key) == "999999":
                env.pop(key)
    elif mode == "freeze":
        env["AUTOHARNESS_ALLOW_GLOBAL_WRITES"] = "0"
    else:
        raise ValueError(f"unknown mode: {mode}")

    out["env"] = env
    return out


def load_settings(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    if "env" in data and data["env"] is not None and not isinstance(data["env"], dict):
        raise ValueError(f"{path}: env must be a JSON object")
    return data


def write_settings(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".autoharness-wms.bak"))
    tmp = path.with_suffix(path.suffix + ".autoharness-wms.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("probation", "production", "freeze"), default="probation")
    parser.add_argument("--settings", type=Path, default=Path.home() / ".claude" / "settings.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    before = load_settings(args.settings)
    after = apply_mode(before, args.mode)
    if args.dry_run:
        print(json.dumps({k: after["env"].get(k) for k in sorted(WMS_KEYS)}, indent=2))
        return 0

    write_settings(args.settings, after)
    print(f"AutoHarness WMS user profile set to {args.mode}: {args.settings}")
    print(f"global writes={after['env'].get('AUTOHARNESS_ALLOW_GLOBAL_WRITES')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
