
import threading
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import time
import websocket

from random import randint

CONTROL_TIME = 10

global running
global ws
clients = []
netbook = []
bbb = []
c=0
#Initialize TOrnado to use 'GET' and load index.html
class MainHandler(tornado.web.RequestHandler):
  def get(self):
    loader = tornado.template.Loader(".")
    self.write(loader.load("index.html").generate())

#Code for handling the data sent from the webpage
class WSHandlerNetbook(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
    		return True
	def open(self):
		print 'Netbook connection opened...'
		netbook.append(self)
	def on_message(self, message):
		print 'Netbook Message: ', message
	def on_close(self):
		print 'Netbook connection closed...'
		netbook.remove(self)
	def msg(self, url):
		self.write_message(u"controlling" + url)
	def msg2(self):
		self.write_message(u"asdf")

class WSHandlerBBB(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
    		return True
	def open(self):
		print 'BBB connection opened...'
		bbb.append(self)
	def on_message(self, message):
		print 'BBB Message: ', message
	def on_close(self):
		print 'BBB connection closed...'
		bbb.remove(self)
	def send_message(self, message):
		self.write_message(message)

def sendBBBMessage(message):
	if len(bbb) == 0:
		print 'BBB has not connected yet'
	else:
		bbb[0].send_message(message)


#Code for handling the data sent from the webpage
class WSHandler(tornado.websocket.WebSocketHandler):
	active=False
	count=CONTROL_TIME
	def check_origin(self, origin):
    		return True
	def open(self):
		clients.append(self)
		print 'connection opened...'
		print clients
	def on_message(self, message):
		if clients.index(self) == 0:
			print 'received:', message
			sendBBBMessage(message)
	def on_close(self):
		clients.remove(self)
		print 'connection closed...'
		print clients
		netbook[0].write_message(u"closed")

	def msg(self):
		self.write_message(u"Controlling... Time Left: " + str(self.count)+ "sec | Queue Size: " + str(len(clients)))
	
	def waitmsg(self):
		self.write_message(u"Waiting... " + str(len(clients)) + " In queue |  Your location is " + str(clients.index(self)) + " | Approx wait time: " + str(clients.index(self) * CONTROL_TIME))
	
	def activate(self):
		if self.active == False:
			self.active = True
			s = str(randint(3333,4444));
			self.write_message(u"controlling" +  s)			
			if len(netbook) != 0:
				netbook[0].msg(s)
			else:
				print "netbook not connected"

application = tornado.web.Application([
  (r'/ws', WSHandler),
  (r'/netbook', WSHandlerNetbook),
  (r'/bbb', WSHandlerBBB),
  (r'/', MainHandler),
  (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Ready"
        while running:
        	time.sleep(1)              # sleep for 200 ms
		if len(clients) != 0:		
			clients[0].count = clients[0].count - 1
			clients[0].msg()
			clients[0].activate()

			if clients[0].count == 0:
				clients[0].close()
				clients.remove(clients[0]);
				if len(netbook) != 0:
					netbook[0].write_message(u"closed")


			for i in range(1, len(clients)):
				clients[i].waitmsg()

		#print ws.connected
		#print ws._tunnel
		#print ws.recv
		if len(netbook) == 0:
			print 'netbook not connected'

		if len(bbb) == 0:
			print 'bbb not connected'

def stuff(self):
	l = dir(ws)
	print ws.l

if __name__ == "__main__":
	running = True	
	thread1 = myThread(1, "Thread-1", 1)
	thread1.setDaemon(True)
	thread1.start()  
	application.listen(9093) #9093         	#starts the websockets connection

	#websocket.enableTrace(True)
	#ws = websocket.create_connection("ws://192.168.1.101:9094/ws")
	#connectToBBB()

	#ws.on_error = on_error2

#	ws = websocket.WebSocketApp("ws://192.168.1.101:9094/ws", on_error = on_error2, on_close = on_close2)


#	ws.run_forever()

	tornado.ioloop.IOLoop.instance().start()

