__author__ = 'Heinz'


import sys
import shutil
import matplotlib

import math
import os
import ast
import copy
import uuid
import DB_Handler_TPL3
import Workbench
import matplotlib.ticker as ticker
import matplotlib.image as image
import matplotlib.pyplot as plt
import EngFormat
#from PIL import Image
import matplotlib.image as image
from GraphClient import *
from PyQt4.QtGui import *
import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import EngFormatter
from matplotlib.widgets import Cursor
from matplotlib.lines import Line2D
from NeedfullThings import *
from LineInfo import LineInfo
from Marker import MarkerText
from GraphClient import Client

from pydispatch import dispatcher

#process_name = 'Graph'

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')


#workarount for matplotlib bug if more than 1 axis
def figure_pick(self, mouseevent):
    for a in self.get_children():
        if not a.get_visible():
            continue
        a.pick(mouseevent)
matplotlib.figure.Figure.pick = figure_pick

def axes_pick(self, *args):
    if len(args)>1:
        raise DeprecationWarning('New pick API implemented -- '
                                 'see API_CHANGES in the src distribution')
    mouseevent = args[0]
    if not self.in_axes(mouseevent):
        return
    for a in self.get_children():
        if not a.get_visible():
            continue
        a.pick(mouseevent)
matplotlib.axes.Axes.pick = axes_pick

class Marker(object):
    def __init__(self, ax,parent):
        self.ax = ax
        self.parent = parent
        self.xy = None
        self.xyT = None
        self.text = ''
        self.anno = None
        self.localIdx = ''

    def newMouseMarker(self,x,y):
        mrk = MarkerText()
        mrk.exec()
        if mrk.ret:
            self.text = mrk.text
        else:
            return

        inv = self.ax.transData.inverted()
        self.xy = inv.transform([x,y])
        self.xyT = inv.transform([x+20,y+20])

        self.anno = self.ax.annotate(self.text, xy=self.xy,  xytext=self.xyT, size=15,picker = 5,arrowprops=dict(facecolor='black', shrink=1, width=2, headwidth=2))
        self.localIdx = str(uuid.uuid1())
        self.parent.markerList.append(self)
        self.parent.signalGraphUpdate.emit()
        return

    def newDataBaseMarker(self,xy,xyT,text):
        self.anno = self.ax.annotate(text, xy=xy,  xytext=xyT, size=15,picker = 5,arrowprops=dict(facecolor='black', shrink=1, width=2, headwidth=2))
        self.parent.signalGraphUpdate.emit()
        return

class CursorStatic(object):
    def __init__(self, ax, x, y, col, parent):
        self.parent = parent
        self.removed = False
        self.x = x
        self.y = y
        _xlim = ax.get_xlim()
        _ylim = ax.get_ylim()
        self.line1 = Line2D(_xlim, (y,y), picker=5)
        self.line2 = Line2D((x,x), _ylim, picker=5)
        self.line1.set_color(col)
        self.line2.set_color(col)
        ax.add_line(self.line1)
        ax.add_line(self.line2)
        parent.signalGraphUpdate.emit()

    def delLine(self):
        if self.removed:
            return
        self.line1.remove()
        self.line2.remove()
        self.removed = True
        self.parent.signalGraphUpdate.emit()



