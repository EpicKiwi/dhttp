import http.server
from socketserver import BaseServer
import socket
import uuid
import io
import selectors

from pyupcn.aap import AAPMessage, AAPMessageType, InsufficientAAPDataError

class UPCNServer(BaseServer):

    _selector = selectors.DefaultSelector()

    def __init__(self, RequestHandlerClass, eid_suffix=None, socket_address: str = "/tmp/upcn.socket"):
        super().__init__(socket_address, RequestHandlerClass)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.eid_suffix = eid_suffix or str(uuid.uuid4())

    def recv_aap(self):
        buf = bytearray()
        msg = None
        while msg is None:
            buf += self.sock.recv(1)
            try:
                msg = AAPMessage.parse(buf)
            except InsufficientAAPDataError:
                continue
        return msg

    def serve_forever(self, poll_interval = 0.5):
        self.sock.connect(self.server_address)

        print("Connected to uPCN, awaiting WELCOME message...")
        msg_welcome = self.recv_aap()
        assert msg_welcome.msg_type == AAPMessageType.WELCOME
        print("WELCOME message received! ~ EID = {}".format(msg_welcome.eid))

        print("Sending REGISTER message...")
        self.sock.send(AAPMessage(AAPMessageType.REGISTER, self.eid_suffix).serialize())
        msg_ack = self.recv_aap()
        assert msg_ack.msg_type == AAPMessageType.ACK
        print("ACK message received!")

        return super().serve_forever(poll_interval)

    def get_request(self):
        msg = self.recv_aap()
        if not msg:
            print("Disconnected.")
            return
        assert msg.msg_type == AAPMessageType.RECVBUNDLE
        print("Received bundle from '{}'".format(
            msg.eid,
        ))
        return (BundleRequest(msg.bundle_id, msg.eid, msg.payload, self), msg.eid)

    def server_close(self):
        print("Terminating connection...")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def fileno(self):
        return self.sock.fileno()


    def send(self, dest_eid, payload):
        print("Sending bundle...")
        self.sock.send(AAPMessage(AAPMessageType.SENDBUNDLE,
                            dest_eid,
                            payload).serialize())
        msg_sendconfirm = self.recv_aap()
        assert msg_sendconfirm.msg_type == AAPMessageType.SENDCONFIRM
        print("SENDCONFIRM message received! ~ ID = {}".format(
            msg_sendconfirm.bundle_id
        ))

    def close_request(self, request):
        self.send(request.eid, request.response.getvalue())

class BundleRequest:
    def __init__(self, id, eid, payload, server: UPCNServer) -> None:
        self.id = id
        self.eid = eid
        self.payload = payload
        self.request = io.BytesIO(self.payload)
        self.response = io.BytesIO()
        self._server = server
    
    def makefile(self, mode, buffer_size):
        assert(mode == "rb" or mode == "wb")
        if mode == "rb":
            return self.request
        elif mode == "wb":
            return self.response
    
    def settimeout(self, _):
        pass

    def setsockopt(self, _, __):
        pass

    def sendall(self, b):
        self.response.write(b)
