# Server Class
#
import snakemq.link
import snakemq.packeter
import snakemq.messaging
import snakemq.message
import snakemq.rpc
from PyQt4 import QtCore
import pickle
import threading

from pydispatch import dispatcher
import logging
from NeedfullThings import Signal
import queue

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.INFO,
                    format='%(asctime)s %(message)s Server',
                    datefmt='%m.%d.%Y %I:%M:%S')

class myClass(object):
    def getX(self):
        return "test"

    @snakemq.rpc.as_signal
    def snakeSignal(self):
        print ('SnakeSignal')


class ServerGraph(QtCore.QObject):
    signalItemActive = QtCore.pyqtSignal(list)  #access Gui
    signalItemComplete = QtCore.pyqtSignal(list) #access Gui
    signalMeasStarted = QtCore.pyqtSignal() #access Gui
    signalWait = threading.Event()
    signalWaitForProcessThumbnail = threading.Event()

    def __init__( self,parent = None ):
        QtCore.QObject.__init__(self)
        self.signals=Signal()
        self.graphName = ''
        self.parent = parent

        snakemq.init_logging()
        logger = logging.getLogger("snakemq")
        logger.setLevel(logging.ERROR)
        self.q = queue.Queue()
        self.qRun = False

        self.link = snakemq.link.Link()
        self.link.add_listener(("",4000))

        _pktr = snakemq.packeter.Packeter(self.link)
        self.messaging = snakemq.messaging.Messaging("Controller", "", _pktr)
#        self.messaging.on_message_recv.add(self.on_recv)
        rh = snakemq.messaging.ReceiveHook(self.messaging)
        srpc = snakemq.rpc.RpcServer(rh)
        srpc.register_object(myClass(),"test")
        self.signalWaitForProcessThumbnail.set()
        t = threading.Thread(name="ClientWorker",target=self.worker)
        t.start()



    def start(self):
        print('start')
        pass

    def worker(self):
        self.link.loop()
        self.link.cleanup()

    def stop(self):
        self.link.stop()
        self.qRun = False
        self.q.put(None) # make sure, that q reads flag

    def resumeWorker(self):
        self.signalWait.set()

    def writeGraph(self,data):
        try:
            sdata = pickle.dumps(data)
            msg = snakemq.message.Message(sdata,ttl=600)
            self.messaging.send_message(self.graphName,msg)

        except Exception as _err:
            logging.info (_err)
            print('writeGraph',_err)
    def on_drop(self,ident,message):
        m = pickle.loads(message.data)


    def qWorker(self):
        self.qRun = True

        while (self.qRun):

            try:
                _data = self.q.get()
                if _data != None:
                    _sdata = pickle.loads(_data)
                    print ('SV:',_sdata)

                    if _sdata[0] == self.signals.MEAS_STARTED:
                        self.signalMeasStarted.emit()
                        pass

                    elif _sdata[0] == self.signals.MEAS_ERROR:
                        logging.info('MEAS_ERROR')
                        dispatcher.send(self.signals.MEAS_ERROR, dispatcher.Anonymous)

                    elif _sdata[0] == self.signals.ITEM_ACTIVE:
                        self.signalItemActive.emit(_sdata[1])
                        pass

                    elif _sdata[0] == self.signals.ITEM_COMPLETE:
                        self.signalItemComplete.emit(_sdata[1])

                    elif _sdata[0] == self.signals.JOB_COMPLETE:
                        dispatcher.send(self.signals.JOB_COMPLETE, dispatcher.Anonymous)

                    elif _sdata[0] == self.signals.GRAPH_NEW_PLOT:
                        dispatcher.send(self.signals.GRAPH_NEW_PLOT, dispatcher.Anonymous, _sdata[1])
                        #wait until new plot is established
                        self.signalWait.clear()
                        _ret = self.signalWait.wait(5)

                    elif _sdata[0] == self.signals.GRAPH_NEW_LINE:
                        dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _sdata[1])

                    elif _sdata[0] == self.signals.GRAPH_NEW_TRACE:
                        dispatcher.send(self.signals.GRAPH_NEW_TRACE, dispatcher.Anonymous, _sdata[1])

                    elif _sdata[0] == self.signals.MEAS_PLOT_COMPLETE:
                        dispatcher.send(self.signals.MEAS_PLOT_COMPLETE, dispatcher.Anonymous)


                    elif _sdata[0] == self.signals.MEAS_RESULT:
                        dispatcher.send(self.signals.MEAS_RESULT, dispatcher.Anonymous,_sdata[1])

                    elif _sdata[0] == self.signals.GRAPH_THUMBNAIL_READY:
                        print ("SG:ThumbnailReady")
                        dispatcher.send(self.signals.GRAPH_THUMBNAIL_READY, dispatcher.Anonymous)

                       # self.parent().signalWaitForFinishedLastPlot.set()
                       # print ("SignaSEt")
                  #  elif _sdata[0] == self.signals.GRAPH_STARTED:
                   #     logging.info('GRAPH_STARTED')
                   #    dispatcher.send(self.signals.GRAPH_STARTED,dispatcher.Any)

                    elif _sdata[0] == self.signals.GRAPH_ERROR:
                        logging.info('GRAPH_ERROR')
                        dispatcher.send(self.signals.GRAPH_ERROR, dispatcher.Anonymous, _sdata[1])

                    elif _sdata[0] == self.signals.GRAPH_STOPPED:
                        logging.info('GRAPH_STOPPED')
                        dispatcher.send(self.signals.GRAPH_STOPPED, dispatcher.Anonymous, _sdata[1])

                    elif _sdata[0] == self.signals.WB_GET_LINE:
                        dispatcher.send(self.signals.WB_GET_LINE, dispatcher.Anonymous, _sdata[1])
                        print('server_ WB_GET_LINE')

            except Exception as _err:
                logging.exception(_err)

