from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

import pika
import sys
import time


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, rabbit_host, rabbit_port, *args, **kwargs):
        self.rabbit_host = rabbit_host
        self.rabbit_port = rabbit_port

        super(SimpleHTTPRequestHandler, self).__init__(*args, **kwargs)


    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')


    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        parameters = pika.ConnectionParameters(host = self.rabbit_host, 
                                               port = self.rabbit_port)

        with pika.BlockingConnection(parameters) as connection:
            channel = connection.channel()

            channel.queue_declare('test_queue')

            channel.basic_publish(exchange = '',
                                  routing_key = 'test_queue',
                                  body = body)

        self.send_response(201)
        self.end_headers()


class SimpleHTTPServer:
    def __init__(self, host, port, rabbit_port):
        self.host = host
        self.__port = port
        self.rabbit_port = rabbit_port
        self.httpd = None


    def get_exposedPort(self):
       if self.httpd == None:
           return 0

       return self.httpd.server_address[1]


    def make_request_handler(self):
        rabbit_port = self.rabbit_port

        class SimpleHTTPRequestHandlerAdapter(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super(SimpleHTTPRequestHandlerAdapter, self).__init__('localhost', rabbit_port, *args, **kwargs)
 
        return SimpleHTTPRequestHandlerAdapter


    def __serve(self):
        self.httpd = HTTPServer((self.host, self.__port), self.make_request_handler())
        self.httpd.serve_forever()


    def serve(self):
        t = Thread(target=self.__serve, daemon=True)
        t.start()

        while self.get_exposedPort() == 0:
            time.sleep(1)

        return t


    def serve_forever(self):
        t = self.serve()

        try:
            t.join()
        except:
            print("Simple web server exiting...")


if __name__ == "__main__":
    server = SimpleHTTPServer('localhost', int(sys.argv[1]), int(sys.argv[2]))
    server.serve_forever()
