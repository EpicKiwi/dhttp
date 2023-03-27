#!/bin/env python3

from server import UPCNServer
from http.server import SimpleHTTPRequestHandler
from os import path
import os

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server, directory=".")

    def end_headers(self) -> None:
        self.send_header("Content-Location", self.path)
        return super().end_headers()

UPCNServer(Handler, 
           eid_suffix="www",
           socket_address="/var/run/user/{}/upcn.socket".format(os.getuid())
        ).serve_forever()