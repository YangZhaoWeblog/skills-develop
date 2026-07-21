#!/usr/bin/env python3
# approved_contract_revision == contract_revision
# channel != ""
# evidence != ""
import json
import re
import sys
from pathlib import Path

content = Path(sys.argv[1]).read_text(encoding="utf-8")
contracts = []
for block in re.findall(r"```json[^\n]*\n(.*?)```", content, re.DOTALL):
    try:
        candidate = json.loads(block)
    except json.JSONDecodeError:
        raise SystemExit(1) from None
    if (
        isinstance(candidate, dict)
        and "contract_revision" in candidate
        and "human_start_gate" in candidate
    ):
        contracts.append(candidate)
if len(contracts) != 1:
    raise SystemExit(1)
contract = contracts[0]
gate = contract["human_start_gate"]
if not isinstance(gate, dict):
    raise SystemExit(1)
approved = (
    gate.get("status") == "approved"
    and gate.get("approved_contract_revision") == contract["contract_revision"]
    and bool(gate.get("channel"))
    and bool(gate.get("evidence"))
)
raise SystemExit(0 if approved else 1)
