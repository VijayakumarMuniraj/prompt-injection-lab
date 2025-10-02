#!/usr/bin/env python3
import click, re, textwrap, yaml, os
from pathlib import Path
from score_engine import check_flag

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ROOT / "scenarios"

def load_meta(scenario):
    base = SCENARIOS / scenario
    if not base.exists():
        raise FileNotFoundError(f"Scenario '{scenario}' not found")
    meta = yaml.safe_load((base / "meta.yaml").read_text())
    user_input = (base / "input.txt").read_text()
    return meta, user_input

def _extract_quoted(token_name, text):
    m = re.search(rf'{re.escape(token_name)}\s*[:=]\s*["\'](.*?)["\']', text, re.IGNORECASE)
    return m.group(1) if m else None

def _find_flag_anywhere(text):
    m = re.search(r'FLAG\{.*?\}', text)
    return m.group(0) if m else None

def vulnerable_sim(system_prompt, user_input):
    """
    Vulnerable simulator: intentionally permissive detection for CTFs.
    It checks several common patterns and will return any FLAG{...}
    found in the attacker input to simulate an exfil.
    """
    # Highest priority: explicit OUTPUT="..."
    v = _extract_quoted("OUTPUT", user_input)
    if v:
        return f"[VULNERABLE] {v}"

    # SECRET="..."
    s = _extract_quoted("SECRET", user_input)
    if s:
        return f"[VULNERABLE] {s}"

    # common shell echo patterns (echo SECRET=... or echo "FLAG{...}")
    m_echo_flag = re.search(r'echo\s+["\']?(FLAG\{.*?\})["\']?', user_input, re.IGNORECASE)
    if m_echo_flag:
        return f"[VULNERABLE] {m_echo_flag.group(1)}"

    # As a robust fallback for CTFs: if any FLAG{...} appears anywhere, return it
    f = _find_flag_anywhere(user_input)
    if f:
        return f"[VULNERABLE] {f}"

    # classic "ignore previous instructions" patterns
    if re.search(r'ignore (previous|earlier) instructions', user_input, re.IGNORECASE):
        return "[VULNERABLE] Ignored system prompt and executed nested instruction"

    # simulated other behaviours
    if "CHAIN_STEP" in user_input:
        return "[VULNERABLE] Chain executed: FLAG{SIM_CHAIN_EXFIL}"
    if "EXEC_TOOL" in user_input:
        return "[VULNERABLE] Tool executed: FLAG{SIM_TOOL_ABUSE}"
    if "ORACLE?" in user_input:
        return "[VULNERABLE] Revealed pattern: FLAG{SIM_ORACLE}"

    return "[VULNERABLE] Summarized content (simulated)"

def safe_sim(system_prompt, user_input):
    """
    Safe simulator: rejects instruction-like payloads including OUTPUT/SECRET/echo/FLAG exposures.
    """
    if re.search(r'ignore (previous|earlier) instructions', user_input, re.IGNORECASE):
        return "[SAFE] Rejected instruction-like content."
    if _extract_quoted("OUTPUT", user_input):
        return "[SAFE] Rejected explicit OUTPUT request."
    if _extract_quoted("SECRET", user_input):
        return "[SAFE] Rejected explicit SECRET exposure attempt."
    if re.search(r'echo\s+SECRET', user_input, re.IGNORECASE) or re.search(r'echo\s+["\']?FLAG\{', user_input, re.IGNORECASE):
        return "[SAFE] Rejected echo/print of secret-like token."
    # refuse to use flagged content even if it appears
    if _find_flag_anywhere(user_input):
        return "[SAFE] Refused to reveal or echo flags in responses."
    if "CHAIN_STEP" in user_input:
        return "[SAFE] Refused to follow chained outputs as instructions."
    if "EXEC_TOOL" in user_input:
        return "[SAFE] Refused to invoke tools from user-derived prompts."
    if "ORACLE?" in user_input:
        return "[SAFE] Declined to infer/guess secrets from patterns."
    return "[SAFE] Summarized content (sanitised)"

@click.command()
@click.option("--scenario", required=True, help="Scenario name under /scenarios")
@click.option("--mode", default="vulnerable", type=click.Choice(["vulnerable","safe"]), help="Simulator mode")
def main(scenario, mode):
    ci_simulated = os.environ.get('CI_SIMULATED', 'false').lower() in ['1','true','yes']
    meta, user_input = load_meta(scenario)

    # If running CI simulation, substitute PR placeholders safely (no external calls).
    if ci_simulated and "PR_BODY_PLACEHOLDER" in (meta.get("system_prompt","") + user_input):
        user_input = user_input.replace("PR_BODY_PLACEHOLDER", user_input)

    print("=== Scenario:", meta.get("title"))
    print("\nSystem Prompt:\n" + textwrap.indent(meta.get("system_prompt","(none)"), "  "))
    print("\nAttacker/User Input:\n" + textwrap.indent(user_input, "  "))
    print("\n--- Execution ---")
    out = vulnerable_sim(meta.get("system_prompt",""), user_input) if mode=="vulnerable" else safe_sim(meta.get("system_prompt",""), user_input)
    print(out)
    print("\n--- Scoring ---")
    flag_expected = meta.get("flag")
    score, details = check_flag(out, flag_expected)
    print("Score:", score)
    print("Details:", details)

if __name__ == "__main__":
    main()