class CustomToolbar(NavigationToolbar):
    def __init__(self,canvas_,parentframe_,parclass):
        self.parclass = parclass
        # images: Python34\Lib\site-packages\matplotlib\mpl-data\images
        self.toolitems = (
            ('Home', 'original scale', 'home', 'home'),
            #('Back', 'consectetuer adipiscing elit', 'back', 'back'),
            #('Forward', 'sed diam nonummy nibh euismod', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'pan', 'move', 'pan'),
            (None, None, None, None),
            ('Zoom', 'zoom', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Print','Print','printer','onPrint'),
            (None, None, None, None),
            ('PDF','PDF','pdf','onPDF'),
            (None, None, None, None),
            #('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
            ('Save', 'save to file', 'filesave', 'save_figure'),
            (None, None, None, None),
            ('ShowPage1', 'show page 1', 'page1', 'onShowPage1'),
            (None, None, None, None),
            ('ShowPage2', 'show page 2', 'page2', 'onShowPage2'),
            (None, None, None, None),
            ('NoVS', 'no VS', 'novs', 'onNoVS'),
            (None, None, None, None),
            (None, None, None, None),
            ('Cursor','Cursor','cursor','onCursor'),
            (None, None, None, None),
            )
        NavigationToolbar.__init__(self,canvas_,parentframe_,False)

    def onNoVS(self):
        self.parclass.toggleVS()

    def onPrint(self):
        self.parclass.print()

    def onPDF(self):
        self.parclass.printPDF()

    def onShowPage1(self):
        self.parclass.switchPage1()
    def onShowPage2(self):

        self.parclass.switchPage2()

    def onCursor(self):
        if self.parclass.cursorActive :
            self.parclass.cursorActive= False
          #  self.cursor.setChecked(False)
        else:
            self.parclass.cursorActive = True
           # self.cursor.setChecked(True)

        self.parclass.signalShowCursor.emit()


    def _init_toolbar(self):
        self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan','onCursor']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        self.buttons = {}

        self.cbA = QRadioButton('Cursor A ->',self)
        self.cbA.setChecked(True)
        self.labelcA = QLabel('')
        self.labelcA.setMinimumSize(100,30)

        self.cbB = QRadioButton('Cursor B ->',self)
        self.labelcB = QLabel('')
        self.labelcB.setMinimumSize(100, 30)

        self.labelcC = QLabel('Delta ->')
        self.labelcC.setMinimumSize(100,30)

        self.labelcD = QLabel('Mouse ->')
        self.labelcD.setMinimumSize(100,30)

        self.addWidget(self.cbA)
        self.addWidget(self.labelcA)
        self.addWidget(self.cbB)
        self.addWidget(self.labelcB)
        self.addWidget(self.labelcC)
        self.addWidget(self.labelcD)

        self.cbA.toggled.connect(self.onRBtoggled)
        self.adj_window = None

    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        self._actions['pan'].setChecked(self._active == 'PAN')
        self._actions['zoom'].setChecked(self._active == 'ZOOM')
       # self._actions['onHLine'].setChecked(self._active == 'HLINE')
       # self._actions['onVLine'].setChecked(self._active == 'VLINE')

    def onRBtoggled(self):
        return
        if self.cbA.isChecked():
            pass

class Graphics(QMainWindow):
    signalShowTitle = QtCore.pyqtSignal(str)
    signalGraphUpdate = pyqtSignal()
    waitEvent = threading.Event()
    signalPrint = pyqtSignal()
    signalPDF = pyqtSignal()
    signalPrintEnd = threading.Event()
    signalShowCursor = pyqtSignal()
    signalSetMarker = pyqtSignal(float,float)

    def __init__(self, parent = None):
        QMainWindow.__init__(self,parent)
        # create a simple main widget to keep the figure
        #self.mainWidget = QWidget()
        #self.setCentralWidget(self.mainWidget)
        #layout = QVBoxLayout()
        #self.mainWidget.setLayout(layout)
        self.setWindowTitle('TMV3-Graph')
        self.defaultColor = 'black'
        self.defaultStyle = '-'
        self.defaultWidth = 1.1
        self.backgroundPlot = False
        self.signals = Signal()
        self.config = configparser.ConfigParser()
        self.config.read('../Lib/TMV3.ini')
        self.graphUpdate = True
        try:
            process_name = "Graph" + sys.argv[2]
        except Exception as _err:
            process_name = "Graph"
        self.Client = Client(process_name)


        self.workBenchDB = self.config['DataBases']['workbench']
        self._workingDir = self.config['Pathes']['workingdir']
        self.autoPrint = int(self.config['Print']['autoprint'])
        self.ticket = Workbench.Ticket()
        self.limits = []
        self.limitsVisible = True
        self.sensorList = []
        self.rbwList = []
        self.attList = []
        self.ampList = []
        self.page = 1
        self.fig = Figure()
        #        self.fig = Figure((10.0, 5.0), 100)


       # self.fig2 = Figure((10.0, 5.0), 100)
       # self.fig2 = plt.figure()
        self.fig2 = Figure()
        self.dyfig2 = self.fig2
        self.fig = plt.figure()
        self.dyfig = self.fig
        print ('dyfig = ',id(self.dyfig))
        self.line1TextFlag = False
        self.line2TextFlag = False
        self.corrAntYEndPos = 0
        self.corrCabYEndPos = 0
        self.corrProbeYEndPos = 0
        self.corrAntLabel = None
        self.corrCabLabel = None
        self.corrProbeLabel = None
        self.currentStaticPlot = None
        self.currentStaticPlotCorrList = None
        self.currentStaticPlotFlag = False
        self.currentPlotID = 0
        self.cursorActive = False #enable button on mpl
        self.cursorA = None
        self.cursorB = None
        self.cursorD = None
        self.marker0 = None
        self.marker1 = None
        self.line1 = None
        self.line2 = None
        self.markerList=[]
        #Messages
        self.signalShowTitle.connect(self.onShowTitle) #access to Gui via signal
        self.signalGraphUpdate.connect(self.onGraphUpdate) #access to Gui via signal
        self.signalShowCursor.connect(self.toggleCursor)
        self.signalPrint.connect(self.print)
        self.signalPDF.connect(self.printPDF)
        self.signalSetMarker.connect(self.setMouseMarker)
        dispatcher.connect(self.onNewPlot, self.signals.GRAPH_NEW_PLOT, dispatcher.Any)
        dispatcher.connect(self.onNewTrace, self.signals.GRAPH_NEW_TRACE, dispatcher.Any)
        dispatcher.connect(self.onNewLine, self.signals.GRAPH_NEW_LINE, dispatcher.Any)
        dispatcher.connect(self.onNewAnnotation, self.signals.GRAPH_NEW_ANNOTATION, dispatcher.Any)
        dispatcher.connect(self.onNewClassification, self.signals.GRAPH_NEW_CLASSIFICATION, dispatcher.Any)
        dispatcher.connect(self.onNewDescription, self.signals.GRAPH_NEW_DESCRIPTION, dispatcher.Any)
        dispatcher.connect(self.onNewNumber, self.signals.GRAPH_NEW_NUMBER, dispatcher.Any)
#        dispatcher.connect(self.onPrint, self.signals.GRAPH_PRINT, dispatcher.Any)
        dispatcher.connect(self.onStop, self.signals.GRAPH_STOP, dispatcher.Any)
        dispatcher.connect(self.onShowPlot, self.signals.GRAPH_SHOW_PLOT, dispatcher.Any)
        dispatcher.connect(self.onResult,self.signals.GRAPH_RESULT,dispatcher.Any)
        dispatcher.connect(self.onMakeThumbnail,self.signals.GRAPH_MAKE_THUMBNAIL,dispatcher.Any)

        logging.info('TMV3 Graph started')

        try:
            self.create_main_frame()
            _sData = []
            _sData.append(self.signals.GRAPH_STARTED)
            self.Client.send(_sData)
        except Exception as _err:
            pass

    def toggleVS(self):
        # if self.labelD == None:
        #     self.labelD = self.host.text(self.labelX,13,'Test')
        # else:
        #     self.labelX += 1e6
        #     self.labelD.set_x(self.labelX)
        # self.signalGraphUpdate.emit()

         if self.limitsVisible:
             self.limitsVisible = False
             for x in self.limits:
                 x.set_visible(False)
             self.fig.suptitle("VS-Nur für den Dienstgebrauch",color='blue',size=15)
         else:
             self.limitsVisible = True
             for x in self.limits:
                 x.set_visible(True)
             self.fig.suptitle("VS-Vertraulich",color='blue',size=15)
         self.signalGraphUpdate.emit()

    def toggleCursor(self):
        print('toggleCursor')


        if self.cursorActive:
            inv = self.host.transData.inverted()

            _xlim = self.host.get_xlim()
            _ylim = self.host.get_ylim()
            _xy1 = self.host.transData.transform((_xlim[0],_ylim[1]))
            _xy2 = self.host.transData.transform((_xlim[1],_ylim[0]))
            #_xy1 = self.host.transData.transform((_posx[0],_posy[0]))
            #ä_xy2 = self.host.transData.transform((_posx[1],_posy[1]))

            _x1 = _xy1[0]+20
            _x2 = _xy1[0]+40
            _y1 = _xy2[1]+20
            _y2 = _xy2[1]+40

            _xy1t = inv.transform((_x1,_y1))
            _xy2t = inv.transform((_x2,_y2))
            self.cursorA = CursorStatic(self.host,_xy1t[0],_xy1t[1],'gray',self)
            self.cursorB = CursorStatic(self.host,_xy2t[0],_xy2t[1],'black',self)
            self.showCursorPos(self.cursorA.x,self.cursorA.y,'A')
            self.showCursorPos(self.cursorB.x,self.cursorB.y,'B')
            self.showCursorPos(math.fabs(self.cursorB.x-self.cursorA.x),math.fabs(self.cursorB.y-self.cursorA.y),'C')
            # # self.line = Line2D(_xy1,_xy2)

            # self.line1 = Line2D(_xlim, (_xy2t[1],_xy2t[1]))
            # self.line2 = Line2D((_xy1t[0],_xy1t[0]), _ylim)
            # self.host.add_line(self.line1)
            # self.host.add_line(self.line2)
            # self.signalGraphUpdate.emit()
            print ('cursor added')
#           self.cursorD = Cursor(self.host, useblit=False, color='blue', linewidth=2)
        else:
            self.cursorA.delLine()
            self.cursorA = None
            self.cursorB.delLine()
            self.cursorB = None

    def switchPage1(self):
        self.canvas.setVisible(True)
        self.canvas2.setVisible(False)
        self.mpl_toolbar.canvas=self.canvas
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        self.page = 1
        self.signalGraphUpdate.emit()

    def switchPage2(self):
        self.canvas2.setVisible(True)
        self.canvas.setVisible(False)
        self.mpl_toolbar.canvas=self.canvas2
        self.canvas2.setFocusPolicy(Qt.StrongFocus)
        self.canvas2.setFocus()
        self.page = 2

    def clear(self):
        self.fig.clear()
        self.sensorList.clear()
        self.rbwList.clear()
        self.attList.clear()
        self.ampList.clear()
        return
        self.fig.delaxes(self.host)
        self.fig.delaxes(self.par1)
        self.fig.delaxes(self.par2)
        self.fig.delaxes(self.par3)
        self.fig.delaxes(self.par4)
        self.sensorList.clear()
        self.rbwList.clear()
        self.attList.clear()
        self.ampList.clear()
        self.signalGraphUpdate.emit()

    def onPrint(self):
        self.signalPrint.emit()
        self.signalPrintEnd.wait()

    def onPdf(self):
        self.signalPDF.emit()
        self.signalPrintEnd.wait()

    def printPDF(self):
        dlg = QFileDialog()
        pdf_FileName = dlg.getSaveFileName(self,"Save as PDF","","*.pdf")
        if pdf_FileName:
            _dirname = os.path.dirname(pdf_FileName)
            _filename = os.path.splitext(os.path.basename(pdf_FileName))[0]
            pdf_FileName1 = _dirname + '/' + _filename + ' 1.pdf'
            pdf_FileName2 = _dirname + '/' + _filename + ' 2.pdf'


            QApplication.setOverrideCursor(Qt.WaitCursor)
            with PdfPages(pdf_FileName)as pdf:
                pdf.savefig(self.dyfig)
                pdf.savefig(self.dyfig2)

        self.signalPrintEnd.set()
        QApplication.restoreOverrideCursor()


    def print(self):
        printer = QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printer.setDuplex(QPrinter.DuplexAuto)
        printerDialog = QPrintDialog(printer)
        ret = printerDialog.exec()
        if ret == QDialog.Accepted:
            _dpi = 96
            painter = QPainter(printer)
            self.dyfig.savefig("../WorkingDir/Page1.png",dpi=_dpi)
            image = QImage("../WorkingDir/Page1.png")
            pageRect = printer.pageRect()
            imageRect = image.rect()
            xOffset = (pageRect.width() - imageRect.width())/2
            yOffset = (pageRect.height() - imageRect.height())/2 - pageRect.y()/2 # ? to fit layout like pdf
            painter.drawImage(QPoint(xOffset,yOffset),image)
            painter.end()

            painter = QPainter(printer)
            self.dyfig2.savefig("../WorkingDir/Page2.png",dpi=_dpi)
            image = QImage("../WorkingDir/Page2.png")
            painter.drawImage(QPoint(0,0),image)
            painter.end()
            self.signalPrintEnd.set()

    def create_main_frame(self):
        self.main_frame = QWidget()


        self.canvas =  FigureCanvas(self.fig)
        self.canvas2 =  FigureCanvas(self.fig2)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame,self)
        self.canvas.mpl_connect('pick_event',self.onPick)
        self.canvas.mpl_connect('motion_notify_event',self.onMouseMotion)
      #  self.canvas.mpl_connect('button_press_event',self.onButtonPress)
        self.canvas.mpl_connect('button_release_event',self.onButtonRelease)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.canvas)  # the matplotlib canvas
        self.vbox.addWidget(self.canvas2)  # the matplotlib canvas
        self.vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)


        self.fig.clear()

        self.genPlotPage()
        self.genTextPage()
        self.switchPage1()

    def genTextPage(self):

        self.canvas2.draw()
        _size = 12
        _x = 0.05
        _y = 0.91
        _offset = -0.05
        _header = ["Eut:","Test-No:","Serial-No:","Model-No:","Model-Name:","Test-Date:","Company:",
                   "Technician:","Plan:","Routine:","Sheet:","Annotation:","","","",""]
        for _s in  _header:
            self.fig2.text(_x,_y,_s,size=_size, verticalalignment='top')
            _y = _y +_offset

    def setText(self,dataList):

        _size = 12
        _x = 0.20
        _y = 0.91
        _offset = -0.05
        for _s in dataList:
            self.fig2.text(_x,_y,_s,size=_size, verticalalignment='top')
            _y = _y +_offset

        self.host.text(0.1,1.2,dataList[0],horizontalalignment='left',transform=self.host.transAxes)
        self.host.text(0.1,1.12,dataList[1],horizontalalignment='left',transform=self.host.transAxes)

    def genPlotPage(self):

        self.host = self.fig.add_subplot(111)
        #pos = self.host.get_position()
       # self.host.set_position([0.2,0.6,0.7,0.3])
        self.fig.subplots_adjust(bottom=0.25,left=0.07,right=0.93,top=0.8)
       # self.host.set_axis_bgcolor('#323232')
        self.host.set_ylabel('dBµV')
        self.host.set_xlabel('Hz')
        self.host.grid(which='minor', alpha=0.2)
        self.host.grid(which='major', alpha=0.5)

        self.host.grid(True)
        self.host.set_xscale('log')
        self.host.set_xlim(1e3,1e9)
        self.host.set_ylim(-20,80)
        font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 9}
        matplotlib.rc('font', **font)
        self.par1 = self.host.twiny()
        self.make_patch_spines_invisible(self.par1)
        self.par1.text(-0.05,-0.18,"source",horizontalalignment='left',transform=self.par1.transAxes)
        self.par1.text(-0.05,-0.24,"rbw",horizontalalignment='left',transform=self.par1.transAxes)
      #  self.par1.spines["bottom"].set_position(("outward", 50))
        self.par1.spines["bottom"].set_position(("axes", -0.20))
        self.par1.xaxis.set_ticks_position('bottom')
        self.par1.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
        self.par1.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')

        self.par2 = self.host.twiny()
        self.make_patch_spines_invisible(self.par2)
