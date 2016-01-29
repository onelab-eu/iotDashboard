import logging, json
from tornado import websocket, gen

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
        #self.write_message(json.dumps({ "message": "Waiting for changes" }))
        logger.info("WebSocket msg received (%s)" % message)
        self.send_to_clients(message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
        logger.info("WebSocket closed (%s)" % self.request.remote_ip)

    @gen.coroutine
    def send_to_clients(self, message):
        for client in cl:
            if client is not self:
                client.write_message(json.dumps(message))

