"""REF launch vehicle: deterministically assemble the reflector input → detached spawn a child session → connect to promoter.drain.

architecture line 29 / [reflector-subagent] / [cap]: at trigger time CAP gives "redacted episode window +
trigger cadence"; this step assembles the three pieces (window + the existing skill description index
(compare-first dedupe source, skips archived) + the single-source format_spec) and feeds them via
stdin to the cross-process reflector — nothing is persisted; the bundle lives only in the pipe. spawn sets CHILD_SESSION_ENV (recursion guard) +
injects run_id/root via env (stage_skill uses these to append back to the queue), then drains the intent
queue to disk after the child session ends. Authoring and landing are fully split across processes from
here: the reflector only appends intents, the promoter exclusively validates and lands.

ponytail: run() is the body of the "detached background job" (synchronous spawn→wait→drain); the "do not block the host Stop" detach is started in the background at the hook top level by the Phase 7 dispatch calling run(). spawn_fn is injectable (system tests use a fake reflector script in place of the real claude). Precise handling of the transcript upper-bound race (cap.md open) is still tolerated at v0.
"""
import os
import subprocess
import sys
import tarfile
from pathlib import Path

from autoharness import config
from autoharness.hook import capture, promoter
from autoharness.lib import counters, layer, sidecar, skill_store, validate


def description_index(roots=None, *, agent_only=False):
    roots = roots or {}
    lines = []
    for lyr in layer.LAYERS:
        root = roots.get(lyr)
        skills = layer.skills_dir(lyr, root)
        if not skills.exists():
            continue
        for path in sorted(skills.glob(f"*/{skill_store.SKILL_FILE}")):
            symbol = path.parent.name
            if agent_only and not sidecar.is_agent_created(lyr, symbol, root):
                continue  # curator only ever sees its own skills; native/user stay out of the pool
            fm = validate._frontmatter(path.read_text()) or {}
            name = fm.get("name") or symbol
            desc = fm.get("description") or "(no description)"
            lines.append(f"- {name} [{lyr}]: {desc}")
    return "\n".join(lines) if lines else "(no live skills yet)"


def build_bundle(window, index, spec, digest=""):
    preamble = (
        "# Prior context digest (older exchanges, tool outputs omitted — background only,"
        " never an evidence source)\n\n" + digest + "\n\n"
    ) if digest else ""
    return (
        preamble
        + "# Episode window (redacted)\n\n" + window
        + "\n\n# Existing skills (compare-first: dedupe / patch / where)\n\n" + index
        + "\n\n# Authoring + format spec (write to satisfy this)\n\n" + spec + "\n"
    )


def build_curator_bundle(index, spec):
    # The curator consolidates the whole agent-authored library, not one episode — so no window.
    return (
        "# Agent-authored skills (consolidate: merge narrow siblings into class-level umbrellas)\n\n"
        + index
        + "\n\n# Authoring + format spec (merged skills must satisfy this)\n\n" + spec + "\n"
    )


# The upstream fork carrier replays the parent transcript and therefore bypasses the WMS redacted-bundle
# boundary. Keep its builders for compatibility/tests, but WMS run() fails closed to the bundle carrier.
FORK_INSTRUCTION = (
    "Autoharness reflection pass (forked session: the conversation above is your evidence source).\n"
    "Compare-first against the skill index below: prefer patching an existing skill over creating a\n"
    "new one; distill only class-level reusable lessons, never session narratives. When you distill\n"
    "a new rule or preference, search the managed skill trees for overlapping or contradicting\n"
    "statements and stage updates so the new supersedes the old. Propose every change exclusively\n"
    "via the stage_skill tool — never write files directly. Evidence must quote this session\n"
    "verbatim. If nothing is worth keeping, stage nothing.\n"
)


STAGE_SKILL_TOOL = "mcp__plugin_autoharness_stage_skill__stage_skill"


def _unattended_permissions():
    # Claude Code >=2.1.259: no interactive approver exists, so every unapproved call is denied.
    # --tools restricts built-ins; --allowedTools pre-approves only Read + our deterministic stage MCP.
    return ["--permission-mode", "dontAsk", "--permission-prompts", "none",
            "--tools", "Read", "--allowedTools", "Read", STAGE_SKILL_TOOL]


def build_fork_command(*, session_id, claude_bin):
    return ([claude_bin, "-p", "--resume", str(session_id), "--fork-session"]
            + _unattended_permissions())


