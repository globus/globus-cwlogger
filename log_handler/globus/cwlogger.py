import json
import logging
import logging.handlers
import socket
import sys
import time

try:
    # Python 2
    UNICODE_TYPE = unicode
except NameError:
    # Python 3
    UNICODE_TYPE = str

# Backports Python3 SocketHandler features that allow using UNIX sockets
# instead of TCP sockets:


class BackportedSocketHandler(logging.handlers.SocketHandler):

    def __init__(self, host, port):
        """
        Backported from Python 3

        Initializes the handler with a specific host address and port.
        When the attribute *closeOnError* is set to True - if a socket error
        occurs, the socket is silently closed and then reopened on the next
        logging call.
        """
        logging.Handler.__init__(self)
        self.host = host
        self.port = port
        if port is None:
            self.address = host
        else:
            self.address = (host, port)
        self.sock = None
        self.closeOnError = False
        self.retryTime = None
        #
        # Exponential backoff parameters.
        #
        self.retryStart = 1.0
        self.retryMax = 30.0
        self.retryFactor = 2.0

    def makeSocket(self, timeout=1):
        """
        Backported from Python 3.

        A factory method which allows subclasses to define the precise
        type of socket they want.
        """
        if self.port is not None:
            result = socket.create_connection(self.address, timeout=timeout)
        else:
            result = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            result.settimeout(timeout)
            try:
                result.connect(self.address)
            except OSError:
                result.close()  # Issue 19182
                raise
        return result


if sys.version_info < (3, 4):
    SocketHandlerBase = BackportedSocketHandler
else:
    SocketHandlerBase = logging.handlers.SocketHandler


class GlobusSocketHandler(SocketHandlerBase):
    """
    Subclass of the Python SocketHandler that avoids
    using pickle. Our Cloudwatch log daemon understands
    JSON bytestrings, not binary pickles.
    """

    def emit(self, record):
        """
        Emit a record.

        Overrides the parent to call makePayload() instead of makePickle() and
        also to close the socket once we've sent the record.

        Serializes the record to JSON bytestring and writes it to the socket.
        If there is an error with the socket, silently drop the packet.
        If there was a problem with the socket, re-establishes the
        socket.
        """
        try:
            s = self.makePayload(record)
            self.send(s)
        except Exception:
            self.handleError(record)
        finally:
            # Our daemon only uses the socket
            # for one message, so we want to
            # close here and get a new one next
            # time.
            self.close()

    def makePayload(self, record):
        """
        Used in place of makePickle to generate a
        JSON bytestring payload instead of a binary pickle.

        Our cloudwatch daemon expects a JSON object
        with keys 'timestamp' and 'message'.

        'message' can also be another JSON string, depending
        on what formatters you attach.
        """

        message = self.format(record)
        payload = {
            "message": message,
            "timestamp": int(time.time() * 1000)
        }
        payload = json.dumps(payload,
                             separators=(',', ':'),
                             indent=None) + '\n'
        if isinstance(payload, UNICODE_TYPE):
            payload = payload.encode("utf-8")
        return payload


cloudwatch_handler = GlobusSocketHandler(host='\0org.globus.cwlogs', port=None)
