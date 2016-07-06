__author__ = 'HS'
# Standard test script for RF-Measurements
#


import configparser
import os
#from PyQt4.QtGui import QMessageBox
from JobTables import JobTable
from DB_Handler_TDS3 import *
#from DB_Handler_TLM3 import *
from DB_Handler_TPL3 import *
from NeedfullThings import Signal
from pydispatch import dispatcher
from Routing import Router
from Instruction import Instruction
import pickle
import importlib.machinery
import time
import threading
import logging
import LimitCheck
import numpy
import Measurement
#from Analyzer import SpectrumAnalyzer
#from DEV_ESI7_Drv import ESI7

""""
list of float to string:
    a = [1, 1.1,2,2.2,3,3.3,4,4.4]
    x= (",".join(map(str,a))) -> '1,1.1,2,2.2,3,3.3,4,4.4'
string to list of float
    x = '1,1.1,2,2.2,3,3.3,4,4.4'
    y = list(map(float,x.split(','))) ->  [1, 1.1,2,2.2,3,3.3,4,4.4]

dic to string
    a = {200: 10.2, 400: 5.5, 300: 20.4, 100: 30.1}
    x = str(a) -> '{200: 10.2, 300: 20.4, 400: 5.5, 100: 30.1}'
string to dic
    x = '{200: 10.2, 300: 20.4, 400: 5.5, 100: 30.1}'
    y = ast.literal_eval(x) -> {200: 10.2, 400: 5.5, 300: 20.4, 100: 30.1}
    or
    y = eval(x)
"""""

class RT_StandardHF(object):
    global globalStop
    eventWait = threading.Event()
    def __init__(self,parent = None):
        self.parent = parent
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.deviceList=[]
        self.spec_analyzer = 0 #device1
        self.device2 = 0
        self.device3 = 0
        self.signals = Signal()
        self.job_table = JobTable()
        self.workingDir = self.config['Pathes']['workingdir']
        self.activeTestPlan = os.path.join(self.workingDir,"ActiveTestPlan.TDS3")
        self.currentSetting = DatasetSetting
        self.activeAntenna = None
        self.activeCable = None
        self.activeProbe = None
        self.activeMatrix = None
        self.activeRoute = None
        self.activeRoutine = ""
        self.setRouteFlag = False
        self.startAutoRange = False
        self.autoRangeTrace1 = self.config['Const']['auto_range_trace1']
        self.limitCheck = LimitCheck.LimitCheck()
        self.stopExecution =  False
        self.corIDs = []
      #  print('init RT_StandardHF')
        pass
        dispatcher.connect(self.onStop, self.signals.MEAS_STOP, dispatcher.Any)

