# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:42:08 2013

@author: HS
"""
import threading
#import os.path

import os.path
import configparser
import time
import importlib.machinery
from PyQt4 import uic, QtGui , QtCore
from MeasClient import *
from NeedfullThings import Signal
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import Tpl3Plot
from JobTables import JobTable




logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')
logging.raiseExceptions = False


class MainForm(QtGui.QMainWindow):
    signalShowMessage = QtCore.pyqtSignal(str)
    signalWait = threading.Event()
    signalErrorEnd = threading.Event()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.ui = uic.loadUi("Measurement.ui", self)
        self.workingDir = self.config['Pathes']['workingdir']
        self.activeTestPlan = os.path.join(self.workingDir,"ActiveTestPlan.TDS3")
        self.job_table = JobTable()
        self.client = Client(self)
        self.item = None
        self.signals = Signal()
        self.hwd = self
        self.deviceList = []

        self.pa = threading.Thread(name = "Parser",target = self.parser)
        #self.client.sendMeasStarted()
        #Messages
        dispatcher.connect(self.onShowMessageA, self.signals.SHOW_MESSAGE, dispatcher.Any)
        self.signalShowMessage.connect(self.onShowMessageB)

      #  dispatcher.connect(self.onStop, self.signals.MEAS_STOP, dispatcher.Any)
        dispatcher.connect(self.onPause, self.signals.MEAS_PAUSE, dispatcher.Any)
        dispatcher.connect(self.onStartJob, self.signals.JOB_TABLE, dispatcher.Any)
        dispatcher.connect(self.onNextJob, self.signals.JOB_NEXT, dispatcher.Any)
        dispatcher.connect(self.onStartJob, self.signals.JOB_START, dispatcher.Any)
        dispatcher.connect(self.onGoOn, self.signals.MEAS_GOON, dispatcher.Any)
        logging.info('TMV3 Measurement started')

        _job_table_path = os.path.join(self.workingDir,"JobTable.TJT3")

        self.addItem("Measurement Socket started, waiting for JobTable")
        #
        # else:
        #     if os.path.isfile(_job_table_path):
        #         self.addItem("Measurement Socket NOT started, trying to read JobTable from File")
        #         ret = QMessageBox.information(self, 'TMV3',
        #                                       "Start Measurement from JobTable-File ?",
        #                                       QMessageBox.Yes | QMessageBox.No)
        #
        #         if ret == QMessageBox.Yes:
        #             # print(jobTablePath)
        #             # with open(jobTablePath,"rb") as f:
        #             # self.jobTable = pickle.load(f)
        #
        #             dispatcher.send(self.signals.JOB_START,dispatcher.Anonymous)
        #         else:
        #             exit(0)
        #
        #             # wort = "default_measurement"
        #             # a = __import__(wort)
        #             # b = a.DefaultMeasurement()

    def onShowMessageB(self, text):
        self.addItem(text)
        pass

    def onShowMessageA(self, data):
        text = pickle.loads(data)
        #Message from foreign thread => access gui via qt-signal
        self.signalShowMessage.emit(text)
        pass

    def addItem(self, Text):
        try:
            self.item = QtGui.QListWidgetItem(Text)
            self.ui.listWidget.addItem(self.item)
            self.ui.listWidget.scrollToBottom()
        except Exception as _err:
            print ('Fehler')
            print (_err)

    def onStartJob(self):
        #Message from foreign thread => access gui via qt-signal
        _ret = self.job_table.getJob()
        _s = ("Starting JobTable" )
        self.signalShowMessage.emit(_s)
        if (_ret != 0):
            self.pa._stop()
            self.pa.start()
           # if (self.parser() == 0):
            #    print('JobComplete 1')
               # dispatcher.send(self.signals.JOB_COMPLETE, dispatcher.Anonymous)

           #     return 0
        pass

    def onNextJob(self):
#        _ret = self.job_table.getJob()
#        if (_ret != 0):
#            self.pa._stop()
#            self.pa.start()
#         #   if (self.parser() == 0):
#         #       return 0
#        else:
#            pass
#        #    dispatcher.send(self.signals.JOB_COMPLETE, dispatcher.Anonymous)
        pass

    def onPause(self):
        self.addItem("Signal from Controller: Measurement paused")
        pass

    def onStop(self):
        self.pa._stop()
        self.signalErrorEnd.wait()

        self.addItem("Signal from Controller: Measurement stop")
        ret = self.Client.stop()
        self.ui.close()
        exit()

    def onGoOn(self):
        print("set WaitSignal")
        self.signalWait.set()

    def parser(self):

        _ret = 1
        while (_ret != 0):
            if (self.job_table.Name == "Plot"):
                _ds_plan = DatasetPlan(self.activeTestPlan)
                _ds_plot = DatasetPlot(self.activeTestPlan, self.job_table.DBIdx)
                if (_ds_plot.read() == 0): return False
                new_plot = Tpl3Plot("", 0)
                new_plot.plot_title = _ds_plot.title
                new_plot.plan_title = _ds_plan.title
                new_plot.x1 = _ds_plot.x1
                new_plot.x2 = _ds_plot.x2
                new_plot.y1 = _ds_plot.y1
                new_plot.y2 = _ds_plot.y2
                new_plot.log =_ds_plot.log
                new_plot.unit = _ds_plot.unit
                new_plot.lines = ""
                new_plot.routines = ""
                new_plot.annotations = _ds_plot.annotation

                dispatcher.send(self.signals.GRAPH_NEW_PLOT, dispatcher.Anonymous, new_plot)

                self.sendItemComplete(self.job_table.TreeItem)
                pass

            _ret = 1
            if (self.job_table.Name == "Routine"):
                self.addItem('process Routine {0}'.format(str(self.job_table.Title)))
                _error_text = 'can not read Routine '
                _module_path = ''
                try:
                    #read requested Routine from TestPlan
                    _ds_routine = DatasetRoutine(self.activeTestPlan, self.job_table.DBIdx)
                    if (_ds_routine.read() == 0):
                        return 0
                    _module_name = _ds_routine.title
                    _module_path = os.path.abspath(os.path.join(self.workingDir,_module_name)+".py")
                    _ds_files = DatasetFile(self.activeTestPlan,0)

                    #export Routine-Script to WorkingDir
                    _ret = _ds_files.export(_module_name,'Routine',_module_path)
                    if (_ret == 0):
                        _s = "can't export Routine" + _module_name + ' ' + _module_path
                        self.addItem(_s)
                        return 0
                    #
                    #---for comfortable development
                    if (self.config['Development']['development'] == '1'):
                        self.addItem('Development = True')
                        _module_name = self.config['Development']['modulname_routine']
                        _module_path = self.config['Development']['modulpath_routine']

                    _loader = importlib.machinery.SourceFileLoader(_module_name,_module_path)
                    _py_mod = _loader.load_module()
                    _py_mod_class = getattr(_py_mod, _module_name)
                    self.addItem('Routine Module {0}, {1} loaded'.format(str(_module_name),str(_module_path)))


                    self.deviceList = list(_ds_routine.device1.split(','))

                    for d in self.deviceList:
                        _error_text = 'can not read Driver '
                        _module_name = d
                        _module_path = os.path.abspath(os.path.join(self.workingDir,_module_name)+".py")

                        _ds_files = DatasetFile(self.activeTestPlan,0)
                        _ret = _ds_files.export(_module_name,'Driver',_module_path)
                        if (_ret == 0):
                            _s = "can't export Driver" + _module_name + ' ' + _module_path
                            self.addItem(_s)
                            return 0

                    self.sendItemComplete(self.job_table.TreeItem)
                    #start Routine
                    try:

                       _rt = _py_mod_class()
                       _ret = _rt.startRoutine(_ds_routine,self.job_table)
                       if (_ret == False):
                            print("wait for Error-End")
                            dispatcher.send(self.signals.MEAS_ERROR, dispatcher.Anonymous)
                            self.signalErrorEnd.wait()
                       print("send Meas Plot Complete")

                       dispatcher.send(self.signals.MEAS_PLOT_COMPLETE,dispatcher.Anonymous)
                       self.signalWait.clear()
                       self.signalWait.wait()
                    except Exception as _err:
                        print ('Measurement.py, 238',_err)
                        logging.exception(_err)

                except Exception as _err:
                    print('Measurement.py, 241',_err)
                    self.addItem(_error_text)
                    #QMessageBox.information(self, 'TMV3', _error_text, QMessageBox.Ok)
                    logging.exception(_err)
                    dispatcher.send(self.signals.MEAS_ERROR, dispatcher.Anonymous)
                    return 0
            _ret = self.job_table.getJob()

        dispatcher.send(self.signals.JOB_COMPLETE, dispatcher.Anonymous)
        return _ret

    def sendItemComplete(self,item):
        _sdata = []
        _sdata.append (self.signals.ITEM_COMPLETE)
        _sdata.append(item)
        dispatcher.send(self.signals.ITEM_COMPLETE,dispatcher.Anonymous,_sdata)
    def sendItemActive(self,item):
        _sdata = []
        _sdata.append (self.signals.ITEM_ACTIVE)
        _sdata.append(item)
        dispatcher.send(self.signals.ITEM_ACTIVE,dispatcher.Anonymous,_sdata)
def main():
    app = QtGui.QApplication(sys.argv)
    form = MainForm()
    form.move(0,750)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()



