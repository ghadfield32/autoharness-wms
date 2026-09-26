# AutoHarness WMS — Global Rollout and Security Contract

## Purpose

This repository is the canonical WMS distribution of AutoHarness. The plugin is installed at **Claude
Code user scope**, so one installation is available across local projects. Learned skills remain
layered:

- **project**: repo-specific procedures and conventions under the repo's `.claude/skills/`;
- **global**: repo-agnostic techniques and durable workflow preferences under `~/.claude/skills/`.

A global plugin does **not** mean every learned lesson becomes a global skill. The promoter still
enforces the project/global distinction.

## Provenance

- Upstream: `tigerless-labs/autoharness`
- Pinned upstream baseline: `ca39a72e4353ebef11b7de13c1fc7fa5f4df421b`
- WMS security hardening began at commit `e0109bd`
- Windows Claude launcher fix: `48b2b78`
- WMS release line: `0.5.4-wms.2`

## Security invariants

The WMS fork must keep all of these true:

1. **Every persisted byte is redacted at egress.** Evidence, SKILL.md bodies, and landed support files
   all pass through the same redactor.
2. **Known secret literals are removed in memory.** Values of environment variables whose names end
   in KEY, TOKEN, SECRET, PASSWORD/PASSWD, CREDENTIAL(S), or AUTH are redacted anywhere they occur.
   `AUTOHARNESS_REDACT_ENV_VARS` adds explicit names without persisting their values.
3. **Project rules append; they never replace built-ins.**
   `AUTOHARNESS_EXTRA_REDACTION_RULES` may point to an additional TOML rules file.
4. **Background reflection never uses bypassPermissions.** It starts with Claude Code `dontAsk`,
   `--permission-prompts none`, and a reduced built-in tool surface.
5. **Background reads are skill-only.** The reflector/curator may read live AutoHarness-managed skill
   files. It cannot inspect application source, credential files, archives, shell state, Git, Railway,
   web tools, or arbitrary MCP servers.
6. **Only the exact stage_skill MCP is writable.** The deterministic promoter remains the sole disk
   writer and validates routing, ownership, structure, traversal, completeness, and safety.
7. **No fork carrier.** WMS executes only the redacted bundle carrier; a fork request fails closed to
   bundle.
8. **AutoHarness never edits human-authored skills.** Lifecycle and consolidation operate only on
   self-authored symbols carrying AutoHarness sidecar/ledger markers.
9. **Global writes fail closed.** `AUTOHARNESS_ALLOW_GLOBAL_WRITES=0` rejects every global-layer
   create/update/patch/delete/remove-file at the promoter while project learning and existing recall remain available.
10. **Correctness remains external.** Skill reuse is evidence of usefulness, not truth. Repository
   tests, schemas, holdouts, geometry checks, model evaluations, and CI remain authoritative.

## Global installation

### Windows

```powershell
./scripts/install-global.ps1
```

### macOS / Linux

```bash
./scripts/install-global.sh
```

Equivalent shell commands:

```text
claude plugin marketplace add ghadfield32/autoharness-wms
claude plugin install autoharness@autoharness-wms --scope user
```

User scope is intentional: local Claude Code surfaces on the machine use the same user-level plugin
configuration. The repo installers also apply the **probation** profile: automatic reflection is paused,
global writes are frozen, and lifecycle graduation is suspended until the installed runtime canary
passes. `scripts/promote-global.*` enables production mode; `scripts/freeze-global.*` immediately
freezes new shared-library writes again.

## Operating model

```text
verified work episode
        |
        v
redacted capture + digest
        |
        v
deny-by-default reflector
        |
        v
candidate intent
        |
        v
deterministic promoter
        |
        +--> project skill
        |
        +--> global skill (only when repo-agnostic)
        |
        v
later reuse / patch / consolidation
```

Use `/autoharness:learn` after a lesson has been verified and is worth preserving immediately.
During installer probation, automatic reflection is deliberately paused. Production promotion restores
the normal cadence; manual and automatic learning use the same promoter and security boundary.

## Test gates

A release is acceptable only when:

- the upstream-derived unit suite passes on Linux/macOS/Windows, except capability-specific tests
  explicitly skipped when the host cannot provide that capability;
- WMS secret-shape, literal-env, persistence, permission-wall, and traversal tests pass;
- Windows resolves the actual Claude executable rather than assuming a POSIX executable shim;
- the plugin/marketplace metadata validates;
- no test or implementation reintroduces `--dangerously-skip-permissions` into the background path.

## Upgrading from upstream

Do not auto-merge upstream changes. For each upstream update:

1. fetch the new upstream ref;
2. review changes touching capture, redaction, promoter, stage_skill, hooks, spawn, layer paths, agents,
   plugin metadata, and lifecycle;
3. rebase or cherry-pick into a dedicated update branch;
4. run the complete matrix;
5. re-run the WMS security tests;
6. bump the WMS plugin version only after the branch is green;
7. merge to the WMS default branch.

The WMS fork should remain small: security boundary, Windows/cross-platform support, distribution
automation, tests, and documentation. Upstream learning logic should be changed only when necessary.
