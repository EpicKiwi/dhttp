#!/bin/env python3

from http import HTTPStatus
import http.server
from dhttpaap import *;
import re;
import views;
import shutil;
import time;

PORT = 4555

with DHTTPAAP(
    "127.0.0.1",
    PORT,
    content_directory=os.path.expanduser("~/.cache/dhttp"),
    socket_address="/var/run/user/{}/upcn.socket".format(os.getuid())   ) as aap:

    class DHTTPProxyHandler(http.server.BaseHTTPRequestHandler):

        def try_send_cache(self, eid, agent, path):
            with open(aap.get_file_path(eid, agent, path), "rb") as cache_file:
                shutil.copyfileobj(cache_file, self.wfile)
                return

        def proxy_request(self):
            url_result = re.match("^/([^/]+)/([^/]+)(/?.*)$", self.path)

            if url_result is None:
                body = views.bad_url(self.path).encode("utf-8")

                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            eid = url_result[1]
            agent = url_result[2]
            path = url_result[3]

            if not path.startswith("/"):
                path = "/"+path

            try:
                self.try_send_cache(eid, agent, path)
                return
            except FileNotFoundError as e:
                pass

            self.headers.add_header("EID", "dtn://{}/{}".format(eid, agent))
            self.headers.replace_header("Host", eid)

            payload = bytearray()
            payload += "{} {} {}\r\n".format(self.command, path, self.request_version).encode('iso-8859-1')
            payload += bytes(self.headers)

            length = self.headers.get('content-length')
            if length is not None and int(length) > 0:
                payload += bytes(self.rfile.read(int(length)))

            aap.send("dtn://{}/{}".format(eid, agent), payload)

            body = views.dtn_sent(eid, agent, path).encode("utf-8")

            time.sleep(0.5)

            try:
                self.try_send_cache(eid, agent, path)
                return
            except FileNotFoundError as e:
                pass

            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def handle_one_request(self):
            try:
                self.raw_requestline = self.rfile.readline(65537)
                if len(self.raw_requestline) > 65536:
                    self.requestline = ''
                    self.request_version = ''
                    self.command = ''
                    self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                    return
                if not self.raw_requestline:
                    self.close_connection = True
                    return
                if not self.parse_request():
                    return
                
                self.proxy_request()

                self.wfile.flush()
            except TimeoutError as e:
                self.log_error("Request timed out: %r", e)
                self.close_connection = True
                return

    print("dhttp proxy started on 127.0.0.1:{}".format(PORT))
    http.server.HTTPServer(("127.0.0.1", PORT), DHTTPProxyHandler).serve_forever()