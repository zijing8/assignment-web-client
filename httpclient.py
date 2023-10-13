#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Zijing Lu
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
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        # takes in a url, parse it, then return host and port
        parsedUrl = urlparse(url)
        host = parsedUrl.hostname
        port = parsedUrl.port

        # if no host use default 80
        if port is None:
            port = 80

        # print(host)
        # print(port)
        return host, port

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # take the data and return the status code
        code = int(data.split()[1])
        return code

    def get_headers(self,data):
        # take the date and return the header
        header = data.split('\r\n\r\n')[0]
        return header


    def get_body(self, data):
        # take the data and return the body
        body = data.split('\r\n\r\n')[-1]
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
        # parse the url for the path
        parsedUrl = urlparse(url)
        path = parsedUrl.path
        host, port = self.get_host_port(url)

        # set path to default if no path is given
        if path == "":
            path = "/"

        # connect, request, and recive date from host
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
        request += f"Connection: close\r\n\r\n"
        self.connect(host, port)
        self.sendall(request)

        # recieve the data
        result = self.recvall(self.socket)
        code = self.get_code(result)
        body = self.get_body(result)

        # close the connection
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # parse the url for the path
        parsedUrl = urlparse(url)
        path = parsedUrl.path
        host, port = self.get_host_port(url)

        # set path to default if no path is given
        if path == "":
            path = "/"

        # get the paramters and content length and encode the special characters
        paramters = ''
        contentLength = 0
        if bool(args):
            for each in args:
                if len(paramters) != 0:
                    paramters+='&'
                paramters += each + '='
                encode = (args[each]).replace('\r', '%0D').replace('\n', '%0A').replace(' ', '+')
                paramters += encode
            contentLength = len(paramters)

        request = f"POST {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += f"Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {contentLength}\r\n"
        request += f"Connection: close\r\n\r\n"

        request += f"{paramters}\r\n"

        # connect, request, and recive date from host
        self.connect(host, port)
        self.sendall(request)
        
        # recieve the data
        result = self.recvall(self.socket)
        code = self.get_code(result)
        body = self.get_body(result)
        # print(result)

        # close the connection
        self.close()

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