#    def __enter__(self):
#        return self
    def onStop(self):
        print('Stoop')
        self.stopExecution = True

    def __exit__(self, type, value, traceback):
        print(type, value, traceback)
        return 1

    def startRoutine(self, ds_routine, job_table):

        self.deviceList = list(ds_routine.device1.split(','))
        self.job_table = job_table
        assert isinstance(ds_routine,DatasetRoutine)
        _ds_routine = ds_routine
        self.activeRoutine = ds_routine.title
        #operator-instructions
        if (_ds_routine.instruction != ""):
            # show instructions text
            pass

        _loaded = False
        for d in self.deviceList:
            _ret = self.loadDriver(d)
            if _ret:
                _loaded = True
                break


        if not _loaded:
            return False

        _ret = self.parser

        return _ret
    def loadDriver(self,device):
        _error_text = "error load DeviceDriver"
        #Test Device 1 (always Spectrum Analyser)
        try:
            #export Driver-Script to WorkingDir
            _module_name = device
            _module_path =os.path.abspath(os.path.join(self.workingDir,_module_name)+".py")

            #---for comfortable development
            _ret = self.config['Development']['development']
            if (self.config['Development']['development'] == '1'):
                _module_name = self.config['Development']['modulname_devicedriver']
                _module_path = self.config['Development']['modulpath_devicedriver']

            _error_text = "error load DeviceDriver {0} {1}".format(str(_module_name),str(_module_path))

            _loader = importlib.machinery.SourceFileLoader(_module_name,_module_path)
            _py_mod = _loader.load_module()
            _py_mod_class = getattr(_py_mod, _module_name)
            self.showMessage('Driver Module {0}, {1} loaded'.format(str(_module_name),str(_module_path)))
            self.spec_analyzer = _py_mod_class()

            #Test Spectrum Analyser' connection
            _error_text = "error checkConnection DeviceDriver {0}".format(str(_module_name))
            _ret = self.spec_analyzer.checkConnection()
            if (not _ret):
                self.showMessage(_error_text)
                return False
        except  Exception as _err:
            logging.exception(_err)
            self.showMessage(_error_text)
            return 0
            _text = "Connection DeviceDriver {0} established ".format(str(_module_name))
            self.showMessage(_text)

        return True

    @property
    def parser(self):
        self.startOfRoutine()
        _error_text='error in Measurement parser '
        _ret = self.job_table.getJob()
        try:
            while (_ret != 0):
                self.parent.signalPause.wait()
                if self.stopExecution:
                    self.showMessage('Measurement stopped')
                    self.eventWait.wait()

                if (self.job_table.Name == "Plot"):
                    # close current Measurement and go back to main parser
                    self.job_table.replaceJob()
                    self.endOfPlot()
                    return 1

                if (self.job_table.Name == "Routine"):
                    # close current Measurement and go back to main parser
                    self.job_table.replaceJob()
                    self.endOfRoutine()
                    return 1

                if (self.job_table.Name == "Line"):
                    self.startOfLine()
                    _error_text='can not start Line {0}'.format(str(self.job_table.Title))
                    self.showMessage('process Line {0}'.format(str(self.job_table.Title)))
                    self.sendItemActive(self.job_table.TreeItem)
                    _ds_line = DatasetLine(self.activeTestPlan, self.job_table.DBIdx)
                    _ret = _ds_line.read()
                    if (_ret == 0):
                        return 0
                    self.sendItemComplete(self.job_table.TreeItem)
                    self.endOfLine()

                if (self.job_table.Name == "Limit"):
                    self.startOfLimit()
                    _error_text='can not start Limit {0}'.format(str(self.job_table.Title))
                    self.showMessage('process Limit {0}'.format(str(self.job_table.Title)))
                    self.sendItemActive(self.job_table.TreeItem)
                    _limit = self.job_table.Object
                    print('M: new limit')
                    dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _limit)
                    self.sendItemComplete(self.job_table.TreeItem)
                    #time.sleep(1)
                    self.limitCheck.addLimit(_limit)
                    self.endOfLimit()

                if (self.job_table.Name == "Setting"):
                    self.startOfSetting()
                    _error_text='can not start Setting {0}'.format(str(self.job_table.Title))
                    self.showMessage('process Setting {0}'.format(str(self.job_table.Title)))
                    self.sendItemActive(self.job_table.TreeItem)
                    _setting_treeItem = self.job_table.TreeItem
                    _setting_DBIdx = self.job_table.DBIdx

                    _error_text='can not start Setting {0}'.format(str(_setting_DBIdx))
                    if self.startSetting(_setting_DBIdx) == False:
                        self.eventWait.wait()
                        return False
                    self.sendItemComplete(_setting_treeItem)
                    self.endOfSetting()


                    # first handle route (should be done before activating any inputs)
