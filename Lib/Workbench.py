# in this version you should not write to workbench from different processes
# in this version you should not write to workbench from different processes
# there is no concurrency handling

# call from controller will be processed directly
# calls from other processes will be queued


import configparser
import subprocess
import os
from pydispatch import dispatcher
from NeedfullThings import *
from datetime import datetime, timedelta
import queue
#import time
import DB_Handler_TDS3
import DB_Handler_TPL3
import logging
import uuid
import mmap


class Workbench(object):
    def __init__(self,workbench):
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self.signals = Signal()
        self.q = queue.Queue()
        self._current_test = -1
        self._current_plan = -1
        self.name = workbench
        self._current_workDir = ''
        self._run = False
        self.test_no_header = self.config['Welcome']['company_short']


        # if self._name != "":
        #     _ret = self.config['Current']['current_testID']
        #     if _ret != "":
        #         self._current_testID = _ret
        #     _ret = self.config['Current']['current_planID']
        #     if _ret != "":
        #         self._current_planID = _ret
        #     _ret = self.config['Pathes']['workingDir']
        #     if _ret != "":
        #         self._current_workDir = _ret

        dispatcher.connect(self.onCreateNewWorkbench, signal = self.signals.WB_CREATE_NEW_WB, sender = dispatcher.Any)
        dispatcher.connect(self.onCopyWorkbench,self.signals.WB_COPY_WB,dispatcher.Any)
#        dispatcher.connect(self.onAddTest, signal=self.signals.WB_ADD_TEST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTest, signal=self.signals.WB_GET_TEST, sender=dispatcher.Any)
        dispatcher.connect(self.onCloneTest, signal=self.signals.WB_CLONE_TEST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestFirst, signal=self.signals.WB_GET_TEST_FIRST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestPrev, signal=self.signals.WB_GET_TEST_PREV, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestNext, signal=self.signals.WB_GET_TEST_NEXT, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestLast, signal=self.signals.WB_GET_TEST_LAST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestIDs, signal=self.signals.WB_GET_MASTER_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetTestIDs, signal=self.signals.WB_GET_TEST_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetMasterPlot, signal=self.signals.WB_GET_MASTER_PLOT, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectTestIDs, signal=self.signals.WB_GET_PROJECTS_TEST_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProject, signal=self.signals.WB_GET_PROJECT, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectFirst, signal=self.signals.WB_GET_PROJECT_FIRST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectPrev, signal=self.signals.WB_GET_PROJECT_PREV, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectNext, signal=self.signals.WB_GET_PROJECT_NEXT, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectLast, signal=self.signals.WB_GET_PROJECT_LAST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetProjectIDs, signal=self.signals.WB_GET_PROJECT_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetNewProject, signal=self.signals.WB_GET_NEW_POJECT, sender=dispatcher.Any)
        dispatcher.connect(self.onUpdateProject, signal=self.signals.WB_UPDATE_PROJECT,sender=dispatcher.Any)
        dispatcher.connect(self.onDelPlot, signal=self.signals.WB_DEL_PLOT,sender=dispatcher.Any)
        dispatcher.connect(self.onDelTest, signal=self.signals.WB_DEL_TEST,sender=dispatcher.Any)

        dispatcher.connect(self.onGetTestInfo, signal=self.signals.WB_GET_TESTINFO, sender=dispatcher.Any)
        dispatcher.connect(self.onAddPlan, signal=self.signals.WB_ADD_PLAN, sender=dispatcher.Any)
        dispatcher.connect(self.onGetNewTest, signal=self.signals.WB_GET_NEW_TEST, sender=dispatcher.Any)
        dispatcher.connect(self.onGetLine, signal=self.signals.WB_GET_LINE, sender=dispatcher.Any)
        dispatcher.connect(self.onGetLineIDs, signal=self.signals.WB_GET_LINE_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetLineExists, signal=self.signals.WB_GET_LINE_EXISTS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetRoute, signal=self.signals.WB_GET_ROUTE, sender=dispatcher.Any)
        dispatcher.connect(self.onGetRouteIDs, signal=self.signals.WB_GET_ROUTE_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onAddRoute, signal=self.signals.WB_ADD_ROUTE, sender=dispatcher.Any)
        dispatcher.connect(self.onUpdateRoute, signal=self.signals.WB_UPDATE_ROUTE, sender=dispatcher.Any)
        dispatcher.connect(self.onDelRoutes, signal=self.signals.WB_DEL_ROUTE, sender=dispatcher.Any)
        dispatcher.connect(self.onGetRelais, signal=self.signals.WB_GET_RELAIS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetRelaisIDs, signal=self.signals.WB_GET_RELAIS_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetPlotInfoIDs,signal=self.signals.WB_GET_PLOT_INFO_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onGetPlotInfo,signal=self.signals.WB_GET_PLOT_INFO, sender=dispatcher.Any)
        dispatcher.connect(self.onGetPlot,signal=self.signals.WB_GET_PLOT, sender=dispatcher.Any)
        dispatcher.connect(self.onGetPlotCorrIDs,signal=self.signals.WB_GET_PLOT_CORR_IDS, sender=dispatcher.Any)
        dispatcher.connect(self.onSetResult,signal=self.signals.WB_SET_RESULT, sender=dispatcher.Any)
        dispatcher.connect(self.onSetGroup,signal=self.signals.WB_SET_GROUP, sender=dispatcher.Any)
        dispatcher.connect(self.onSetImage,signal=self.signals.WB_SET_IMAGE, sender=dispatcher.Any)


        dispatcher.connect(self.onUpdateTest, signal=self.signals.WB_UPDATE_TEST,sender=dispatcher.Any)
        dispatcher.connect(self.onExportTDS, signal=self.signals.WB_EXPORT_TDS,sender=dispatcher.Any)
        dispatcher.connect(self.onExportTDS, signal=self.signals.WB_EXPORT_FILE,sender=dispatcher.Any)
        dispatcher.connect(self.onExportLimit, signal=self.signals.WB_EXPORT_LIMIT,sender=dispatcher.Any)
        dispatcher.connect(self.onExportCorr, signal=self.signals.WB_EXPORT_CORR,sender=dispatcher.Any)
        dispatcher.connect(self.onGetTicket, signal=self.signals.WB_GET_TICKET,sender=dispatcher.Any)
        dispatcher.connect(self.onNewPlot,signal=self.signals.WB_NEW_PLOT,sender=dispatcher.Any)
        dispatcher.connect(self.onAddLine,signal=self.signals.WB_ADD_LINE,sender=dispatcher.Any)
        dispatcher.connect(self.onAddTrace,signal=self.signals.WB_ADD_TRACE,sender=dispatcher.Any)
        dispatcher.connect(self.onAddMark,signal=self.signals.WB_ADD_MARK,sender=dispatcher.Any)
        dispatcher.connect(self.onAddObject,signal=self.signals.WB_ADD_OBJECT,sender=dispatcher.Any)
