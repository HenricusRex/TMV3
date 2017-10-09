from DD_Analyzer import SpectrumAnalyzer
from NeedfullThings import  BaseCommand

class DD_ESIB(SpectrumAnalyzer):
    def __init__(self):
        super(DD_ESIB,self).__init__('ESIB')

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

    def setup(self):
        try:
            #Initiate Service Request
            if not self.checkStatusCode(self.sa.write("*CLS")): return False      #Reset status reporting system
            if not self.checkStatusCode(self.sa.write("*SRE 96")): return False  #Permit service request for STAT:OPER,STAT:QUES and ESR registe
            if not self.checkStatusCode(self.sa.write("*ESE 1")): return False   #Set event enable bit for command, execution, device-dependent, Operation Complete
                                    #and query error
            if not self.checkStatusCode(self.sa.write("STAT:OPER:ENAB 0")): return False  #Set OPERation enable bit for all events
            if not self.checkStatusCode(self.sa.write("STAT:OPER:PTR 32767")): return False   #Set appropriate OPERation Ptransition bits
            if not self.checkStatusCode(self.sa.write("STAT:QUES:ENAB 0")): return False  #Set questionable enable bits for all events
            if not self.checkStatusCode(self.sa.write("STAT:QUES:PTR 32767")): return False   #Set appropriate questionable Ptransition bits

            if not self.checkStatusCode(self.sa.write("*RST")): return False

            if not self.checkStatusCode(self.sa.write("INST:SEL SAN; *WAI")): return False #SpectrumAnalyser nMode
            if not self.checkStatusCode(self.sa.write("SYSTEM:DISP:UPDATE ON; *WAI")): return False
            if not self.checkStatusCode(self.sa.write("INIT:CONT OFF; *WAI")): return False
            if not self.checkStatusCode(self.sa.write("INP:ATT 30DB; *WAI")): return False
            if not self.checkStatusCode(self.sa.write("SENSE:DET:FUNC POS; *WAI")): return False
            if not self.checkStatusCode(self.sa.write("UNIT:POW DBUV; *WAI")): return False


        except Exception as _err:
            s = "Analyzer setup error \n {0}".format(_err)
            self.showMessage(s)
            return False

        return True

    def set_ResBW(self,*par:['1','2','3','5',
                   '10','20','30','50',
                   '100','200','300','500',
                   '1k','2k','3k','5k',
                   '10k','20k','30k','50k',
                   '100k','200k','300k','500k',
                   '1M','2M','3M','5M','10M']):
        return(super().set_ResBW(par))


    def set_VidBW(self,*par:['auto','1','2','3','5',
                   '10','20','30','50',
                   '100','200','300','500',
                   '1k','2k','3k','5k',
                   '10k','20k','30k','50k',
                   '100k','200k','300k','500k',
                   '1M','2M','3M','5M','10M']):
        return(super().set_VidBW(par))

    def set_Attenuator(self,*par:'S0'):
        return (super().set_Attenuator(par))

    def set_StartFreq(self,*par:'S3'):
        f = float(*par[0])
        return super().set_StartFreq(f)

    def set_StopFreq(self,*par:'S3'):
        return super().set_StopFreq(par)

    def set_PreAmplifier (self,*par:['On','Off']):
        # setting the Amplifier is not possible, if Preselector = OFF
        _ret = super().get_PreselectorState()
        if not _ret:
            return False
        self.set_AmplifierState(par)
        return True

    def get_PreAmplifier(self):
        if self.get_PreselectorState():
            return self.get_AmplifierState()
        else:
            return False

    def set_PreSelector (self,*par:['On','Off']):
        self.set_PreselectorState(par)
        return True

    def set_SweepTime(self,*par:'S0'):
        return super().set_SweepTime(par)

    def set_StepTime(self,*par:'S0'):
        return super().set_SweepTime(par)

    def set_RefLevel(self,*par:'S0'):
        return super().set_RefLevel(par)

    def validate(self,*args):
        return True

    def getEditableCommands(self):
        return(self.editableCommands)

    def set_Detector(self,*par:['Max Peak','Min Peak','Average','AC Video']):
        return (super().set_Detector(par))
