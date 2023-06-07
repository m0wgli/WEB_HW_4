from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import socket
import threading
import json
import os
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            if self.command == 'POST':
                self.handle_message_post()
            else:
                self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)


    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'): {key: value for key,
                                                                    value in [el.split('=') for el in data_parse.split('&')]}}
        print(data_dict)

        threading.Thread(target=self.run_client, args=(data_dict,)).start()

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, file_name, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(file_name, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header('Content-type', mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        file_path = f'.{self.path}'
        if pathlib.Path(file_path).exists():
            with open(file_path, 'rb') as fd:
                self.wfile.write(fd.read())


    def run_client(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            server = 'localhost', 5000
            sock.connect(server)
            print(f'Connection established {server}')
            sock.sendall(json.dumps(data).encode())
            response = sock.recv(1024).decode()
            print(f'Response data: {response}')
        print(f'Data transfer completed')


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_server(host, port):
    data_file = 'storage/data.json'
    if not os.path.exists(data_file) or os.stat(data_file).st_size == 0:
        # Створити новий порожній файл data.json
        with open(data_file, 'w') as fd:
            json.dump({}, fd)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(f'Server listening on {host}:{port}')

        while True:
            conn, addr = s.accept()
            print(f'Connection established from {addr}')
            data_dict = conn.recv(4096).decode()
            print(f'Received data: {data_dict}')

            try:
                with open(data_file) as fd:
                    data = json.load(fd)
            except json.JSONDecodeError:
                # Обробка недійсного формату JSON
                response_data = "Invalid data format"
                response = json.dumps(response_data)
                conn.sendall(response.encode())
                conn.close()
                continue

            try:
                # Обробка отриманих даних
                data.update(json.loads(data_dict))
                with open(data_file, 'w') as fd:
                    json.dump(data, fd)
                # Виконати потрібні дії з отриманими даними
                response_data = "Data processed successfully"
                response = json.dumps(response_data)
            except json.JSONDecodeError:
                # Обробка недійсного формату JSON
                response_data = "Invalid data format"
                response = json.dumps(response_data)

            # Відправка відповіді клієнту
            conn.sendall(response.encode())
            conn.close()



if __name__ == '__main__':
    threading.Thread(target=run).start()
    print('Server started!')

    server = threading.Thread(target=run_server, args=('localhost', 5000))
    server.start()
    server.join()
