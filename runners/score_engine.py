#!/usr/bin/env python3
import re
def check_flag(output: str, expected_flag: str):
    if expected_flag is None:
        return 0, "No expected flag configured for this scenario."
    if expected_flag in output:
        return 1, f"Flag matched: {expected_flag}"
    m = re.search(r'FLAG\{.*?\}', output)
    if m and m.group(0) == expected_flag:
        return 1, f"Flag matched by regex: {m.group(0)}"
    return 0, "Flag not found in output."
