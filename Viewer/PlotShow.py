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
from DB_Handler_TPL3 import Tpl3Plot,Tpl3Traces,Tpl3Lines
from JobTables import JobTable
from Filter import Filter
from Session import Session
from GraphViewer import GraphViewer

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



class PlotShow(QtGui.QDialog):
    signalGraphUpdate = QtCore.pyqtSignal()

    def __init__(self,List1,List2):
        QtGui.QWidget.__init__(self)
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.ui = uic.loadUi("PlotShow.ui", self)
        self.setWindowFlags(self.windowFlags() |
                                      QtCore.Qt.WindowSystemMenuHint |
                                      QtCore.Qt.WindowMaximizeButtonHint)
    #   self.window().showFullScreen()
        self.workBenchDB = self.config['DataBases']['workbench']
    #    self.figure_canvas = FigureCanvas(Figure())

        self.ui.Btn11.clicked.connect(self.onBtn11)
        self.ui.Btn12.clicked.connect(self.onBtn12)
        self.ui.Btn21.clicked.connect(self.onBtn21)
        self.ui.Btn22.clicked.connect(self.onBtn22)
        self.ui.BtnAddLimit.clicked.connect(self.onBtnAddLimit)
        self.ui.BtnSave.clicked.connect(self.onBtnSave)
        self.ui.BtnPrint.clicked.connect(self.onBtnPrint)
        self.ui.BtnPDF.clicked.connect(self.onBtnPDF)
        self.ui.BtnExit.clicked.connect(self.onBtnExit)
        self.ui.BtnV1.clicked.connect(self.onBtnV1)
        self.ui.BtnV2.clicked.connect(self.onBtnV2)

#        self.signalGraphUpdate.connect(self.onGraphUpdate)
    #    self.initGraph()

        dq = QtGui.QPixmap()
        if len(List1) > 0:
            List1.append([0,'None',dq])
            List1.append([0,'None',dq])
            List1.insert(0,[0,'None',dq])
            List1.insert(0,[0,'None',dq])
            self.ui.Btn11.setEnabled(True)
            self.ui.Btn12.setEnabled(True)
            self.plotList1 = List1
            self.pos1 = 5
            self.pos1ID = 0
            self.fillList1(5)
        else:
            self.ui.Btn11.setEnabled(False)
            self.ui.Btn12.setEnabled(False)

        if len(List2) > 0:
            List2.append([0,'None',dq])
            List2.append([0,'None',dq])
            List2.insert(0,[0,'None',dq])
            List2.insert(0,[0,'None',dq])
            self.ui.Btn21.setEnabled(True)
            self.ui.Btn22.setEnabled(True)
            self.plotList2 = List2
            self.pos2 = 5
            self.pos2ID = 0
            self.fillList2(5)
        else:
            self.ui.Btn21.setEnabled(False)
            self.ui.Btn22.setEnabled(False)

        self.ui.BtnAddLimit.setEnabled(False)
        self.ui.BtnPDF.setEnabled(True)

        self.ui.BtnAddLimit.setEnabled(False)
        self.ui.BtnSave.setEnabled(True)
        self.ui.BtnPrint.setEnabled(True)
        self.ui.BtnPDF.setEnabled(True)
        self.ui.BtnExit.clicked.connect(self.onBtnExit)
        self.graphViewer = GraphViewer(self)


    def onBtnV1(self):
        self.ui.BtnV1.enabled = False
        plot = Tpl3Plot(self.workBenchDB,self.pos1ID)
        data = plot.read()
        self.graphViewer.clear()
        self.graphViewer.genPlotPage()
        self.graphViewer.onShowPlot(plot,self.getPlotCorrIDs(self.pos1ID),False)
        self.ui.BtnV1.enabled = True

    #    graphViewer.show()
       # graphViewer.exec()

        #self.onShowPlot(self.pos1ID)

    def onBtnV2(self):

        plot = Tpl3Plot(self.workBenchDB,self.pos2ID)
        data = plot.read()

        self.graphViewer.onShowPlot(plot,self.getPlotCorrIDs(self.pos2ID),False)
        print('onLabel13')

    def onBtnAddLimit(self):
        QtGui.QMessageBox.information(self, 'TMV3', 'not yet installed', QtGui.QMessageBox.Ok)
    def onBtnSave(self):
        QtGui.QMessageBox.information(self, 'TMV3', 'not yet installed', QtGui.QMessageBox.Ok)

    def onBtnPrint(self):
        self.graphViewer.onPrint()

    def onBtnPDF(self):
        self.graphViewer.onPdf()

    def onBtnExit(self):
        self.close()

    def onBtn11(self):
        if self.pos1 < len(self.plotList1):
            self.pos1 += 1
            self.fillList1(self.pos1)

    def onBtn12(self):
        if self.pos1 > 5:
            self.pos1 -= 1
            self.fillList1(self.pos1)
        pass

    def onBtn21(self):
        if self.pos2 < len(self.plotList2):
            self.pos2 += 1
            self.fillList2(self.pos2)
        pass

    def onBtn22(self):
        if self.pos2 > 5:
            self.pos2 -= 1
            self.fillList2(self.pos2)
        pass

    def fillList1(self,pos):
        d = self.plotList1[pos-5]
        self.ui.label11.setText(str(d[0])+' :'+d[1])
        self.ui.label11V.setPixmap(d[2])
        d = self.plotList1[pos-4]
        self.ui.label12.setText(d[1])
        self.ui.label12V.setPixmap(d[2])
        d = self.plotList1[pos-3]
        self.pos1ID = d[0]
        self.ui.label13.setText(str(d[0])+':'+d[1])
        self.ui.BtnV1.setIcon(QtGui.QIcon(d[2]))
        d = self.plotList1[pos-2]
        self.ui.label14.setText(d[1])
        self.ui.label14V.setPixmap(d[2])
        d = self.plotList1[pos-1]
        self.ui.label15.setText(d[1])
        self.ui.label15V.setPixmap(d[2])

    def fillList2(self,pos):
        d = self.plotList2[pos-5]
        self.ui.label21.setText(d[1])
        self.ui.label21V.setPixmap(d[2])
        d = self.plotList2[pos-4]
        self.ui.label22.setText(d[1])
        self.ui.label22V.setPixmap(d[2])
        d = self.plotList2[pos-3]
        self.pos2ID = d[0]
        self.ui.label23.setText(d[1])
        self.ui.BtnV2.setIcon(QtGui.QIcon(d[2]))
        d = self.plotList2[pos-2]
        self.ui.label24.setText(d[1])
        self.ui.label24V.setPixmap(d[2])
        d = self.plotList2[pos-1]
        self.ui.label25.setText(d[1])
        self.ui.label25V.setPixmap(d[2])

    def getPlotCorrIDs(self,plotID):
        corrIDList = []
        corrList = []
        trace = Tpl3Traces(self.workBenchDB,0)
        ret = trace.readCorrIDs(plotID)
        try:
            if ret != None:
                for x in ret:
                    for y in x:
                        if not y is None:
                            yi = eval(y)
                            for z in yi :
                                if z not in corrIDList:
                                    corrIDList.append(z)
                for i in corrIDList:
                    line = Tpl3Lines(self.workBenchDB, i)
                    line.read()
                    corrList.append((i, line))
        except Exception as _err:
                 print("Graph: onNewLine: {0}".format(str(_err)))
                 logging.exception(_err)


        return corrList

    def onBtnPrint(self):
        self.graphViewer.onPrint()
        pass