#        dispatcher.connect(self.onImportCorr,signal=self.signals.WB_IMPORT_CORE,sender=dispatcher.Any)
#        dispatcher.connect(self.onImportLimit,signal=self.signals.WB_IMPORT_LIMIT,sender=dispatcher.Any)
    #                t = threading.Thread(target = _meas_class.parser)
    #                t.start()

        # Autobackup !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def start(self):
        #queue jobs for workbench
        self._run = True
        while(self._run):
            _job = self.q.get()
            if _job[0] == "AddPlan":
                self.AddPlan(_job[1])
            if _job[0] == "NewPlot":
                self.newPlot(_job[1])
            if _job[0] == "AddLine":
                self.addLine(_job[1])
            if _job[0] == "AddTrace":
                self.addTrace(_job[1])
            if _job[0] == "SetResult":
                self.setResult(_job[1])
            if _job[0] == "SetImage":
                self.setImage(_job[1])

    def stop(self):
        self._run = False

    def onCreateNewWorkbench(self):
        self.q.put("onCreateNewWorkbench")
        pass

    def onCopyWorkbench(self):
        pass

    def refreshTestNo(self):
        _test = DB_Handler_TPL3.TPL3Test(self.name,0)

    def onCloneTest(self,ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.data)
        #get all data from source Test
        _ret = _test.read()
        if _ret == 0:
            ticket.data = None
            return
        #get new Test, old data still exists but with new testID
        _ret = _test.new()
        if _ret == 0:
            ticket.data = None
            return

        #change date and testNo
        d = datetime.now()
        _test.date_time = datetime(d.year,d.month,d.day,d.hour,d.minute,d.second).isoformat(' ')
        _test.test_no = self.test_no_header + '-' + self.getNumber(d)

        _ret = _test.update()
        if _ret == 0:
            ticket.data = None
            return
        else:
            ticket.data = _test


    def onGetNewTest(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,0)
        d = datetime.now()
        _test.date_time = datetime(d.year,d.month,d.day,d.hour,d.minute,d.second).isoformat(' ')
        _test.test_no = self.test_no_header + '-' + self.getNumber(d)
        _ret = _test.new()
        if not _ret:
            ticket.data = None
        else:
            ticket.data = _test
        return

    def onGetTest(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.read(ticket.data)
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onDelTest(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.delete()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = ticket.testID
        pass
    def onDelPlot(self, ticket):
        _plot = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.plotID)
        _ret = _plot.delete()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = ticket.plotID
        pass

    def onGetTestFirst(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.readFirst(ticket.data)
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetTestPrev(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.readPrev(ticket.data)
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetTestNext(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.readNext(ticket.data)
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetTestLast(self, ticket):
        _test = DB_Handler_TPL3.TPL3Test(self.name,ticket.testID)
        _ret = _test.readLast(ticket.data)
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetProjectTestIDs(self,ticket):
        #find all TestIDs of KMV-Masters
        _test = ticket.data
        _ret = _test.findProject()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetTestIDs(self,ticket):
        #find all TestIDs of KMV-Masters
        _test = DB_Handler_TPL3.TPL3Test(self.name,0)
        _test.category = ticket.data
        _ret = _test.findCategory()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _test
        pass

    def onGetMasterPlot(self,ticket):
        #find all TestIDs of KMV-Masters
        _plot = ticket.data
        assert  isinstance(_plot,DB_Handler_TPL3.Tpl3Plot)
        _plot.filename = self.name
        _ret = _plot.findMasterPlot()
        if _ret == 0:
            ticket.data = None
            return 0
        _ret = _plot.read()
        if _ret == 0:
            ticket.data = None
            return 0

        return 1
        pass

    def onGetTestInfo(self,client):
        _test = DB_Handler_TPL3.TPL3TestInfo(self.name)

        _ret = _test.read()
        if _ret == -1:
            dispatcher.send(self.signals.WB_ERROR, dispatcher.Anonymous,client,"not able to get TestInfo")
            return
        if _ret == 0:
            dispatcher.send(self.signals.WB_TESTINFO,dispatcher.Anonymous, client, None)
        else:
            dispatcher.send(self.signals.WB_TESTINFO,dispatcher.Anonymous, client, _test)

        pass

    def onUpdateTest(self,ticket):
       # assert isinstance(test,DB_Handler_TPL3.Tpl3Test)
        _test = ticket.data
        _ret = _test.update()
        if _ret == 0:
            ticket.data = None
    def onUpdateProject(self,ticket):
       # assert isinstance(test,DB_Handler_TPL3.Tpl3Test)
        _project = ticket.data
        _ret = _project.update()
        if _ret == 0:
            ticket.data = None
    def onGetNewProject(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,0)
        _ret = _project.add()
        if not _ret:
            ticket.data = None
        else:
            ticket.data = _project
        return

    def onGetProject(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,ticket.data)
        _ret = _project.read()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onGetProjectFirst(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,ticket.data)
        _ret = _project.readFirst()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onGetProjectPrev(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,ticket.data)
        _ret = _project.readPrev()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onGetProjectNext(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,ticket.data)
        _ret = _project.readNext()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onGetProjectLast(self, ticket):
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,ticket.data)
        _ret = _project.readLast()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onGetProjectIDs(self,ticket):
        #find all TestIDs of KMV-Masters
        _project = DB_Handler_TPL3.Tpl3Projects(self.name,0)
        _project.category = ticket.data
        _ret = _project.readIDs()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _project
        pass

    def onUpdateProject(self,ticket):
        _project = ticket.data
        _ret = _project.update()
        if _ret == 0:
            ticket.data = None


    def onAddPlan(self,plan,id, sender):
        # not queued
        #_command = "AddPlan",plan
        #self.q.put(_command)

        #copy file to memory

        try:
            with open(plan,"r+b") as f:
                _mm = mmap.mmap(f.fileno(), 0)
                _test_plan = DB_Handler_TDS3.DatasetPlan(plan)
                _test_plan.read()

        except Exception as _err:
            dispatcher.send(self.signals.WB_ERROR, self, sender,"not able to add testplan")
            logging.exception(_err)
            return

        _tpl3files = DB_Handler_TPL3.Tpl3Files(self.name, -1)
        _tpl3files.title = _test_plan.title
        _tpl3files.type = 'Testplan'
        _tpl3files.crc = 0
        _tpl3files.data = _mm
        _tpl3files.version = _test_plan.version
        _tpl3files.comment = _test_plan.comment
        _tpl3files.test_id = id

        _ret = _tpl3files.add()
        if _ret == 0:
            dispatcher.send(self.signals.WB_ERROR, self, sender,"not able to add testplan")
        else:
            dispatcher.send(self.signals.WB_OK, self, sender)

    def onExportTDS(self,ticket):
        #exports TestPlan to working dir as 'Active Testplan'
        #exports needed limits to Active Testplan
        #exports needet corrections to Active Testplan
        _tpl3file = ticket.data
        assert isinstance(_tpl3file,DB_Handler_TPL3.Tpl3Files)
        _tpl3file.filename=self.name
#        _dir = os.path.join(self._current_workDir,_destination)
#        _tpl3files = DB_Handler_TPL3.Tpl3Files(self.name, _planID)
        _tpl3file.export()
        #get list Limits


    def AddPlan(self,plan):
        pass
        # copy Plan to Workbench FileTable
        # open Plan and read VersionNo and Date
        # send Information of all linked Plans to


    def onExportCorr(self):
        pass

    def onExportLimit(self):
        pass

    def onGetTicket(self):
        _t = self.getTicket()
        _t.testID = self._current_testID
        _t.planID = self._current_planID
        return self.getTicket()

    def getTicket(self):
        return(Ticket())

    def onNewPlot(self,ticket):
        _command = "NewPlot", ticket
        self.q.put(_command)

    def newPlot(self, ticket):
        assert isinstance(ticket.data,DB_Handler_TPL3.Tpl3Plot)
        _plot = ticket.data
        _plot.filename = self.name
        _ret = _plot.add()
        if not _ret:
            print('WB: Fehler newPlot ')
        ticket.plotID = _plot.plot_id #
        dispatcher.send(self.signals.WB_NEW_PLOT_ID, dispatcher.Anonymous,_plot.plot_id)

    def onAddTrace(self,ticket):
        _command = "AddTrace", ticket
        self.q.put(_command)

    def addTrace(self,ticket):

        assert isinstance(ticket.data, DB_Handler_TPL3.Tpl3Traces)
        _trace = ticket.data
        _trace.filename = self.name
        _trace.plotID = ticket.plotID
        _trace.add()

        _pl = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.plotID)
        _pl.updateRoutine(_trace.routine)

    def onAddLine(self,ticket):
        _command = "AddLine", ticket
        self.q.put(_command)

    def addLine(self,ticket):
        #test whether line already exists. if yes: increment used-Counter
        #if no: add line to line-table
        #last not least, add line to plot
#        assert isinstance(ticket.data, DB_Handler_TPL3.Tpl3Lines)
        _line = ticket.data
        _line.filename = self.name
        # if _line.type == 'Antenna' or _line.type == 'Cable' or _line.type == 'Probe':
        #     _ret = _line.existsCut()
        # else:
        _ret = _line.exists()
        if _ret == 0: return

        if _line.line_id == 0:
            _line.used = 1
            _id = _line.add()
        else:
            _line.update()
        _pl = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.plotID)
        _pl.updateLines(_line.line_id)

    def onSetResult(self,ticket):
        _command = "SetResult", ticket
        self.q.put(_command)
    def onSetImage(self,ticket):
        _command = "SetImage", ticket
        self.q.put(_command)

    def setResult(self,ticket):
        try:
            _plot = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.plotID)
            _plot.updateResult(ticket.data)
        except Exception as _err:
            print (_err)
    def setImage(self,ticket):
        print("WB Set Image 2")
        try:
            _plot = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.plotID)
            _plot.updateImage()
        except Exception as _err:
            print (_err)

        dispatcher.send(self.signals.GRAPH_STOPPED, dispatcher.Anonymous)

    def onSetGroup(self,ticket):
        try:
            _id = ticket.data[0]
            _text = ticket.data[1]
            _plot = DB_Handler_TPL3.Tpl3Plot(self.name,_id)
            _plot.updateGroup(_text)
        except Exception as _err:
            print (_err)

    def onAddMark(self,ticket):
        _command = "AddMark", ticket
        self.q.put(_command)

    def onAddObject(self,ticket):
        _command = "AddObject", ticket
        self.q.put(_command)

    def onGetRouteIDs(self, ticket):
        #reads route from table and return an route object
        _route = DB_Handler_TPL3.Tpl3Routes(self.name,0)
        _ret = _route.readIDs()
        ticket.data = _route
        return
    def onGetRoute(self, ticket):
        #reads route from table and return an route object
        _route = DB_Handler_TPL3.Tpl3Routes(self.name,0)
        _route.alias = ticket.data
        _ret = _route.readAlias()
        ticket.data = _route
        return
    def onDelRoutes(self,ticket):
        _route = DB_Handler_TPL3.Tpl3Routes(self.name,0)
        _route.alias = ticket.data
        _route.delete()
        return
        pass
    def onAddRoute(self,ticket):
        _route = ticket.data
        _route.filename = self.name
        _route.add()
        pass

    def onUpdateRoute(self,ticket):
        _route = ticket.data
        _route.filename = self.name
        _route.update()
        pass

    def onGetLineExists(self,ticket):
        _line = ticket.data
        _line.filename = self.name
        _line.exists()
        return
    def onGetLine(self,ticket):
        #reads lines from table
        _line = DB_Handler_TPL3.Tpl3Lines(self.name,0)
        _line.line_id = ticket.data
        _line.read()
        ticket.data = _line
  #      print("workbench: line gelesen id",_line.line_id)
        return

    def onGetLineIDs(self, ticket):
        #reads route from table and return an route object
        _line = DB_Handler_TPL3.Tpl3Lines(self.name,0)
        _line.type = ticket.data
        _ret = _line.readIDs()
        ticket.data = _line
        return
    def onGetPlotInfo(self,ticket):
        _plot = DB_Handler_TPL3.Tpl3PlotInfo(self.name,ticket.data)
        _plot.plot_id = ticket.data
        _ret = _plot.read()
        ticket.data = _plot
        return
        pass
    def onGetPlotInfoIDs(self,ticket):
        _plot = DB_Handler_TPL3.Tpl3PlotInfo(self.name,0)
        _plot.test_id = ticket.testID
        _ret = _plot.readIDs()
        ticket.data = _plot
        return

    def onGetPlot(self,ticket):
        _plot = DB_Handler_TPL3.Tpl3Plot(self.name,ticket.data)
        _plot.plot_id = ticket.data
        _ret = _plot.read()
        ticket.data = _plot
        return
        pass
    def onGetRelais(self,ticket):
        #reads Relais from table and return an relais object
        _relais = DB_Handler_TPL3.Tpl3Relais(self.name,0)
        _relais.id = ticket.data
        _ret = _relais.read()
        if _ret == 0:
            ticket.data = None
        else:
            ticket.data = _relais
        return

    def onGetRelaisIDs(self, ticket):
        #reads relais from table and return an relais object
        _relais = DB_Handler_TPL3.Tpl3Relais(self.name,0)
        _ret = _relais.readIDs()
        ticket.data = _relais
        return
    def onGetPlotCorrIDs(self, ticket):
        corrIDList = []
        corrList = []
        plotID = ticket.data
        trace = DB_Handler_TPL3.Tpl3Traces(self.name,0)
        ret = trace.readCorrIDs(plotID)
        if ret != None:
            for x in ret:
                for y in x:
                    yi = eval(y)
                    for z in yi :
                        if z not in corrIDList:
                            corrIDList.append(z)

        for i in corrIDList:
            line = DB_Handler_TPL3.Tpl3Lines(self.name,i)
            line.read()
            corrList.append((i, line))
        ticket.data = corrList

        #    line = DB_Handler_TPL3.Tpl3Lines(self.name,x)


    def getNumber(self,d):
        #get seconds since 2014 converted to base34 (base 36 without I and O)
        db = datetime(2015,1,1,0,0,0,0)
        td = d-db
        sec = int(td.total_seconds())
        alphabet = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ'

        base34 = ''
        while sec:
            sec, i = divmod(sec, 34)
            base34 = alphabet[int(i)] + base34

        return base34
class Ticket():
    def __init__(self):
        self.ticketID = uuid.uuid4()
        self.testID = -1
        self.plotID = -1
        self.planID = -1
        self.data = None
        return