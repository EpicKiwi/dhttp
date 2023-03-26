import socket
import uuid
import selectors

from pyupcn.aap import AAPMessage, AAPMessageType, InsufficientAAPDataError

class AAPSender:

    sock = None
    socket_path = None
    eid_suffix = None
    _selector = selectors.DefaultSelector()

    def __init__(self, eid_suffix = None, socket_path = "/tmp/upcn.socket"):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket_path = socket_path
        self.eid_suffix = eid_suffix or str(uuid.uuid4())
    
    def __enter__(self):
        self._selector.register(self.sock, selectors.EVENT_READ)
        self.sock.connect(self.socket_path)

        print("Connected to uPCN, awaiting WELCOME message...")

        msg_welcome = self.recv_aap()
        assert msg_welcome.msg_type == AAPMessageType.WELCOME

        print("Sending REGISTER message...")
        self.sock.send(AAPMessage(AAPMessageType.REGISTER, self.eid_suffix).serialize())
        msg_ack = self.recv_aap()
        assert msg_ack.msg_type == AAPMessageType.ACK

        print("Connected to uPCN")

        return self
 
    def __exit__(self, *args):
        print("Terminating connection to uPCN...")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def recv_aap(self, timeout=None):
        buf = bytearray()
        msg = None

        result = self._selector.select(timeout=timeout)
        
        if len(result) < 1:
            return None

        while msg is None:
            buf += self.sock.recv(1)
            try:
                msg = AAPMessage.parse(buf)
            except InsufficientAAPDataError:
                continue
        return msg


    def send(self, dest_eid, payload):
        self.sock.send(AAPMessage(AAPMessageType.SENDBUNDLE,
                            dest_eid,
                            payload).serialize())
        msg_sendconfirm = self.recv_aap()
        assert msg_sendconfirm.msg_type == AAPMessageType.SENDCONFIRM
        print("Bundle sent ID = {}".format(
            msg_sendconfirm.bundle_id
        ))