#                    _ret = self.job_table.getJob()
#                    self.setRouteF = False
 #                   while _ret != 0:

                if (self.job_table.Name == "Route"):
                    _error_text='can not start Route {0}'.format(str(self.job_table.Title))
                    self.showMessage('process Route {0}'.format(str(self.job_table.Title)))
                    self.sendItemActive(self.job_table.TreeItem)
                    self.activeRoute = self.job_table.Object
                    self.setRouteFlag = True
                    print ("setRouteF",self.setRouteFlag)
                    self.sendItemComplete(self.job_table.TreeItem)

                if (self.job_table.Name == "Antenna"):
                    if self.setRouteFlag:
                        _error_text='can not start Antenna {0}'.format(str(self.job_table.Title))
                        self.showMessage('process Antenna {0}'.format(str(self.job_table.Title)))
                        self.activeAntenna = self.job_table.Object

                if (self.job_table.Name == "Cable"):
                    if self.setRouteFlag:
                        _error_text='can not start Cable {0}'.format(str(self.job_table.Title))
                        self.showMessage('process Cable {0}'.format(str(self.job_table.Title)))
                        self.activeCable = self.job_table.Object
                if (self.job_table.Name == "Probe"):
                    if self.setRouteFlag:
                        _error_text='can not start Probe {0}'.format(str(self.job_table.Title))
                        self.showMessage('process Probe {0}'.format(str(self.job_table.Title)))
                        self.activeProbe = self.job_table.Object

                if (self.job_table.Name == "Matrix"):
                    if self.setRouteFlag:
                        _error_text='can not start Matrix {0}'.format(str(self.job_table.Title))
                        self.showMessage('process Matrix {0}'.format(str(self.job_table.Title)))
                        self.activeMatrix = self.job_table.Object

                #        else: break
                #        _ret = self.job_table.getJob()


                if (self.job_table.Name == "Trace"):
                    print ("Trace setRouteF",self.setRouteFlag)
                    if self.setRouteFlag:
                        self.startRoute()
                        self.setRouteFlag = False

                    self.startOfTrace()
                    _error_text='can not start Trace {0}'.format(str(self.job_table.Title))
                    self.showMessage('process Trace {0}'.format(str(self.job_table.Title)))
                    self.sendItemActive(self.job_table.TreeItem)
                    if self.startTrace(self.job_table.DBIdx) == False:
                        print('err')
                        return False

                    self.sendItemComplete(self.job_table.TreeItem)
                    self.endOfTrace()

                _ret = self.job_table.getJob()

        except Exception as _err:
            print (_err)
            self.showMessage(_error_text)
            logging.exception(_err)
            return 0

        self.job_table.replaceJob()
        self.endOfPlot()
        return 1

    def start(self):

        pass

    def startSetting(self,id):
        print('M: Setting {0}'.format(str(id)))
        self.currentSetting = DatasetSetting(self.activeTestPlan, id)
        self.currentSetting.read()
        self.startAutoRange = False
        if self.currentSetting.autorange:
            self.startAutoRange = True

        if not self.currentSetting.instruction == None:
            print("i = ",self.currentSetting.instruction)
            self.parent.onShowInstruction(self.currentSetting.instruction)
          # instr = Instruction(self.currentSetting.instruction,self)
          #  instr.exec_()
          #
          #   instr.close()
            # show instructions text
            pass

        #open resource
        self.spec_analyzer.checkConnection()
        #set all parameters given by command_list
        if self.currentSetting.step == True:
            self.spec_analyzer.stepMode = True
        self.spec_analyzer.setup()
        try:
            for row in self.currentSetting.command_list:
                _func = getattr(self.spec_analyzer, row.command)
                _error_text = 'can not set command {0}'.format(str(_func))
                _ret = _func(row.parameter)
                if _ret == False:
                    return False
        except Exception as _err:
            _s = 'Fehler {0}'.format(str(_err))
            self.showMessage(_s)
            logging.exception(_err)
            return False

        self.spec_analyzer.closeSession()

    def startRoute(self):
    #    self.spec_analyzer.checkConnection()
    #    self.spec_analyzer.checkConnection()
        print('routing')
        self.corIDs.clear()
        _alias = self.currentSetting.route
        _ret = self.config['Route']['route_active']
        if _ret == 0:
            return True

        _router = Router()
        _router.cutFreqX1 = self.currentSetting.start_freq
        _router.cutFreqX2 = self.currentSetting.stop_freq

        _ret = _router.setRoute(self.spec_analyzer,_alias,self.activeAntenna,self.activeCable,
                                self.activeProbe,self.activeMatrix)
        if _ret == False:
            self.showMessage("could not set route")
            return False

        # _ant,_cab,_probe are modified copies of original lines, data range is limited to trace range
        if self.activeAntenna != None:
            _ant = self.activeAntenna
            _data = ast.literal_eval(_ant.data_xy)
            _sdata = sorted(_data,key = lambda x: x[0])
            _cutdata = _router.cutRange(_sdata)
            _ant.data_xy = str(_cutdata)
            _ant.masterID = _ant.line_id
            self.corIDs.append(_ant.line_id)
           # _ant.cutfreqA = self.currentSetting.start_freq
           # _ant.cutfreqB = self.currentSetting.stop_freq
            dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _ant)
        if self.activeCable != None:
            _cab = self.activeCable
            _data = ast.literal_eval(_cab.data_xy)
            _sdata = sorted(_data,key = lambda x: x[0])
            _cutdata = _router.cutRange(_sdata)
            _cab.data_xy = str(_cutdata)
            _cab.masterID = _cab.line_id
            self.corIDs.append(_cab.line_id)
            #_cab.cutfreqA = self.currentSetting.start_freq
            #_cab.cutfreqB = self.currentSetting.stop_freq
            dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _cab)
        if self.activeProbe != None:
            _prb = self.activeProbe
            _data = ast.literal_eval(_prb.data_xy)
            _sdata = sorted(_data,key = lambda x: x[0])
            _cutdata = _router.cutRange(_sdata)
            _prb.data_xy = str(_cutdata)
            _prb.masterID = _prb.line_id
            self.corIDs.append(_prb.line_id)
            #_prb.cutfreqA = self.currentSetting.start_freq
            #_prb.cutfreqB = self.currentSetting.stop_freq
            dispatcher.send(self.signals.GRAPH_NEW_LINE, dispatcher.Anonymous, _prb)

        #reset route for next setting
        self.activeAntenna = None
        self.activeCable = None
        self.activeProbe = None
        self.activeMatrix = None
        self.activeRoute = None
        #Instruction-File
        #Instruction-Text


        self.spec_analyzer.closeSession()
        return True

    def startTrace(self,id):
        _maxPeak = ''
        _values = ''

        try:
            self.spec_analyzer.checkConnection()
            _ds = DatasetTrace(self.activeTestPlan, id)
            _ds.read()
            #step mode or sweep mode ?
            if self.currentSetting.step:
                if self.startAutoRange:
                    #start AutoRange

                    #only first Trace ?
                    if self.autoRangeTrace1:
                        self.startAutoRange = False
                    pass
                _stepWidth = self.currentSetting.step_width
                _stepTime = self.currentSetting.step_time
                _currentFreq = _ds.start_freq

                # ZeroSpan Mode
                _func = getattr(self.spec_analyzer,'set_ZeroSpan')
                if _func() == 0: return False

                _funcCenterFreq = getattr(self.spec_analyzer,'set_CenterFreq')
                _funcMarkerPeak = getattr(self.spec_analyzer,'get_MaxPeak')
                while (_currentFreq <= _ds.stop_freq):
                    if _funcCenterFreq(_currentFreq) == 0: return False
                    time.sleep(_stepTime)
                    if (_funcMarkerPeak(_maxPeak) == 0): return False
                    _currentFreq += _stepWidth
                pass
            else:
                _func = getattr(self.spec_analyzer,'set_StartFreq')
                if _func(_ds.start_freq) == 0: return False

                _func = getattr(self.spec_analyzer,'set_StopFreq')
                if _func(_ds.stop_freq) == 0: return False

                if self.startAutoRange:
                    _func = getattr(self.spec_analyzer,'autoRange')
                    _ret, amp, att =  _func()
                    print(_ret,amp,att)
                    if not _ret: return False

                _funcTimeout = getattr(self.spec_analyzer,'set_TimeOut')
                _msTimeout = self.currentSetting.step_time * 1000 + 1000
                if not _funcTimeout(_msTimeout): return False

                _func = getattr(self.spec_analyzer,'take_Sweep')
                if not _func(self.currentSetting.step_time):
                    return False

                _func = getattr(self.spec_analyzer,'get_Trace')
                _ret =_func(1)

                if not _ret[0]: return False
                if not _funcTimeout(2000): return False
                _floatResults = list(map(float,_ret[1].split(',')))
                #_result = [_ds.start_freq, _ds.stop_freq, _floatResults]
                #print(_result)
                new_trace = Tpl3Traces("",0)
                new_trace.tdsID = _ds.id_trace
                new_trace.x1 = _ds.start_freq
                new_trace.x2 = _ds.stop_freq
                new_trace.y1 = 0.0
                new_trace.y2 = 0.0
                new_trace.color = ""
                new_trace.data_y = _floatResults
                _func = getattr(self.spec_analyzer,'get_PreAmplifier')
                new_trace.amplifier = _func()
                _func = getattr(self.spec_analyzer,'get_Attenuator')
                new_trace.attenuator = _func()
                _func = getattr(self.spec_analyzer,'get_ResBW')
                new_trace.rbw = _func()
                new_trace.autorange =  self.startAutoRange
                print (new_trace.autorange,self.startAutoRange)
                _func = getattr(self.spec_analyzer,'get_HF_Overload')
                new_trace.hf_overload = _func()
                _func = getattr(self.spec_analyzer,'get_IF_Overload')
                new_trace.if_overload = _func()
                _func = getattr(self.spec_analyzer,'get_Uncal')
                new_trace.uncal = _func()
                new_trace.data_xy_mode = 'Sweep'
                new_trace.routine = self.activeRoutine
                new_trace.corIDs = self.corIDs
                dispatcher.send(self.signals.GRAPH_NEW_TRACE, dispatcher.Anonymous, new_trace)
                if type(new_trace.data_y) == str:
                    _y = eval(new_trace.data_y)
                else:
                    _y = numpy.array(new_trace.data_y)
               # _stepFreq = (_ds.stop_freq - _ds.start_freq)/len(_y)
                _x = numpy.linspace(_ds.start_freq,_ds.stop_freq,len(_y))
                self.limitCheck.testLimit(list(zip(_x,_y)))

                pass
        except Exception as _err:
            self.showMessage(str(_err))
            logging.exception(_err)
            return False

        self.spec_analyzer.closeSession()
        return True
        pass

    def cutRange(self,data_xy,startFreq,stopFreq):
        _xyf = eval(data_xy)
        _xys = sorted(_xyf)
        _list = []


        _first = 0
        for x in _xys:
            if x[0] > startFreq: break
            _first = x

        _last = 0
        for x in _xys:
            _last = x
            if x[0] > stopFreq: break


        _inc = False
        for x in _xys:
            if x == _first:
                _inc = True
            if x == _last:
                _list.append(x)
                _inc = False
            if _inc:
                _list.append(x)


        return str(_list)

    def getLimitList(self):
        return self.limitCheck.getList()

    def showMessage(self,text):
        sdata = pickle.dumps(text)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)

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

    def startOfRoutine(self):
        pass
    def endOfRoutine(self):
        pass
    def startOfLine(self):
        pass
    def endOfLine(self):
        pass
    def startOfLimit(self):
        pass
    def endOfLimit(self):
        pass
    def startOfSetting(self):
        pass
    def endOfSetting(self):
        pass
    def startOfTrace(self):
        pass
    def endOfTrace(self):
        pass
    def startOfPlot(self):
        pass
    def endOfPlot(self):
        pass

