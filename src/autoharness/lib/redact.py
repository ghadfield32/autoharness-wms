"""egress redline consumer: redacts secret/PII slices at the moment they are materialized downstream.

The rule set is the single source pointed to by config (redaction_rules.toml, shared by CAP egress +
LED); this module only consumes rules, it does not own them. Each match is replaced wholesale with
[REDACTED:<category>:<name>], erring on the side of over-redaction for safety.

Three layers, applied in order:
1. literal values of secret-bearing environment variables (names matching config.SECRET_ENV_NAME, plus
   any listed in AUTOHARNESS_REDACT_ENV_VARS) — catches a secret printed without its variable name;
2. packaged rules + an optional project rules file (AUTOHARNESS_EXTRA_REDACTION_RULES), appended;
3. nothing else — the values read in layer 1 live only in memory and are never persisted.
"""
import functools
import os
import re
import tomllib
from pathlib import Path

from autoharness import config


def _load(path):
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return [(category, rule["name"], re.compile(rule["pattern"]))
            for category in ("secret", "pii") for rule in data.get(category, [])]


@functools.lru_cache(maxsize=8)
def _rules(rules_path, extra_path):
    compiled = _load(rules_path or config.REDACTION_RULES)
    if extra_path:
        compiled += _load(extra_path)  # project rules append to, never replace, the packaged set
    return compiled


def _secret_literals(env):
    names = {n.strip() for n in env.get(config.REDACT_ENV_VARS_ENV, "").split(",") if n.strip()}
    names |= {n for n in env if config.SECRET_ENV_NAME.search(n)}
    values = {env[n] for n in names if len(env.get(n) or "") >= config.SECRET_LITERAL_MIN_LEN}
    return sorted(values, key=len, reverse=True)  # longest first so a prefix never masks a longer value


def redact(text, rules_path=None, *, env=None):
    env = os.environ if env is None else env
    out = text
    for value in _secret_literals(env):
        out = out.replace(value, "[REDACTED:secret:env_literal]")
    for category, name, rx in _rules(rules_path, env.get(config.EXTRA_REDACTION_RULES_ENV) or None):
        out = rx.sub(f"[REDACTED:{category}:{name}]", out)
    return out
