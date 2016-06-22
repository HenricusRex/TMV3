__author__ = 'Heinz'
#import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.artist
import subprocess
#import matplotlib.pyplot as plt
import math
import shlex
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar2
from matplotlib.ticker import EngFormatter
from NeedfullThings import *
from PyQt4 import *
import logging
import configparser
import DB_Handler_TPL3
from GraphClient import Client
import os
from pydispatch import dispatcher

#process_name = 'Graph'

logging.basicConfig(filename="TMV3log.txt",
                    level=logging.error,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')

class CustomToolbar(NavigationToolbar2):
    def __init__(self,canvas_,parent_):
        self.toolitems = (
            ('Home', 'original scale', 'home', 'home'),
            #('Back', 'consectetuer adipiscing elit', 'back', 'back'),
            #('Forward', 'sed diam nonummy nibh euismod', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'pan', 'move', 'pan'),
            ('Zoom', 'zoom', 'zoom_to_rect', 'zoom'),
            (None, None, None, None),
            ('Print','Print','','onPrint'),
            #('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
            ('Save', 'save to file', 'filesave', 'save_figure'),
            )

        NavigationToolbar2.__init__(self,canvas_,parent_)


    def onPrint(self):
        print('print')


class axisLabel(object):
    def __init__(self,x1,x2,label,log=True):
        self.startX = x1
        self.stopX = x2
        self.label = label
        if log:
            self.labelPos = math.pow(10,(math.log10(x2)-math.log10(x1))/2 + math.log10(x1))
        else:
            self.labelPos = (x2 - x1) / 2 + x1


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)


        # create a figure
layout = QtGui.QVBoxLayout()
fig = Figure((5.0, 4.0), dpi=100)
canvas = FigureCanvas(fig)
canvas.draw()
#figure_canvas = FigureCanvas(Figure())
layout.addWidget(canvas, 10)

        # and the axes for the figure
host = canvas.figure.add_subplot(111)
host.set_axis_bgcolor('#323232')
host.set_ylabel('dBµV')
host.set_xlabel('Hz')
host.grid(True)
host.set_xscale('log')
canvas.draw()

formatterHZ = EngFormatter(unit = '',places=0)
formatterDB = EngFormatter(unit = '',places=1)
host.xaxis.set_major_formatter(formatterHZ)
host.yaxis.set_major_formatter(formatterDB)
navigation_toolbar = CustomToolbar(canvas, None)
#layout.addWidget(navigation_toolbar)

rbwList = []
rbw = axisLabel(1e1,1e2,'100')
rbwList.append(rbw)
rbw = axisLabel(1e2,1e3,'1k')
rbwList.append(rbw)
rbw = axisLabel(1e3,1e4,'10k')
rbwList.append(rbw)
rbw = axisLabel(1e4,1e5,'100k')
rbwList.append(rbw)
rbw = axisLabel(1e5,1e6,'1M')
rbwList.append(rbw)

x2=[]
x2pos=[]
labels2=[]
j = -1
x2pos.append(0)
labels2.append('')

for i in rbwList:
    if i.startX > j:
        x2.append(i.startX)
        j = i.startX
    x2.append(i.stopX)
    x2pos.append(i.labelPos)
    labels2.append(i.label)

sensorList = []
sensor = axisLabel(1e1,2e3,'Ant1')
sensorList.append(sensor)
sensor = axisLabel(2e3,2e5,'Ant2')
sensorList.append(sensor)
sensor = axisLabel(2e5,1e6,'Ant3')
sensorList.append(sensor)

x1=[]
x1pos=[]
labels1=[]
j = -1
x1pos.append(0)
labels1.append('')

for i in sensorList:
    if i.startX > j:
        x1.append(i.startX)
        j = i.startX
    x1.append(i.stopX)
    x1pos.append(i.labelPos)
    labels1.append(i.label)
    print(i.label,i.labelPos)


