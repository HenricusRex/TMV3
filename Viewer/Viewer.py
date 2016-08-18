# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:42:08 2013

@author: HS
"""
import threading
#import os.path

import os.path
import configparser
import importlib.machinery
from PyQt4 import uic, QtGui , QtCore
from MeasClient import *
from NeedfullThings import Signal
from DB_Handler_TDS3 import *
from DB_Handler_TPL3 import Tpl3Plot
from JobTables import JobTable
from Filter import Filter
from Session import Session

import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.ticker import EngFormatter

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')
logging.raiseExceptions = False

Ref, Cur, Both,  = 0,1,2


class MainForm(QtGui.QMainWindow):
    signalShowMessage = QtCore.pyqtSignal(str)
    signalGraphUpdate = QtCore.pyqtSignal()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.ui = uic.loadUi("Viewer.ui", self)
        self.workBenchDB = self.config['DataBases']['workbench']
        self.figure_canvasReference = FigureCanvas(Figure())
        self.figure_canvasCurrent = FigureCanvas(Figure())
        self.plotsRef = []
        self.plotsRefPos = 0
        self.plotsCur = []
        self.plotsCurPos = 0
        self.mode = -1

        self.defBackground = 0
        self.ui.BtnCurrent.setChecked(False)
        self.ui.BtnReference.setChecked(False)

        self.ui.BtnLoadPlotsRef.clicked.connect(self.onBtnLoadRef)
        self.ui.BtnLoadPlotsCur.clicked.connect(self.onBtnLoadCur)
        self.ui.BtnSum.clicked.connect(self.onBtnApply)
        self.ui.BtnDiff.clicked.connect(self.onBtnApply)
        self.ui.BtnPrint.clicked.connect(self.onBtnApply)
        self.ui.BtnEditor.clicked.connect(self.onBtnApply)
        self.ui.BtnReference.clicked.connect(self.onBtnRefCur)
        self.ui.BtnCurrent.clicked.connect(self.onBtnRefCur)
        self.ui.BtnFRwd.clicked.connect(self.onBtnFRwd)
        self.ui.BtnRwd.clicked.connect(self.onBtnRwd)
        self.ui.BtnFwd.clicked.connect(self.onBtnFwd)
        self.ui.BtnFFwd.clicked.connect(self.onBtnFFwd)

        self.signalGraphUpdate.connect(self.onGraphUpdate)

        self.ui.BtnReference.setStyleSheet("QPushButton {background-color: lightGray}"
                                           "QPushButton:checked {background-color: yellow}")
        self.ui.BtnCurrent.setStyleSheet("QPushButton {background-color: lightGray}"
                                           "QPushButton:checked {background-color: green}")

        self.initGraph()
      #  self.openSession()
    def onBtnFRwd(self):
        if self.mode == Ref:
            self.plotsRefPos = 0
            self.onShowPlot(self.plotsRef[0],Ref)
        if self.mode == Cur:
            self.plotsCurPos = 0
            self.onShowPlot(self.plotsCur[0],Cur)
        if self.mode == Both:
            self.plotsRefPos = 0
            self.plotsCurPos = 0
            self.onShowPlot(self.plotsRef[0],Ref)
            self.onShowPlot(self.plotsCur[0],Cur)
        pass
    def onBtnRwd(self):
        if self.mode == Ref:
            if self.plotsRefPos > 0:
                self.plotsRefPos -= 1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
        if self.mode == Cur:
            if self.plotsCurPos > 0:
                self.plotsCurPos -= 1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        if self.mode == Both:
            if self.plotsRefPos > 0:
                self.plotsRefPos -= 1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
            if self.plotsCurPos > 0:
                self.plotsCurPos -= 1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        pass
    def onBtnFwd(self):
        print ("FWD",self.mode)
        if self.mode == Ref:
            if self.plotsRefPos < len(self.plotsRef)-1:
                self.plotsRefPos += 1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
        if self.mode == Cur:
            if self.plotsCurPos < len(self.plotsCur)-1:
                self.plotsCurPos += 1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        if self.mode == Both:
            if self.plotsRefPos < len(self.plotsRef)-1:
                self.plotsRefPos += 1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
            if self.plotsCurPos < len(self.plotsCur)-1:
                self.plotsCurPos += 1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        pass
    def onBtnFFwd(self):
        if self.mode == Ref:
            self.plotsRefPos = len(self.plotsRef)-1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
        if self.mode == Cur:
            self.plotsCurPos = len(self.plotsCur)-1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        if self.mode == Both:
            self.plotsRefPos = len(self.plotsRef)-1
            self.onShowPlot(self.plotsRef[self.plotsRefPos],Ref)
            self.plotsCurPos = len(self.plotsCur)-1
            self.onShowPlot(self.plotsCur[self.plotsCurPos],Cur)
        pass
    def onBtnRefCur(self):
        if (self.ui.BtnCurrent.isChecked() and self.ui.BtnReference.isChecked()):
            self.mode = Both
            print (self.mode)
        elif (self.ui.BtnCurrent.isChecked() and not self.ui.BtnReference.isChecked()):
            self.mode = Cur
            print (self.mode)
        elif (not self.ui.BtnCurrent.isChecked() and self.ui.BtnReference.isChecked()):
            self.mode = Ref
            print (self.mode)
        else:
            self.mode = -1
            print (self.mode)
    def openSession(self):
        session = Session()
        session.exec()
        if session.ret:
            if session.new:
                self.onBtnLoadRef()
            else:
                print(session.sel)
    def onGraphUpdate(self):
        self.figure_canvas.draw()
    def onShowMessageB(self, text):
        self.addItem(text)
        pass

    def onShowMessageA(self, data):
        text = pickle.loads(data)
        #Message from foreign thread => access gui via qt-signal
        self.signalShowMessage.emit(text)
    def onBtnApply(self):
        pass
    def onBtnLoadRef(self):
        filter = Filter()
        filter.exec()
        if filter.ret:
            print(filter.sel)
            self.plotsRef = filter.sel


        pass
    def onBtnLoadCur(self):
        filter = Filter()
        filter.exec()
        if filter.ret:
            print(filter.sel)
            self.plotCur = filter.sel
        pass
    def onShowPlot(self, id, dest):
        print ("id, dest",id,dest)
        _Plot = Tpl3Plot(self.workBenchDB,id)
        if _Plot.read():
            self.onNewPlot(_Plot, dest)
            for _t in _Plot.traces:
                self.onNewTrace(_t, dest)

            #_lines = eval (data.lineObjects)
            for _line in _Plot.lineObjects:
                self.onNewLine(_line, dest)
            return True
        else:
            _err = "Error reading Plot {}".format(str(id))
            QtGui.QMessageBox.information(self, 'TMV3', _err, QtGui.QMessageBox.Ok)
            return False
    def onNewPlot(self, data, dest):
        if dest == Ref:
            self.axesR.set_xlim(data.x1,data.x2)
            self.axesR.set_ylim(data.y1,data.y2)
        if dest == Cur:
            self.axesC.set_xlim(data.x1,data.x2)
            self.axesC.set_ylim(data.y1,data.y2)
         #   self.signalShowTitle.emit(data.plot_title)
        self.signalGraphUpdate.emit()
        pass

    def onShowTitleRef(self,txt):
        #access to Gui only via signal
        self.setWindowTitle(txt)

    def onGraphUpdate(self):
        self.figure_canvasReference.draw()
        self.figure_canvasCurrent.draw()


    def onNewLine(self, data, dest):
        try:
          #  print ('Graph: new Line {0} {1} {2}'.format(data.type, str(data.line_id), str(len(data.data_xy))))
            _xyf = eval(data.data_xy)
          #  print(_xyf, type(_xyf))

            _xys = sorted(_xyf,key = lambda x: x[0])
            _x, _y = zip(*_xys)

            self.getDefaultLineStyle(data.type)
            _color = self.defaultColor
            _style = self.defaultStyle
            _width = self.defaultWidth
         #   print(data.color, data.style, data.width)
            if data.color == '': _color = self.defaultColor
            if data.style == '': style = self.defaultStyle
            if data.style == '0.0': _width = self.defaultWidth
            #if self.backgroundPlot == 'True':
            #    _color = 'grey'

            if dest == Ref:
                self.axesR.plot(_x, _y, picker=5, label=data.title, color=_color,ls=_style, lw=_width)
            else:
                self.axesC.plot(_x, _y, picker=5, label=data.title, color=_color,ls=_style, lw=_width)

            if data.type == "Limit":
                _yTextPos = _y[-1]
                _xTextPos = self.axes.get_xlim()[1]
                _text = ' ' + data.title
                if dest == Ref:
                    self.axesR.text(_xTextPos,_yTextPos,_text)
                else:
                    self.axesC.text(_xTextPos,_yTextPos,_text)
                pass
            #self.figure_canvas.draw()
            self.signalGraphUpdate.emit()
        except Exception as _err:
            print("Graph: onNewLine: {0}".format(str(_err)))
            logging.exception(_err)

    def onNewTrace(self, data, dest):
        print('GRAPH NewTrace')
        _x = []
        _y = []
        try:
            _startFreq = data.x1
            _stopFreq = data.x2
            if data.data_xy_mode == 'Sweep':
                if type(data.data_y) == str:
                    _y = eval(data.data_y)
                else:
                    _y = data.data_y
                _stepFreq = (_stopFreq - _startFreq)/len(_y)
                _x = numpy.arange(_startFreq,_stopFreq,_stepFreq)
            else:
                pass

            self.getDefaultLineStyle('Trace')
            if data.hf_overload == True or data.if_overload == True:
                self.getDefaultLineStyle('TraceOverload')
            if data.uncal == True:
                self.getDefaultLineStyle('TraceUncal')
            _color = self.defaultColor
            _style = self.defaultStyle
            _width = self.defaultWidth
         #   if self.backgroundPlot == 'True': _color = 'grey'
            if dest == Ref:
                self.axesR.plot(_x, _y, picker=5,color=_color, ls=_style, lw=_width)
            self.signalGraphUpdate.emit()
            pass
        except Exception as _err:
            print("Graph: onNewTrace: {0}".format(str(_err)))
            logging.exception(_err)
        pass

    def onResult(self,data):

        right = 0.9
        top = 0.9
        self.axes.text(right, top, data,
            horizontalalignment='right',
            verticalalignment='top',
            fontsize=20, color='red',
            transform=self.axes.transAxes)
        self.signalGraphUpdate.emit()

    def onNewAnnotation(self, data):
        print('GRAPH NewAnnotation')
        pass

    def onNewClassification(self, data):
        print('GRAPH NewClassification')
        pass

    def onNewDescription(self, data):
        print('GRAPH NewDescription')
        pass

    def onNewNumber(self, data):
        print('GRAPH NewNumber')
        pass

    def onPrint(self, data):
        print('GRAPH Print')
        pass

    def onStop(self, data):
        print('GRAPH Stop')
        self.Client.stop()
        pass

    def getDefaultLineStyle(self,type):
        if type == 'Limit':
            self.defaultColor = self.config['LineStyle']['limit_color']
            self.defaultStyle = self.config['LineStyle']['limit_style']
            self.defaultWidth = self.config['LineStyle']['limit_width']
        if type == 'Antenna':
            self.defaultColor = self.config['LineStyle']['antenna_color']
            self.defaultStyle = self.config['LineStyle']['antenna_style']
            self.defaultWidth = self.config['LineStyle']['antenna_width']
        if type == 'Cable':
            self.defaultColor = self.config['LineStyle']['cable_color']
            self.defaultStyle = self.config['LineStyle']['cable_style']
            self.defaultWidth = self.config['LineStyle']['cable_width']
        if type == 'Line':
            self.defaultColor = self.config['LineStyle']['line_color']
            self.defaultStyle = self.config['LineStyle']['line_style']
            self.defaultWidth = self.config['LineStyle']['line_width']
        if type == 'Trace':
            self.defaultColor = self.config['LineStyle']['trace_color']
            self.defaultStyle = self.config['LineStyle']['trace_style']
            self.defaultWidth = self.config['LineStyle']['trace_width']
        if type == 'TraceOverload':
            self.defaultColor = self.config['LineStyle']['trace_overload_color']
            self.defaultStyle = self.config['LineStyle']['trace_overload_style']
            self.defaultWidth = self.config['LineStyle']['trace_overload_width']
        if type == 'TraceUncal':
            self.defaultColor = self.config['LineStyle']['trace_uncal_color']
            self.defaultStyle = self.config['LineStyle']['trace_uncal_style']
            self.defaultWidth = self.config['LineStyle']['trace_uncal_width']
        if type == 'Analyse':
            self.defaultColor = self.config['LineStyle']['anaylse_color']
            self.defaultStyle = self.config['LineStyle']['anaylse_style']
            self.defaultWidth = self.config['LineStyle']['anaylse_width']
        pass

    def initGraph(self):
                # create a figure

        self.figure_canvasReference.setParent(self.ui.frame_3)
        layoutR = QtGui.QVBoxLayout()
        self.ui.frame_3.setLayout(layoutR)
        layoutR.addWidget(self.figure_canvasReference, 0)
        # and the axes for the figure
        self.axesR = self.figure_canvasReference.figure.add_subplot(111)
        self.axesR.set_ylabel('dBµV')
        self.axesR.set_xlabel('Hz')
        self.axesR.grid(True)
        self.axesR.set_xscale('log')
        formatterHZ = EngFormatter(unit = '',places=0)
        formatterDB = EngFormatter(unit = '',places=1)
        self.axesR.xaxis.set_major_formatter(formatterHZ)
        self.axesR.yaxis.set_major_formatter(formatterDB)
        self.axesR.xaxis.label.set_color('yellow')
        self.axesR.yaxis.label.set_color('yellow')
        self.axesR.title.set_color('yellow')
        self.axesR.title.set_text('Reference')
        self.figure_canvasReference.show()

        self.figure_canvasCurrent.setParent(self.ui.frame_4)
        layoutC = QtGui.QVBoxLayout()
        self.ui.frame_4.setLayout(layoutC)
        layoutC.addWidget(self.figure_canvasCurrent, 2)
        self.ui.frame_4.setLayout(layoutC)
        # and the axes for the figure
        self.axesC = self.figure_canvasCurrent.figure.add_subplot(111)
        self.axesC.set_ylabel('dBµV')
        self.axesC.set_xlabel('Hz')
        self.axesC.grid(True)
        self.axesC.set_xscale('log')
        formatterHZ = EngFormatter(unit = '',places=0)
        formatterDB = EngFormatter(unit = '',places=1)
        self.axesC.xaxis.set_major_formatter(formatterHZ)
        self.axesC.yaxis.set_major_formatter(formatterDB)
        self.axesC.xaxis.label.set_color('green')
        self.axesC.yaxis.label.set_color('green')
        self.axesC.title.set_color('green')
        self.axesC.title.set_text('Current')
        self.figure_canvasCurrent.show()

#        self.signalGraphUpdate.emit()
def main():
    app = QtGui.QApplication(sys.argv)

   # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) # setting the style
    sshFile = "../Templates/darkorange.css"
    form = MainForm()
    with open (sshFile,"r") as fh:
        app.setStyleSheet(fh.read())
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()



