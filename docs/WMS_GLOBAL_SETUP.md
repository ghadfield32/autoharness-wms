# WMS AutoHarness — Global Production Setup

Canonical distribution: `ghadfield32/autoharness-wms`  
Release line: `0.5.4-wms.2`  
Pinned upstream base: `tigerless-labs/autoharness@ca39a72e4353ebef11b7de13c1fc7fa5f4df421b`

## What "global" means

One **user-scope Claude Code plugin installation** is available across local projects, while learned
knowledge remains split by blast radius:

- **project skills** → `<repo>/.claude/skills/`
- **global skills** → `~/.claude/skills/`

A global installation does not mean every lesson is globally shared. Repo-, framework-, provider-,
dataset-, model-, sport-, metric-, API-, or file-layout-specific knowledge stays project-scoped.
Global skills are reserved for durable rules that apply unchanged across unrelated repositories.

## Security boundary

The WMS distribution differs from the pinned upstream build in these important ways:

1. every persisted evidence slice, SKILL.md body, and support file passes the redactor;
2. literal values from secret-bearing environment variables are redacted in memory;
3. built-in rules cover provider tokens, generic secret assignments, complete private-key blocks,
   credentialed database/cache URIs, JWTs, and existing upstream secret/PII patterns;
4. project redaction rules can append through `AUTOHARNESS_EXTRA_REDACTION_RULES`;
5. unattended reflection never uses `--dangerously-skip-permissions`;
6. unattended Claude uses deny-by-default permission handling and only the exact stage_skill MCP is
   writable;
7. background reads are confined to **live AutoHarness-managed skill files**, not application source,
   credential stores, archives, shell state, Git, Railway, web tools, or arbitrary MCPs;
8. reflection always uses the redacted `bundle` carrier; a `fork` request fails closed to bundle;
9. Windows resolves the actual Claude executable instead of assuming a POSIX shim;
10. `AUTOHARNESS_ALLOW_GLOBAL_WRITES=0` rejects **all** global create/update/patch/delete/remove-file
    operations at the deterministic promoter while project learning and existing recall continue;
11. global candidate content must pass the existing repo-agnostic validator;
12. the reflector and `/autoharness:learn` are instructed to choose project scope whenever global
    applicability is uncertain.

## Install globally

The preferred installer performs two actions: installs the plugin at Claude Code **user scope** and
writes a safe AutoHarness profile into `~/.claude/settings.json` while preserving unrelated settings.

### Windows

```powershell
./scripts/install-global.ps1
```

### macOS / Linux

```bash
./scripts/install-global.sh
```

Equivalent plugin-only commands:

```text
claude plugin marketplace add ghadfield32/autoharness-wms
claude plugin install autoharness@autoharness-wms --scope user
```

The plugin-only path does not write the complete probation profile, although the code default still
keeps new global-skill writes frozen.

## Lifecycle

### 1. Probation — installer default

`scripts/install-global.*` calls:

```text
scripts/configure-user-settings.py --mode probation
```

The effective AutoHarness profile is:

```json
{
  "AUTOHARNESS_CARRIER": "bundle",
  "AUTOHARNESS_ALLOW_GLOBAL_WRITES": "0",
  "AUTOHARNESS_INDEX_SUSPENDED": "0",
  "AUTOHARNESS_GRADUATION_SUSPENDED": "1",
  "AUTOHARNESS_REFLECT_EVERY_N": "999999",
  "AUTOHARNESS_CONSOLIDATE_EVERY_N": "999999",
  "AUTOHARNESS_MATURITY_GLOBAL": "300",
  "AUTOHARNESS_CAPACITY_GLOBAL": "20",
  "AUTOHARNESS_MATURITY_PROJECT": "100",
  "AUTOHARNESS_CAPACITY_PROJECT": "50",
  "AUTOHARNESS_SNAPSHOT_KEEP": "5"
}
```

