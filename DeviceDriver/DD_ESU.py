from DD_Analyzer import SpectrumAnalyzer

class DD_ESU(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('ESU')

        self.preSelectorState = False
        self.stepMode = False
        pass
    def editorGetName(self):
        return('ESU')

    def editorGetBaseCommands(self):
        baseCommands = []
        baseCommands.append(('StartFreq','float','set_StartFreq','validate_StartFreq'))
        baseCommands.append(('StopFreq','float','set_StartFreq','validate_StopFreq'))
        baseCommands.append(('ResBw','set_RewBw'))
        baseCommands.append(('VidBw','set_VidBw'))
        baseCommands.append(('SweepTime','set_SweepTime'))
        baseCommands.append(('PreSelector','set_StartFreq'))
        baseCommands.append(('PreAmplifier','set_StartFreq'))
        baseCommands.append(('PreAmplifier','set_StartFreq'))
        baseCommands.append(('PreAmplifier','set_StartFreq'))


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