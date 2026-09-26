"""WMS security gate: secret shapes seen in the Betts/WMS stack must never survive the egress redline."""
import pytest

from autoharness.lib.redact import redact

CANARY = "AUTOHARNESS_TEST_SECRET_DO_NOT_KEEP_9f83a7d1_CANARY"
NO_ENV = {}

SECRETS = [
    "sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "sk-proj-abcdefghijklmnopqrstuvwxyz012345",
    "rk_live_9f83a7b6c5d4e3f2a1b0",
    "rk_9f83a7b6c5d4e3f2a1b0c9d8",
    "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "AKIAABCDEFGHIJKLMNOP",
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload",
]

ASSIGNMENTS = [
    "AWS_SECRET_ACCESS_KEY=abcd1234abcd1234abcd1234abcd1234abcd1234",
    "R2_KEY=abc123secretvalue",
    "R2_SECRET_ACCESS_KEY=f00dbabef00dbabef00dbabe",
    "WEAVE_ROUTER_KEY=zzzzyyyyxxxxwwww",
    "RAILWAY_TOKEN=6f1c1e2a-1111-2222-3333-444455556666",
    "ANTHROPIC_API_KEY=whatever-the-value-is-here",
    "export R2_KEY=abc123secretvalue",
    "$env:R2_KEY = 'abc123secretvalue'",
    'R2_KEY="abc123secretvalue"',
    '{"r2_secret_access_key": "abc123secretvalue"}',
    "password: hunter2longpass",
]


@pytest.mark.parametrize("secret", SECRETS)
@pytest.mark.parametrize("frame", ["{}", "connecting with {} now", "Error: auth failed for '{}'", '{{"k": "{}"}}'])
def test_provider_shapes_redacted_in_any_frame(secret, frame):
    out = redact(frame.format(secret), env=NO_ENV)
    assert secret not in out and "[REDACTED:secret:" in out


@pytest.mark.parametrize("line", ASSIGNMENTS)
def test_secret_assignments_redacted(line):
    value = line.split("=", 1)[-1].split(":", 1)[-1].strip(" '\"}")
    out = redact(line, env=NO_ENV)
    assert value not in out, out


def test_bare_literal_redacted_via_auto_detected_env_name():
    env = {"R2_SECRET_ACCESS_KEY": CANARY}
    for text in (CANARY, f"echo {CANARY}", f"connecting with {CANARY}", f"export R2_KEY={CANARY}"):
        assert CANARY not in redact(text, env=env)


def test_bare_literal_redacted_via_explicit_env_list():
    env = {"R2_BUCKET_THING": CANARY, "AUTOHARNESS_REDACT_ENV_VARS": "R2_BUCKET_THING"}
    assert CANARY not in redact(f"used {CANARY} to connect", env=env)


def test_short_env_values_do_not_shred_text():
    env = {"SOME_TOKEN": "1", "FLAG_KEY": "true"}
    assert redact("step 1 is true", env=env) == "step 1 is true"


def test_extra_rules_append_not_replace(tmp_path):
    rules = tmp_path / "extra.toml"
    rules.write_text("[[secret]]\nname = \"wms_internal\"\npattern = '''wms_int_[a-z0-9]{12}'''\n", encoding="utf-8")
    env = {"AUTOHARNESS_EXTRA_REDACTION_RULES": str(rules)}
    out = redact("wms_int_abcdef123456 and ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", env=env)
    assert "wms_int_abcdef123456" not in out
    assert "ghp_" not in out  # packaged rules still apply


NONSECRETS = [
    "commit ca39a72e4353ebef11b7de13c1fc7fa5f4df421b",
    "run 3f2b8c1e-9a4d-4e7b-b1c2-7d8e9f0a1b2c finished",
    "SOURCE_PLAYER_ID nba:1629029",
    "model sha256 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "metric PROD_SURPLUS for CANONICAL_PLAYER_ID",
    "cache/canonical/player_season/league=ALL/data.parquet",
    "row count 254512",
]


@pytest.mark.parametrize("text", NONSECRETS)
def test_engineering_context_survives(text):
    assert redact(text, env=NO_ENV) == text


def test_full_private_key_block_redacted():
    key = """-----BEGIN PRIVATE KEY-----
ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
more-private-material
-----END PRIVATE KEY-----"""
    out = redact("before\n" + key + "\nafter", env=NO_ENV)
    assert "more-private-material" not in out
    assert "BEGIN PRIVATE KEY" not in out


@pytest.mark.parametrize("uri", [
    "postgresql://user:supersecret@db.example.com:5432/app",
    "redis://default:supersecret@cache.example.com:6379/0",
    "mongodb+srv://user:supersecret@cluster.example.net/db",
])
def test_credentialed_connection_uri_redacted(uri):
    out = redact(f"connection failed: {uri}", env=NO_ENV)
    assert uri not in out
    assert "supersecret" not in out


def test_standalone_jwt_redacted():
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signatureABCDEFG"
    assert token not in redact(f"token={token}", env=NO_ENV)
