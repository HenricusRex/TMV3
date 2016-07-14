from RT_StandardHF import *
from pydispatch import dispatcher
from NeedfullThings import Signal

class RT_ZoneKMV(RT_StandardHF):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = Signal()
        pass


    def startOfRoutine(sel):
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
        ret = self.checkLimits()
        dispatcher.send(self.signals.MEAS_RESULT, dispatcher.Anonymous, ret)
        print(ret)
        pass

    def checkLimits(self):

        _z1 = False
        _z2 = False
        _z3 = False
        lList = super().getLimitList()
        _ret = len(lList)
        if _ret == 0: return

        for entry in lList:
            if entry.title == 'z1_er_d' and entry.result == True:
                _z1 = True
            if entry.title == 'z1_er_g' and entry.result == True:
                _z1 = True
            if entry.title == 'z2_er_d' and entry.result == True:
                _z2 = True
            if entry.title == 'z2_er_g' and entry.result == True:
                _z2 = True
            if entry.title == 'z3_er_d' and entry.result == True:
                _z3 = True
            if entry.title == 'z3_er_g' and entry.result == True:
                _z3 = True

        if _z1:
            _s = 'Zone 1 '
        elif _z2:
            _s = 'Zone 2'
        elif _z3:
            _s = 'Zone 3'
        else:
            _s ='complies no Zone-Limit'

        return _s

