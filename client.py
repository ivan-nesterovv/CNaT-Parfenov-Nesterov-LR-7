"""ЛР7: проверка всех маршрутов и CRUD через http.client."""
import http.client
import json
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else '192.168.1.1'
checks = 0


def request(method, path, expected, body=None, raw=None):
    global checks
    connection = http.client.HTTPConnection(HOST, 8000, timeout=10)
    payload = raw if raw is not None else (
        json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None)
    headers = {'Content-Type': 'application/json'} if payload is not None else {}
    connection.request(method, path, body=payload, headers=headers)
    response = connection.getresponse()
    text = response.read().decode('utf-8')
    print('{} {} -> {} {}'.format(method, path, response.status, response.reason))
    print('Content-Type: {}; Content-Length: {}'.format(
        response.getheader('Content-Type'), response.getheader('Content-Length')))
    print(text or '<empty body>')
    assert response.status == expected, (path, response.status, expected)
    connection.close()
    checks += 1
    return json.loads(text) if text and not text.startswith('<') else text


if __name__ == '__main__':
    print('CLIENT -> {}:8000'.format(HOST))
    assert 'Hello from Python server' in request('GET', '/', 200)
    assert request('GET', '/status', 200)['status'] == 'ok'
    assert isinstance(request('GET', '/data', 200), list)
    request('GET', '/data/1', 200)
    request('GET', '/missing', 404)
    sample = {'student': 'Lab7', 'message': 'Hello HTTP', 'value': 7}
    assert request('POST', '/submit', 201, sample)['saved']
    assert request('POST', '/echo', 200, sample) == sample
    item = request('POST', '/data', 201, {'title': 'REST task', 'done': False})
    path = '/data/{}'.format(item['id'])
    assert request('GET', path, 200)['title'] == 'REST task'
    request('PUT', path, 200, {'title': 'REST updated', 'done': True})
    assert request('GET', path, 200)['done'] is True
    request('DELETE', path, 204)
    request('GET', path, 404)
    request('POST', '/echo', 400, raw=b'{broken')
    print('PASS: {} HTTP checks; CRUD, echo and invalid JSON verified'.format(checks))