#        self.par2.spines["bottom"].set_position(("outward", 50))
        self.par2.spines["bottom"].set_position(("axes", -0.20))
        self.par2.xaxis.set_ticks_position('bottom')
        self.par2.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par2.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par2.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
        self.par2.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5,labelbottom='on')

        self.par3 = self.host.twiny()
        self.make_patch_spines_invisible(self.par3)
#        self.par3.spines["bottom"].set_position(("outward", 90))
        self.par3.spines["bottom"].set_position(("axes", -0.34))
        self.par3.text(-0.05,-0.33,"amp",horizontalalignment='left',transform=self.par3.transAxes)
        self.par3.text(-0.05,-0.40,"att",horizontalalignment='left',transform=self.host.transAxes)
        self.par3.xaxis.set_ticks_position('bottom')
        self.par3.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par3.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par3.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-10, labelbottom='on')
        self.par3.xaxis.set_tick_params(which='major',length=10,direction='in', pad=-20,labelbottom='on')

        self.par4 = self.host.twiny()
        self.make_patch_spines_invisible(self.par4)
        self.par4.spines["bottom"].set_position(("axes", -0.34))
        self.par4.xaxis.set_ticks_position('bottom')
        self.par4.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par4.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par4.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
        self.par4.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5,labelbottom='on')


        formatterHZ = EngFormatter(unit = '',places=0)
        formatterDB = EngFormatter(unit = '',places=0)
        self.host.xaxis.set_major_formatter(formatterHZ)
        self.host.yaxis.set_major_formatter(formatterDB)
       # self.setTestData()

       # self.host.set_title('Kat C, Test-No: 3F423, Date: 2016.3.1 11:31')
        self.host.text(-0.0,1.2,"EUT:",horizontalalignment='left',transform=self.host.transAxes)
        self.host.text(-0.0,1.12,"Test-No:",horizontalalignment='left',transform=self.host.transAxes)
        self.fig.suptitle("VS-Vertraulich",color='blue',size=15)

    def setMouseMarker(self,x,y):
        self.marker = Marker(self.host,self)
        self.marker.newMouseMarker(x,y)
        _mark = DB_Handler_TPL3.Tpl3Marks(self.workBenchDB,0)
        _mark.plotID = self.currentPlotID
        _mark.x = self.marker.xy[0]
        _mark.y = self.marker.xy[1]
        _mark.xT = self.marker.xyT[0]
        _mark.yT = self.marker.xyT[1]
        _mark.localIdx = self.marker.localIdx
        _mark.marker_text = self.marker.text
        _mark.add()

    def onPick(self, event):
        if self.cursorActive:
            return
        #pick on marker => delete that marker
        artist = event.artist
        title = '{}'.format(event.artist)
        if title.startswith('Anno'):
            if event.mouseevent.button == 3:
                print (title)
                for i in self.markerList:
                    title2 = '{}'.format(i.anno)
                    if title2 == title:
                        _mark = DB_Handler_TPL3.Tpl3Marks(self.workBenchDB,0)
                        _mark.plotID = self.currentPlotID
                        _mark.localIdx = i.localIdx
                        _mark.remove()
                        i.anno.remove()
                        self.signalGraphUpdate.emit()

        else:
            xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
            x, y = artist.get_xdata(), artist.get_ydata()
            ind = event.ind
           # print ('Artist picked:', event.artist)
           # print ('{} vertices picked'.format(len(ind)))
           # print ('Pick between vertices {} and {}'.format(min(ind), max(ind)+1))
            xy = '{:.2f},{:.2f}'.format(xmouse, ymouse)
            data = '{},{}'.format( x[ind[0]], y[ind[0]])

            if event.mouseevent.button == 1:
                info = LineInfo(title,xy,data,self)
                info.show()
            if event.mouseevent.button == 3:
                self.signalSetMarker.emit(event.mouseevent.x, event.mouseevent.y)

    def onButtonRelease(self,event):
        if self.cursorActive:
            inv = self.host.transData.inverted()
            pos = inv.transform((event.x, event.y))

            if event.button == 1:
                if not self.cursorD is None:
                    self.cursorD.set_active(False)
                if self.mpl_toolbar.cbA.isChecked():
                    if self.cursorA is None:
                        self.cursorA = CursorStatic(self.host, pos[0], pos[1], 'gray', self)
                else:
                    if self.cursorB is None:
                        self.cursorB = CursorStatic(self.host, pos[0], pos[1], 'black', self)

    def onMouseMotion(self,event):
        inv =  self.host.transData.inverted()
        pos = inv.transform((event.x,event.y))

        if self.cursorActive:
            if event.button == 1:
                #QtGui.QApplication.setOverrideCursor((QtGui.QCursor(Qt.CrossCursor)))
                #activate Crossline Cursor
                if self.cursorD is None:
                    self.cursorD = Cursor(self.host, useblit=False)
                else:
                    self.cursorD.set_active(True)

                if self.mpl_toolbar.cbA.isChecked():
                    if not self.cursorA is None: #delete static Cursorline if Cursor is active
                        self.cursorA.delLine()
                        self.cursorA = None
                    self.showCursorPos(pos[0], pos[1], 'A')
                    self.showCursorPos(math.fabs(pos[0]-self.cursorB.x), math.fabs(pos[1]-self.cursorB.y), 'C')
                    self.cursorD.lineh.set_color('gray')
                    self.cursorD.linev.set_color('gray')

                else:
                    if not self.cursorB is None: #delete static Cursorline if Cursor is active
                        self.cursorB.delLine()
                        self.cursorB = None
                    self.showCursorPos(pos[0], pos[1], 'B')
                    self.showCursorPos(math.fabs(pos[0]-self.cursorA.x), math.fabs(pos[1]-self.cursorA.y), 'C')
                    self.cursorD.lineh.set_color('black')
                    self.cursorD.linev.set_color('black')

                event.inaxes = self.host
                self.cursorD.onmove(event)
            else:
                self.showCursorPos(pos[0],pos[1],'D')
                #QtGui.QApplication.restoreOverrideCursor()
        else:
            self.showCursorPos(pos[0], pos[1], 'D')

    def showCursorPos(self,x,y,pos):
        form = EngFormat.Format()
        _x = form.FloatToString(x, 3)
        _y = form.FloatToString(y, 1)
        _value = '{0}Hz,{1}dB'.format(_x, _y)

        if pos == 'A':
            self.mpl_toolbar.labelcA.setText(_value)
        if pos == 'B':
            self.mpl_toolbar.labelcB.setText(_value)
        if pos == 'C':
            _value = '  Delta -> {0}Hz,{1}dB'.format(_x, _y)
            self.mpl_toolbar.labelcC.setText(_value)
        if pos == 'D':
            _value = '      Mouse -> {0}Hz,{1}dB'.format(_x, _y)
            self.mpl_toolbar.labelcD.setText(_value)

    def compressLabel(self,list):
        i = 1
        n = len(list)
        while i < n:
            _sensor_a = list[i-1]
            _sensor_b = list[i]
            if _sensor_a.label == _sensor_b.label:
                _sensor_a.stopX = _sensor_b.stopX
                list.remove(_sensor_b)
                self.compressLabel(list)
                return
            i += 1

    def setLineSensor(self):
        try:
            self.compressLabel(self.sensorList)

            x1=[]
            x1pos=[]
            labels1=[]

            j = -1
            x1pos.append(0)
            labels1.append('')
           # self.setTestData()
            for i in self.sensorList:
                if i.startX > j:
                    x1.append(i.startX)
                    j = i.startX
                    x1.append(i.stopX)
                    x1pos.append(i.labelPos)
                    labels1.append(i.label)


            self.par1.xaxis.set_major_formatter(ticker.NullFormatter())
            self.par1.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
            self.par1.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
            self.par1.xaxis.set_ticks(x1)

        except Exception as _err:
            print(_err)
            logging.exception(_err)
            pass

    def setLineRBW(self):

        self.compressLabel(self.rbwList)

        try:
            x1 = []
            x1pos = []
            labels1 = []
            j = -1
            x1pos.append(0)
            labels1.append('')
           # self.setTestData()
            for i in self.rbwList:
                if i.startX > j:
                    x1.append(i.startX)
                    j = i.startX
                x1.append(i.stopX)
                x1pos.append(i.labelPos)
                labels1.append(i.label)

         #   self.par2.spines["bottom"].set_position(("outward", 50))
         #   self.par2.xaxis.set_ticks_position('bottom')
