# WMS AutoHarness 0.5.4-wms.1

Canonical repository: `ghadfield32/autoharness-wms`

Default branch: `wms/security-hardening`

Pinned upstream base: `tigerless-labs/autoharness@ca39a72e4353ebef11b7de13c1fc7fa5f4df421b`

## What this release adds

- literal secret-value redaction sourced from secret-bearing environment variables;
- redaction patterns for `sk-ant-`, `sk-` / `sk-proj-`, `rk_`, and generic secret assignments;
- optional appended project rules via `AUTOHARNESS_EXTRA_REDACTION_RULES`;
- persisted SKILL.md bodies and support files pass the redaction boundary;
- reflector child sessions are hook-limited to Read/Grep/Glob/stage_skill;
- common credential-bearing paths are denied to reflector reads;
- Windows Claude Code executable resolution for npm `.cmd` installs;
- deterministic `AUTOHARNESS_ALLOW_GLOBAL_WRITES` kill switch;
- conservative reflector and `/learn` guidance for global promotion;
- Linux full-suite and Windows security/global GitHub Actions gates;
- global production and rollback runbook.

## Scope model

`project` skills live under `<repo>/.claude/skills/`.

`global` skills live under `~/.claude/skills/` and are visible across projects.

Global is reserved for repo-agnostic workflow rules and durable preferences. Domain- or stack-specific
knowledge remains project-scoped.

## Test history

Before hardening, the upstream redactor failed WMS fake-secret cases including router-style,
Anthropic-style, AWS/R2-style values. The WMS security suite was added to prevent regression.

The production CI gate runs:

- full upstream + WMS suite on Linux;
- WMS security/global suite on Windows.

## Operator controls

Freeze new global writes:

```
AUTOHARNESS_ALLOW_GLOBAL_WRITES=0
```

Disable the recall index:

```
AUTOHARNESS_INDEX_SUSPENDED=1
```

Pause automatic reflection:

```
AUTOHARNESS_REFLECT_EVERY_N=999999
AUTOHARNESS_CONSOLIDATE_EVERY_N=999999
```

See `docs/WMS_GLOBAL_SETUP.md` for installation, verification, acceptance gates, and rollback.
