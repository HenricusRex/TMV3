import logging
import visa
from PyQt4.QtGui import QMessageBox
from pydispatch import dispatcher
import pickle
from NeedfullThings import Signal
import time
from datetime import datetime
import logging
logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')
import threading

class SpectrumAnalyzer():
    def __init__(self,device_name):
        self.name = device_name
        self.signals = Signal()
        self.devConnectionsString = ""
        self.rm = visa.ResourceManager()
        self.sa = self.rm
        pass

    def checkStatusCode(self,status):
        if str(status).startswith('error') or str(status).startswith('warning'):
            return False
        else:
            return True

    def checkConnection(self):
        #Test given connection
        try:
            self.sa = self.rm.open_resource(self.name)
            #self.sa.open()
            _ret = self.sa.query("*IDN?")
        except visa.VisaIOError as _err:
            _msg = visa.Error(_err)
            logging.exception(_msg)
           # self.showMessage(_msg)
            return False
        return True

    def closeSession(self):
        self.sa.close()

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
            self.showMessage("Analyzer setup error")
            logging.exception(_err)
            return False

        return True


    def handleSRQ(self):
        stb = self.sa.stb
        print (stb)

        if stb > 0:
            if (stb and 16): _ret = self.outputQueue()
            if (stb and 4):  _ret = self.errorQueueHandler()
            if (stb and 8):  _ret = self.questionableStatus()
            if (stb and 128): _ret = self.operationStatus()
            if (stb and 32): _ret = self.esrRead()

        return True

    def waitForEventx(self,ms):
        print ('Visa: wait for srq {0}'.format(str(ms)))
        _ret = self.sa.wait_for_srq()

        if str(_ret).startswith("error"):
            print('Visa: error')
            if _ret == visa.constants.StatusCode.error_timeout:
                self.showMessage(_ret)
        else :
            print('Visa: SRQ')
            _ret = self.handleSRQ()

        return _ret

    def waitForEvent(self,ms):
        _t1 = datetime.now()
        _t2 = _t1
        _td = _t2 - _t1

        while _td.total_seconds() < ms:
            time.sleep(0.2)
            _ret = self.esrRead()
            if _ret :
              #  print('WFE',_td.total_seconds())
                return True
            _td = datetime.now() - _t1
        return False
    def questionableStatus(self):
        pass
    def quesPowerReg(self):
        _ret = self.sa.query("STAT:QUES:POW:COND?")
        _retInt = int(_ret)
        HFOverload = False
        IFOverload = False
        if _retInt & 0x0000:
            HFOverload = True
        if _retInt & 0x0002:
            IFOverload = True

        return HFOverload,IFOverload
    def errorQueueHandler(self):
        _error = self.sa.query("SYSTEM:ERROR?")
        if _error[0] == '0' :
            return True
        else:
            print (_error)
            self.showMessage(str(_error))
            logging.error(_error)
            return False
    def outputQueue(self):
        pass
    def operationStatus(self):
        pass
    def esrRead(self):
        _esr = self.sa.query("*ESR?")
        if int(_esr) & 1:
            return True
        else:
            return False

    def get_HF_Overload(self):
        _ret = self.sa.query("STAT:QUES:POW:COND?")
        _retInt = int(_ret)
        HFOverload = False
        if _retInt & 0x0001:
            HFOverload = True

        return HFOverload


    def get_IF_Overload(self):
        _ret = self.sa.query("STAT:QUES:POW:COND?")
        _retInt = int(_ret)
        IFOverload = False
        if _retInt & 0x0004:
            IFOverload = True

        return IFOverload

    def get_HFIF_Overload(self):
        _ret = self.sa.query("STAT:QUES:POW:COND?")
        _retInt = int(_ret)
        HFOverload = False
        IFOverload = False
        if _retInt & 0x0001:
            HFOverload = True
        if _retInt & 0x0004:
            IFOverload = True

        return HFOverload,IFOverload

    def get_Uncal(self):
        return False
        pass

    def take_HardCopy(self):
        if not self.checkStatusCode(self.sa.write("HCOPY:ITEM:ALL")): return False
        return True

    def take_Sweep(self,s):
        _timeout = s*1000 + 2000 # sweeptime[ms] + spare
        self.set_SweepTime(s)
        self.sa.write("ABORT; INIT:IMM; *OPC;")
        self.waitForEvent(_timeout)
      #  if not self.errorQueueHandler() : return False
        return True
    def take_SweepAuto(self):
        self.sa.write("SENSE:SWEEP:TIME:AUTO ON ")
        _ret = self.sa.query("SENSE:SWEEP:TIME?")
        _timeout  = float(_ret)
        _timeout *= 10
        self.sa.write("ABORT; INIT:IMM; *OPC;")
        if not self.waitForEvent(_timeout):
            print ('timeout')
      #  time.sleep(0.1)
        _ret,value = self.get_maxPeak()
        self.sa.write("SENSE:SWEEP:TIME:AUTO OFF ")
        return _ret,value



    def get_maxPeak(self):
        self.sa.write("CALC:MARK:MAX:PEAK;*WAI;")
        if not self.errorQueueHandler() : return False,0
        _ret = self.sa.query("CALC:MARK:Y?")
        print("max Peak",_ret)
        if not self.errorQueueHandler() : return False,0
        return True,float(_ret)

    def set_TimeOut(self,ms):
        self.sa.timeout = ms
        return True
    def get_Trace(self, *par):
        _result = self.sa.query("Trace? Trace{0};".format(str(par[0])))
        if not self.errorQueueHandler() : return False
        return True, _result

    def set_SweepTimeAuto(self):
        self.sa.write("SENSE:SWEEP:TIME:AUTO ON ")
        if not self.errorQueueHandler() : return False
        return True

    def set_SweepTime(self,fSweepTime):
        sSweepTime = str(fSweepTime) + "S"
        self.sa.write("SENSE:SWEEP:TIME " + sSweepTime)
        if not self.errorQueueHandler() : return False
        return True
        pass
    def get_SweepTime(self):
        ret = self.sa.query("SENSE:SWEEP:TIME?")
        if not self.errorQueueHandler() : return False
        return ret
        pass
    def set_ContSweep(self,bSweepCont):
        if bSweepCont:
            self.sa.write("INIT:CONT ON")
        else:
            self.sa.write("INIT:CONT OFF")

        if not self.errorQueueHandler() : return False

    def set_Detector(self,detector):
        if detector == "Auto Peak":
            self.sa.write("SENSE:DET:FUNC APE")
        elif detector == "Min Peak":
            self.sa.write("SENSE:DET:FUNC NEG")
        elif detector == "Max Peak":
            self.sa.write("SENSE:DET:FUNC POS")
        elif detector == "Sample":
            self.sa.write("SENSE:DET:FUNC SAMP")
        elif detector ==  "RMS":
             self.sa.write("SENSE:DET:FUNC RMS")
        elif detector ==  "Average":
            self.sa.write("SENSE:DET:FUNC AVER")
        elif detector ==  "AC Video":
            self.sa.write("SENSE:DET:FUNC ACV")

    def get_Detector(self):
        ret = self.sa.query ("SENSE:DET:FUNC?")
        if ret == "APE":
            detektor = "Auto Peak"
        elif ret == "NEG":
            detektor = "Min Peak"
        elif ret == "POS":
            detektor = "Max Peak"
        elif ret == "SAM":
            detektor = "Sample"
        elif ret == "RMS":
            detektor = "RMS"
        elif ret == "AVE":
            detektor = "Average"
        elif ret == "ACV":
            detektor = "AC Video"
        return detektor
    def set_CenterFreq (self,fFreq):
        sFreq = str(fFreq) + "HZ"
        self.sa.write("SENSE:FREQ:CENTER " + sFreq)
        if not self.errorQueueHandler(): return False
        return True

    def get_CenterFreq(self):
        sFreq = self.sa.query("SENSE:FREQ:CENTER?")
        return float(sFreq)

    def set_StartFreq (self,*par):

        sFreq = str(par[0]) + "HZ"
        self.sa.write("SENSE:FREQ:START " + sFreq)
        if not self.errorQueueHandler(): return False
        return True

    def get_StartFreq(self):
        sFreq = self.sa.query("SENSE:FREQ:START?")
        return float(sFreq)

    def set_StopFreq (self,*par):
        sFreq = str(par[0]) + "HZ"
        self.sa.write("SENSE:FREQ:STOP " + sFreq)
        if not self.errorQueueHandler(): return False
        return True

    def get_StopFreq(self):
        sFreq = self.sa.query("SENSE:FREQ:STOP?")
        return float(sFreq)

    def set_Span(self,fSpan):
        sSpan = str(fSpan) + "HZ"
        self.sa.write("SENSE:FREQ:SPAN " + sSpan)
        if not self.errorQueueHandler(): return False
        return True

    def get_Span(self):
        sSpan = self.sa.query("SENSE:FREQ:SPAN?")
        return float(sSpan)

    def set_ResBW(self,*par):
        sRBw = str(par[0])
        self.sa.write("SENSE:BAND " + sRBw)
        if not self.errorQueueHandler(): return False
        return True

    def get_ResBW(self):
        sRBw = self.sa.query("SENSE:BAND?")
        return float(sRBw)

    def set_VidBW(self,*par):
        sVBw = str(par[0])
        self.sa.write("SENSE:BAND:VID {0}; *WAI" .format(str(sVBw)))
        if not self.errorQueueHandler(): return False
        return True

    def get_VidBW(self):
        sVBw = self.sa.query("SENSE:BAND:VID?")
        return float(sVBw)

    def set_RefLevel(self,*par):
        sRevLevel=str(par[0])
        self.sa.write("DISP:TRAC:Y:RLEV " + sRevLevel)
        if not self.errorQueueHandler(): return False
        return True
    def get_RefLevel(self):
        ret = self.sa.query("DISP:TRAC:Y:RLEV?")
        if not self.errorQueueHandler(): return False,0
        return True,float(ret)


    def set_Attenuator(self,fAttenuator):
        sAttenuator=str(fAttenuator)
        self.sa.write("INP:ATT " + sAttenuator)
        if not self.errorQueueHandler(): return False
        return True
    def get_Attenuator(self):
        sAtt = self.sa.query("INP:ATT?")
        return float(sAtt)
    def set_AmplifierState (self,*par):
        if par[0] == '1':
            self.sa.write("INP:GAIN:STATE ON; *WAI")
        else:
            self.sa.write("INP:GAIN:STATE OFF; *WAI")

        if not self.errorQueueHandler() : return False
        return True
    def get_AmplifierState(self):
        _sAs= self.sa.query("INP:GAIN:STAT?")
        if _sAs[0] == '1':
            return True
        else:
            return False
    def set_Amplifier(self, *par):
        _sAs= self.sa.query("INP:GAIN:STAT?")
        if _sAs[0] == '0':
            self.sa.write("INP:GAIN:STAT ON")
        self.sa.write ("INP:GAIN {0}; *WAI".format(par[0]))
        if not self.errorQueueHandler() : return False
        return True
    def get_Amplifier(self):
        _sAs= self.sa.query("INP:GAIN?")
        return float(_sAs)

    def set_PreselectorState(self,*par):
        if par[0] == '1':
            self.sa.write("INP:PRES:STAT ON; *WAI")
        else:
            self.sa.write("INP:PRES:STAT OFF; *WAI")

        if not self.errorQueueHandler() : return False
        return True
    def get_PreselectorState(self):
        _sPs= self.sa.query("INP:PRES:STAT?")
        if _sPs[0] == '1':
            return True
        else:
            return False
    def set_Preselector(self, *par):
        _s = ("INP:PRES:SET {0}".format(par[0]))
        self.sa.write(_s)
        if not self.errorQueueHandler() : return False
        return True

    def set_Transducer(self,Title,Unit,Data):

        self.sa.write("CORR:TRAN:SEL '{0}'".format(str(Title)))
        if not self.errorQueueHandler() : return False

        self.sa.write("CORR:TRAN:UNIT 'DB'")
        if not self.errorQueueHandler() : return False

        self.sa.write("CORR:TRAN:SCAL LIN")
        if not self.errorQueueHandler() : return False

        s = "CORR:TRAN:DATA " + Data
        self.sa.write("CORR:TRAN:DATA " + Data)
        if not self.errorQueueHandler() :
            print ('Fehler in setTransducer')
            return False
        return True


    def set_TransducerSet(self,Title,Factors,sUnit,StartFreq,StopFreq):
        s = "CORR:TSET:SEL '{0}'".format(str(Title))
        self.sa.write(s)
        if not self.errorQueueHandler() :
            print("DD_Analyzer: {0} ".format(s))
            #return False

        s = "CORR:TSET:DEL"
        self.sa.write(s)
      #  if not self.errorQueueHandler() :
            #may be, that there is no TSET, so the error is no error
            #print("DD_Analyzer: {0}{1} ".format(s,str(Title)))
            #return False
      #      pass
        self.sa.write("CORR:TSET:UNIT 'DB'")
        if not self.errorQueueHandler() :
            print("DD_Analyzer: {0} ".format(s))
            #return False

     #   s = "CORR:TSET:SEL '{0}'".format(str(Title))
     #   self.sa.write(s)
     #   if self.errorQueueHandler() < 0: return False

        s = "CORR:TSET:RANG1 {0}HZ, {1}HZ ".format(str(StartFreq),str(StopFreq))
        #s = "CORR:TSET:RANG 100MHZ, 200MHZ "
        for e in Factors:
            s += ",'{0}'".format(str(e))
        self.sa.write(s)
        if not self.errorQueueHandler() : return False


        self.sa.write(s)
        s = "CORR:TSET ON"
        self.sa.write(s)
        if not self.errorQueueHandler() : return False

        return True
    def set_TransducerSetState(self,title,state):
        s = "CORR:TSET:SEL '{0}'".format(str(title))
        self.sa.write(s)
        if not self.errorQueueHandler() : return False

        if state:
            self.sa.write("CORR:TEST ON")
            if not self.errorQueueHandler() : return False

        else:
            self.sa.write("CORR:TEST OFF")
            if not self.errorQueueHandler() : return False
        return True


    def set_LimitLine(self,iNr,sName,sUnit,lLimit):
        sLimit = ""
        sNr = str(iNr)
        #delete old Limitlines

        self.sa.write("CALC:LIM" + sNr + ":DEL")
        if not self.errorQueueHandler() : return False

        #set Limitlines
        self.sa.write("CALC:LIM" + sNr + ":NAME '")
        if not self.errorQueueHandler() : return False

        self.sa.write("CALC:LIM" + sNr + ":CONT:DOM FREQ")
        if not self.errorQueueHandler() : return False

        self.sa.write("CALC:LIM" + sNr + ":UNIT " + sUnit)
        if not self.errorQueueHandler() : return False

        self.sa.write("CALC:LIM" + sNr + ":CONTROL:SPACING LIN")
        if not self.errorQueueHandler() : return False

        assert isinstance(lLimit,list)
        n = len(lLimit)
        n = 0
        while n < len(lLimit):
            sLimit += lLimit[n]
            sLimit += ","
            n += 2
        sLimit -= ","

        self.sa.write("CALC:LIM" + sNr + ":CONT " + sLimit)
        if not self.errorQueueHandler() : return False

        sLimit = ""
        n = 1
        while n < len(lLimit):
            sLimit += lLimit[n]
            sLimit += ","
            n += 2
        sLimit -= ","

        self.sa.write("CALC:LIM" + sNr + ":UPP " + sLimit)
        if not self.errorQueueHandler() : return False

        self.sa.write("CALC:LIM" + sNr + ":UPP:STATE ON")
        if not self.errorQueueHandler() :
            return False


    def writeSA(self,*par):
        self.sa.write(par[0])


    def showMessage(self,text):
        s = str(text).replace('\r','')
        s = s.replace('\n','')
        sdata = pickle.dumps(s)
        dispatcher.send(self.signals.SHOW_MESSAGE, dispatcher.Anonymous,sdata)




