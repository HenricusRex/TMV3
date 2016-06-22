__author__ = 'Heinz'
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
import snakemq.rpc
import threading
import logging

#logging.basicConfig(filename="TMV3log.txt",
#                    level=logging.INFO,
#                    format='%(asctime)s %(message)s Server',
#                    datefmt='%m.%d.%Y %I:%M:%S')

# following class is needed to route messages to RPC
#rh = snakemq.messaging.ReceiveHook(my_messaging)

class MyClass(object):

    def get_fo(self):
        print('get_fo')
        return "fo value"



    @snakemq.rpc.as_signal
    def mysignal(self,text):
        print("signal---",text)

class Server(object):
    def __init__(self):
        self.link = snakemq.link.Link()
        self.link.add_listener(("",4001))
        self.link.add_connector(("localhost", 4000))
        self.my_packeter = snakemq.packeter.Packeter(self.link)
        self.my_messaging = snakemq.messaging.Messaging('server', "", self.my_packeter)
        self.my_messaging.on_message_recv.add(self.on_recv)

        snakemq.init_logging()
        logger = logging.getLogger("snakemq")
        logger.setLevel(logging.ERROR)


        rh = snakemq.messaging.ReceiveHook(self.my_messaging)
        srpc = snakemq.rpc.RpcServer(rh)
        srpc.register_object(MyClass(), "myinstance")

        self.t = threading.Thread(name="ServerWorker",target=self.worker)
        self.t.start()
    def on_recv(self,conn,ident,message):
        #print("MeaS: received from:",conn,ident,message.data)
        print('y',message.data)

    def sendServer(self,text):
        msg = snakemq.message.Message(b'Server',ttl=600)
        self.my_messaging.send_message('client',msg)

    def worker(self):
        self.link.loop()
        self.link.cleanup()

class Client(object):
    def __init__(self):
        self.link = snakemq.link.Link()
        self.link.add_listener(("",4000))
        self.link.add_connector(("localhost", 4001))
        self.my_packeter = snakemq.packeter.Packeter(self.link)
        self.my_messaging = snakemq.messaging.Messaging('client', "", self.my_packeter)
        self.my_messaging.on_message_recv.add(self.on_recv)


        snakemq.init_logging()
        logger = logging.getLogger("snakemq")
        logger.setLevel(logging.ERROR)


        rh = snakemq.messaging.ReceiveHook(self.my_messaging)
        crpc = snakemq.rpc.RpcClient(rh)
        self.proxy = crpc.get_proxy('server', "myinstance")
        self.proxy.mysignal.as_signal(50)  # 10 seconds TTL
      #  self.proxy.mysignal.

        _t = threading.Thread(name="ServerWorker",target=self.worker)
        _t.start()
    def on_recv(self,conn,ident,message):
    #print("MeaS: received from:",conn,ident,message.data)
        print('x',message.data)
    def sendClient(self,text):
        msg = snakemq.message.Message(b'Client',ttl=600)
        self.my_messaging.send_message('server',msg)
    def sendProxy(self):
        _tt = threading.Thread(name="x",target=self.proxy2)
        _tt.start()
    def proxy2(self):
        self.proxy.mysignal('X')
        ret = self.proxy.get_fo()
        print(ret)
    def worker(self):
        self.link.loop()
        self.link.cleanup()

