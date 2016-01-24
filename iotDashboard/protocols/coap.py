'''
Created on 08-09-2012

@author: Maciej Wasilak
'''

import sys
import logging

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource

# Send the value received from CoAP to a websocket
from tornado import websocket, gen, ioloop

class Agent():
    """
    Example class which performs single GET request to iot.eclipse.org
    port 5683 (official IANA assigned CoAP port), URI "obs".
    Request is sent 1 second after initialization.
    
    Remote IP address is hardcoded - no DNS lookup is preformed.

    Method requestResource constructs the request message to
    remote endpoint. Then it sends the message using protocol.request().
    A deferred 'd' is returned from this operation.

    Deferred 'd' is fired internally by protocol, when complete response is received.

    Method printResponse is added as a callback to the deferred 'd'. This
    method's main purpose is to act upon received response (here it's simple print).
    """

    def __init__(self, protocol):
        self.protocol = protocol
        self.message = None
        reactor.callLater(1, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        #Send request to "coap://iot.eclipse.org:5683/obs"
        # coap://californium.eclipse.org:5683
        # coap get -o coap://[2001:660:5307:3101::a869]:5683/light
        request.opt.uri_path = ('light',)
        request.opt.observe = 0
        request.remote = ("2001:660:5307:3101::a869", coap.COAP_PORT)
        d = protocol.request(request, observeCallback=self.printLaterResponse)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

    def printResponse(self, response):
        log.msg("printResponse")
        print 'First result: ' + response.payload
        self.message = response.payload
        ioloop.IOLoop.instance().run_sync(self.send_ws)
        #reactor.stop()

    def printLaterResponse(self, response):
        log.msg("printLaterResponse")
        print 'Observe result: ' + response.payload
        self.message = response.payload
        ioloop.IOLoop.instance().run_sync(self.send_ws)

    def noResponse(self, failure):
        log.msg("noResponse")
        print 'Failed to fetch resource:'
        print failure
        self.message = failure
        ioloop.IOLoop.instance().run_sync(self.send_ws)
        #reactor.stop()

    @gen.coroutine
    def send_ws(self):
        print "connect ws"
        ws = yield websocket.websocket_connect("ws://localhost:8111/ws")
        print "send msg ws"
        s = ws.write_message(self.message)
        print "msg sent ws"
        ws.close()


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filename="iotDashboard.coap.log", filemode="a")

log.startLogging(sys.stdout)
endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)

# IPv4
#reactor.listenUDP(61616, protocol)
# IPv6
reactor.listenUDP(61616, protocol, interface='::')

reactor.run()
