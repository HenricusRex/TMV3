from __future__ import print_function
import time
import sys
import math
import numpy as np
import matplotlib
import matplotlib.ticker as ticker
import matplotlib.text
from matplotlib.figure import Figure
from matplotlib.ticker import EngFormatter
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
#from matplotlib.backends import qt4_compat
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
class CustomToolbar(NavigationToolbar):
    def __init__(self,canvas_,parentframe_,parclass):
        self.parclass = parclass
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
            ('ShowPlot', 'show plot', 'page1', 'onShowPlot'),
            (None, None, None, None),
            ('ShowText', 'show text', 'page2', 'onShowText'),
            (None, None, None, None)
            )
        NavigationToolbar.__init__(self,canvas_,parentframe_)
    def onPrint(self):
        self.parclass.a()
    def onShowPlot(self):
        print ('onShowPlot')
#        self.fig.subplots_adjust(bottom=0.25,left=0.07,right=0.93,top=0.8)
#        self.canvas.draw()
        self.parclass.a()
    def onShowText(self):
        print ('onShowText')
#        self.fig.subplots_adjust(bottom=-0.6,left=0.07,right=0.93,top=-0.00)
        self.parclass.b()
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
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        #self.x, self.y = self.get_data()
        self.data = self.get_data2()
        self.sensorList = []
        self.create_main_frame()
       # self.on_draw()


    def a(self):
        print('a')
        self.canvas.setVisible(True)
        self.canvas2.setVisible(False)
        self.mpl_toolbar.canvas=self.canvas

    def b(self):
        print('b')
        self.canvas2.setVisible(True)
        self.canvas.setVisible(False)
        self.mpl_toolbar.canvas=self.canvas2

    def create_main_frame(self):
        self.main_frame = QWidget()

        self.fig = Figure((10.0, 5.0), dpi=100)
        self.fig2 = Figure((10.0, 5.0), dpi=100)
        self.canvas =  FigureCanvas(self.fig)
        self.canvas2 =  FigureCanvas(self.fig2)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        self.mpl_toolbar = CustomToolbar(self.canvas, self.main_frame,self)

        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.canvas)  # the matplotlib canvas
        self.vbox.addWidget(self.canvas2)  # the matplotlib canvas
        self.vbox.addWidget(self.mpl_toolbar)
        self.main_frame.setLayout(self.vbox)
        self.setCentralWidget(self.main_frame)


        self.fig.clear()
        self.genPlotPage()
        self.genTextPage()

    def genTextPage(self):
        _size = 12
        _x = 0.05
        _y = 0.91
        _offset = -0.05
        _header = ["Eut:","Serial-No:","Model-No:","Model-Name:","Test-No:","Test-Date:","Company:",
                   "Technician:","Plan:","Routine:","Sheet:","Annotation:","","","Sources:"]

        for _s in  _header:
            print(_s)
            self.fig2.text(_x,_y,_s,size=_size)
            _y = _y +_offset

    def genPlotPage(self):



        self.host = self.fig.add_subplot(111)
        pos = self.host.get_position()
        print(pos)
       # self.host.set_position([0.2,0.6,0.7,0.3])
        self.fig.subplots_adjust(bottom=0.25,left=0.07,right=0.93,top=0.8)
       # self.host.set_axis_bgcolor('#323232')
        self.host.set_ylabel('dBµV')
        self.host.set_xlabel('Hz')
        self.host.grid(True)
        self.host.set_xscale('log')
        self.host.set_xlim(1e3,1e9)
        self.host.set_ylim(-20,80)

        self.par1 = self.host.twiny()
        #par2 = self.host.twiny()
        #par3 = self.host.twiny()
        # par4 = host.twiny()
        self.make_patch_spines_invisible(self.par1)
        formatterHZ = EngFormatter(unit = '',places=0)
        formatterDB = EngFormatter(unit = '',places=0)
        self.host.xaxis.set_major_formatter(formatterHZ)
        self.host.yaxis.set_major_formatter(formatterDB)
       # self.setTestData()
        self.fig.suptitle("VS-Nfd",color='blue')
        self.host.set_title('Kat C, Test-No: 3F423, Date: 2016.3.1 11:31')
        self.host.text(-0.0,1.2,"EUT:",horizontalalignment='left',transform=self.host.transAxes)
        self.host.text(-0.0,1.12,"Test-No:",horizontalalignment='left',transform=self.host.transAxes)
        font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 9}
        matplotlib.rc('font', **font)

        self.setLineSensor()


    def setLineSensor(self):
        x1=[]
        x1pos=[]
        labels1=[]
        j = -1
        x1pos.append(0)
        labels1.append('')
        self.setTestData()
        for i in self.sensorList:
            if i.startX > j:
                x1.append(i.startX)
                j = i.startX
            x1.append(i.stopX)
            x1pos.append(i.labelPos)
            labels1.append(i.label)
            print(i.label,i.labelPos)

        _pos = self.host.transAxes.transform([0, 0])
        _pos[1] -= 50
        print(_pos)
        _pos2 = self.host.transAxes.inverted().transform(_pos)
        print(_pos2)
        self.par1.text(-0.05,-0.22,"source",horizontalalignment='left',transform=self.host.transAxes)
        self.par1.text(-0.05,-0.3,"rbw",horizontalalignment='left',transform=self.host.transAxes)

        self.par1.spines["bottom"].set_position(("outward", 50))
        self.par1.xaxis.set_ticks_position('bottom')
        self.par1.set_xlim(1e3,1e9)
        self.par1.set_xscale('log')
        self.par1.xaxis.set_major_formatter(ticker.NullFormatter())
        self.par1.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
        self.par1.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
        self.par1.xaxis.set_ticks(x1)
        self.par1.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
        self.par1.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')

        #self.canvas.draw()


    def setTestData(self):
        self.sensor = axisLabel(1e1,2e3,'Ant1')
        self.sensorList.append(self.sensor)
        self.sensor = axisLabel(2e3,2e5,'Ant2')
        self.sensorList.append(self.sensor)
        self.sensor = axisLabel(2e5,1e6,'Ant3')
        self.sensorList.append(self.sensor)

    def get_data2(self):
        return np.arange(20).reshape([4, 5]).copy()

    def on_draw(self):

        #self.axes.plot(self.x, self.y, 'ro')
 #       self.axes.imshow(self.data, interpolation='nearest')
        #self.axes.plot([1,2,3])
  #      self.canvas.draw()
        pass
    def on_key_press(self, event):
        print('you pressed', event.key)
        # implement the default mpl key press events described at
        # http://matplotlib.org/users/navigation_toolbar.html#navigation-keyboard-shortcuts
     #   key_press_handler(event, self.canvas, self.mpl_toolbar)
    def make_patch_spines_invisible(self,ax):
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(True)
        #ax.set_frame_on(False)
       # ax.patch.set_visible(True)
       # for sp in ax.spines.values():
       #     sp.set_visible(True)
class axisLabel(object):
    def __init__(self,x1,x2,label,log=True):
        self.startX = x1
        self.stopX = x2
        self.label = label
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
    y = 0
    #y = int(sys.argv[1]) + 40
    form.setGeometry(x,y,1200,700)
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
