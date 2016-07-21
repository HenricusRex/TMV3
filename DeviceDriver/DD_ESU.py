from DD_Analyzer import SpectrumAnalyzer

class DD_ESU(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('ESU')

        self.preSelectorState = False
        self.stepMode = False
        pass


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return 1

    def set_PreAmplifier (self,*par):
        # setting the Amplifier is not possible, if Preselector = OFF
        _ret = super().get_PreselectorState()
        if not _ret:
            return True
        self.set_AmplifierState(par)
        return True

    def set_PreSelector (self,*par):
        self.set_PreselectorState(par)
        return True

    def get_PreAmplifier(self):
        if self.get_PreselectorState():
            return self.get_AmplifierState()
        else:
            return False

    def set_StepTime(self,sec):
        if self.stepMode == False:
            super().set_SweepTime(sec)