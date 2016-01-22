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
        self.write_message(json.dumps({ "message": "Waiting for changes" }))
        self.jobs()

    def on_close(self):
        if self in cl:
            cl.remove(self)
        logger.info("WebSocket closed (%s)" % self.request.remote_ip)

    @gen.coroutine
    def jobs(self):
        conn = None
        try :
            conn = yield r.connect(host="localhost", port=28015)
        except r.RqlDriverError :
            logger.error("can't connect to RethinkDB")
            self.write_message(json.dumps({ "ret" : 0, "msg" : "connection error" }, ensure_ascii = False))

        if (conn) :
            feed = yield r.db("myops2").table("jobs").changes().run(conn)
            while (yield feed.fetch_next()):
                change = yield feed.next()
                #self.write_message(json.dumps(change['new_val'], ensure_ascii = False).encode('utf8'))
                self.write_message(json.dumps(change['new_val']))