This gives a machine-global installation and recall surface while avoiding surprise background
learning or writes to the shared global skill tree before the installed runtime is checked.

### 2. Live acceptance

Use a disposable/synthetic task with a fake secret stored in a secret-bearing environment variable.

Required checks:

1. plugin loads in a fresh Claude Code session;
2. `/autoharness:learn` can stage and land a **project** lesson;
3. the exact fake secret is absent from project/global AutoHarness state and skills;
4. a new session can recall the learned project skill;
5. global creation is rejected while the probation profile is active;
6. no background process gains Bash, Write/Edit, web, deployment, GitHub mutation, or arbitrary MCP
   access.

This is the one gate that cannot be proven by repository CI alone because it exercises the installed
Claude Code host/plugin runtime.

### 3. Production promotion

After the live acceptance passes:

Windows:

```powershell
./scripts/promote-global.ps1
```

macOS / Linux:

```bash
./scripts/promote-global.sh
```

Production mode sets:

```text
AUTOHARNESS_ALLOW_GLOBAL_WRITES=1
AUTOHARNESS_GRADUATION_SUSPENDED=0
```

and removes the installer's `999999` cadence overrides so the normal AutoHarness reflection and
consolidation defaults apply. Existing custom cadence values are preserved.

### 4. Emergency freeze

Windows:

```powershell
./scripts/freeze-global.ps1
```

macOS / Linux:

```bash
./scripts/freeze-global.sh
```

Freeze mode changes only:

```text
AUTOHARNESS_ALLOW_GLOBAL_WRITES=0
```

so project learning and existing global/project recall remain available.

## Global promotion policy

Good global candidates:

- reproduce → diagnose → patch → targeted test → full gate;
- do not claim frontend completion from backend evidence alone;
- inspect existing architecture before creating parallel infrastructure;
- separate engineering evidence from scientific/model evidence;
- update the reusable procedure when a recurring correction is discovered.

Project-only examples:

- basketball EPV/VORP/VORA definitions;
- camera calibration geometry or coordinate conventions;
- Railway deployment topology;
- R2 bucket layout;
- WMS API/schema names;
- player-card implementation details;
- repo-specific model/data paths.

## CI / release gates

The canonical distribution is not ready to merge unless all of these remain green:

- Ruff lint;
- full upstream-derived suite on Linux;
- cross-platform unit suite on Windows/macOS/Linux with host-capability skips explicitly documented;
- Python 3.11 plus the supported Python 3.12 Linux check;
- WMS redaction/persistence/tool-wall/traversal tests;
- global create and all-action freeze tests;
- user-profile probation/production/freeze tests;
- plugin/marketplace distribution metadata tests;
- source regression test proving unattended spawn never reintroduces
  `--dangerously-skip-permissions`.

## Correctness model

AutoHarness decides whether a procedure appears reusable. It does **not** decide whether a scientific
or engineering assertion is true.

```text
reuse/adherence          -> evidence of usefulness
tests/evals/holdouts/CI  -> evidence of correctness
```

Model validation, geometry checks, schemas, holdouts, CI, and domain-specific tests remain above the
skill layer.

## Upgrade policy

Do not auto-merge upstream releases. For an upstream update:

1. fetch and pin the new upstream ref;
2. review capture, redaction, promoter, stage_skill, hooks, spawn, layer paths, agents, lifecycle,
   plugin metadata, and permissions;
3. integrate on a dedicated branch;
4. run the complete WMS matrix;
5. re-run the redaction/security tests;
6. bump the WMS release version;
7. merge only after all gates are green.

## Rollback

Plugin uninstall:

```text
claude plugin uninstall autoharness@autoharness-wms --scope user
```

Optional marketplace removal:

```text
claude plugin marketplace remove autoharness-wms
```

Uninstalling intentionally leaves learned skills/state on disk. Review AutoHarness sidecars/ledgers
before archiving or removing those folders; never bulk-delete human-authored skills.
