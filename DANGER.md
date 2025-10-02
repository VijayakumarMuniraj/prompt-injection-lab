# DANGER — Safety & Execution Rules
1) NEVER run scenarios against production models or production data.
2) DO NOT include real secrets, API keys, credentials, or PII in scenario data.
3) Default runner uses a deterministic local simulator. If you enable any LLM, keep it offline with no tool access.
4) Use isolated containers/VMs for experiments.
5) If any real vulnerability is discovered, follow responsible disclosure per policy.
