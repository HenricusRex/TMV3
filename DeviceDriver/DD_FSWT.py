import math

from DD_Analyzer import SpectrumAnalyzer

class DD_FSWT(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('FSWT')
        self.stepMode = False
        pass


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return 1
    def setup(self):
        _ret = super().setup()
        if not _ret:
            return False
        #not attenuator protection
        _ret = self.sa.write("INP:ATT:PROT 0")
        #calculate autorange with transducer
        self.sa.write("CORR:TRAN:ADJ:RLEV ON")
        if not _ret:
            return False
        return True



    def set_StepTime(self,sec):
        if self.stepMode == False:
            super().set_SweepTime(sec)

    def set_PreSelector(self,pre):
        _ret = True
        if pre != 'WIDE':
            pre = 'NARROW'
        _ret = super().get_PreselectorState()
        if _ret == False:
            super().set_PreselectorState('1')
        _ret = super().set_Preselector(pre)
        return _ret
    def set_PreAmplifier(self,amp):
        #if amp == 0:
        #    _ret = super().set_AmplifierState('0')
        #else:
        #    _ret = super().get_AmplifierState()
        #    if _ret == False:
        _ret = super().set_AmplifierState('1')
        if not _ret: return _ret
        _ret = super().set_Amplifier(amp)
        return _ret
    def get_PreAmplifier(self):
        _ret = super().get_AmplifierState()
        if _ret == False:
            return 0
        if _ret == True:
            _ret =  super().get_Amplifier()
            return _ret

    def set_VidBW(self,VBw):
        if float(VBw) > 50e6:
            return True
        else:
            _ret =  super().set_VidBW(VBw)
            return _ret

    def setAutoLevel(self):
        self.sa.write("SENSE:ADJUST:LEVEL")
        if not self.errorQueueHandler(): return False
        return True


    def autoRange(self):
        #start position
        _HF_Overload = False
        _IF_Overload = False
        _AMP = 0
        _ATT = 30

        _ret = super().set_AmplifierState('1')
        if not _ret:
            return False,0,0
        if not (self.setAutoLevel):
            return False,0,0
        print('return Autolevel')
        # _ret = self.get_RefLevel()
        #
        # _ref = float(_ret[1])
        #
        # _ret = self.get_maxPeak()
        # _peak = float(_ret[1])
        # _peak = math.ceil(_peak)
        # print('ref,peak',_ref,_peak)
        # if _peak > (_ref -10):
        #     self.set_RefLevel(str(_peak+10))
        #     print ('setRef',(_peak+10))
        _att = self.get_Attenuator()
        _amp = self.get_Amplifier()
        print('_att,_amp',_att,_amp)
        return True,_amp,_att

