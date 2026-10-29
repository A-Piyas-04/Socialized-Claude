# Security policy

## What this project is, in security terms

Socialized-Claude ships **text, not code**. Both distributable archives contain Markdown files
and one JSON manifest. Specifically, the plugin declares:

- one skill, and
- no agents, no hooks, no MCP servers, no LSP servers, no commands, no `bin/` executables.

So there is nothing in the installable artifacts that runs on your machine, opens a network
connection, reads your files, or asks for a credential. You can confirm this yourself:

```bash
python -m zipfile -l dist/socialized.zip
python -m zipfile -l dist/socialized-claude-plugin.zip
```

The Python under `scripts/` and `tests/` is build and validation tooling for contributors. It
is not shipped to users, uses only the standard library plus `pyyaml` and `pytest`, and makes
no network calls.

The realistic risk from a skill is therefore not code execution. It is **instruction content**:
a skill's text becomes instructions Claude follows. A malicious edit to `SKILL.md` could try to
change how Claude behaves for anyone who installed it. That is the threat this project guards
against, with deterministic packaging, committed per-file hashes, and a version lock.

## Verifying what you installed

Every release records SHA-256 digests per archive and per file inside it:

- `dist/socialized.manifest.json`
- `dist/socialized-claude-plugin.manifest.json`
- `scripts/version_lock.json`

Builds are deterministic and platform-independent, so you can rebuild from source and compare
bytes rather than trusting a download:

```bash
python scripts/package_skill.py --check
python scripts/build_plugin.py --check
```

Both print that the committed archive matches the source, or name exactly what differs.

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report it privately through GitHub's private vulnerability reporting on this repository:
**Security → Report a vulnerability**, at
<https://github.com/A-Piyas-04/Socialized-Claude/security/advisories/new>.

> **Maintainer note (not yet done):** private vulnerability reporting must be switched on in
> **Settings → Code security** before that link works. Until it is, the link returns a 404.
> This is item 7 in [`docs/RELEASE_READINESS.md`](docs/RELEASE_READINESS.md).

No other reporting channel is published, and no email address is listed here, because listing
one that nobody monitors is worse than listing none.

### What to expect

This is a single-maintainer project with no funding, no bug bounty, no security team and no
monitoring. **No response time is promised.** Reports are read when the maintainer is working
on the project. If that is not acceptable for your disclosure timeline, say so in the report.

### In scope

- Content in `skill/socialized/**` or the built archives that would make Claude behave against
  the user's interest — prompt injection, instruction smuggling, data exfiltration phrasing.
- A packaging flaw: path traversal in an archive, an unexpected file in a distributable, a
  `--check` gate that would not catch a tampered package.
- Anything in `scripts/` that executes untrusted input or leaks a credential.
- A credential, token or personal path committed to the repository or appearing in a built
  archive.

### Out of scope

- Claude's own behaviour, model output, refusals or accuracy. Report those to Anthropic.
- The research archive under `research-results-2026-10-26/`, which is read-only input data.
- The quality of explanations. That is a correctness concern, not a security one — use
  [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

## Secrets

No credential, API key or token belongs in this repository, in a built archive, or in committed
output. The project needs no API key to run or to validate. If you find one, treat it as a
vulnerability and report it privately as above.
