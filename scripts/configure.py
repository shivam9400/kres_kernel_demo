#!/usr/bin/env python3
"""Keep generated config local; reuse CLI authentication without copying secrets."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / '.runtime/kres/models/codex-codes.json'
config = json.loads(path.read_text())
# Upstream's isolated home lacks this environment's injected CLI authentication.
config.pop('codex_home', None)
# A dotted override creates an invalid transport-less MCP entry when this
# environment has no meta_core server. Disable inherited MCP entries as a table.
config['codex_config'].pop('mcp_servers.meta_core.enabled', None)
config['codex_config']['mcp_servers'] = {}
path.write_text(json.dumps(config, indent=2) + '\n')
