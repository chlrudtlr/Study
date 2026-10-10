#!/usr/bin/env python3
"""Zero-dependency local demo server. Python 3.10+."""
import argparse
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from adapters import DemoAdapter
from store import Store, Conflict
from worker import Worker

ROOT = Path(__file__).resolve().parent


def make_handler(store, token=''):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'SmartRackDemo/1.0'

        def log_message(self, fmt, *args):
            # Avoid logging request URLs, tokens or payloads.
            pass

        def respond(self, status, body, content_type='application/json; charset=utf-8'):
            if isinstance(body, (dict, list)):
                body = json.dumps(body, ensure_ascii=False).encode('utf-8')
            elif isinstance(body, str):
                body = body.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'same-origin')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            # Origin enforcement + Host validation protect the loopback demo
            # from cross-site mutations and DNS rebinding. CLI requests may omit Origin.
            host = self.headers.get('Host', '')
            parsed_host = urlsplit('http://' + host).hostname
            if not token and parsed_host not in ('localhost', '127.0.0.1', '::1'):
                self.respond(403, {'error': '로컬 Host만 허용됩니다.'})
                return False
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + host:
                self.respond(403, {'error': '다른 Origin의 요청은 허용하지 않습니다.'})
                return False
            if token and not hmac.compare_digest(self.headers.get('Authorization', '').encode('utf-8'), ('Bearer ' + token).encode('utf-8')):
                self.respond(401, {'error': 'API 토큰을 입력하세요.'})
                return False
            return True

        def do_GET(self):
            path = unquote(urlsplit(self.path).path)
            if path.startswith('/api/'):
                if not self.authorized():
                    return
                try:
                    if path == '/api/state':
                        self.respond(200, store.state())
                    elif path.startswith('/api/ports/'):
                        self.respond(200, store.detail(path.removeprefix('/api/ports/')))
                    else:
                        self.respond(404, {'error': 'API 경로를 찾을 수 없습니다.'})
                except KeyError as exc:
                    self.respond(404, {'error': str(exc)})
                return
            files = {
                '/': ('index.html', 'text/html; charset=utf-8'),
                '/index.html': ('index.html', 'text/html; charset=utf-8'),
                '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
                '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
            }
            if path not in files:
                self.respond(404, {'error': '페이지를 찾을 수 없습니다.'})
                return
            name, mime = files[path]
            self.respond(200, (ROOT / 'static' / name).read_bytes(), mime)

        def do_POST(self):
            if not self.authorized():
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16384:
                    raise ValueError('JSON 본문 크기는 1~16384 bytes여야 합니다.')
                if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    raise ValueError('Content-Type: application/json이 필요합니다.')
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError('JSON object가 필요합니다.')
                path = unquote(urlsplit(self.path).path)
                if path == '/api/settings':
                    result = store.update_config(payload)
                elif path == '/api/retry':
                    result = store.enqueue(payload['port_id'])
                elif path == '/api/review':
                    result = store.review(payload['port_id'], payload['classification'], payload['note'], payload.get('auto_allowed', False))
                elif path == '/api/demo/failure':
                    result = store.simulate_failure(payload['port_id'], payload['scenario'])
                else:
                    self.respond(404, {'error': 'API 경로를 찾을 수 없습니다.'})
                    return
                self.respond(200, result)
            except Conflict as exc:
                self.respond(409, {'error': str(exc)})
            except (ValueError, TypeError, KeyError) as exc:
                self.respond(400, {'error': str(exc)})
            except Exception:
                self.respond(500, {'error': '서버 처리 오류 · 터미널 또는 상태를 확인하세요.'})

    return Handler


def main():
    parser = argparse.ArgumentParser(description='Smart Rack Dashboard demo')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--db', type=Path, default=ROOT / 'data' / 'dashboard.sqlite3')
    args = parser.parse_args()
    token = os.getenv('AURA_API_TOKEN', '')
    if args.host not in ('127.0.0.1', 'localhost') and len(token) < 24:
        parser.error('외부 바인딩에는 24자 이상의 AURA_API_TOKEN이 필요합니다.')
    args.db.parent.mkdir(parents=True, exist_ok=True)
    config = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    store = Store(args.db, config)
    worker = Worker(store, DemoAdapter())
    server = ThreadingHTTPServer((args.host, args.port), make_handler(store, token))
    server.daemon_threads = True
    worker.start()
    print(f'\nSmart Rack Dashboard · DEMO\nhttp://{args.host}:{args.port}\n실제 장비 동작 없음 · 종료: Ctrl+C\n', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        worker.stop()
        worker.join(timeout=5)
        if not worker.is_alive():
            store.close()


if __name__ == '__main__':
    main()
