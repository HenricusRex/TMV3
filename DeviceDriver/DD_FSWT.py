from DD_Analyzer import SpectrumAnalyzer

class DD_FSWT(SpectrumAnalyzer):
    def __init__(self):
        super().__init__('FSWT')
        self.stepMode = False
        self.editableCommands = ['set_StartFreq',
                                'set_StopFreq',
                                'set_ResBW',
                                'set_VidBW',
                                'set_Attenuator',
                                'set_PreAmplifier',
                                'set_PreSelector',
                                'set_RefLevel',
                                'set_SweepTime',
                                'set_Detector']
        pass



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

    def set_StartFreq(self,*par:'S3'):
        f = float(par[0])
        return super().set_StartFreq(f)

    def set_StopFreq(self,*par:'S3'):
        f = float(par[0])
        return super().set_StopFreq(f)

    def set_RefLevel(self,*par:'S0'):
        return (super()).set_RefLevel(par[0])

    def set_Detector(self,*par:['Max Peak','Min Peak','Average','AC Video']):
        return (super().set_Detector(par[0]))

    def set_Attenuator(self,*par:'S0'):
        return(super().set_Attenuator(par[0]))

    def set_ResBW(self, *par: ['1', '2', '3', '5',
                               '10', '20', '30', '50',
                               '100', '200', '300', '500',
                               '1k', '2k', '3k', '5k',
                               '10k', '20k', '30k', '50k',
                               '100k', '200k', '300k', '500k',
                               '1M', '2M', '3M', '5M',
                               '10M', '20M', '30M', '50M',
                               '100M', '200M', '300M', '500M']):
        return (super().set_ResBW(par[0]))

    def set_VidBW(self,*par:['auto','1','2','3','5',
                   '10','20','30','50',
                   '100','200','300','500',
                   '1k','2k','3k','5k',
                   '10k','20k','30k','50k',
                   '100k','200k','300k','500k',
                   '1M','2M','3M','5M','10M','30M','50M']):
        _vf = float(par[0])
        if _vf > 50e6:
            return (True)
        return(super().set_VidBW(par[0]))

    def set_StepTime(self,*par:'f0'):
        if self.stepMode == False:
            super().set_SweepTime(par[0])

    def set_SweepTime(self,*par:'S0'):
        self.stepMode = False
        return super().set_SweepTime(par[0])

    def set_PreSelector(self,*par:['WIDE','NARROW']):
        _ret = True
        # to make it compatible to FSET with Preselector 'NORMAL'
        _ps = par[0]
        if _ps != 'WIDE':
            _ps = 'NARROW'
        _ret = super().get_PreselectorState()
        if _ret == False:
            super().set_PreselectorState('1')
        _ret = super().set_Preselector(_ps)
        return _ret

    def set_PreAmplifier(self,*par:['0','10','20','30']):
        #if amp == 0:
        #    _ret = super().set_AmplifierState('0')
        #else:
        #    _ret = super().get_AmplifierState()
        #    if _ret == False:
        _ret = super().set_PreselectorState('1')
        if not _ret: return _ret
        _ret = super().set_Amplifier(par[0])
        return _ret


    def get_PreAmplifier(self):
        _ret = super().get_PreselectorState()
        if _ret == False:
            return 0
        if _ret == True:
            _ret =  super().get_Amplifier()
            return _ret

    def set_Attenuator(self,*par:'S0'):
        return (super().set_Attenuator(par[0]))

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

        self.set_Attenuator(30)
        _ret = super().set_PreselectorState('1')
        if not _ret:
            return False,0,0
        self.set_Attenuator(30)
        self.set_Amplifier(0)

        if not (self.setAutoLevel):
            return False,0,0

        _Attn = self.get_Attenuator()
        _Amp = self.get_Amplifier()
#        self.take_SweepAuto()
#        _RF_Overload, _IF_Overload = super().get_HFIF_Overload()
#        while not (_RF_Overload or _IF_Overload) and (_Amp < 30):
#            _tAmp = _Amp + 10
#            super().set_Amplifier(_tAmp)
#            self.take_SweepAuto()
#            _RF_Overload, _IF_Overload = super().get_HFIF_Overload()
#            if not(_RF_Overload or _IF_Overload):
#                _Amp = _tAmp

#        super().set_Amplifier(_Amp)
        return True,_Amp,_Attn


