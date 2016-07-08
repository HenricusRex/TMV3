# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 15:42:53 2013

@author: HS
"""
from pydispatch import dispatcher
from NeedfullThings import Signal
import sqlite3 as lite
import sys
import ast
import logging
import pickle
from datetime import datetime, timedelta
from EngFormat import Format


from PyQt4.QtGui import QMessageBox


logging.basicConfig(filename="TMV3log.txt",
                    level=logging.ERROR,
                    format='%(asctime)s %(message)s',
                    datefmt='%m.%d.%Y %I:%M:%S')
def changeCharToBool(c):
    if c == 'True':
        return True
    else:
        return False

class Tpl3Filter(object):

    def __init__(self,filename,id):
        self.filter_id = id
        self.filename = filename
        self.title = "?"
        self.type = "?"
        self.company = "?"
        self.group = "?"
        self.plot_title = "?"
        self.routine = "?"
        self.project = "?"
        self.text = "?"
        self.zuNo = "?"
        self.testNo = "?"
        self.testID = "?"
        self.dateFrom = "?"
        self.dateTo = "?"
        self.andor = "?"
        self.sql = "?"
        self.comment = "?"
        self.date = "?"

    def read(self):
        _error_text = 'can not read Sessions of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Filter]  WHERE [Filter].[FilterID] = {0}".format(str(self.filter_id)))
            _session = _cur.fetchone()
            _r = RegFieldNames(_cur,_session)
            self.filter_id = _r.FilterID
            self.title = _r.Title
            self.type = _r.Type
            self.company = _r.Company
            self.group = _r.Group
            self.plot_title = _r.PlotTitle
            self.routine = _r.Routine
            self.project = _r.Project
            self.text = _r.Text
            self.zuNo = _r.ZuNo
            self.testNo = _r.TestNo
            self.testID = _r.TestID
            self.dateFrom = _r.dateFrom
            self.dateTo = _r._dateTo
            self.andor = _r.AndOr
            self.sql = _r.SQL
            self.comment = _r.Comment
            self.date = _r.Date

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def readTitle(self,title):
        _error_text = 'can not read Sessions of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Filter]  WHERE [Filter].[Title] = '{0}'".format(title))
            _filter = _cur.fetchone()
            if _filter == None: return 0
            _r = RegFieldNames(_cur,_filter)
            self.filter_id = _r.FilterID
            self.title = _r.Title
            self.type = _r.Type
            self.company = _r.Company
            self.group = _r.Group
            self.plot_title = _r.PlotTitle
            self.routine = _r.Routine
            self.project = _r.Project
            self.zuNo = _r.ZuNo
            self.testNo = _r.TestNo
            self.testID = _r.TestID
            self.dateFrom = _r.DateFrom
            self.dateTo = _r.DateTo
            self.andor = _r.AndOr
            self.sql = _r.SQL
            self.comment = _r.Comment
            self.date = _r.Date

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("INSERT INTO [Filter] (Title, Type, Company, [Group], PlotTitle, Routine, Project, Text, ZuNo,"
                         "TestNo, TestID, DateFrom, DateTo, AndOr, SQL, Comment, Date ) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (self.title, self.type, self.company, self.group, self.plot_title, self.routine,
                        self.project, self.text, self.zuNo, self.testNo, self.testID,
                        self.dateFrom, self.dateTo, str(self.andor), self.sql, self.comment, self.date))
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0
        return _lastRowID


class Tpl3Sessions(object):

    def __init__(self,filename,session_id):
        self.session_id = session_id
        self.filename = filename
        self.title = ""
        self.sqlReverence = ""
        self.sqlCurrent = ""
        self.text = ""
        self.math = ""
        self.idList = []
    def read(self):
        _error_text = 'can not read Sessions of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Sessions]  WHERE [Sessions].[ID] = {0}".format(str(self.session_id)))
            _session = _cur.fetchone()
            _r = RegFieldNames(_cur,_session)
            self.session_id = _r.ID
            self.title = _r.Title
            self.sqlReverence = _r.SQLReverence
            self.sqlCurrent = _r.SQLCurrent
            self.text = _r.Text
            self.mathIDs = _r.Math

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def readIDs(self):
        _error_text = 'can not read Sessions of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT ID,Title FROM [Sessions]  WHERE [Sessions].[ID] = {0}".format(str(self.session_id)))
            self.idList = _cur.fetchall()
        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("INSERT INTO [Sessions] (Title,SQLReference,SQLCurrent,Text,Math) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (str(self.title),str(self.sqlReverence), str(self.sqlCurrent), str(self.text), str(self.math)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

class Tpl3Relais(object):
    def __init__(self,filename,id):
        self.id = id
        self.filename = filename
        self.title = ""
        self.device = ""
        self.command = ""
        self.comment = ""
        self.relaisIDs = []

    def readIDs(self):
        _error_text = 'can not read Relais of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()

            _cur.execute ("SELECT [ID] FROM [Relais]")
            self.relaisIDs = _cur.fetchall()

        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def read(self):
        _error_text = 'can not read Relais of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Relais] " +
                  "WHERE [Relais].[ID] = " + str(self.id))
            _relais = _cur.fetchone()
            _r = RegFieldNames(_cur,_relais)
            self.id = _r.ID
            self.title = _r.Title
            self.device = _r.Device
            self.command = _r.Command
            self.comment = _r.Comment

        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

class Tpl3Routes(object):
    def __init__(self,filename,id):
        self.id = id
        self.filename = filename
        self.alias = ""
        self.antennaID = ""
        self.cableID = ""
        self.probeID = ""
        self.relaisID = ""
        self.comment = ""
        self.alias_list = []

    def readIDs(self):
        _error_text = 'can not read Route of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()

            _cur.execute ("SELECT [Alias] FROM [Routes]")
            self.alias_list = _cur.fetchall()

        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def read(self):
        _error_text = 'can not read Route of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Routes] " +
                  "WHERE [Routes].[ID] = " + str(self.id))
            _route = _cur.fetchone()
            _r = RegFieldNames(_cur,_route)
            self.alias = _r.Alias
            self.antennaID = _r.AntennaID
            self.cableID = _r.CableID
            self.probeID = _r.ProbeID
            self.relaisID = _r.RelaisID
            self.comment = _r.Comment


        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readAlias(self):
        _error_text = 'can not read Route of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Routes] " +
                  "WHERE [Routes].[Alias] = '{0}'".format(str(self.alias)))
            _route = _cur.fetchone()
            if _route != None:
                _r = RegFieldNames(_cur,_route)
                self.id = _r.ID
                self.alias = _r.Alias
                self.antennaID = _r.AntennaID
                self.cableID = _r.CableID
                self.probeID = _r.ProbeID
                self.relaisID = _r.RelaisID
                self.comment = _r.Comment


        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("INSERT INTO [Routes] (Alias,AntennaID,CableID,ProbeID,RelaisID,Comment)"
                         "VALUES (?, ?, ?, ?, ?, ?)",
                         (str(self.alias), str(self.antennaID), str(self.cableID), str(self.probeID),
                          str(self.relaisID), str(self.comment)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0,0
        return 1,_lastRowID

    def delete(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute("DELETE  from [Routes]"
                        "WHERE [Routes].[Alias] = '{0}'".format(str(self.alias)))
            _con.commit()
            _con.close()
        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0,0
        return 1,0

    def update(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("UPDATE [Routes] Set Alias=?,AntennaID=?,CableID=?,ProbeID=?,RelaisID=?,"
                         "Comment=? WHERE ID=?",
                        (str(self.alias), str(self.antennaID), str(self.cableID), str(self.probeID),
                         str(self.relaisID), str(self.comment),str(self.id)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

class Tpl3Files(object):

    def __init__(self,filename,file_id):
        self.file_id = file_id
        self.filename = filename #name of workbench
        self.crc = 0
        self.test_id = 0
        self.data = None
        self.type = ""
        self.title = ""
        self.comment = ""
        self.version = ""
        self.destination = ''
        self.date = 0


    def read(self,title = '',version=''):
        _error_text = 'can not read Files of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            if title == '':
                _cur.execute ("SELECT * FROM [Files] WHERE [Files].[FileID] = {0}".format(str(self.file_id)))
            else:
                _cur.execute ("SELECT * FROM [Files] WHERE [Files].[Title] = '{0}' AND "
                                                        "[Files].[Version] = '{1}'".format(title,version))

            _file = _cur.fetchone()
            if _file == None:
               return(0)

            _r = RegFieldNames(_cur,_file)
            self.title = _r.Title
            self.type = _r.Type
            self.test_id = _r.TestID
            self.crc = _r.CRC
            self.data = _r.Data
            self.file_id = _r.FileID
            self.comment = _r.Comment
            self.version = _r.Version
            self.date = _r.Date

        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

    def add(self):

        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute("INSERT INTO Files (Title, CRC, Data, Type, TestID, Date,Version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (str(self.title),str(self.crc),self.data,str(self.type),str(self.test_id),str(self.date),str(self.version)))
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

    def modify(self):
        pass

    def delete(self):
        pass

    def export(self):
        _error_text = 'can not export File of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT Data FROM [Files] WHERE [Files].[FileID] = {0}".format(str(self.file_id)))
            _file = _cur.fetchone()
            output_file = open(self.destination,"wb")
            output_file.write(_file[0])

        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return (0)
        _cur.close()
        _con.close()
        return(1)

class Tpl3Marks(object):

    def __init__(self,filename,mark_id):
        self.mark_id = mark_id
        self.filename = filename
        self.x = 0
        self.x = 0
        self.marker_text = ""

    def read(self):
        _error_text = 'can not read Marks of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Marks] WHERE [Marks].[MarkID] = {0}".format(str(self.mark_id)))
            _mark = _cur.fetchone()
            _r = RegFieldNames(_cur,_mark)
            self.x = _r.X
            self.y = _r.Y
            self.marker_text = _r.MarkerText

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

class Tpl3Lines(object):
    #all lines like Limits, CorrectionLines, etc
    #will be added by 'add Plan'; selected by Name and Version
    #Plot gets LineID as Link
    def __init__(self,filename,line_id):
        self.line_id = line_id
        self.filename = filename
        self.type = ""
        self.title = ""
        self.version = ""
        self.color = ""
        self.width = 0
        self.style = ""
        self.data_xy = ""
        self.used = 0
        self.date = ""
        self.serialNo = ""
        self.comment = ""
        self.lineIDs = []

    def read(self):
        _error_text = 'can not read Lines of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Lines] " +
                  "WHERE [Lines].[LineID] = " + str(self.line_id))
            _line = _cur.fetchone()
            _r = RegFieldNames(_cur,_line)
            self.type = _r.Type
            self.title = _r.Title
            self.version = _r.Version
            self.color = _r.Color
            self.width = _r.Width
            self.style = _r.Style
            self.data_xy = _r.DataXY
            self.used = _r.Used
            self.date = _r.Date
            self.comment = _r.Comment


        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readIDs(self):
        _error_text = 'can not read Lines of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [LineID] FROM [Lines] " +
                  "WHERE [Lines].[Type] = '{0}'".format(str(self.type)))
            self.lineIDs = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readCorrIDs(self):
        _error_text = 'can not read Lines of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [LineID] FROM [Lines] " +
                  "WHERE ([Lines].[Type]='Antenna' OR [Lines].[Type]='Cable' OR [Lines].[Type]='Probe')")
            self.lineIDs = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readPlotCorr(self):
        #read all corr-lines of plot x
        _error_text = 'can not read Lines of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Lines] " +
                  "WHERE [Plot].Traces[]"
                  "WHERE [Lines].[LineID] = " + str(self.line_id))
            _line = _cur.fetchone()
            _r = RegFieldNames(_cur,_line)
            self.type = _r.Type
            self.title = _r.Title
            self.version = _r.Version
            self.color = _r.Color
            self.width = _r.Width
            self.style = _r.Style
            self.data_xy = _r.DataXY
            self.used = _r.Used
            self.date = _r.Date
            self.comment = _r.Comment


        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readLimitIDs(self):
        _error_text = 'can not read Lines of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [LineID] FROM [Lines] WHERE ([Lines].[Type]='Limit')")
            self.lineIDs = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
    def readLimitTitles(self):
        _error_text = 'can not read Lines of TPL3 %s '
        ret = []
        try:
            _con = lite.connect(self.filename)
            #_con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [Title],[Version] FROM [Lines] WHERE ([Lines].[Type]='Limit')")
            ret = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return 0,ret

        _con.close()
        return 1,ret

    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute("INSERT INTO [lines] ([Type],Title,Version,Color,Width,Style,DataXY,Used,[Date],Comment)"
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (str(self.type), str(self.title), str(self.version), str(self.color), str(self.width),
                          str(self.style), str(self.data_xy), str(self.used), str(self.date), str(self.comment)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0,0
        return 1,_lastRowID

    def exists(self):

        self.line_id = 0
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            if self.type =='Limit':
                _s = ("SELECT [Lines].[LineID] FROM [Lines]  WHERE [Lines].[Title]='{0}' "
                      "AND [Lines].[Version] = '{1}' AND [Lines].[Type]='{2}'"
                      .format(str(self.title),str(self.version),str(self.type)))
            else:
                _s = ("SELECT [Lines].[LineID] FROM [Lines]  WHERE [Lines].[Title]='{0}' "
                      "AND [Lines].[Version] = '{1}' AND [Lines].[Date]='{2}' AND [Lines].[Type]='{3}'"
                      .format(str(self.title),str(self.version),str(self.date),str(self.type)))
            _cur.execute (_s)
            self.line_id = _cur.fetchone()
            _con.close()
            if self.line_id == None:
                self.line_id = 0
            else:
                self.read()

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return 1


    def update(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("UPDATE [Lines] Set Used = Used + 1 WHERE LineID={1}".format(str(self.used), str(self.line_id)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

class Tpl3Traces(object):

    def __init__(self,filename,trace_id):
        self.trace_id = trace_id
        self.plotID = 0
        self.tdsID = 0
        self.filename = filename
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.amplifier = 0
        self.attenuator = 0
        self.rbw = 0
        self.autorange = 0
        self.hf_overload = 0
        self.if_overload = 0
        self.uncal = 0
        self.color = 0
        self.data_y = None
        self.data_xy = None
        self.data_xy_mode = ""
        self.CorIDs = []
        self.routine = ""
    def read(self):
        _error_text = 'can not read Traces of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Traces]  WHERE [Traces].[TraceID] = {0}".format(str(self.trace_id)))
            _trace = _cur.fetchone()
            _r = RegFieldNames(_cur,_trace)
            self.plotID = _r.PlotID
            self.tdsID = _r.TdsID
            self.x1 = _r.X1
            self.x2 = _r.X2
            self.y1 = _r.Y1
            self.y2 = _r.Y2
            self.amplifier = _r.Amplifier
            self.attenuator =_r.Attenuator
            self.rbw = _r.RBW
            self.autorange = changeCharToBool(_r.Autorange)
            self.hf_overload = changeCharToBool(_r.HFOverload)
            self.if_overload = changeCharToBool(_r.IFOverload)
            self.uncal = changeCharToBool(_r.Uncal)
            self.color = _r.Color
            self.data_y = _r.DataY
            self.data_xy = _r.DataXY
            self.data_xy_mode = _r.DataXYMode
            self.corIDs = _r.CorIDs
            self.routine = _r.Routine

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def readCorrIDs(self, plotID):
        error_text = 'can not read Traces of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT [CorIDS] FROM [Traces]  "
                          "INNER JOIN [Plot] on [Plot].[PlotID] = [Traces].[PlotID] "
                          "WHERE [Plot].[PlotID] = {0}".format(str(plotID)))
            ret = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_err)
            logging.exception(_err)
            return None

        _con.close()
        return ret
    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("INSERT INTO [Traces] (PlotID,TdsID,X1,X2,Y1,Y2,Amplifier,Attenuator,RBW,Autorange,HFOverload,"
                         "IFOverload,Uncal,Color,DataY,DataXY,DataXYMode,CorIDs,Routine)"
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (str(self.plotID),str(self.tdsID),str(self.x1), str(self.x2), str(self.y1), str(self.y2), str(self.amplifier),
                         str(self.attenuator),str(self.rbw),str(self.autorange),str(self.hf_overload),str(self.if_overload),str(self.uncal),str(self.color),
                         str(self.data_y),str(self.data_xy),str(self.data_xy_mode),
                         str(self.corIDs),self.routine))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

class Tpl3Plot(object):
    def __init__(self,filename,plot_id):
        self.plot_id = plot_id
        self.test_id = 0
        self.date_time = ""
        self.technician = ""
        self.eut = ""
        self.serial_no = ""
        self.model_no = ""
        self.model_name = ""
        self.test_no = ""
        self.user_no = ""
        self.plan_title = ""
        self.plot_title = ""
        self.routines = ""
        self.lines = [] #IDs
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.log = 0
        self.unit = ""
        self.annotations = ""
        self.comment = ""
        self.tmv3_version = ""
        self.plot_no = 0
        self.meas_no = 0
        self.group = ""
        self.result = ""
        self.image= None
        self.company = ""
        self.sources = ""
        self.lineObjects = []
        self.marks = []
        self.traces = []
        self.filename = filename

    def read(self):

        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not read TPL3 %s '

            _cur.execute ("SELECT  * FROM [Plot] WHERE [Plot].[PlotID] = " + str(self.plot_id))
            _plot = _cur.fetchone()
            _r = RegFieldNames(_cur, _plot)
            self.plot_id = _r.PlotID
            self.test_id = _r.TestID
            self.date_time = _r.DateTime
            self.technician = _r.Technician
            self.eut = _r.EUT
            self.serial_no = _r.SerialNo
            self.model_no = _r.ModelNo
            self.model_name = _r.ModelName
            self.test_no = _r.TestNo
            self.user_no = _r.UserNo
            self.plan_title = _r.PlanTitle
            self.plot_title = _r.PlotTitle
            self.routines = _r.Routines
            self.lines = _r.Lines
            self.x1 = _r.X1
            self.x2 = _r.X2
            self.y1 = _r.Y1
            self.y2 = _r.Y2
            self.log = _r.Log
            self.unit = _r.Unit
            self.annotations = _r.Annotations
            self.comment = _r.Comment
            self.tmv3_version = _r.TMV3Version
            self.plot_no = _r.PlotNo
            self.meas_no = _r.MeasNo
            self.group = _r.Group
            self.result = _r.Result
            self.image= _r.Image
            self.company = _r.Company
            self.sources = _r.Sources



            # read all Traces
            _cur.execute ("SELECT TraceID FROM [Traces] WHERE [Traces].[PlotID] = {0}".format(str(self.plot_id)))
            _rows=_cur.fetchall()
            for _row in _rows:
              _t = Tpl3Traces(self.filename,_row[0])
              if _t.read() == 0:
                  return 0
              self.traces.append(_t)

            # read all Marks
            _cur.execute ("SELECT MarkID FROM [Marks] WHERE [Marks].[PlotID] = {0}".format(str(self.plot_id)))
            _rows=_cur.fetchall()
            for _row in _rows:
              _t = Tpl3Marks(self.filename,_row[0])
              if _t.read() == 0:
                  return 0
              self.marks.append(_t)

            # read all Lines
            if len(self.lines) > 0:
                _lineIDs = eval (self.lines)
                for _ID in _lineIDs:
                    _line = Tpl3Lines(self.filename,_ID)
                    if _line.read() == 0:
                        return 0
                    self.lineObjects.append(_line)


        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _stext = "final"
            _cur.execute("INSERT INTO [Plot] (TestID,EUT,SerialNo,UserNo,DateTime,"
                           "Technician,PlanTitle,PlotTitle,Routines,Lines,"
                           "X1,X2,Y1,Y2,Log,"
                           "Unit,Annotations,Comment,TMV3Version,PlotNo,"
                           "Image,MeasNo,[Group],Result,ModelNo,ModelName,TestNo,Company,Sources) "
                           "VALUES (?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?, ?,?,?,?,? )",
                           (str(self.test_id), self.eut, self.serial_no, self.user_no, str(self.date_time),
                            self.technician, self.plan_title, self.plot_title, self.routines, self.lines,
                            str(self.x1), str(self.x2), str(self.y1), str(self.y2), str(self.log),
                            self.unit,self.annotations, self.comment, self.tmv3_version, str(self.plot_no),
                            self.image,str(self.meas_no),self.group,self.result,
                            self.model_no,self.model_name,self.test_no,self.company,self.sources))


            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0
        self.plot_id = _lastRowID
        return True
    def delete(self):
        try:
            _con = lite.connect(self.filename)
            _con.execute("PRAGMA foreign_keys = ON")
            _cur = _con.cursor()
            _cur.execute("DELETE FROM [Plot] WHERE PlotID={0}".format( str(self.plot_id)))
            _con.commit()
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return str(self.plot_id)
        pass
    def updateLines(self,lineID):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT Lines FROM [Plot] WHERE PlotID={0}".format( str(self.plot_id)))
            _ret = _cur.fetchone()
            if (_ret != None) and (_ret != ""):
                self.lines = ast.literal_eval(_ret)
            self.lines.append(lineID)
            _s=("UPDATE [Plot] Set Lines='{0}' WHERE PlotID={1}".format(str(self.lines), str(self.plot_id)))
            _cur.execute(_s)

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID
    def updateResult(self,result):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _s=("UPDATE [Plot] Set Result='{0}' WHERE PlotID={1}".format(str(result), str(self.plot_id)))
            _cur.execute(_s)
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID
    def updateRoutine(self,routine):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _s=("UPDATE [Plot] Set Routines='{0}' WHERE PlotID={1}".format((routine), str(self.plot_id)))
            _cur.execute(_s)
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID
    def updateImage(self):
        print("update")
        try:
            _f = open("../WorkingDir/ThumbNail.png",'rb')
            _image = _f.read()
            _f.close()
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _s=("UPDATE [Plot] Set [Image]=? WHERE PlotID={0}".format(str(self.plot_id)))
            _cur.execute(_s,(_image,))
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID

    def updateGroup(self,group):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _s=("UPDATE [Plot] Set [Group]='{0}' WHERE PlotID={1}".format(str(group), str(self.plot_id)))
            _cur.execute(_s)
            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _lastRowID
    def findMasterPlot(self):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT PlotID FROM [Plot] WHERE TestID={0} AND PlotTitle='{1}'".format(str(self.test_id),self.plot_title))
            _ret = _cur.fetchone()
            _con.close()
            if _ret == None:
                return 0
            else:
                self.plot_id = _ret
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret
    def findGroups(self):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT DISTINCT [Group] FROM [Plot]")
            _ret = _cur.fetchall()
            print (_ret)
            _con.close()
            if _ret == None:
                return 0

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret
    def findPlotTitle(self):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT DISTINCT [PlotTitle] FROM [Plot]")
            _ret = _cur.fetchall()
            print (_ret)
            _con.close()
            if _ret == None:
                return 0

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret

class Tpl3PlotInfo(object):
    def __init__(self,filename,plot_id):
        self.plot_id = plot_id
        self.test_id = 0
        self.date_time = ""
        self.technician = ""
        self.eut = ""
        self.serial_no = ""
        self.user_no = ""
        self.plan_title = ""
        self.plot_title = ""
        self.routines = ""
        self.annotations = ""
        self.plot_no = 0
        self.meas_no = 0
        self.group = ""
        self.result = ""
        self.image= None
        self.filename = filename
        self.ids = []
        self.signals = Signal()

    def read(self):

        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not read TPL3PlotInfo %s '
            _cur.execute ("SELECT  * FROM [Plot] WHERE [Plot].[PlotID] = {0}".format(str(self.plot_id)))
            _plot = _cur.fetchone()
            _r = RegFieldNames(_cur, _plot)
            self.plot_id = _r.PlotID
            self.test_id = _r.TestID
            self.date_time = _r.DateTime
            self.technician = _r.Technician
            self.eut = _r.EUT
            self.serial_no = _r.SerialNo
            self.user_no = _r.UserNo
            self.plan_title = _r.PlanTitle
            self.plot_title = _r.PlotTitle
            self.routines = _r.Routines
            self.annotations = _r.Annotations
            self.plot_no = _r.PlotNo
            self.meas_no = _r.MeasNo
            self.group = _r.Group
            self.result = _r.Result
            self.image= _r.Image

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            dispatcher.send(self.signals.ERROR_MESSAGE,dispatcher.Anonymous,str(_err))
            logging.exception(_err)
            return 0

        _con.close()
        return 1
    def readIDs(self):
        _error_text = 'can not read PlotsIDs of TPL3'
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [PlotID] FROM [Plot] " +
                  "WHERE [Plot].[TestID] = '{0}'".format(str(self.test_id)))
            self.ids = _cur.fetchall()

        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            dispatcher.send(self.signals.ERROR_MESSAGE,dispatcher.Anonymous,_error_text)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

class TPL3Info(object):
    # TPL3 handler for short information to get Plot-Overview
    def __init__(self,filename):
        self.filename = filename
        self.plot_list = []
        pass

    def read(self):
        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not read TPL3 %s '
            _cur.execute ("SELECT PlotID FROM [Plot]")
            _plot_ids = _cur.fetchall()
            for _id in _plot_ids:
                _plot =  Tpl3PlotInfo(self.filename, _id[0])
                if _plot.read() == 0 :
                    return 0
                self.plot_list.append(_plot)##

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_error_text % self.filename)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class TPL3Test(object):
    def __init__(self,filename, test_id):
        self.filename = filename
        self.test_id = test_id
        self.project_id = 0
        self.test_no = ""
        self.category = ""
        self.group = ""
        self.setup = '?'
        self.eut = "?"
        self.serial_no = "?"
        self.model_no = "?"
        self.model_name = "?"
        self.user_no = "?"
        self.environment = "?"
        self.company = "?"
        self.technician = "?"
        self.lab = "?"
        self.result = "?"
        self.procedure = "?"
        self.label_no = "?"
        self.tempest_z_no = '?'
        self.report_no = "?"
        self.date_time = ""
        self.comment = "comment"
        self.type_of_user = 0
        self.type_of_test = 0
        self.type_of_eut = 0
        self.ids = []
        self.plan_list = []
        self.readMode = ""

    def readNext(self,category):
        self.readMode = 'next'
        return self.read(category)

    def readPrev(self,category):
        self.readMode = 'prev'
        return self.read(category)

    def readFirst(self,category):
        self.readMode = 'first'
        return self.read(category)

    def readLast(self,category):
        self.readMode = 'last'
        return self.read(category)

    def read(self,category=None):

        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
          #  _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _error_text = 'can not read TPL3Test %s '

            if self.readMode == '':
#                _s = ("SELECT * FROM [Tests] WHERE [Tests].[TestID] = {0} AND [Tests].[Category] = '{1}'".format(str(self.test_id),str(category)))
                _s = ("SELECT * FROM [Tests] WHERE [Tests].[TestID] = {0}".format(str(self.test_id)))
              #  print(_s)
                _cur.execute (_s)

            if self.readMode == 'prev':
                _cur.execute ("SELECT * FROM [Tests] WHERE [Tests].[TestID] < {0} AND [Tests].[Category] = '{1}' ORDER BY [Tests].[TestID] DESC LIMIT 1".format(str(self.test_id),str(category)))
                self.readMode = ''

            if self.readMode == 'next':
                _cur.execute ("SELECT * FROM [Tests] WHERE [Tests].[TestID] > {0} AND [Tests].[Category] = '{1}' ORDER BY [Tests].[TestID] ASC LIMIT 1".format(str(self.test_id),str(category)))
                self.readMode = ''

            if self.readMode == 'first':
                _cur.execute ("SELECT * FROM [Tests] WHERE [TestID] = (SELECT MIN([TestID]) FROM [Tests]) AND [Tests].[Category] = '{0}'".format(str(category)))
                self.readMode = ''

            if self.readMode == 'last':
                _s = ("SELECT * FROM [Tests] WHERE [TestID] = (SELECT MAX([TestID]) FROM [Tests]) AND [Tests].[Category] = '{0}'".format(str(category)))
                _cur.execute (_s)
                self.readMode = ''

            _test = _cur.fetchone()
            if _test != None:
                _r = RegFieldNames(_cur, _test)
                self.test_id = _r.TestID
                self.test_no = _r.TestNo
                self.project_id = _r.ProjectID
                self.setup = _r.Setup
                self.procedure = _r.Procedure
                self.category = _r.Category
                self.group = _r.Group
                self.eut = _r.EUT
                self.serial_no = _r.SerialNo
                self.model_no = _r.ModelNo
                self.model_name = _r.ModelName
                self.environment =  '?'
                self.environment = _r.Environment
                self.user_no = _r.UserNo
                self.company = _r.Company
                self.lab = _r.Lab
                self.technician = _r.Technician
                self.date_time = _r.DateTime
                self.result = _r.Result
                self.tempest_z_no = _r.TempestZNo
                self.label_no = _r.LabelNo
                self.report_no = _r.ReportNo
                self.comment = _r.Comment
                self.type_of_user = _r.TypeOfUser
                self.type_of_test = _r.TypeOfTest
                self.type_of_eut = _r.TypeOfEut

                _cur.execute ("SELECT FileID,Title,Version,Date,Comment FROM [Files] WHERE [Files].[TestID] = {0} AND [Files].[Type] = 'Testplan'".format(str(self.test_id)))
                self.plan_list = _cur.fetchall()
             #       _test =  TPL3Test(self.filename, _id[0])
             #       if _test.read() == 0 :
             #           return 0
             #       self.test_list.append(_test)

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_error_text, _err)
            _con.close()
            logging.exception(_err)
            return 0

        _con.close()
        return 1

    def findCategory(self):

        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _error_text = 'can not read TPL3Test %s '
            _s = ("SELECT TestID FROM [Tests] WHERE [Tests].[Category] = '{0}'".format(str(self.category)))

            _cur.execute (_s)
            self.ids = _cur.fetchall()

        except Exception as _err:
            print (_error_text % self.filename)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

    def findCompany(self):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT DISTINCT [Company] FROM [Tests]")
            _ret = _cur.fetchall()
            _con.close()
            if _ret == None:
                return 0

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret

    def findProjects(self):
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT DISTINCT [Project] FROM [Tests]")
            _ret = _cur.fetchall()
            _con.close()
            if _ret == None:
                return 0

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret

    def updateTestNo(self):
        'only for tests: generate testNo from date'
        try:
            _con = lite.connect(self.filename)
           # _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT [TestID],[DateTime] FROM [Tests]")
            _ret = _cur.fetchall()
            for x,y in _ret:
                _id = x
                _dt = datetime.strptime(y, "%Y-%m-%d %H:%M:%S")
                _no = 'BS-' + self.getNumber(_dt)
                _cur.execute("Update [Tests] SET TestNo='{0}' Where TestID={1}".format(_no ,_id))
                _con.commit()
            _con.close()
            if _ret == None:
                return 0

        except  Exception as _err:
            logging.exception(_err)
            return 0
        return _ret

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

    def new(self):
        _error_text = 'can not open TPL3 '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
           # _cur.execute("Select count() FROM Tests")
            _error_text = 'can not open TPL3Test %s '
            _cur.execute("INSERT INTO Tests DEFAULT VALUES")
            _con.commit()
            self.test_id = _cur.lastrowid
            _cur.execute("UPDATE Tests SET TestNo = '{0}' WHERE TestID={1}".format(self.test_no, self.test_id))
            _con.commit()
            #self.test_id = _cur.lastrowid

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            print (_error_text +"%s" %self.filename)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

    def delete(self):
        try:
            _con = lite.connect(self.filename)
            _con.execute("PRAGMA foreign_keys = ON")
            _cur = _con.cursor()
            _cur.execute("DELETE FROM [Tests] WHERE TestID={0}".format( str(self.test_id)))
            _con.commit()
            _con.close()
        except  Exception as _err:
            logging.exception(_err)
            return 0
        return str(self.test_id)
        pass

        pass
    def update(self):
        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not update TPL3Test %s '
            _s = ("UPDATE Tests SET TestNo='{0}',ProjectID='{1}',Setup='{2}',Category='{3}',EUT='{4}',SerialNo='{5}',"
                  "ModelNo='{6}',ModelName='{7}',UserNo='{8}',ReportNo='{9}',Environment='{10}',"
                  "TempestZNo='{11}',Company='{12}',Technician='{13}',Lab='{14}',Procedure='{15}',Result='{16}',LabelNo='{17}',"
                  "DateTime='{18}',Comment='{19}',TypeOfUser='{20}',TypeOfTest='{21}',TypeOfEut='{22}',[Group]='{24}' "
                  "WHERE TestID={23}". format(self.test_no, self.project_id,self.setup,self.category, self.eut,self.serial_no,
                                              self.model_no,self.model_name,self.user_no,self.report_no,self.environment,
                                              self.tempest_z_no,self.company,self.technician,self.lab,self.procedure,self.result,self.label_no,
                                              self.date_time,self.comment,self.type_of_user, self.type_of_test,self.type_of_eut,
                                              str(self.test_id),self.group))

            _cur.execute(_s)
            _con.commit()

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            print (_error_text % self.filename)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class Tpl3Projects(object):
    def __init__(self,filename,id):
        self.id = id
        self.filename = filename
        self.title = ""
        self.type = ""
        self.comment = ""
        self.ids = []
        self.test_ids = []
        self.readMode = ''

    def readIDs(self):
        _error_text = 'can not read Project of TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()

            _cur.execute ("SELECT [ProjectID] FROM [Projects]")
            self.ids = _cur.fetchall()

        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

    def readNext(self):
        self.readMode = 'next'
        return self.read()

    def readPrev(self):
        self.readMode = 'prev'
        return self.read()

    def readFirst(self):
        self.readMode = 'first'
        return self.read()

    def readLast(self):
        self.readMode = 'last'
        return self.read()

    def read(self):

        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not read TPL3Project %s '

            if self.readMode == '':
                _cur.execute ("SELECT * FROM [Projects] WHERE [Projects].[ProjectID] = {0}".format(str(self.id)))
                _project = _cur.fetchone()

            if self.readMode == 'prev':
                _cur.execute ("SELECT * FROM [Projects] WHERE [Projects].[ProjectID] < {0} ORDER BY [Projects].[ProjectID] DESC LIMIT 1".format(str(self.id)))
                self.readMode = ''
                _project = _cur.fetchone()
                if _project == None:
                    self.readMode = 'first'

            if self.readMode == 'next':
                _cur.execute ("SELECT * FROM [Projects] WHERE [Projects].[ProjectID] > {0} ORDER BY [Projects].[ProjectID] ASC LIMIT 1".format(str(self.id)))
                self.readMode = ''
                _project = _cur.fetchone()
                if _project == None:
                    self.readMode = 'last'

            if self.readMode == 'first':
                _cur.execute ("SELECT * FROM [Projects] WHERE [Projects].[ProjectID] = (SELECT MIN(ProjectID) FROM [Projects])")
                self.readMode = ''
                _project = _cur.fetchone()

            if self.readMode == 'last':
                _cur.execute ("SELECT * FROM [Projects] WHERE [Projects].[ProjectID] = (SELECT MAX(ProjectID) FROM [Projects])")
                self.readMode = ''
                _project = _cur.fetchone()

            if _project != None:
                _r = RegFieldNames(_cur,_project)
                self.id = _r.ProjectID
                self.title = _r.Title
                self.type = _r.Type
                self.comment = _r.Comment
                _cur.execute ("SELECT TestID FROM [Tests] WHERE [Tests].[ProjectID] = '{0}'".format(str(self.id)))
                _ids = _cur.fetchall()
                self.test_ids.clear()
                for i in _ids:
                    self.test_ids.append(i[0])

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_error_text, _err)
            _con.close()
            logging.exception(_err)
            return 0

        _con.close()
        return 1

    def add(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("INSERT INTO [Projects] (Title,Type,Comment)"
                         "VALUES (?, ?, ?)",
                         (self.title, self.type, self.comment))

            _con.commit()
            _lastRowID = _cur.lastrowid
            self.id = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return 0,0
        return 1,_lastRowID

    def update(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()

            _cur.execute("UPDATE [Projects] Set Title=?,Type=?,Comment=?"
                         "WHERE ProjectID=?",
                        (self.title, self.type, self.comment,str(self.id)))

            _con.commit()
            _lastRowID = _cur.lastrowid
            _con.close()
        except  Exception as _err:
            print (_err)
            logging.exception(_err)
            return 0
        return _lastRowID
class TPL3TestInfo(object):
    # TPL3 handler for short information about all Test
    def __init__(self,filename):
        self.filename = filename
        self.test_list = []
        pass

    def read(self):
        _error_text = 'can not open TPL3 %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _error_text = 'can not read TPL3 %s '
            _cur.execute ("SELECT TestID FROM [Tests]")
            self.test_list = _cur.fetchall()
         #   _test_ids = _cur.fetchall()
         #   for _id in _test_ids:
         #       _test =  TPL3Test(self.filename, _id[0])
         #       if _test.read() == 0 :
         #           return 0
         #       self.test_list.append(_test)

        except Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print(_error_text % self.filename)
            logging.exception(_err)
            return -1

        _con.close()
        return len(self.test_list)

class RegFieldNames(object):
        def __init__(self, cursor, row):
            try:
                for (attr, val) in zip((d[0] for d in cursor.description), row):
                    setattr(self, attr, val)
            except Exception as _err:
                print (_err)



