
# Git/GitHub & CI Risks — Prompt Injection Lab

Key risks:
- Commit message / PR-body injection: CI that incorporates PR contents into scripts, commands, or environment variables can cause secrets to be echoed or commands to run.
- Workflow parsing: workflows that parse commit messages to create commands (e.g. `deploy: env=prod`) are vulnerable to injection unless strictly validated.
- CI artifact leakage: logs may contain secrets if sensitive-looking strings are printed.
- Token misuse: avoid storing service tokens in workflows unless masked & scoped.

Lab best-practices:
- Default to local simulator; never run vulnerable workflows on GitHub-hosted runners with real secrets.
- Use `DANGER.md` prominently.
- Add a CI gating policy: `CI_SIMULATED=true` must be set to enable any "vulnerable" tests.

Remediation patterns:
- Sanitize PR/commit inputs before usage.
- Use allow-lists for commands parsed from text.
- Mask secrets and avoid printing them in logs.
- Use ephemeral, scoped tokens for any automation.