#            self.par2.set_xscale('log')
            self.par2.xaxis.set_major_formatter(ticker.NullFormatter())
            self.par2.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
            self.par2.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
            self.par2.xaxis.set_ticks(x1)
            self.par2.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
            self.par2.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5,labelbottom='on')

        except Exception as _err:
            print(_err)
            logging.exception(_err)

    def setLineAMP(self):

        self.compressLabel(self.ampList)

        try:
            x1 = []
            x1pos = []
            labels1 = []
            j = -1
            x1pos.append(0)
            labels1.append('')
           # self.setTestData()
            for i in self.ampList:
                if i.startX > j:
                    x1.append(i.startX)
                    j = i.startX
                x1.append(i.stopX)
                x1pos.append(i.labelPos)
                labels1.append(i.label)


            if not self.line2TextFlag:
                # self.par3.text(-0.05,-0.33,"amp",horizontalalignment='left',transform=self.host.transAxes)
                # self.par3.text(-0.05,-0.40,"att",horizontalalignment='left',transform=self.host.transAxes)
               #  self.par3.spines["bottom"].set_position(("outward", 90))
                 self.par3.xaxis.set_ticks_position('bottom')
                 self.par3.xaxis.set_major_formatter(ticker.NullFormatter())
                 self.par3.xaxis.set_minor_formatter(ticker.NullFormatter())
                 self.par3.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-10, labelbottom='on')
                 self.par3.xaxis.set_tick_params(which='major',length=10,direction='in', pad=-20,labelbottom='on')
                 self.line2TextFlag = True

            self.par3.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
            self.par3.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
            self.par3.xaxis.set_ticks(x1)

            #set color for autorange indication
            _Ret = self.par3.xaxis.get_minorticklabels()
            n = 0
            for i in _Ret:
                if self.ampList[n].color =='r':
                    i._color = 'r' #sorry, found no other access
                if n < len(self.ampList) - 1:
                    n += 1
        except Exception as _err:
            print(_err)
            logging.exception(_err)
        pass

    def setLineATT(self):

        self.compressLabel(self.attList)

        try:
            x1 = []
            x1pos = []
            labels1 = []
            j = -1
            x1pos.append(0)
            labels1.append('')
           # self.setTestData()
            for i in self.attList:
                if i.startX > j:
                    x1.append(i.startX)
                    j = i.startX
                x1.append(i.stopX)
                x1pos.append(i.labelPos)
                labels1.append(i.label)


       #     self.par4.spines["bottom"].set_position(("outward", 90))
       #     self.par4.xaxis.set_ticks_position('bottom')
           # # self.par1.set_xlim(1e3,1e9)
           #  self.par4.set_xscale('log')
            self.par4.xaxis.set_major_formatter(ticker.NullFormatter())
            self.par4.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
            self.par4.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
            self.par4.xaxis.set_ticks(x1)
            self.par4.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
            self.par4.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5,labelbottom='on')

            _Ret = self.par4.xaxis.get_minorticklabels()
            n = 0
            for i in _Ret:
                if self.attList[n].color =='r':
                    i._color = 'red'
                if n < len(self.attList) - 1:
                    n += 1

          #  self.signalGraphUpdate.emit()
        except Exception as _err:
            print(_err)
            logging.exception(_err)
        pass

    def addSensor(self,startFreq,stopFreq,title,log=True):
        _sensor = axisLabel(startFreq,stopFreq,title,'b',log)
        self.sensorList.append(_sensor)
        pass

    def addRBW(self,startFreq,stopFreq,rbw,log=True):
        form = EngFormat.Format()
        _sRBW = form.FloatToString(rbw,0)
        _rbw = axisLabel(startFreq,stopFreq,_sRBW,'b',log)
        self.rbwList.append(_rbw)

        pass

    def addAtt(self,startFreq,stopFreq,att,autorange,log=True):
        form = EngFormat.Format()
        _sATT = form.FloatToString(att,0)
        col='b'
        if autorange:
            col = 'r'
        _Att = axisLabel(startFreq,stopFreq,_sATT,col,log)
        self.attList.append(_Att)

    def addAmp(self,startFreq,stopFreq,amp,autorange,log=True):
        print('addAmp',startFreq,stopFreq,amp,autorange)
        form = EngFormat.Format()
        _sAMP = form.FloatToString(amp,0)
        col='b'
        if autorange:
            col = 'r'
        _Amp = axisLabel(startFreq,stopFreq,_sAMP,col,log)
        self.ampList.append(_Amp)

    def onShowPlot(self,data,corrList,backgroundPlot):
        try:
            assert isinstance(data,DB_Handler_TPL3.Tpl3Plot)
            self.backgroundPlot = backgroundPlot
            self.onNewPlot(data)
            self.onShowTitle(data.plot_title)
            if not backgroundPlot:
                self.onResult(data.result)
            self.currentPlotID = data.plot_id

            print('ShowPlot, Master={0}, ID={1}, Title={2}, Result={3}',format(self.backgroundPlot),data.plot_id,data.plan_title,data.result)

            #remember data for interactive user clicks
            self.currentStaticPlotFlag = True
            self.currentStaticPlotCorrList = corrList
            self.currentStaticPlot = data

            for _t in data.traces:
                self.onNewTrace(_t)
                # show Corrections as line
                corrDict = dict(corrList)
                if not _t.corIDs is None:
                    for x in eval(_t.corIDs):
                        line = corrDict[x]
                        assert isinstance(line,DB_Handler_TPL3.Tpl3Lines)
                        dxy = self.cutRange(line.data_xy,_t.x1,_t.x2)
                        dline = copy.deepcopy(line)
                        dline.data_xy = dxy
                        self.onNewLine(dline)


            #_lines = eval (data.lineObjects)
            for _line in data.lineObjects:
                if _line.type == 'Antenna': pass
                elif _line.type == 'Cable': pass
                elif _line.type == 'Probe': pass
                else:
                    self.onNewLine(_line)

            for mark in data.marks:
                m = Marker(self.host,self)
                xy = (mark.x,mark.y)
                xyT = (mark.xT,mark.yT)
                m.newDataBaseMarker(xy,xyT,mark.marker_text)


            # if self.corrAntYEndPos > 0:
            #     _text = 'Antenna'
            #     self.host.text(self.host.get_xlim()[1],self.corrAntYEndPos,_text)
            # if self.corrCableYEndPos > 0:
            #     _text = 'Cable'
            #     self.host.text(self.host.get_xlim()[1],self.corrCableYEndPos,_text)
            # if self.corrProbeYEndPos > 0:
            #     _text = 'Probe'
            #     self.host.text(self.host.get_xlim()[1],self.corrProbeYEndPos,_text)


            self.backgroundPlot = False
            descriptionData = []
            descriptionData.append(data.eut)
            descriptionData.append(data.test_no)
            descriptionData.append(data.serial_no)
            descriptionData.append(data.model_no)
            descriptionData.append(data.model_name)
            descriptionData.append(data.date_time)
            descriptionData.append(data.company)
            descriptionData.append(data.technician)
            descriptionData.append(data.plan_title)
            descriptionData.append(data.routines)
            descriptionData.append(data.plot_no)
            descriptionData.append(data.annotations)
            sList = data.sources.split(',')
            if len(sList) > 0:
                for s in sList:
                    descriptionData.append(s)
            self.setText(descriptionData)
            self.signalGraphUpdate.emit()
        except Exception as _err:
            print("Graph: onShowPlot: {0}".format(str(_err)))
            logging.exception(_err)

    def onNewPlot(self, data):
     #   print ('Graph: new Plot')
        assert isinstance(data,DB_Handler_TPL3.Tpl3Plot)
        self.host.set_xlim(data.x1,data.x2)
        self.host.set_ylim(data.y1,data.y2)
        self.par1.set_xlim(data.x1,data.x2)
        self.par2.set_xlim(data.x1,data.x2)
        self.par3.set_xlim(data.x1,data.x2)
        self.par4.set_xlim(data.x1,data.x2)
        self.par1.set_xscale('log')
        self.par1.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par2.set_xscale('log')
        self.par2.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par2.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par3.set_xscale('log')
        self.par3.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par3.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par4.set_xscale('log')
        self.par4.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par4.xaxis.set_minor_formatter(ticker.NullFormatter())
        #self.setWindowTitle(data.plot_title)
        self.signalShowTitle.emit(data.plot_title)
        #self.figure_canvas.draw()
        descriptionData = []
        descriptionData.append(data.eut)
        descriptionData.append(data.test_no)
        descriptionData.append(data.serial_no)
        descriptionData.append(data.model_no)
        descriptionData.append(data.model_name)
        descriptionData.append(data.date_time)
        descriptionData.append(data.company)
        descriptionData.append(data.technician)
        descriptionData.append(data.plan_title)
        descriptionData.append(data.routines)
        descriptionData.append(data.plot_no)
        descriptionData.append(data.annotations)
        sList = data.sources.split(',')
        if len(sList) > 0:
            for s in sList:
                descriptionData.append(s)
        self.setText(descriptionData)
        self.signalGraphUpdate.emit()

        self.currentStaticPlotFlag = False
        pass

    def onShowTitle(self,txt):
        #access to Gui only via signal
        self.setWindowTitle(txt)
        self.host.title.set_text(txt)

    def onGraphUpdate(self):
        if self.graphUpdate:
            self.canvas.draw()

    def onNewLine(self, data):
       # print('onNewLineStart')
        try:
            assert isinstance(data,DB_Handler_TPL3.Tpl3Lines)

          #  print ('Graph: new Line {0} {1} {2}'.format(data.type, str(data.line_id), str(len(data.data_xy))))
            if isinstance(data.data_xy,str):
                _xyf = eval(data.data_xy)
            else:
                _xyf = data.data_xy
          #  print(_xyf, type(_xyf))

            _xys = sorted(_xyf,key = lambda x: x[0])
            _x, _y = zip(*_xys)
            if data.type == 'Antenna':
                self.corrAntYEndPos = _y[-1]
            if data.type == 'Cable':
                self.corrCableYEndPos = _y[-1]
            if data.type == 'Probe':
                self.corrProbeYEndPos = _y[-1]


            self.getDefaultLineStyle(data.type)
            _color = self.defaultColor
            _style = self.defaultStyle
            _width = self.defaultWidth
         #   print(data.color, data.style, data.width)
            if data.color == '': _color = self.defaultColor
            if data.style == '': style = self.defaultStyle
            if data.width  == '0.0': _width = self.defaultWidth
            if self.backgroundPlot == 'True':
                _color = 'grey'

           # line, = self.host.plot(_x, _y, picker=5, label=data.title, color=_color,ls=_style, lw=_width)
