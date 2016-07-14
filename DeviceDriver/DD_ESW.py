from DD_Analyzer import SpectrumAnalyzer

class DD_ESW(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('ESW')

        self.preSelectorState = False
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

        super().set_ContSweep(False)
        return True

    def set_PreSelector(self,pre):
        print('SetPreSelector',pre)
        if (pre == '1'):
            _ret = super().set_PreselectorState('1')
        else:
            _ret = super().set_PreselectorState('0')
        return _ret

    def get_PreSelector(self):
        _ret = super().get_PreselectorState()
        return(_ret)
    def set_PreAmplifier(self,amp):
        print('SetPreAmplifier',amp)

        if (amp == '1'):
            _ret = super().set_PreselectorState('1')
            _ret = super().set_AmplifierState('1')
        else:
            _ret = super().set_AmplifierState('0')
        return _ret
    def get_PreAmplifier(self):
        print('GetPreAmplifier')
        _ret = super().get_AmplifierState()
        if _ret == False:
            return 0
        if _ret == True:
            _ret =  super().get_Amplifier()
            return _ret


    def set_StepTime(self,sec):
        if self.stepMode == False:
            super().set_SweepTime(sec)