def build_fork_prompt(index, spec):
    return (FORK_INSTRUCTION
            + "\n# Existing skills (compare-first: dedupe / patch / where)\n\n" + index
            + "\n\n# Authoring + format spec (write to satisfy this)\n\n" + spec + "\n")


def build_command(*, agent, claude_bin):
    # Unattended, but never bypassPermissions: permission prompts are denied and the tool surface is
    # explicitly reduced. The hook-level allowlist remains a second, independent wall.
    return [claude_bin, "-p", "--agent", agent] + _unattended_permissions()


def child_env(run_id, root, *, base_env=None):
    env = dict(os.environ if base_env is None else base_env)
    env[config.CHILD_SESSION_ENV] = "1"
    env[config.RUN_ID_ENV] = run_id
    env[config.PROJECT_ROOT_ENV] = str(root)
    return env


def _detached_spawn(argv, env, bundle):
    subprocess.run(argv, input=bundle, text=True, env=env, capture_output=True, check=False)


def run(window_text, run_id, *, roots, repo_name=None, agent=None, claude_bin=None,
        spec_path=None, digest="", session_id=None, carrier=None, spawn_fn=None):
    roots = roots or {}
    proot = roots.get(layer.PROJECT)
    spec = (spec_path or config.FORMAT_SPEC).read_text()

    # WMS hardening: always use the redacted bundle. A fork replays the full parent transcript and
    # therefore crosses the redaction boundary even if its tool permissions are narrow.
    # carrier/session_id remain in the public call signature for upstream compatibility; WMS ignores
    # both for reflection transport and always materializes the redacted bundle.
    argv = build_command(agent=agent or config.REFLECTOR_AGENT,
                         claude_bin=claude_bin or config.CLAUDE_BIN)
    payload = build_bundle(window_text, description_index(roots), spec, digest=digest)

    env = child_env(run_id, proot)
    (spawn_fn or _detached_spawn)(argv, env, payload)

    return promoter.drain(run_id, roots=roots, repo_name=repo_name)


def _snapshot_skills(run_id, roots):
    """Pre-run library snapshot (direction E, mirrors Hermes): covers the one risk atomic landing
    and reversible archiving cannot — a whole curator run writing the library wrong. Recovery is a
    manual unpack; rotation keeps SNAPSHOT_KEEP per layer."""
    snapdir = layer.state_dir(layer.PROJECT, roots.get(layer.PROJECT)) / "snapshots"
    snapdir.mkdir(parents=True, exist_ok=True)
    for lyr in layer.LAYERS:
        skills = layer.skills_dir(lyr, roots.get(lyr))
        if not skills.exists():
            continue
        with tarfile.open(snapdir / f"{run_id}-{lyr}.tar.gz", "w:gz") as tar:
            tar.add(skills, arcname="skills")
        kept = sorted(snapdir.glob(f"*-{lyr}.tar.gz"), key=lambda p: p.stat().st_mtime)
        for old in kept[: max(0, len(kept) - config.SNAPSHOT_KEEP)]:
            old.unlink()


def run_curator(run_id, *, roots, repo_name=None, agent=None, claude_bin=None,
                spec_path=None, spawn_fn=None):
    roots = roots or {}
    try:
        _snapshot_skills(run_id, roots)
    except Exception:
        pass  # a transient disk issue must not silently disable curation (Hermes's exact trade-off)
    spec = (spec_path or config.FORMAT_SPEC).read_text()
    bundle = build_curator_bundle(description_index(roots, agent_only=True), spec)

    argv = build_command(agent=agent or config.CURATOR_AGENT,
                         claude_bin=claude_bin or config.CLAUDE_BIN)
    env = child_env(run_id, roots.get(layer.PROJECT))
    (spawn_fn or _detached_spawn)(argv, env, bundle)

    return promoter.drain(run_id, roots=roots, repo_name=repo_name)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "--curate":
        run_id, proot, groot = argv[1:]
        return run_curator(run_id, roots={layer.PROJECT: Path(proot), layer.GLOBAL: Path(groot)})
    transcript_path, session_id, run_id, proot, groot = argv
    roots = {layer.PROJECT: Path(proot), layer.GLOBAL: Path(groot)}
    offset = counters.session_offset(session_id, roots[layer.PROJECT])
    window_text, new_offset = capture.window(transcript_path, offset)
    result = run(window_text, run_id, roots=roots, session_id=session_id,
                 digest=capture.digest(transcript_path, offset))
    counters.write_session_offset(session_id, new_offset, roots[layer.PROJECT])
    return result


if __name__ == "__main__":
    main()