#            line, = self.host.plot(_x, _y, picker=5, label=data.title, color=_color, lw=_width)

            line, = self.host.plot(_x, _y,picker=5, label=data.title,color=_color,ls=_style,lw= 1)


            if data.type == "Limit":
                _yTextPos = _y[-1]
                _xTextPos = self.host.get_xlim()[1]
                anz = len(_xys)
                #n = 0
                for n in range(anz-1):
                    if (_xys[n][0] == _xTextPos):
                        _yTextPos = _xys[n][1]
                        break
                    elif (_xys[n][0] < _xTextPos) & (_xys[n+1][0] >= _xTextPos):
                        x1 = math.log10(_xys[n][0])
                        x2 = math.log10(_xys[n+1][0])
                        y1 = _xys[n][1]
                        y2 = _xys[n+1][1]
                        a = (y2 - y1) / (x2 - x1)
                        b = y1 - a * x1
                        _yTextPos = a * math.log10(_xTextPos) + b
                        break

               # print("yTextPos",x1,y1,x2,y2,a,b,_yTextPos)
                _text = ' ' + data.title
                self.host.text(_xTextPos,_yTextPos,_text)
                self.limits.append(line)
                pass
            if data.type == "Antenna":
                _xStartPos = _x[0]
                _xEndPos = _x[len(_x)-1]
                _title = data.title
                self.addSensor(_xStartPos,_xEndPos,_title)
                self.setLineSensor()
                if self.corrAntLabel is None:
                    self.corrAntLabel = self.host.text(self.host.get_xlim()[1],self.corrAntYEndPos,'Antenna')
                else:
                    self.corrAntLabel.set_y(self.corrAntYEndPos)
            if data.type == "Cable":
                if self.corrCabLabel is None:
                    self.corrCabLabel = self.host.text(self.host.get_xlim()[1],self.corrCabYEndPos,'Cable')
                else:
                    self.corrCabLabel.set_y(self.corrCabYEndPos)
            if data.type == "Probe":
                if self.corrProbeLabel is None:
                    self.corrProbeLabel = self.host.text(self.host.get_xlim()[1],self.corrProbeYEndPos,'Probe')
                else:
                    self.corrProbeLabel.set_y(self.corrProbeYEndPos)
            #self.figure_canvas.draw()
            self.signalGraphUpdate.emit()



        except Exception as _err:
            print("Graph: onNewLine: {0}".format(str(_err)))
            logging.exception(_err)
        #print('onNewLineEnd')

    def onNewTrace(self, data):
        #print('GRAPH NewTrace autorange:',data.autorange)
        _x = []
        _y = []
        try:
            assert isinstance(data,DB_Handler_TPL3.Tpl3Traces)
            _startFreq = data.x1
            _stopFreq = data.x2
            if data.data_xy_mode == 'Sweep':
                if type(data.data_y) == str:
                    _y = numpy.array(eval(data.data_y))
                else:
                    _y = numpy.array(data.data_y)
                #_stepFreq = (_stopFreq - _startFreq)/len(_y)
                _x = numpy.array(numpy.linspace(_startFreq,_stopFreq,len(_y)))
            else:
                pass

            self.getDefaultLineStyle('Trace')
            if data.hf_overload == True or data.if_overload == True:
                self.getDefaultLineStyle('TraceOverload')
            if data.uncal:
                self.getDefaultLineStyle('TraceUncal')
            _color = self.defaultColor
            _style = self.defaultStyle
            _width = self.defaultWidth
            if self.backgroundPlot == 'True': _color = 'grey'
            label = "TraceID{}".format(str(data.trace_id))
            self.host.plot(_x, _y, picker=5, label=label, color=_color, ls=_style, lw=1)

       #     self.signalGraphUpdate.emit()
            self.addRBW(_startFreq,_stopFreq,data.rbw)
            self.addAmp(_startFreq,_stopFreq,data.amplifier,data.autorange)
            self.addAtt(_startFreq,_stopFreq,data.attenuator,data.autorange)

            self.setLineRBW()
            self.setLineAMP()
            self.setLineATT()
            self.signalGraphUpdate.emit()
            pass
        except Exception as _err:
            print("Graph: onNewTrace: {0}".format(str(_err)))
            logging.exception(_err)
        pass

    def onResult(self,data):
        #print('onResultStart')

        right = 0.9
        top = 0.9
        self.host.text(right, top, data,
            horizontalalignment='right',
            verticalalignment='top',
            fontsize=20, color='red',
            transform=self.host.transAxes)
        self.signalGraphUpdate.emit()
        #print('onResultEnd')

    def onNewAnnotation(self, data):
        print('GRAPH NewAnnotation')
        pass

    def onNewClassification(self, data):
        print('GRAPH NewClassification')
        pass

    def onNewDescription(self, data):
        print('onNewDescription')
        self.setText(data)
        pass

    def onNewNumber(self, data):
        print('GRAPH NewNumber')
        pass

    def onMakeThumbnail(self):
        try:
            #t1 = "../WorkingDir/x " + time.ctime() + ".png"
            #t1x = t1.replace(':', ' ')
            self.fig.savefig('../WorkingDir/Page1.png', format='png')
            image.thumbnail('../WorkingDir/Page1.png','../WorkingDir/ThumbNail.png',scale=0.10)

            if self.autoPrint:
                print ("autoPrint",self.autoPrint)
                self.onPrint()

        except Exception as _err:
            print(_err)
            self.fig.savefig('../WorkingDir/Pagex.png', format = 'png',dpi=300)
            logging.exception(_err)
        _sData = []
        _sData.append(self.signals.GRAPH_THUMBNAIL_READY)
        self.Client.send(_sData)


        pass

    def onStop(self, data):
        print('GRAPH Stop')
        self.Client.stop()
        pass

    def cutRange(self,data,cutFreqA,cutFreqB):

        _data = ast.literal_eval(data)
        _sdata = sorted(_data,key = lambda x: x[0])


        _xa1 = [0,0]
        _xa2 = [0,0]
        _xe1 = [0,0]
        _xe2 = [0,0]
        _xaSet = False
        _xeSet = False


        try:
            #find index near arround cut points
            for x in _sdata:
                _xa1 = _xa2
                _xa2 = x
                if x[0] == cutFreqA:
                    _xaSet = True
                    break
                if x[0] > cutFreqA:
                    break

            for x in _sdata:
                _xe1 = _xe2
                _xe2 = x
                if x[0] == cutFreqB:
                    _xeSet = True
                    break
                if x[0] > cutFreqB:
                    break

            if not _xaSet:
                _x1 = _xa1[0]
                _x2 = _xa2[0]
                _y1 = _xa1[1]
                _y2 = _xa2[1]

                _a = (_y2 - _y1) / (_x2 - _x1)
                _b = _y2- _x2 * _a
                _y = _a * cutFreqA + _b
                _y = round(_y, 1)
                _data.append((cutFreqA, _y))


            if not _xeSet:
                _x1 = _xe1[0]
                _x2 = _xe2[0]
                _y1 = _xe1[1]
                _y2 = _xe2[1]

                _a = (_y2 - _y1) / (_x2 - _x1)
                _b = _y2- _x2 * _a
                _y = _a * cutFreqB + _b
                _y = round(_y, 1)
                _data.append((cutFreqB, _y))

            _l1 = sorted(_data,key = lambda x: x[0])

            _l2 = []
            for x in _l1:
                if (x[0] >= cutFreqA) and (x[0] <= cutFreqB):
                    _l2.append(x)

        except Exception as _err:
            print ("Graphic: cutRange: {0}".format(str(_err)))
            logging.exception(_err)

        return _l2

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

    def make_patch_spines_invisible(self,ax):
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)

    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
     #   key_press_handler(event, self.canvas, self.mpl_toolbar)

    def setCorrLabel(self,a,c,p):
        self.aXposOld = 0

