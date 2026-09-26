# WMS AutoHarness 0.5.4-wms.2

This is the first WMS release intended as the canonical **user-scope/global distribution**.

## Base

- Upstream: `tigerless-labs/autoharness`
- Pinned upstream commit: `ca39a72e4353ebef11b7de13c1fc7fa5f4df421b`
- Previous WMS release: `0.5.4-wms.1`

## Security and distribution changes since wms.1

- removes unattended `--dangerously-skip-permissions`;
- runs background Claude with deny-by-default permission handling;
- forces reflection through the redacted bundle carrier; fork requests fail closed to bundle;
- restricts background file reads to live AutoHarness-managed skill files;
- allows only the exact AutoHarness stage_skill MCP as the child write surface;
- adds complete private-key-block, credentialed DB/cache URI, and JWT redaction;
- keeps literal environment-secret redaction and provider/generic-assignment rules from wms.1;
- keeps persisted SKILL.md, support-file, and evidence redaction from wms.1;
- keeps Windows Claude executable resolution;
- fixes the global-write freeze so **create/update/patch/delete/remove_file** are all rejected while frozen;
- changes the code default for global writes to frozen;
- adds conservative project-vs-global promotion guidance;
- adds user-scope Windows/macOS/Linux installers and uninstallers;
- adds an idempotent `~/.claude/settings.json` profile configurator;
- adds probation → production → freeze operating modes;
- expands CI/lint and cross-platform coverage;
- adds regression tests for plugin metadata, permission boundary, distribution profile, and global lifecycle.

## Global lifecycle

Installers start in **probation**:

- plugin installed at Claude Code user scope;
- `AUTOHARNESS_ALLOW_GLOBAL_WRITES=0`;
- automatic reflection/consolidation paused;
- graduation review suspended;
- recall/index remain available;
- manual project-scope `/autoharness:learn` can be used for the live canary.

After the installed-runtime acceptance test:

```text
scripts/promote-global.ps1
# or
scripts/promote-global.sh
```

Production mode:

- enables global writes;
- restores normal reflection/consolidation cadence;
- restores lifecycle graduation.

Emergency rollback of shared-library mutation:

```text
scripts/freeze-global.ps1
# or
scripts/freeze-global.sh
```

Freeze mode leaves project learning and existing recall intact.

## Canonical docs

- `docs/WMS_GLOBAL_SETUP.md`
- `docs/WMS_GLOBAL_ROLLOUT.md`

## Correctness contract

AutoHarness reuse/adherence measures usefulness. Repository tests, model evaluation, holdouts, schemas,
geometry validation, CI, and domain truth remain authoritative.
