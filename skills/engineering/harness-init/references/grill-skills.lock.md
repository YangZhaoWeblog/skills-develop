# Grill Skills Snapshot

Canonical source: `https://github.com/mattpocock/skills`

Pinned commit: `e9fcdf95b402d360f90f1db8d776d5dd450f9234`

License: MIT, Copyright (c) 2026 Matt Pocock

The installable directories under `skills/` are the canonical local snapshot. The copies under `assets/baseline/.agents/skills/` must remain byte-for-byte identical, including `LICENSE` and `NOTICE`.

| SHA-256 | Upstream path |
|---|---|
| `6189dfceb7304a6e5558f75d87e68fa3bc7fcf7ba120e44f21f8a61fe01eba54` | `skills/productivity/grill-me/SKILL.md` |
| `c061e39c3e0f9d865fb1b97556d485704af2a8a58f4b8221a8917a5c2074a32b` | `skills/productivity/grill-me/agents/openai.yaml` |
| `44331dda57f461db4fec3f2efb6ddabe7aaaa0a57ae0f88a883bc61aed8a0587` | `skills/productivity/grilling/SKILL.md` |
| `cf29b9a8dbf35a58a908a6ca4f64dcd86c2b2130291eee0a78b9f706b138825b` | `skills/productivity/grilling/agents/openai.yaml` |
| `610d091047bcfb9db0f75c057d15538481a721111579fc5ec7f83ad9131a2165` | `skills/engineering/grill-with-docs/SKILL.md` |
| `94cd0ab161fb468a836349f5ed482ba58ce8e709a05c57ce533d739dbd35cca9` | `skills/engineering/grill-with-docs/agents/openai.yaml` |
| `152e2c97239affb12a60c5f4a7e74ab546a49ae169688c81f4e2ccc42dafa579` | `skills/engineering/domain-modeling/SKILL.md` |
| `f6bf2aa996c6e6f53fdd0708e18a0d16a56aed8322cca59fedbe3c0d2c75f06b` | `skills/engineering/domain-modeling/agents/openai.yaml` |
| `b8cc318f2a4285b530e908b6bc43901c3c5cd11100362636bbc4216639bef597` | `skills/engineering/domain-modeling/CONTEXT-FORMAT.md` |
| `f1f36cd3f8d3b6474ddd5855da4e233bfc4ae1a1c5024909ccf11871819a41b2` | `skills/engineering/domain-modeling/ADR-FORMAT.md` |

To update the snapshot: choose a new immutable commit, refresh all listed files plus the upstream MIT license, review the upstream diff, update the hashes and every `NOTICE`, synchronize the baseline copies, then run skill validation and the harness-init acceptance suite. `harness-init` must never fetch upstream `main` while generating a target repository.
