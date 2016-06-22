__author__ = 'Heinz'
from shapely.geometry import LineString,Polygon
from DB_Handler_TPL3 import Tpl3Lines
from pydispatch import dispatcher
from NeedfullThings import Signal
import math
import pickle

class LimitEntry(object):
    def __init__(self,title,data):
        self.title = title
        self.line = data
        self.result = True

class LimitCheck(object):
    def __init__(self):
        self.limitList = []
        self.signals = Signal()

    def testLimit(self,data):
        try:
            for _limit in self.limitList:
                _xyf = eval(_limit.line.data_xy)
                _len = len(_xyf) - 1

                _result = True
                for p in data:
                    for n in  range(_len):
                        x1 = _xyf[n][0]
                        x2 = _xyf[n+1][0]
                        if p[0] >= x1 and p[0] <= x2:
                            ret = self.crossLine(_xyf[n], _xyf[n+1], p)
                            if not ret:
                                _result = False
                                break
                    if not _limit:
                        break


                _limit.result = _result
                if _result :
                    _text = _limit.title + " passed"
                else:
                    _text = _limit.title + " failed"

                self.showMessage(_text)
        except Exception as _err:
            print (_err)
    def crossLine(self, lp1, lp2, p):
        try:
            _y = (lp2[1] - lp1[1]) / math.log10(lp2[0]/ lp1[0]) * math.log10(p[0]/lp1[0]) + lp1[1]
        except Exception as _err:
            print (_err)

        if p[1] >= _y:
            return False
        else:
            return True

    def addLimit(self,line):
        self.limitList.append(LimitEntry(line.title, line))

    def getList(self):

        return self.limitList

    def showMessage(self,text):
        sdata = pickle.dumps(text)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)

