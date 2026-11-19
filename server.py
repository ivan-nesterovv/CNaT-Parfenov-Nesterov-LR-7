"""ЛР7: HTTP-сервер и REST API, Python 3.8+, без внешних пакетов."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

DATA = {1: {'id': 1, 'title': 'Networks', 'done': False}}
NEXT_ID = 2
SAVE_FILE = Path(__file__).with_name('submitted.json')


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def reply(self, status, value=None, html=False):
        body = b'' if value is None else (
            value.encode('utf-8') if html else
            json.dumps(value, ensure_ascii=False).encode('utf-8'))
        self.send_response(status)
        self.send_header('Content-Type',
                         ('text/html' if html else 'application/json') + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def resource(self):
        path = urlsplit(self.path).path
        parts = path.strip('/').split('/')
        ident = int(parts[1]) if (len(parts) == 2 and parts[0] == 'data'
                                  and parts[1].isdigit()) else None
        return path, ident

    def read_json(self):
        if self.headers.get_content_type() != 'application/json':
            raise ValueError('Content-Type must be application/json')
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 < length <= 65536:
            raise ValueError('JSON body must contain 1..65536 bytes')
        result = json.loads(self.rfile.read(length).decode('utf-8'))
        if not isinstance(result, dict):
            raise ValueError('JSON object required')
        return result

    def do_GET(self):
        path, ident = self.resource()
        if path == '/':
            self.reply(200, '<!doctype html><html><body><h1>Hello from Python server</h1></body></html>', True)
        elif path == '/status':
            self.reply(200, {'status': 'ok', 'message': 'server is alive'})
        elif path == '/data':
            self.reply(200, list(DATA.values()))
        elif ident in DATA:
            self.reply(200, DATA[ident])
        else:
            self.reply(404, {'error': 'Resource not found'})

    def do_POST(self):
        global NEXT_ID
        path, _ = self.resource()
        try:
            body = self.read_json()
        except (ValueError, UnicodeDecodeError) as exc:
            self.close_connection = True
            return self.reply(400, {'error': str(exc)})
        if path == '/submit':
            SAVE_FILE.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding='utf-8')
            self.reply(201, {'saved': True, 'file': SAVE_FILE.name})
        elif path == '/echo':
            self.reply(200, body)
        elif path == '/data':
            body['id'] = NEXT_ID
            DATA[NEXT_ID] = body
            NEXT_ID += 1
            self.reply(201, body)
        else:
            self.reply(404, {'error': 'Resource not found'})

    def do_PUT(self):
        _, ident = self.resource()
        try:
            body = self.read_json()
        except (ValueError, UnicodeDecodeError) as exc:
            self.close_connection = True
            return self.reply(400, {'error': str(exc)})
        if ident not in DATA:
            return self.reply(404, {'error': 'Resource not found'})
        body['id'] = ident
        DATA[ident] = body
        self.reply(200, body)

    def do_DELETE(self):
        _, ident = self.resource()
        if ident not in DATA:
            return self.reply(404, {'error': 'Resource not found'})
        del DATA[ident]
        self.reply(204)


if __name__ == '__main__':
    print('HTTP server: 0.0.0.0:8000; data file: ' + str(SAVE_FILE), flush=True)
    HTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
