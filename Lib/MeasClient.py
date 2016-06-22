""" 

"""

import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
from PyQt4 import QtCore
import pickle
import threading
#import queue
import time
from pydispatch import dispatcher
import logging
import configparser
from NeedfullThings import Signal

import queue

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.INFO,
                    format='%(asctime)s %(message)s Meas',
                    datefmt='%m.%d.%Y %I:%M:%S')


class Client():
    signalPause = threading.Event()

    def __init__(self,parent=None):

        self.sig = Signal()
        self.parent = parent
        snakemq.init_logging()
        logger = logging.getLogger("snakemq")
        logger.setLevel(logging.ERROR)
        self.q = queue.Queue()
        self.qRun = False
        self.pause = False
        self.link = snakemq.link.Link()
        self.link.add_connector(("localhost", 4000))
        self.link.on_ready_to_send.add(self.on_ready_to_send)
        _pktr = snakemq.packeter.Packeter(self.link)
        self.messaging = snakemq.messaging.Messaging("Meas", "", _pktr)
        self.messaging.on_message_recv.add(self.on_recv)
        #self.messaging.on_message_sent.add(self.on_send)

        dispatcher.connect(self.onJobComplete, self.sig.JOB_COMPLETE, dispatcher.Any)
        dispatcher.connect(self.onItemComplete, self.sig.ITEM_COMPLETE, dispatcher.Any)
        dispatcher.connect(self.onItemActive, self.sig.ITEM_ACTIVE, dispatcher.Any)
        dispatcher.connect(self.onGraphNewPlot, self.sig.GRAPH_NEW_PLOT, dispatcher.Any)
        dispatcher.connect(self.onGraphNewLine, self.sig.GRAPH_NEW_LINE, dispatcher.Any)
        dispatcher.connect(self.onGraphNewTrace, self.sig.GRAPH_NEW_TRACE, dispatcher.Any)
        dispatcher.connect(self.onPlotComplete, self.sig.MEAS_PLOT_COMPLETE, dispatcher.Any)
        dispatcher.connect(self.onResult,self.sig.MEAS_RESULT,dispatcher.Any)

        self.t = threading.Thread(name="ClientWorker",target=self.worker)
        self.t.start()
#        self.link.loop()

        self.qw = threading.Thread(name = "QueueWorker",target = self.qWorker)
        self.qw.start()
        self.sendMeasStarted()

    def qWorker(self):
        self.qRun = True
        while (self.qRun):
            try:
                _data = self.q.get()
                sdata = pickle.loads(_data)

                if sdata[0] == self.sig.MEAS_STOP:
                    dispatcher.send(self.sig.MEAS_STOP,dispatcher.Anonymous)

                if sdata[0] == self.sig.JOB_TABLE:
                    dispatcher.send(self.sig.JOB_TABLE,dispatcher.Anonymous)

                if sdata[0] == self.sig.MEAS_PAUSE:
                    dispatcher.send(self.sig.MEAS_PAUSE,dispatcher.Anonymous)
                    print('Pause')
                    if not self.pause:
                        self.signalPause.set()
                        self.pause = True
                    else:
                        self.signalPause.clear()
                        self.pause = False

                if sdata[0] == self.sig.MEAS_GOON:
                    dispatcher.send(self.sig.MEAS_GOON,dispatcher.Anonymous)
                    self.parent.signalWait.set()
                    print('GoOn')


            except Exception as _err:
                logging.info (_err)
                print (_err)
                pass


    def on_ready_to_send(self, conn, size):
      #  self.signalWait.set()

        pass

    def on_recv(self,conn,ident,message):
        #print("MeaS: received from:",conn,ident,message.data)
        self.q.put(message.data)
        sdata = pickle.loads(message.data)
        if sdata[0] == self.sig.MEAS_STOP:
            #do it immediately
            dispatcher.send(self.sig.MEAS_STOP,dispatcher.Anonymous)


        return
    def send(self,data):
       # print("Meas send", data)
        try:
            sdata = pickle.dumps(data)
            msg = snakemq.message.Message(sdata,ttl=600)
            self.messaging.send_message("Controller",msg)
            if self.pause:
                self.signalPause.wait()

        except Exception as _err:
            logging.info (_err)
            print(_err)



    def worker(self):
        self.link.loop()

    def stop(self, timeout=None):
        self.link.stop()
        self.link.cleanup()

    def sendJobTable(self):
        dispatcher.send(self.sig.JOB_TABLE)

    def sendMeasStarted(self):
        _sData = []
        _sData.append(self.sig.MEAS_STARTED)
        self.send(_sData)

    def sendMessage(self,msg,data):
        _sData = []
        _sData.append(msg)
        if not data == None:
            _sData.append(data)

        self.send(_sData)
    def sendMeasStop(self):
        dispatcher.send(self.sig.MEAS_STOP)

    def sendMeasPause(self):
        dispatcher.send(self.sig.MEAS_PAUSE)

    def onPlotComplete(self):
        _sData = []
        _sData.append(self.sig.MEAS_PLOT_COMPLETE)
        self.send(_sData)
        print('MC: Plot Complete')

    def onResult(self,data):
        #print('MC: onResult {0}'.format(str(data)))
        _sData = []
        _sData.append(self.sig.MEAS_RESULT)
        _sData.append(data)
        self.send(_sData)
    def onGraphNewPlot(self,data):
        #send data of new Plot to controller for archiving
        _sData = []
        _sData.append(self.sig.GRAPH_NEW_PLOT)
        _sData.append(data)
        self.send(_sData)

    def onGraphNewTrace(self,data):
        #send data of new Plot to controller for archiving
        _sData = []
        _sData.append(self.sig.GRAPH_NEW_TRACE)
        _sData.append(data)
        self.send(_sData)

    def onGraphNewLine(self,data):
        #send data of new Plot to controller for archiving
        _sData = []
        _sData.append(self.sig.GRAPH_NEW_LINE)
        _sData.append(data)
        self.send(_sData)

    def onJobComplete(self):
        _sData = []
        _sData.append(self.sig.JOB_COMPLETE)
        self.send(_sData)

    def onItemComplete(self,data):
        _sData = []
        _sData.append(self.sig.ITEM_COMPLETE)
        _sData.append(data)
        self.send(_sData)

    def onItemActive(self,data):
        _sData = []
        _sData.append(self.sig.ITEM_ACTIVE)
        _sData.append(data)
        self.send(_sData)

    def showMessage(self,text):
        sdata = pickle.dumps(text)
        dispatcher.send(self.sig.SHOW_MESSAGE, dispatcher.Anonymous,sdata)


