#!/usr/bin/env python3
"""Select a configured provider and keep any local bridge scoped to this run."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import threading
from gemini_bridge import server

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--config', default=str(root / 'config/llm.json'))
parser.add_argument('--test', action='store_true')
parser.add_argument('target', nargs='?', default='lib/list_sort.c')
parser.add_argument('turns', nargs='?', default='1')
args = parser.parse_args()
config = json.loads(Path(args.config).read_text())
provider = config['provider']
bridge = None
with tempfile.TemporaryDirectory(prefix='kres-provider-') as tmp:
    if provider == 'codex':
        model = config['model']
        data = json.loads((root / '.runtime/kres/models/codex-codes.json').read_text())
        data['models'] = {model: next(iter(data['models'].values()))}
    elif provider == 'gemini-cli':
        token = secrets.token_urlsafe(32)
        bridge = server(config, token)
        threading.Thread(target=bridge.serve_forever, daemon=True).start()
        model = 'gemini-cli'  # Chat-completions alias; real model selected by CLI config.
        data = {'provider': 'openai', 'proxy': '', 'base_url': f'http://127.0.0.1:{bridge.server_port}/v1',
                'api_key': token, 'models': {model: {'max_tokens': 64000,
                'max_input_tokens': 900000, 'thinking': {'type': 'disabled'}}}}
    else:
        raise SystemExit('provider must be codex or gemini-cli')
    path = Path(tmp) / 'provider.json'
    path.write_text(json.dumps(data))
    os.chmod(path, 0o600)
    cmd = [str(root / 'scripts/kres')]
    if args.test:
        cmd += ['test', str(path), '--model', model, '--prompt', 'Reply with KRES_READY only.']
    else:
        import datetime
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
        cmd += ['--no-tui', '--skills', str(root / '.runtime/kres/skills'),
                '--max-parallel', str(config.get('max_parallel', 2)),
                '--results', str(root / f'results/review-{stamp}-{os.getpid()}'),
                '--turns', args.turns, '--prompt', 'review: ' + args.target]
        for role in ['fast', 'slow', 'main', 'todo']:
            cmd += [f'--{role}-agent', str(path), f'--{role}-model', model]
    env = os.environ.copy()
    # Only loopback bypasses the outbound proxy; external CLI traffic retains it.
    env['NO_PROXY'] = env.get('NO_PROXY', '') + ',127.0.0.1,localhost'
    env['no_proxy'] = env['NO_PROXY']
    try:
        result = subprocess.run(cmd, cwd=root / 'linux', env=env)
    finally:
        if bridge:
            bridge.shutdown()
            bridge.server_close()
    raise SystemExit(result.returncode)
