__author__ = 'Heinz'



import matplotlib

import os

from GraphClient import *
from PyQt4.QtGui import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from NeedfullThings import *

from Graph import Graphics


logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')


#workarount for matplotlib bug if more than 1 axis

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


class GraphViewer(Graphics):
    signalShowTitle = QtCore.pyqtSignal(str)
    signalGraphUpdate = pyqtSignal()
    waitEvent = threading.Event()
    signalPrint = pyqtSignal()
    signalPrintEnd = threading.Event()


    def __init__(self, parent = None):
        Graphics.__init__(self,parent)
        self.parent = parent
        self.create_main_frame()



    def create_main_frame(self):

          self.canvas =  FigureCanvas(self.fig)
          self.canvas2 =  FigureCanvas(self.fig2)
          self.canvas.setParent(self.parent.ui.frame)
          self.canvas.setFocusPolicy(Qt.StrongFocus)
          self.canvas.setFocus()
    #
          self.mpl_toolbar = CustomToolbar(self.canvas, self.parent.ui.mpl,self)
          self.canvas.mpl_connect('pick_event',self.onPick)
          self.canvas.mpl_connect('key_press_event', self.on_key_press)
    #
          self.vbox = QVBoxLayout()
          self.vbox.addWidget(self.canvas)  # the matplotlib canvas
          self.vbox.addWidget(self.canvas2)  # the matplotlib canvas
          self.vbox.addWidget(self.mpl_toolbar)
          self.parent.ui.frame.setLayout(self.vbox)
    #
    # #
          self.fig.clear()
    #
          self.genPlotPage()
          self.genTextPage()
          self.canvas.setVisible(True)
          self.canvas2.setVisible(False)
          self.canvas.setFocusPolicy(Qt.StrongFocus)
          self.canvas.setFocus()
          self.page = 1
          self.signalGraphUpdate.emit()

    def genImage(self):
        self.fig.savefig('../WorkingDir/Page1.png', format='png')