class CorrLabel(object):
    def __init__(self,parent=None):
        self.labelAntenna = None
        self.labelCable = None
        self.oldCPos = -1000
        self.oldPPos = -1000
        self.parent = parent
    def writeAntLabel(self):
        x = self.parent.host.get_xlim()[1]
        if self.labelAntenna is not None:
            self.labelAntenna.set_position(x,self.parent.corrAntYEndPos)
        else:
            self.labelAntenna = self.parent.host.text(x,self.parent.corrAntYEndPos,'Antenna')
        self.parent.draw()
#        self.parent.host.add_artist(self.labelAntenna)
    def writeCabLabel(self):
        x = self.parent.host.get_xlim()[1]
        if self.labelCable is not None:
            self.labelCable.set_position(x,self.parent.corrCabYEndPos)
        else:
            self.labelCab = self.parent.host.text(x,self.parent.corrCabYEndPos,'Cable')
        self.parent.draw()
 #       self.parent.host.add_artist(self.labelCable)
    def writeProbeLabel(self):
        x = self.parent.host.get_xlim()[1]
        if self.oldPPos > -1000:
            self.parent.host.text(x,self.oldPPos,'          ')
        self.parent.host.text(x,self.parent.corrProbeYEndPos,'Probe')
        self.oldPPos = self.parent.corrProbeYEndPos

class axisLabel(object):
    def __init__(self,x1,x2,label,color,log=True):
        self.startX = x1
        self.stopX = x2
        self.label = label
        self.color = color
        if log:
            self.labelPos = math.pow(10,(math.log10(x2)-math.log10(x1))/2 + math.log10(x1))
        else:
            self.labelPos = (x2 - x1) / 2 + x1
def main():

    app = QApplication(sys.argv)
    rec = app.desktop().screenGeometry()
    form = Graphics()
    #right screen pos, show always win-title
    x = rec.width() - 1200 - 10
    y = int(sys.argv[1]) + 40
    form.setGeometry(x,y,1200,700)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()

