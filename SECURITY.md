# Security Policy

AgentForge is educational sample code. It is **not** hardened for production
use, and examples are pinned to older library versions on purpose so they keep
demonstrating the API they were written against. Please treat everything here as
a reference implementation, not a dependency.

## Reporting a vulnerability

Report privately — **do not open a public issue**, and never paste a credential
into an issue, pull request, or discussion.

1. Open a private advisory via
   [GitHub Security Advisories](https://github.com/Olwtelet/AgentForge/security/advisories/new).
2. If that is unavailable, contact the repository owner
   ([@Olwtelet](https://github.com/Olwtelet)) directly.

Please include:

- What the issue is and where (file path, line number).
- How to reproduce it.
- What an attacker could achieve.
- Any suggested fix.

**Never include real credentials in a report.** If a report requires showing a
leaked secret, say *where* it is and *what kind* of secret it is — not its value.

## If you find an exposed credential

An exposed key must be treated as compromised the moment it becomes public,
whether or not it is later deleted — git history and mirrors keep it reachable.

1. **Revoke and rotate it at the provider immediately.** This is the only step
   that actually stops the exposure.
2. Report it privately using the process above, describing the location only.
3. Do not force-push or rewrite history to "hide" it — that does not un-leak the
   key and breaks every existing clone.

## Handling credentials in this repository

- All configuration comes from a local `.env` file, which is git-ignored.
- Each module ships a `.env.example` containing **placeholders only**.
- `.gitignore` excludes `.env` and `.env.*` while explicitly allowing
  `.env.example`.
- CI runs unit tests **without any credentials** — they mock every network call.
  Integration tests run only on manual dispatch, and skip themselves when the
  required secrets are absent.
- Every pull request is scanned for committed secrets by
  [gitleaks](https://github.com/gitleaks/gitleaks-action) in
  [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- A unit test (`tests/unit/test_repo_hygiene.py`) fails the build if a
  credential-shaped literal or a `verify=False` TLS bypass reappears anywhere in
  the repository.

## Known considerations when running the examples

These are inherent to what the examples demonstrate, not bugs:

- **Agent tool execution.** Several frameworks can execute code or shell
  commands as a "tool". Run untrusted prompts only in a sandbox.
- **Outbound API calls.** Examples send your prompts to third-party LLM and
  search providers. Do not feed them confidential data.
- **Local vector stores.** RAG examples write embeddings to disk. Those files
  contain your source documents' content; they are git-ignored, but treat them
  with the same care as the originals.
- **Token spend.** Benchmark loops call paid APIs repeatedly. Check
  `--iterations` before running.

## Supported versions

Fixes are applied to the `main` branch only. There are no released versions or
backports.
