#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    
    def get_host_port(self, url):
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.hostname or url
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        return (host, port)

    def connect(self, host, port):
        addr = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(addr)

    def get_code(self, data):
        try:
            header_index = data.index("\r\n\r\n")
            header_data = data[:header_index].strip()
            headers = header_data.split("\r\n")
            status_line = headers[0]
            status_code = int(status_line.split(" ")[1])
            return status_code
        except ValueError:
            return 404

    def get_headers(self, data):
        try:
            header_index = data.index("\r\n\r\n")
            headers = data[:header_index]
            return headers
        except ValueError:
            print("Error: The string '\r\n\r\n' was not found in the data.")
            return None

    def get_body(self, data):
        if not data:
            return None

        try:
            header_index = data.index("\r\n\r\n")
        except ValueError:
            return None

        body = data[header_index+4:]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port = self.get_host_port(url)
        
        request = f"GET {url} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
        self.connect(host, port)
        self.sendall(request)
        
        response = self.recvall(self.socket)
        self.close()


        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)

        
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port = self.get_host_port(url)
        self.connect(host, port)

        headers = "Content-Type: application/x-www-form-urlencoded\r\n"
        body = urllib.parse.urlencode(args) if args else ""

        request = f"POST / HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(body)}\r\n{headers}\r\n{body}"

        self.sendall(request)
        response = self.recvall(self.socket)
        self.close()
        
        code = self.get_code(response)
        body = self.get_body(response)
        headers = self.get_headers(response)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
