from DD_Analyzer import SpectrumAnalyzer
import math

class DD_FSET(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('FSET')
        self.stepMode = False
        self.Mode22 = False
        self.ResBw = 0
        pass


    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return 1

    def setup(self):
        self.Mode22 = False
        ret = super().setup()
        return ret
    def set_ResBW(self,ResBW):
        self.ResBw = float(ResBW) #remember for autorange
        ret = super().set_ResBW(ResBW)
        return ret

    def set_StepTime(self,sec):
        if self.stepMode == False:
            super().set_SweepTime(sec)

    def set_PreSelector(self,pre):
        # not PreSelector in 22GHZ-Mode
        if self.Mode22: return True

        _ret = True
        if pre != 'WIDE':
            pre = 'NARROW'
        _ret = super().get_PreselectorState()
        if _ret == False:
            super().set_PreselectorState('1')
        _ret = super().set_Preselector(pre)
        return _ret
    def set_PreAmplifier(self,amp):
        if self.Mode22: return
        if amp == 0:
            _ret = super().set_AmplifierState('0')
        else:
            _ret = super().get_AmplifierState()
            if _ret == False:
                super().set_AmplifierState('1')
            _ret = super().set_Amplifier(amp)
        return _ret
    def get_PreAmplifier(self):
        if self.Mode22: return ('20')
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

    def set_StartFreq(self,StartFreq):
        if float(StartFreq) >= 2e9:
            if not self.Mode22: self.set22GHz()
        else:
            if self.Mode22: self.set2GHz()

        super().set_StartFreq(StartFreq)

        pass
    def set22GHz(self):
        super().writeSA("FREQ:RANG 22GHz")
        if not super().errorQueueHandler(): return False
        self.Mode22 = True
        return True

    def set2GHz(self):
        super().writeSA("FREQ:RANG 2GHz")
        if not super().errorQueueHandler(): return False
        self.Mode22 = False
        return True
    def autoRange(self):
        #start position
        _HF_Overload = False
        _IF_Overload = False
        _AMP = 0
        _ATT = 30
        if not (self.set_Attenuator(_ATT)): return False,0,0
        if not self.Mode22:
            if not (self.set_Amplifier(_AMP)):return False,0,0
        _ret,_signal = self.take_SweepAuto()
        if not _ret: return False,0,0

        #calculate amplifier and attenuator and set both for 1. test
        _AMP,_ATT = self.calcAmpAtt(_signal)
        # NoiseSignal = _ATT + 10 * math.log10(self.ResBw / 1000) - 7.3 + 10
        # if _signal < NoiseSignal:
        #     _ATT = _signal - 97
        #     if self.Mode22:
        #         _ATT = _ATT // 10 * 10 + 10
        #         if _ATT < 0:
        #             _ATT = 0
        #     else:
        #         if _ATT < 1:
        #             _ATT = 1

        if not (self.set_Attenuator(_ATT)): return False,0,0
        if not self.Mode22:
            if not (self.set_Amplifier(_AMP)):return False,0,0
        _ret,_signal = self.take_SweepAuto()
        if not _ret: return False,0,0
        _HF_Overload, _IF_Overload = super().get_HFIF_Overload()

        if not (_HF_Overload or _IF_Overload) :
            _AMP,_ATT = self.calcAmpAtt(_signal)
            if not (self.set_Attenuator(_ATT)): return False,0,0
            if not self.Mode22:
                if not (self.set_Amplifier(_AMP)):return False,0,0
            _ret,_signal = self.take_SweepAuto()
            if not _ret: return False,0,0
            _HF_Overload, _IF_Overload = super().get_HFIF_Overload()

        while _HF_Overload or _IF_Overload:
            if _HF_Overload:
                if not self.Mode22: #Mode22 = Amplifier 20dB fix
                    while (_AMP > 0) and _HF_Overload:
                        _AMP -= 10
                        if not (self.set_Amplifier(_AMP)): return False,0,0
                        maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
                        if not (self.set_RefLevel(maxRefLvl)): return False,0,0
                        _ret,_signal = self.take_SweepAuto()
                        if not _ret: return False,0,0
                        _HF_Overload, _IF_Overload = super().get_HFIF_Overload()

                while (_ATT < 60) and _HF_Overload:
                    if _ATT == 1:
                        _ATT += 9
                    else:
                        _ATT += 10

                    if not (self.set_Attenuator(_ATT)): return False,0,0
                    maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
                    if not (self.set_RefLevel(maxRefLvl)): return False,0,0
                    _ret,_signal = self.take_SweepAuto()
                    if not _ret: return False,0,0
                    _HF_Overload, _IF_Overload = super().get_HFIF_Overload()

            if _IF_Overload:
                maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
                if not (self.set_RefLevel(maxRefLvl)): return False,0,0
                _ret,_signal = self.take_SweepAuto()
                if not _ret: return False,0,0
                _HF_Overload, _IF_Overload = super().get_HFIF_Overload()
                while (_ATT < 60) and _IF_Overload:
                    if _ATT == 1:
                        _ATT += 9
                    else:
                        _ATT += 10

                    if not (self.set_Attenuator(_ATT)): return False,0,0
                    maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
                    if not (self.set_RefLevel(maxRefLvl)): return False,0,0
                    _ret,_signal = self.take_SweepAuto()
                    if not _ret: return False,0,0
                    _HF_Overload, _IF_Overload = super().get_HFIF_Overload()


            # signal peak < RefLine
            maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
            if _signal > maxRefLvl:
                _ATT += 10
                if not (self.set_Attenuator(_ATT)): return False,0,0
                maxRefLvl = self.getMaxRefLvl(_ATT,_AMP)
                if not (self.set_RefLevel(maxRefLvl)): return False,0,0
                _ret,_signal = self.take_SweepAuto()
                if not _ret: return False,0,0

        # protect input
     #   if not self.Mode22:
     #       self.set_Amplifier(0)
     #   self.set_Attenuator(30)
        return True,_AMP,_ATT
        pass

    def calcAmpAtt(self,signal):
        _amp = 0
        _att = 0
        if signal >= 137:
            _amp = 0
            _att = 40
        elif (signal >= 128) and (signal < 137):
            _amp = 0
            _att = 40
        elif (signal >= 118) and (signal < 128):
            _amp = 0
            _att = 30
        elif (signal >= 108) and (signal < 118):
            _amp = 0
            _att = 20
        elif (signal >= 98) and (signal < 108):
            _amp = 0
            _att = 10
        elif (signal >= 83) and (signal < 98):
            _amp = 0
            _att = 1
        elif (signal >= 73) and (signal < 83):
            _amp = 10
            _att = 1
        elif (signal >= 58) and (signal < 72):
            _amp = 20
            _att = 1
        else:
            _amp = 30
            _att = 1

        if self.Mode22:
            if _att == 1:
                _att = 0
            _amp = 20

        return(_amp,_att)

    def getMaxRefLvl(self,Att,Amp):
        if Amp == 0:
            _max = 97
        elif Amp == 10:
            _max = 82
        elif Amp == 20:
            _max = 72
        else: #Amp == 30
            _max = 57

        ret = _max + Att
        if (ret) > 137:
            return 137
        else:
            return ret
