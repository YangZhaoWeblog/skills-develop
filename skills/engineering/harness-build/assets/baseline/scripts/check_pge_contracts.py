#!/usr/bin/env python3
# approved_contract_revision == contract_revision
# channel != ""
# evidence != ""
import json
import re
import sys
from pathlib import Path

content = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
if match is None:
    raise SystemExit(1)
contract = json.loads(match.group(1))
gate = contract["human_start_gate"]
approved = (
    gate["status"] == "approved"
    and gate["approved_contract_revision"] == contract["contract_revision"]
    and bool(gate["channel"])
    and bool(gate["evidence"])
)
raise SystemExit(0 if approved else 1)
