import threading
from aapsender import AAPSender
import queue
import re
import http.client
import io;
import os;
from notifypy import Notify

from pyupcn.aap import AAPMessage, AAPMessageType, InsufficientAAPDataError

class DHTTPAAP(AAPSender):

    send_queue = queue.Queue()

    def __init__(self, proxy_addr, proxy_port, content_directory="content", eid_suffix=None, socket_address="/tmp/upcn.socket"):
        super().__init__(eid_suffix, socket_address)
        self.content_directory = content_directory
        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port

    def __enter__(self):
        result = super().__enter__()
        self.receive_thread = threading.Thread(target=DHTTPAAP.run_receive, args=[self])
        self.receive_thread.start()
        return result

    def send(self, dest_eid, payload):
        self.send_queue.put(AAPMessage(AAPMessageType.SENDBUNDLE,
                            dest_eid,
                            payload))

    def handle_received_bundle(self, msg:AAPMessage):
        match = re.match("^[^:]+://([^/]+)/(.+)$", msg.eid)
        eid = match[1]
        agent = match[2]
        
        headers = http.client.parse_headers(io.BytesIO(msg.payload.split(b"\n", maxsplit=1)[1]))
        location = headers.get("Content-Location")

        if location is not None:
            path = self.get_file_path(eid, agent, location)
            filename = path.split("/")[-1]
            dir_path = path.rstrip(filename)
            os.makedirs(dir_path, exist_ok=True)
            with open(path, "wb") as file:
                file.write(msg.payload)
            
            print("Received document from eid: {}, agent: {}, location: {}".format(eid, agent, location))
            
            content_type = headers.get("Content-Type")
            if content_type.startswith("text/") :
                notification = Notify()
                notification.title = "Received {}/{}{}".format(eid, agent, location)
                notification.message = "Web page received and now available on http://{}:{}/{}/{}{}".format(
                    self.proxy_addr,
                    self.proxy_port,
                    eid,
                    agent,
                    location)
                notification.send()

        else:
            print("Warning : Document received without \"Content-Location\" header. Document is dismissed.")

    def get_file_path(self, eid, agent, location):
        return "{}/{}/{}{}.http".format(self.content_directory, eid, agent, location)

    def run_receive(self):
        while True:

            received_bundle = self.recv_aap(timeout=0.5)

            if received_bundle is not None:
                assert received_bundle.msg_type == AAPMessageType.RECVBUNDLE
                self.handle_received_bundle(received_bundle)
                

            while not self.send_queue.empty():
                bundle:AAPMessage = self.send_queue.get()
                self.sock.send(bundle.serialize())
                msg_sendconfirm = self.recv_aap()
                assert msg_sendconfirm.msg_type == AAPMessageType.SENDCONFIRM
                print("Bundle sent ID = {}".format(
                    msg_sendconfirm.bundle_id
                ))
