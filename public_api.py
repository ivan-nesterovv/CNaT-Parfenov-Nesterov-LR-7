"""Публичный учебный API. HTTP выбран для просмотра тела в сниффере."""
import http.client
import json

HOST = 'jsonplaceholder.typicode.com'


def request(method, path, body=None):
    connection = http.client.HTTPConnection(HOST, timeout=30)
    payload = json.dumps(body).encode('utf-8') if body is not None else None
    headers = {'Content-Type': 'application/json; charset=UTF-8'} if payload else {}
    connection.request(method, path, body=payload, headers=headers)
    response = connection.getresponse()
    text = response.read().decode('utf-8')
    print('{} http://{}{} -> {}'.format(method, HOST, path, response.status))
    print('text:', text)
    status = response.status
    connection.close()
    return status, json.loads(text)


if __name__ == '__main__':
    status, data = request('GET', '/posts/1')
    assert status == 200
    print('JSON keys:', ', '.join(data.keys()))
    status, data = request('GET', '/posts/999999')
    assert status == 404
    if status == 404:
        print('Пост не найден')
    status, data = request('POST', '/posts', {'title': 'Lab7', 'body': 'HTTP client test', 'userId': 1})
    assert status == 201 and data['id'] == 101
    print('PASS: public GET, 404 handling, POST')
