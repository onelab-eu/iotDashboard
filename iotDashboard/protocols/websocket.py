import logging, json
from tornado import websocket, gen

import txthings.coap as coap
import txthings.resource as resource

logger = logging.getLogger('iotDashboard.websocket')
cl = []

class Api(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
        logger.info("WebSocket opened (%s)" % self.request.remote_ip)

    def on_message(self, message):
        self.write_message(json.dumps({ "message": "Waiting for changes" }))
        self.jobs()

    def on_close(self):
        if self in cl:
            cl.remove(self)
        logger.info("WebSocket closed (%s)" % self.request.remote_ip)

    def printResponse(self, response):
        print 'First result: ' + response.payload
        self.write_message(response.payload)

    def printLaterResponse(self, response):
        print 'Observe result: ' + response.payload
        self.write_message(response.payload)

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure
        self.write_message(failure)

    @gen.coroutine
    def jobs(self):
        endpoint = resource.Endpoint(None)
        protocol = coap.Coap(endpoint)
        request = coap.Message(code=coap.GET)
        #Send request to "coap://iot.eclipse.org:5683/obs"
        request.opt.uri_path = ('obs',)
        request.opt.observe = 0
        request.remote = ("198.41.30.241", coap.COAP_PORT)
        d = protocol.request(request, observeCallback=self.printLaterResponse)
        d.addCallback(self.printResponse)
        d.addErrback(self.noResponse)

