#!/usr/bin/env python3
"""Exercise real KRes HTTP transport against a deterministic fake Gemini CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class Integration(unittest.TestCase):
    def test_real_kres_to_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp) / 'gemini'
            cli.write_text('''#!/usr/bin/env python3
import json, sys
assert '--output-format' in sys.argv and 'json' in sys.argv
assert '--approval-mode' in sys.argv and 'default' in sys.argv
assert '--model' in sys.argv and 'company-model' in sys.argv
prompt = sys.stdin.read()
assert 'KRES_READY' in prompt and '<user>' in prompt
print(json.dumps({'response': 'KRES_READY'}))
''')
            cli.chmod(0o700)
            config = Path(tmp) / 'llm.json'
            config.write_text(json.dumps({'provider': 'gemini-cli',
                'model': 'company-model', 'gemini_cli': str(cli), 'timeout_seconds': 5}))
            run = subprocess.run([sys.executable, str(ROOT / 'scripts/run.py'),
                '--config', str(config), '--test'], capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('response: KRES_READY', run.stdout)
            self.assertIn('model (actual): company-model', run.stdout)

    def test_bridge_rejects_unauthenticated_requests(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        from gemini_bridge import server
        import threading
        import urllib.request
        import urllib.error
        bridge = server({}, 'expected-token')
        threading.Thread(target=bridge.serve_forever, daemon=True).start()
        try:
            request = urllib.request.Request(
                f'http://127.0.0.1:{bridge.server_port}/v1/chat/completions', data=b'{}')
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request)
            self.assertEqual(error.exception.code, 401)
        finally:
            bridge.shutdown()
            bridge.server_close()


if __name__ == '__main__':
    unittest.main()
