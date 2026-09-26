# WMS AutoHarness — Global Production Setup

This fork is the hardened World Model Sports build of AutoHarness.

## Goal

Run one AutoHarness installation across Claude Code projects while keeping two scopes separate:

- **project** → `<repo>/.claude/skills/`
- **global** → `~/.claude/skills/`

The global layer is for rules that apply unchanged across unrelated repositories. Repo-, framework-,
provider-, model-, dataset-, metric-, sport-, or file-layout-specific lessons stay project-scoped.

## Security changes in this fork

Compared with the pinned upstream base, the WMS fork adds:

1. literal redaction for secret-bearing environment variables;
2. provider patterns for Anthropic/OpenAI-style/router tokens;
3. generic `*_KEY`, `*_TOKEN`, `*_SECRET`, `*_PASSWORD`, and credential assignments;
4. optional appended project redaction rules through `AUTOHARNESS_EXTRA_REDACTION_RULES`;
5. redaction of SKILL.md bodies and support files, not only evidence slices;
6. a hook-enforced reflector tool allowlist: Read/Grep/Glob/stage_skill only;
7. denied reflector reads for common credential-bearing paths;
8. Windows Claude executable resolution;
9. `AUTOHARNESS_ALLOW_GLOBAL_WRITES` as a deterministic kill switch for new global skills;
10. CI gates: complete suite on Linux and hardened security/global suite on Windows.

## Recommended global configuration

Put the following environment values in the environment that launches Claude Code. These values can
also be placed in your global Claude settings if that is how you manage Claude Code environment
variables.

```json
{
  "env": {
    "AUTOHARNESS_CARRIER": "bundle",
    "AUTOHARNESS_ALLOW_GLOBAL_WRITES": "1",
    "AUTOHARNESS_INDEX_SUSPENDED": "0",
    "AUTOHARNESS_GRADUATION_SUSPENDED": "0",
    "AUTOHARNESS_MATURITY_GLOBAL": "300",
    "AUTOHARNESS_CAPACITY_GLOBAL": "20",
    "AUTOHARNESS_MATURITY_PROJECT": "100",
    "AUTOHARNESS_CAPACITY_PROJECT": "50",
    "AUTOHARNESS_SNAPSHOT_KEEP": "5"
  }
}
```

Do not use `fork` carrier for the WMS production profile. The `bundle` carrier keeps the reflector
on the redacted episode path.

### Emergency global freeze

To stop **new global writes** while leaving project learning and existing global recall intact:

```text
AUTOHARNESS_ALLOW_GLOBAL_WRITES=0
```

To stop index injection while measuring its value:

```text
AUTOHARNESS_INDEX_SUSPENDED=1
```

To stop automatic reflection without uninstalling:

```text
AUTOHARNESS_REFLECT_EVERY_N=999999
AUTOHARNESS_CONSOLIDATE_EVERY_N=999999
```

## Installation

In Claude Code:

```text
/plugin marketplace add ghadfield32/autoharness-wms
/plugin install autoharness@autoharness
/reload-plugins
```

The plugin name remains `autoharness` intentionally so its MCP namespace and agent references
continue to match the upstream architecture.

## Global promotion policy

A global skill is allowed only when all of the following are true:

- it can be applied unchanged in unrelated repositories;
- it contains no absolute local path;
- it contains no repository name;
- it is not tied to a framework, deployment provider, dataset, model family, sport, metric, or file layout;
- it expresses a durable workflow or user preference;
- it passes the deterministic promoter and redaction pipeline.

Examples that may be global:

- reproduce → diagnose → patch → targeted test → full gate;
- do not claim frontend completion from backend evidence alone;
- read the existing architecture before creating parallel infrastructure;
- separate engineering evidence from scientific/model evidence;
- update the reusable procedure when a recurring correction is discovered.

Examples that stay project-scoped:

- basketball EPV/VORP/VORA definitions;
- camera calibration geometry and coordinate conventions;
- Railway deployment details;
- R2 bucket layout;
- WMS API/schema names;
- frontend player-card implementation details.

## Acceptance gates

The fork is eligible for production only when:

1. Linux full test suite passes;
2. Windows `tests/security` passes;
3. no dummy secret survives the persisted path;
4. reflector cannot run Bash, Write/Edit, web tools, deployment MCPs, or arbitrary MCPs;
5. global creation fails when `AUTOHARNESS_ALLOW_GLOBAL_WRITES=0`;
6. global repo-specific content is rejected;
7. project learning remains functional when global writes are frozen.

## Runtime verification

After installation, use a synthetic session before relying on the plugin for sensitive work.

1. Put a fake value in a secret-bearing environment variable.
2. Solve a trivial task.
3. Run `/learn`.
4. Search `~/.claude/autoharness`, `~/.claude/skills`, and the current project's
   `.claude/autoharness` / `.claude/skills` trees for the exact fake value.
5. The exact value must not appear anywhere.
6. Start another Claude Code session and verify the learned skill can be recalled.

## Rollback

Freeze global writes:

```text
AUTOHARNESS_ALLOW_GLOBAL_WRITES=0
```

Disable the plugin through Claude Code if needed. Existing skills and state remain on disk. Global
AutoHarness state lives under `~/.claude/autoharness/`; global skills live under
`~/.claude/skills/`. Project equivalents live under each repository's `.claude/` tree.

Archive or remove only AutoHarness-authored skills after reviewing their sidecars/ledgers; do not
bulk-delete hand-written skills.
