# Prompt Injection Lab — Advanced CTF (Local-first)

**Purpose**  
A compact, production-grade, *local-first* CTF-style lab to teach and test advanced prompt-injection techniques against LLM integrations and surrounding infra (CI, Git, tooling). Designed for experienced pentesters and blue teams: realistic attack surfaces, deterministic flags, scoring, and a safe simulator so nothing touches production models or real secrets.

---

## What this lab is (short)
- Hands-on scenarios that reproduce common and advanced prompt-injection classes (instruction override, context poisoning, indirect injection, tool abuse, chain-of-instructions, CI/PR injection, oracle-style exfiltration).  
- Deterministic scoring: each vulnerable scenario exposes a `FLAG{...}` value the harness detects so teams can compete or validate fixes.  
- Safe simulator: all runs are local by default and do **not** call cloud LLMs. You can optionally wire a local model later, but do so behind strict isolation.  
- CI regression: a GitHub Actions workflow verifies the safe baseline to prevent accidental regressions.

---

## Quick goals
- Train red-team techniques to craft prompt-injection and infra-based exfiltration vectors.  
- Train blue-team mitigations: context provenance, sanitization, output filtering, tool isolation.  
- Provide deterministic scoring and repeatable regression tests.

---

## Included scenarios
Each scenario lives in `scenarios/<name>/` and includes `meta.yaml`, `input.txt`, and `README.md`.

- `basic-injection` — instruction override (`ignore previous`, `OUTPUT="..."`).  
- `context-poisoning` — poisoned KB/context that later influences answers.  
- `indirect-injection` — hidden instruction in HTML/comments or scraped content.  
- `tool-abuse` — prompts that attempt to coerce tool commands (simulated).  
- `chain-of-instructions` — chaining outputs into new instructions.  
- `oracle-exfiltration` — coaxing guesses/inferences of secret-like tokens.  
- `github-ci-misconfig` — commit/PR-body → CI log leakage simulation.

---

## Vulnerable vs Safe logic
The harness supports two modes:

- **vulnerable** — intentionally permissive: simulates how an insecure integration might echo or exfiltrate attacker tokens (returns `FLAG{...}` when a scenario is triggered).  
- **safe** — hardened: sanitizes or rejects instruction-like tokens (`OUTPUT=`, `SECRET=`, `echo SECRET`, `FLAG{...}`, `ignore previous instructions`) and does not reveal flags.

**Patterns recognized by the simulator (examples)**  
- `OUTPUT="FLAG{...}"`  
- `SECRET="FLAG{...}"` or `echo SECRET="FLAG{...}"`  
- Any `FLAG{...}` appearing in attacker input (fallback)  
- `ignore previous instructions`, `CHAIN_STEP`, `EXEC_TOOL`, `ORACLE?`

---

## Scoring
- Each scenario’s `meta.yaml` contains `flag`.  
- `runners/score_engine.py` checks the simulated output for the expected flag.  
- Score = `1` if flag found (vulnerable reproduction), `0` otherwise.

---

## Quick start (local)
> Run all commands from repository root.

```bash
# create & activate venv (use python3.11 if available for best compatibility)
python3 -m venv .venv && source .venv/bin/activate

# upgrade tooling and install deps
python -m pip install --upgrade pip setuptools wheel
pip install --only-binary=:all: -r runners/requirements.txt

# enable CI-simulation placeholders used by some scenarios
export CI_SIMULATED=true

# run a vulnerable scenario (shows exfiltration)
python runners/run_scenario.py --scenario github-ci-misconfig --mode vulnerable

# run the same scenario in safe mode (validated mitigations)
python runners/run_scenario.py --scenario github-ci-misconfig --mode safe

# run all scenarios in safe mode (sanity check)
for s in $(ls scenarios); do
  python runners/run_scenario.py --scenario "$s" --mode safe
done
