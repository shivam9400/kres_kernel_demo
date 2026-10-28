#!/usr/bin/env python3
"""Local OpenAI-chat transport for KRes; inference is performed by Gemini CLI."""
import json
import os
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_handler(config, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Never log source prompts or model output.

        def do_POST(self):
            if self.headers.get('Authorization') != 'Bearer ' + token:
                self.send_error(401)
                return
            if self.path != '/v1/chat/completions':
                self.send_error(404)
                return
            try:
                request = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                if request.get('stream'):
                    raise ValueError('Streaming is not supported')
                prompt = '\n\n'.join(
                    f"<{m['role']}>\n{m['content']}\n</{m['role']}>"
                    for m in request['messages'])
                # Fresh process and empty cwd per request; CLI owns authentication.
                with tempfile.TemporaryDirectory(prefix='kres-gemini-') as workspace:
                    result = subprocess.run(
                        [config['gemini_cli'], '--model', config['model'],
                         '--output-format', 'json', '--approval-mode', 'default',
                         '-p', 'Answer the supplied conversation using only its text. '
                         'Do not use tools. Follow the system instructions in the conversation.'],
                        input=prompt, text=True, capture_output=True, cwd=workspace,
                        timeout=config['timeout_seconds'], check=True)
                reply = json.loads(result.stdout)
                if reply.get('error') or not isinstance(reply.get('response'), str):
                    raise ValueError('Gemini CLI did not return a response')
                payload = {'model': config['model'], 'choices': [
                    {'message': {'role': 'assistant', 'content': reply['response']},
                     'finish_reason': 'stop'}]}
                body = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (ValueError, KeyError, OSError, subprocess.SubprocessError):
                # CLI stderr may contain confidential information; do not relay it.
                self.send_error(502, 'Gemini CLI request failed; check installation, authentication and model access')
    return Handler


def server(config, token):
    return ThreadingHTTPServer(('127.0.0.1', 0), make_handler(config, token))