AmpAttList = []
AmpAtt = axisLabel(1e1,1e2,'10/10')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(1e2,1e3,'10/10')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(1e3,1e4,'0/10')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(1e4,1e5,'0/10')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(1e5,2e5,'0/10')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(2e5,3e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(3e5,4e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(4e5,5e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(5e5,6e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(6e5,7e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(7e5,8e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(8e5,9e5,'0/20A')
AmpAttList.append(AmpAtt)
AmpAtt = axisLabel(9e5,1e6,'0/20A')
AmpAttList.append(AmpAtt)

x3=[]
x3pos=[]
labels3=[]
j = -1
x3pos.append(0)
labels3.append('')
last3 = ''
for i in AmpAttList:
    if i.startX > j:
        x3.append(i.startX)
        j = i.startX
    x3.append(i.stopX)
    if i.label != last3:
        x3pos.append(i.labelPos)
        labels3.append(i.label)
        last3 = i.label


#x2 = [1,100,100,1000,1000,10000]
#x12 = [1,100,1000,10000]
#labels = ['1kHz','100kHz','1MHz','10MHz']

#par1high = host.twiny()
par1 = host.twiny()
par2 = host.twiny()
par3 = host.twiny()
# par4 = host.twiny()


par1.spines["bottom"].set_position(("outward", 50))
par1.xaxis.set_ticks_position('bottom')
par1.set_xlim(10,1e6)
par1.set_xscale('log')
par1.xaxis.set_major_formatter(ticker.NullFormatter())
par1.xaxis.set_minor_locator(ticker.FixedLocator(x1pos))
par1.xaxis.set_minor_formatter(ticker.FixedFormatter(labels1))
par1.xaxis.set_ticks(x1)
par1.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
par1.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')


par2.spines["bottom"].set_position(("outward", 50))
par2.xaxis.set_ticks_position('bottom')
par2.set_xlim(10,1e6)
par2.set_xscale('log')
par2.xaxis.set_major_formatter(ticker.NullFormatter())
par2.xaxis.set_minor_locator(ticker.FixedLocator(x2pos))
par2.xaxis.set_minor_formatter(ticker.FixedFormatter(labels2))
par2.xaxis.set_tick_params(which='minor',length=1,direction='out', pad=5, labelbottom='on')
par2.xaxis.set_tick_params(which='major',length=10,direction='out', pad=5, labelbottom='on')

par3.spines["bottom"].set_position(("outward", 90))
par3.xaxis.set_ticks_position('bottom')
par3.set_xlim(10,1e6)
par3.set_xscale('log')
par3.xaxis.set_major_formatter(ticker.NullFormatter())
par3.xaxis.set_minor_locator(ticker.FixedLocator(x3pos))
par3.xaxis.set_minor_formatter(ticker.FixedFormatter(labels3))
par3.xaxis.set_ticks(x3)
par3.xaxis.set_tick_params(which='minor',length=1,direction='in', pad=-15, labelbottom='on')
par3.xaxis.set_tick_params(which='major',length=10,direction='in', pad=20,labelbottom='on')


#host.text(0.5, 0.95, 'VS - Nur für den Dienstgebrauch',transform=host.transFigure,fontsize=14, verticalalignment='top', horizontalalignment='center', color='blue')
#host.text(0.05, 0.9, 'EUT: Testgerät',transform=host.transFigure,fontsize=11, verticalalignment='top', horizontalalignment='left', color='black')
#host.text(0.05, 0.87, 'Serial-No: 01234546',transform=host.transFigure,fontsize=11, verticalalignment='top', horizontalalignment='left', color='black')
#host.text(0.05, 0.84, 'Model-No: 01234546',transform=host.transFigure,fontsize=11, verticalalignment='top', horizontalalignment='left', color='black')
#host.text(0.05, 0.81, 'Model-Name: Heinz',transform=host.transFigure,fontsize=11, verticalalignment='top', horizontalalignment='left', color='black')
#host.text(0.05, 0.78, 'Testprocedure: ZONE KMV',transform=host.transFigure,fontsize=11, verticalalignment='top', horizontalalignment='left', color='black')



p1, = host.plot([0, 1, 2], [0, 1, 2], "b-", label="Density")


host.set_xlim(0, 2)
host.set_ylim(0, 2)

host.set_xlabel("Distance")
host.set_ylabel("Density")
host.yaxis.label.set_color(p1.get_color())
#lines = [p1]
#host.legend(lines, [l.get_label() for l in lines])
canvas.draw()

#plt.show()
#fname = 'testprn.png'
#plt.savefig(fname)
#proc = subprocess.Popen(('print {f}').format(f=fname))
