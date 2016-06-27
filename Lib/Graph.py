__author__ = 'Heinz'


import sys
import matplotlib
import math
import os
import ast
import copy
import DB_Handler_TPL3
import Workbench
import matplotlib.ticker as ticker
import matplotlib.image as image
import EngFormat
from PIL import Image
from GraphClient import *
from PyQt4.QtGui import *
import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import EngFormatter
from NeedfullThings import *
from LineInfo import LineInfo
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
            #('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
            ('Save', 'save to file', 'filesave', 'save_figure'),
            (None, None, None, None),
            ('ShowPage1', 'show page 1', 'page1', 'onShowPage1'),
            (None, None, None, None),
            ('ShowPage2', 'show page 2', 'page2', 'onShowPage2'),
            (None, None, None, None),
            ('NoVS', 'no VS', 'novs', 'onNoVS'),
            (None, None, None, None)
            )
        NavigationToolbar.__init__(self,canvas_,parentframe_)
    def onNoVS(self):
        self.parclass.toggleVS()

    def onPrint(self):
        self.parclass.print()
    def onShowPage1(self):

        self.parclass.switchPage1()
    def onShowPage2(self):

        self.parclass.switchPage2()
    def _init_toolbar(self):
        self.basedir = os.path.join(matplotlib.rcParams['datapath'], 'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QLabel("", self)
            self.locLabel.setAlignment(Qt.AlignRight | Qt.AlignTop)
            self.locLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None



class MainForm(QMainWindow):
    signalShowTitle = QtCore.pyqtSignal(str)
    signalGraphUpdate = pyqtSignal()
    waitEvent = threading.Event()

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
        self.defaultWidth = 1
        self.backgroundPlot = False
        self.signals = Signal()
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.graphUpdate = True
        process_name = "Graph" + sys.argv[2]
        self.Client = Client(process_name)

        self.workBenchDB = self.config['DataBases']['workbench']
        self._workingDir = self.config['Pathes']['workingdir']
        self.ticket = Workbench.Ticket()
        self.limits = []
        self.limitsVisible = True
        self.sensorList = []
        self.rbwList = []
        self.attList = []
        self.ampList = []
        self.page = 1
        self.create_main_frame()
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
        #Messages
        self.signalShowTitle.connect(self.onShowTitle) #access to Gui via signal
        self.signalGraphUpdate.connect(self.onGraphUpdate) #access to Gui via signal


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


        #if (ret):
        #   print("GRAPH Socket started, waiting for jobs")
        #else:
        #   print("GRAPH not connected")
        _sData = []
        _sData.append(self.signals.GRAPH_STARTED)
        self.Client.send(_sData)

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

    def print(self):
        printer = QPrinter()
        printer.setOrientation(QPrinter.Landscape)
        printerDialog = QPrintDialog(printer)
        ret = printerDialog.exec()
        if ret == QDialog.Accepted:
            _dpi = 300
            _xScale=(printer.pageRect().width()/ (self.fig.get_figwidth()* _dpi))
            _yScale=(printer.pageRect().height()/(self.fig.get_figheight() * _dpi))
            painter = QPainter(printer)
            painter.scale(_xScale,_yScale)
            self.fig.savefig("../WorkingDir/Page1.png",dpi=_dpi)
            image = QImage("../WorkingDir/Page1.png")
            painter.drawImage(QPoint(0,0),image)
            painter.end()

            painter = QPainter(printer)
            painter.scale(_xScale,_yScale)
            self.fig2.savefig("../WorkingDir/Page2.png",dpi=_dpi)
            image = QImage("../WorkingDir/Page2.png")
            painter.drawImage(QPoint(0,0),image)
            painter.end()

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.fig = Figure((10.0, 5.0), 100)
        self.fig2 = Figure((10.0, 5.0), 100)
        self.canvas =  FigureCanvas(self.fig)
        self.canvas2 =  FigureCanvas(self.fig2)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame,self)
        self.canvas.mpl_connect('pick_event',self.onPick)
        #self.canvas.mpl_connect('key_press_event', self.on_key_press)

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
        pos = self.host.get_position()



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
        self.par1.text(-0.05,-0.18,"source",horizontalalignment='left',transform=self.host.transAxes)
        self.par1.text(-0.05,-0.25,"rbw",horizontalalignment='left',transform=self.host.transAxes)
        self.par1.spines["bottom"].set_position(("outward", 50))
        self.par1.xaxis.set_ticks_position('bottom')
        self.par1.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
        self.par1.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')

        self.par2 = self.host.twiny()
        self.make_patch_spines_invisible(self.par2)
        self.par2.spines["bottom"].set_position(("outward", 50))
        self.par2.xaxis.set_ticks_position('bottom')
        self.par2.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par2.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par2.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
        self.par2.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5,labelbottom='on')

        self.par3 = self.host.twiny()
        self.make_patch_spines_invisible(self.par3)
        self.par3.text(-0.05,-0.33,"amp",horizontalalignment='left',transform=self.host.transAxes)
        self.par3.text(-0.05,-0.40,"att",horizontalalignment='left',transform=self.host.transAxes)
        self.par3.spines["bottom"].set_position(("outward", 90))
        self.par3.xaxis.set_ticks_position('bottom')
        self.par3.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par3.xaxis.set_minor_formatter(ticker.NullFormatter())
        self.par3.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-10, labelbottom='on')
        self.par3.xaxis.set_tick_params(which='major',length=10,direction='in', pad=-20,labelbottom='on')

        self.par4 = self.host.twiny()
        self.make_patch_spines_invisible(self.par4)
        self.par4.spines["bottom"].set_position(("outward", 90))
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


    def onPick(self, event):
        artist = event.artist
        xmouse, ymouse = event.mouseevent.xdata, event.mouseevent.ydata
        x, y = artist.get_xdata(), artist.get_ydata()
        ind = event.ind

       # print ('Artist picked:', event.artist)
       # print ('{} vertices picked'.format(len(ind)))
       # print ('Pick between vertices {} and {}'.format(min(ind), max(ind)+1))
        title = '{}'.format(event.artist)
        xy = '{:.2f},{:.2f}'.format(xmouse, ymouse)
        data = '{},{}'.format( x[ind[0]], y[ind[0]])

        info = LineInfo(title,xy,data)
        info.show()

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

            # if not self.line1TextFlag:
            #     self.par1.text(-0.05,-0.18,"source",horizontalalignment='left',transform=self.host.transAxes)
            #     self.par1.text(-0.05,-0.25,"rbw",horizontalalignment='left',transform=self.host.transAxes)
            #     self.par1.spines["bottom"].set_position(("outward", 50))
            #     self.par1.xaxis.set_ticks_position('bottom')
            #     self.par1.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
            #     self.par1.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')
            #     self.line1TextFlag = True


    #        self.par1.set_xscale('log')
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

            self.par2.spines["bottom"].set_position(("outward", 50))
            self.par2.xaxis.set_ticks_position('bottom')
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
                 self.par3.text(-0.05,-0.33,"amp",horizontalalignment='left',transform=self.host.transAxes)
                 self.par3.text(-0.05,-0.40,"att",horizontalalignment='left',transform=self.host.transAxes)
                 self.par3.spines["bottom"].set_position(("outward", 90))
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


            self.par4.spines["bottom"].set_position(("outward", 90))
            self.par4.xaxis.set_ticks_position('bottom')
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

            #remember data for interactive user clicks
            self.currentStaticPlotFlag = True
            self.currentStaticPlotCorrList = corrList
            self.currentStaticPlot = data

            for _t in data.traces:
                self.onNewTrace(_t)
                # show Corrections as line
                corrDict = dict(corrList)

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
        print ('Graph: new Plot')
        assert isinstance(data,DB_Handler_TPL3.Tpl3Plot)
        self.host.set_xlim(data.x1,data.x2)
        self.host.set_ylim(data.y1,data.y2)
        self.par1.set_xlim(data.x1,data.x2)
        self.par2.set_xlim(data.x1,data.x2)
        self.par3.set_xlim(data.x1,data.x2)
        self.par4.set_xlim(data.x1,data.x2)
        self.par1.set_xscale('log')
        self.par2.set_xscale('log')
        self.par3.set_xscale('log')
        self.par4.set_xscale('log')
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
            if data.style == '0.0': _width = self.defaultWidth
            if self.backgroundPlot == 'True':
                _color = 'grey'

            line, = self.host.plot(_x, _y, picker=5, label=data.title, color=_color,ls=_style, lw=_width)


            if data.type == "Limit":
                _yTextPos = _y[-1]
                _xTextPos = self.host.get_xlim()[1]
                anz = len(_xys)
                n = 0
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
                if self.corrAntLabel == None:
                    self.corrAntLabel = self.host.text(self.host.get_xlim()[1],self.corrAntYEndPos,'Antenna')
                else:
                    self.corrAntLabel.set_y(self.corrAntYEndPos)
            if data.type == "Cable":
                if self.corrCabLabel == None:
                    self.corrCabLabel = self.host.text(self.host.get_xlim()[1],self.corrCabYEndPos,'Cable')
                else:
                    self.corrCabLabel.set_y(self.corrCabYEndPos)
            if data.type == "Probe":
                if self.corrProbeLabel == None:
                    self.corrProbeLabel = self.host.text(self.host.get_xlim()[1],self.corrProbeYEndPos,'Probe')
                else:
                    self.corrProbeLabel.set_y(self.corrProbeYEndPos)
            #self.figure_canvas.draw()
            self.signalGraphUpdate.emit()



        except Exception as _err:
            print("Graph: onNewLine: {0}".format(str(_err)))
            logging.exception(_err)

    def onNewTrace(self, data):
        print('GRAPH NewTrace autorange:',data.autorange)
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
                _stepFreq = (_stopFreq - _startFreq)/len(_y)
                _x = numpy.array(numpy.linspace(_startFreq,_stopFreq,len(_y)))
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
            if self.backgroundPlot == 'True': _color = 'grey'
            label = "TraceID{}".format(str(data.trace_id))
            self.host.plot(_x, _y, picker=5, label=label, color=_color, ls=_style, lw=_width)

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

        right = 0.9
        top = 0.9
        self.host.text(right, top, data,
            horizontalalignment='right',
            verticalalignment='top',
            fontsize=20, color='red',
            transform=self.host.transAxes)
        self.signalGraphUpdate.emit()


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
            print ('making thumbnail')
            self.fig.savefig('../WorkingDir/Page1.png', format = 'png',dpi=300)
            im = Image.open('../WorkingDir/Page1.png')
            im.thumbnail((150,150))
            im.save("../WorkingDir/ThumbNail.png")


            #image.thumbnail("../WorkingDir/Page1.svg","../WorkingDir/ThumbNail.svg",scale=0.15,interpolation='gaussian')
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
        if self.labelAntenna != None:
            self.labelAntenna.set_position(x,self.parent.corrAntYEndPos)
        else:
            self.labelAntenna = self.parent.host.text(x,self.parent.corrAntYEndPos,'Antenna')
        self.parent.draw()
#        self.parent.host.add_artist(self.labelAntenna)
    def writeCabLabel(self):
        x = self.parent.host.get_xlim()[1]
        if self.labelCable != None:
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
    form = MainForm()
    #right screen pos, show always win-title
    x = rec.width() - 1200 - 10
    y = int(sys.argv[1]) + 40
    form.setGeometry(x,y,1200,700)
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()

