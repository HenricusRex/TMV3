import logging
import visa
from PyQt4.QtGui import QMessageBox
from pydispatch import dispatcher
import pickle
from NeedfullThings import Signal
import time
from datetime import datetime
import logging
logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')

class Relais():
    def __init__(self,device_name):
        self.name = device_name
        self.rl = 0
        self.signals = Signal()
        self.devConnectionsString = ""
        self.rm = visa.ResourceManager()

        pass

    def checkStatusCode(self,status):
        if str(status).startswith('error') or str(status).startswith('warning'):
            return False
        else:
            return True

    def checkConnection(self):
        #Test given connection
        try:
            self.rl = self.rm.open_resource(self.name)
            self.rl.clear()
            #self.sa.open()
          # _ret = self.rl.query("*IDN?")
        except visa.VisaIOError as _err:
            _msg = visa.Error(_err)
            self.showMessage(_msg)
            logging.exception(_msg)
            return False
        return True

    def write(self,command):
            self.rl.write(command)
            self.rl.close()

    def showMessage(self,text):
        s = str(text).replace('\r','')
        s = s.replace('\n','')
        sdata = pickle.dumps(s)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)
