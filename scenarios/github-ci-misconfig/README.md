
# GitHub/CI Misconfiguration — Lab notes

Goal: Demonstrate how untrusted inputs (commit message or PR body) passed to CI scripts can leak secret-like tokens into build logs or cause CI to perform actions.

How to run:
- `python runners/run_scenario.py --scenario github-ci-misconfig --mode vulnerable`
- `python runners/run_scenario.py --scenario github-ci-misconfig --mode safe`

Hints:
- H1: Look at how the runner handles OUTPUT= or SECRET= tokens in input.txt.
- H2: The vulnerable mode echoes commit/PR content directly (simulates log exposure).
- H3: The safe mode sanitizes and refuses to echo tokens that look like secrets.

Scoring:
- The `flag` in meta.yaml is present for deterministic scoring. Use `runners/score_engine.py` to verify.
