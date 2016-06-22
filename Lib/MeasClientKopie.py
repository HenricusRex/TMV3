""" 

"""

from PyQt4 import uic, QtGui, QtCore
import socket
import threading
import pickle
import time
from NeedfullThings import Signal
from pydispatch import dispatcher



class SocketClientThread(threading.Thread):
    def __init__(self,client):
        super(SocketClientThread, self).__init__()
        self.alive = threading.Event()
        self.alive.set()
        self.client = client
        self.signals=Signal()


    def run(self):
        #reading
        self.client.settimeout(1)
        while self.alive.isSet():
            try:
                data = self.client.recv(8192)
                print('.')
                if( None != data ):
                    sdata = pickle.loads(data)
                    print (sdata)
                    if sdata[0] == self.signals.MEAS_STOP:
                       # self.signalMeasStop.emit()
                        dispatcher.send(self.signals.MEAS_STOP,dispatcher.Anonymous)
                    if sdata[0] == self.signals.JOB_TABLE:
                      #  print("jobTable")
                        dispatcher.send(self.signals.JOB_TABLE,dispatcher.Anonymous)
                        #self.signalJobTable.emit()
                    if sdata[0] == self.signals.MEAS_PAUSE:
                        dispatcher.send(self.signals.MEAS_PAUSE,dispatcher.Anonymous)
                        #self.signalMeasPause.emit()
                        pass
                    if sdata[0] == self.signals.MEAS_GOON:
                        print("Signal MEA_GOON")

                        #dispatcher.send(self.signals.MEAS_GOON,dispatcher.Anonymous)

                        #self.signalMeasPause.emit()
                        pass
                else:
                    sdata = pickle.dumps(data)
                   # print(sdata)
            except IOError as e:
               # print ("Client Socketerror %s" % e)
                pass

    def stop(self, timeout=None):
        self.alive.clear()


class SocketClient():

    def __init__(self):
        self.Client = None
        self.ClientThread = None
        self.sig = Signal()
        x = self.pa



    def start(self,Host,Port):
        myHost=Host
        myPort=Port
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((myHost,myPort))
            self.ClientThread = SocketClientThread(self.socket)

            dispatcher.connect(self.onJobComplete, self.sig.JOB_COMPLETE, dispatcher.Any)
            dispatcher.connect(self.onItemComplete, self.sig.ITEM_COMPLETE, dispatcher.Any)
            dispatcher.connect(self.onItemActive, self.sig.ITEM_ACTIVE, dispatcher.Any)
            dispatcher.connect(self.onGraphNewPlot, self.sig.GRAPH_NEW_PLOT, dispatcher.Any)
            dispatcher.connect(self.onGraphNewLine, self.sig.GRAPH_NEW_LINE, dispatcher.Any)
            dispatcher.connect(self.onGraphNewTrace, self.sig.GRAPH_NEW_TRACE, dispatcher.Any)
            dispatcher.connect(self.onPlotComplete, self.sig.MEAS_PLOT_COMPLETE, dispatcher.Any)
            dispatcher.connect(self.onResult,self.sig.MEAS_RESULT,dispatcher.Any)

  #          dispatcher.connect(self.sendMeasStop, self.sig.MEAS_STOP, dispatcher.Any)
  #          dispatcher.connect(self.sendMeasPause, self.sig.MEAS_STOP, dispatcher.Any)
 #           dispatcher.connect(self.sendJobTable, self.sig.JOB_TABLE, dispatcher.Any)

            self.ClientThread.start()
            Kommando = []
            Kommando.append(self.sig.MEAS_STARTED)
            self.send(Kommando)
            return (True)
        except IOError as e:
            print ("Connect Error %s" %e)
            return (False)

    def sendJobTable(self):
        dispatcher.send(self.sig.JOB_TABLE)

    def sendMeasStop(self):
        dispatcher.send(self.sig.MEAS_STOP)

    def sendMeasPause(self):
        dispatcher.send(self.sig.MEAS_PAUSE)

    def onPlotComplete(self):
        _sData = []
        _sData.append(self.sig.MEAS_PLOT_COMPLETE)
        self.send(_sData)

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

    def stop(self):
        try:
            self.socket.close()
            self.ClientThread.stop()

        except Exception as err:
            print ("Exception caught: %s Closing..." % err)

        return(True)

    def send(self,data):

        try:
            _serialized_data = pickle.dumps(data)
            #print ('MC: {0}'.format(str(len(_serialized_data))))
            self.socket.sendall(_serialized_data)
            time.sleep(0.5)
        except IOError as e:
            print ("Send-Error %s" %e)

