#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

from envparse import env

hostname = env("TARGET_ADDRESS", cast=str, default='localhost')
my_port = env("MY_PORT", cast=int, default=9200)


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def set_header():
    headers = {
        'Host': hostname,
        'Content-Type': 'application/json'
    }

    return headers


class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        sent = False
        try:

            url = '{}{}'.format(hostname, self.path)
            req_header = self.parse_headers()

            print(req_header)
            print(url)
            resp = requests.get(url, headers=merge_two_dicts(
                req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            #            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_POST(self, body=True):
        sent = False
        try:
            url = '{}{}'.format(hostname, self.path)
            content_len = self.headers['content-length']
            if content_len == None:
                content_len = 0
            else:
                content_len = int(content_len)
            post_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            resp = requests.post(url, data=post_body, headers=merge_two_dicts(
                req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            #            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_PUT(self, body=True):
        sent = False
        try:

            url = '{}{}'.format(hostname, self.path)
            content_len = self.headers['content-length']
            if content_len == None:
                content_len = 0
            else:
                content_len = int(content_len)
            put_body = self.rfile.read(content_len)
            req_header = self.parse_headers()

            print(req_header)
            print(url)
            myheaders = merge_two_dicts(req_header, set_header())
            resp = requests.put(url, data=put_body,
                                headers=myheaders, verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            #            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def do_DELETE(self, body=True):
        sent = False
        try:

            url = '{}{}'.format(hostname, self.path)
            req_header = self.parse_headers()

            print(req_header)
            print(url)
            resp = requests.delete(url, headers=merge_two_dicts(
                req_header, set_header()), verify=False)
            sent = True

            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            if body:
                self.wfile.write(resp.content)
            return
        finally:
            #            self.finish()
            if not sent:
                self.send_error(404, 'error trying to proxy')

    def parse_headers(self):
        req_header = {}
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return req_header

    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print(key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()


def main():
    print('http server is starting on port {}...'.format(my_port))
    server_address = ('0.0.0.0', my_port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running as reverse proxy')
    httpd.serve_forever()


if __name__ == '__main__':
    main()
