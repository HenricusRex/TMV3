""" 

"""
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
import queue
from PyQt4 import QtCore
import pickle
import threading
#import queue
import time
from pydispatch import dispatcher
import logging
import configparser
from NeedfullThings import Signal

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.INFO,
                    format='%(asctime)s %(message)s Graph',
                    datefmt='%m.%d.%Y %I:%M:%S')





class Client(object):
    waitEvent = threading.Event()

    def __init__(self,name):
        self.signals = Signal()

        snakemq.init_logging()
        logger = logging.getLogger("snakemq")
        logger.setLevel(logging.ERROR)

        self.link = snakemq.link.Link()
        self.link.add_connector(("localhost", 4001))
        _pktr = snakemq.packeter.Packeter(self.link)
        self.messaging = snakemq.messaging.Messaging(name, "", _pktr)
        self.messaging.on_message_recv.add(self.on_recv)
        self.messaging.on_message_sent.add(self.on_send)

        t = threading.Thread(name="ClientWorker",target=self.worker)
        t.start()
        self.q = queue.Queue()
        self.qw = threading.Thread(name = "QueueWorker",target = self.qWorker)
        self.qw.start()



    def qWorker(self):
        self.qRun = True
        while (self.qRun):
            try:
                _data = self.q.get()
                _sdata = pickle.loads(_data)

                if _sdata[0] == self.signals.GRAPH_NEW_PLOT:
                    #_sdata[1] = Plot
                    dispatcher.send(self.signals.GRAPH_NEW_PLOT,dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_NEW_TRACE:
                    #_sdata[1] = Trace-dbRow
                    dispatcher.send(self.signals.GRAPH_NEW_TRACE, dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_NEW_LINE:
                    #_sdata[1] = Line-dbRow
                    dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_NEW_ANNOTATION:
                    #_sdata[1] = Annotation-List
                    dispatcher.send(self.signals.GRAPH_NEW_ANNOTATION, dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_NEW_CLASSIFICATION:
                    #_sdata[1] = Classification-String
                    dispatcher.send(self.signals.GRAPH_NEW_ANNOTATION, dispatcher.Anonymous, _sdata[1])
                    pass

                if _sdata[0] == self.signals.GRAPH_NEW_DESCRIPTION:
                    #_sdata[1] = Description
                    dispatcher.send(self.signals.GRAPH_NEW_DESCRIPTION, dispatcher.Anonymous, _sdata[1])


                if _sdata[0] == self.signals.GRAPH_NEW_NUMBER:
                    #_sdata[1] = Number
                    dispatcher.send(self.signals.GRAPH_NEW_NUMBER, dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_PRINT:
                    #print current Plot
                    dispatcher.send(self.signals.GRAPH_PRINT)

                if _sdata[0] == self.signals.GRAPH_STOP:
                    self.link.stop()
                    self.link.cleanup()

                if _sdata[0] == self.signals.GRAPH_SHOW_PLOT:
                    dispatcher.send(self.signals.GRAPH_SHOW_PLOT, dispatcher.Anonymous, _sdata[1],_sdata[2],_sdata[3])
                    #self.link.stop()
                    #self.link.cleanup()

                if _sdata[0] == self.signals.GRAPH_RESULT:
                    dispatcher.send(self.signals.GRAPH_RESULT, dispatcher.Anonymous, _sdata[1])

                if _sdata[0] == self.signals.GRAPH_MAKE_THUMBNAIL:
                    dispatcher.send(self.signals.GRAPH_MAKE_THUMBNAIL, dispatcher.Anonymous)

                if _sdata[0] == self.signals.WB_GET_LINE:
                    self.waitEvent.set()
                    if _sdata[0] == self.sig.MEAS_STOP:
                        dispatcher.send(self.sig.MEAS_STOP,dispatcher.Anonymous)

                    if _sdata[0] == self.sig.JOB_TABLE:
                        dispatcher.send(self.sig.JOB_TABLE,dispatcher.Anonymous)

                    if _sdata[0] == self.sig.MEAS_PAUSE:
                        dispatcher.send(self.sig.MEAS_PAUSE,dispatcher.Anonymous)
                        print('Pause')
                        if not self.pause:
                            self.signalPause.set()
                            self.pause = True
                        else:
                            self.signalPause.clear()
                            self.pause = False

                    if _sdata[0] == self.sig.MEAS_GOON:
                        dispatcher.send(self.sig.MEAS_GOON,dispatcher.Anonymous)
                        self.parent.signalWait.set()
                        print('GoOn')


            except Exception as _err:
                logging.info (_err)
                print (_err)
                pass


    def worker(self):
        self.link.loop()

    def stop(self, timeout=None):
        self.qRun = False
        self.q.join()
        self.link.stop()
        self.link.cleanup()

    def on_send(self,conn,ident,message_uuid):
        #print('os',conn)
        #print ('os',ident)
        #print ('os',message_uuid)
        pass
    def on_recv(self,conn,ident,message):
        sdata = pickle.loads(message.data)
        if sdata[0] == self.signals.GRAPH_STOP:
            self.stop()
        else:
            self.q.put(message.data)
        return

    def send(self,data):
        print("Graph send", data)
        try:

            sdata = pickle.dumps(data)
            msg = snakemq.message.Message(sdata,ttl=600)
            self.messaging.send_message("Controller",msg)


        except Exception as _err:
            logging.info (_err)
            print(_err)




