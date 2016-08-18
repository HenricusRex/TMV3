# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 15:42:53 2013

@author: HS
"""
import sqlite3 as lite
from pydispatch import dispatcher
import sys
import logging
from EngFormat import Format
from NeedfullThings import Signal


from PyQt4.QtGui import QMessageBox

class DatasetCommand(object):
    def __init__(self,filename,id_command):
        self.id_command = id_command
        self.filename = filename
        self.order = 0
        self.command = ''
        self.parameter = ''

    def read(self):
        _error_text = 'can not read Commands of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Commands] " +
                  "WHERE [Commands].[CommandID] = " + str(self.id_command) +
                  " ORDER BY [Commands].[Order]")

            _command = _cur.fetchone()
            _r = RegFieldNames(_cur,_command)
            self.order = _r.Order
            self.command = _r.Command
            self.parameter = _r.Parameter

        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class DatasetFile(object):
    def __init__(self,filename,id_file):
        self.id_file = id_file
        self.filename = filename
        self.title = ""
        self.type = ""
        self.data = 0

    def read(self):
        _error_text = 'can not read Files of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Files] " +
                  "WHERE [Files].[FileID] = " + str(self.id_file))

            _file = _cur.fetchone()
            _r = RegFieldNames(_cur,_file)
            self.title = _r.Title
            self.type = _r.Type

        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

    def export(self, source, type, destfile):
        _error_text = 'can not export File of TDS3 %s '
        #print(source,type,destfile)
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _s = ("SELECT Data FROM [Files] WHERE [Files].[Title] = '{0}' AND [Files].[Type] = '{1}'".format(str(source),str(type)))
            #_s = ("SELECT Data FROM [Files] WHERE [Files].[Title] = '{0}'".format(str(source)))

            _cur.execute (_s)
            _file = _cur.fetchone()

            if _file != None:
                if isinstance(_file[0], bytes):
                    output_file = open(destfile, 'wb')
                    output_file.write(_file[0])
                else:
                    output_file = open(destfile, 'wt')#, encoding=“utf-8”)
                    output_file.write(str(_file[0]))
            else:
                _cur.close()
                _con.close()
                return 0
        #
        #  output_file = open(destfile,"wt")
        #    output_file.write(_file[0])


        except  Exception as _err:
            print(_err)
            logging.exception(_err)
            return (0)

        _cur.close()
        _con.close()

        return(1)

class DatasetLine(object):
    def __init__(self,filename,id_line):
        self.id_line = id_line
        self.filename = filename
        self.title = ""
        self.color = 0
        self.width = 0
        self.style = 0
        self.type = ""
        self.version = ''
        self.date = ''
        self.dataXY = 0
        self.comment = ''
        self.signals = Signal()

    def readID(self):
        _error_text = 'can not read Line %s ',self.id_line
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Lines] " +
                  "WHERE [Lines].[LineID] = " + str(self.id_line) )

            _line = _cur.fetchone()
            _r = RegFieldNames(_cur,_line)
            self.title = _r.Title
            self.color = _r.Color
            self.width = _r.Width
            self.style = _r.Style
            self.type = _r.Type
            self.dataXY = _r.DataXY
            self.version = _r.Version
            self.date = _r.Date
            self.comment = _r.Comment

        except  Exception as _err:
            dispatcher.send(self.signals.ERROR_MESSAGE, dispatcher.Any,_error_text)
            logging.exception(_err)
            return 0


        _con.close()
        return 1

    def readIDs(self,type):
        ids = []
        _error_text = 'can not read Lines of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute("SELECT [LineID] FROM [Lines] " +
                  "WHERE [Lines].[Type] = '{0}'".format(str(type)))

            ids = _cur.fetchall()

        except  Exception as _err:
            dispatcher.send(self.signals.ERROR_MESSAGE, dispatcher.Any,_error_text)
            logging.exception(_err)
            return 0,ids


        _con.close()
        return 1,ids

    def readTitle(self,title):
        _error_text = 'can not read Lines of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute("SELECT * FROM [Lines] " +
                  "WHERE [Lines].[Title] = '{0}'".format(str(title)))

            _line = _cur.fetchone()
            _r = RegFieldNames(_cur,_line)
            self.title = _r.Title
            self.color = _r.Color
            self.width = _r.Width
            self.style = _r.Style
            self.type = _r.Type
            self.dataXY = _r.DataXY
            self.version = _r.Version
            self.date = _r.Date

        except  Exception as _err:
            dispatcher.send(self.signals.ERROR_MESSAGE, dispatcher.Any,_error_text)
            logging.exception(_err)
            return 0


        _con.close()
        return 1

class DatasetTrace(object):
    def __init__(self,filename,id_trace):
        self.id_trace = id_trace
        self.filename = filename
        self.title = ''
        self.start_freq = 0
        self.stop_freq = 0

    def read(self):
        _error_text = 'can not read Traces of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Traces] " +
                  "WHERE [Traces].[TraceID] = " + str(self.id_trace))
            #" ORDER BY [Traces].[StartFreq]")

            _trace = _cur.fetchone()
            _r = RegFieldNames(_cur,_trace)
            self.start_freq = _r.StartFreq
            self.stop_freq = _r.StopFreq
            _f = Format()
            self.title = _f.FloatToString(self.start_freq,3)+"-"+_f.FloatToString(self.stop_freq,3)
        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class DatasetSetting(object):
    def __init__(self,filename,id_setting):
        self.filename = filename
        self.id_setting = id_setting
        self.title = ""
        self.order = 0
        self.route = ''
        self.instruction = ''
        self.autorange = ''
        self.start_freq = 0
        self.stop_freq = 0
        self.step = 0
        self.step_width = 0
        self.step_time = 0
        self.trace_list = []
        self.command_list = []



    def read(self):
        _error_text = 'can not read Setting of Dataset %s '
        try:
            _error_text = 'can not read Setting of Dataset %s '
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Settings] " +
                    "WHERE [Settings].[SettingID] = {0} ORDER BY [Settings].[Order]".format(str(self.id_setting)))

            _setting = _cur.fetchone()
            _r = RegFieldNames(_cur,_setting)
            self.title = _r.Title
            self.order = _r.Order
            self.route = _r.Route
            self.instruction = _r.Instruction
            self.autorange = _r.Autorange
            self.start_freq = _r.StartFreq
            self.stop_freq = _r.StopFreq
            self.step = _r.Step
            self.step_width = _r.StepWidth
            self.step_time = _r.StepTime

            _cur.execute ("SELECT TraceID FROM [Traces] " +
                  "WHERE [Traces].[SettingID] = {0}".format(str(self.id_setting)))
            _rows = _cur.fetchall()
            for _row in _rows:
                _ret =  DatasetTrace(self.filename,_row[0])
                if _ret.read() == 0 :
                    return 0
                self.trace_list.append(_ret)

            _cur.execute ("SELECT CommandID FROM [Commands] " +
                          "WHERE [Commands].[SettingID] = {0} ORDER BY [Commands].[Order]" .format(str(self.id_setting)))
            _rows = _cur.fetchall()
            for _row in _rows:
                _ret = DatasetCommand(self.filename,_row[0])
                if _ret.read() == 0:
                    return 0
                self.command_list.append(_ret)


        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class DatasetRoutine(object):

    def __init__(self, filename, id_routine):
        self.id_routine = id_routine
        self.filename = filename
        self.title = ''
        self.device1 = ''
        self.device2 = ''
        self.device3 = ''
        self.instruction = ''
        self.instruction_file = ''
        self.signal_class = 0
        self.order = 0
        self.comment = ''
        self.Limits=''
        self.Lines=""
        self.setting_list = []

    def read(self):

        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Routines] " +
                  "WHERE [Routines].[RoutineID] = " + str(self.id_routine) +
                  " ORDER BY [Routines].[Order]")
            _routine = _cur.fetchone()
            _r = RegFieldNames(_cur,_routine)
            self.title = _r.Title
            self.device1 = _r.Device1
            self.device2 = _r.Device2
            self.device3 = _r.Device3
            self.instruction = _r.Instruction
            self.instruction_file = _r.InstructionFile
            self.signal_class = _r.SignalClass
            self.order = _r.Order
            self.limits = _r.Limits
            self.lines = _r.Lines
            self.comment = _r.Comment

            _cur.execute ("SELECT SettingID FROM [Settings] " +
                             "WHERE [Settings].[RoutineID] = " + str(_r.RoutineID))
            _rows = _cur.fetchall()
            for _row in _rows:
                _ret = DatasetSetting(self.filename,_row[0])
                if _ret.read() == 0:
                    return 0
                self.setting_list.append(_ret)

        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            'can not read Routine of Dataset %s ' % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class DatasetPlot(object):

    def __init__(self,filename,id_plot):
        self.id_plot = id_plot
        self.filename = filename
        self.routine_list = []
        self.title = ""
        self.x1 = 0
        self.x2 = 0
        self.y1 = 0
        self.y2 = 0
        self.log = 0
        self.unit = ''
        self.order = 0
        self.annotation = ''
        self.comment = ''

    def read(self):
        _error_text = 'can not read Plot of Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Plots] " +
                  "WHERE [Plots].[PlotID] = " + str(self.id_plot) +
            " ORDER BY [Plots].[Order]")
            _plot = _cur.fetchone()
            _r = RegFieldNames(_cur, _plot)
            self.title = _r.Title
            self.x1 = _r.X1
            self.x2 = _r.X2
            self.y1 = _r.Y1
            self.y2 = _r.Y2
            self.log = _r.Log
            self.unit = _r.Unit
            self.order = _r.Order
            self.annotation = _r.Annotation
            self.comment = _r.Comment

            _cur.execute ("SELECT RoutineID FROM [Routines] " +
                             "WHERE [Routines].[PlotID] = " + str(_r.PlotID))

            _rows=_cur.fetchall()

            for _row in _rows:
                _ret =  DatasetRoutine(self.filename,_row[0])
                if _ret.read() == 0:
                    return 0
                self.routine_list.append(_ret)
        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class DatasetPlan(object):
    def __init__(self,filename):
        self.version = ""
        self.tmv_version = ""
        self.comment = ""
        self.title = ""
        self.operator = ""
        self.kmv = ''
        self.zooning = ''
        self.nato = ''
        self.company = ""
        self.date = ""
        self.plot_list = []
        self.filename = filename



    def read(self):

        _error_text = 'can not open Dataset %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _error_text = 'can not read Dataset %s '

            #_cur.execute ("SELECT * FROM main.Plan")
            _cur.execute ("SELECT * FROM [Plan]")
            _plan = _cur.fetchone()
            _r = RegFieldNames(_cur,_plan)
            self.version = _r.Version
            self.tmv_version = _r.TMVVersion
            self.title = _r.Title
            self.kmv = _r.KMV
            self.zooning = _r.Zooning
            self.nato = _r.NATO
            self.comment = _r.Comment
            self.company = _r.Company
            self.date = _r.Date
            self.operator = _r.Operator


            _cur.execute ("SELECT PlotID FROM [Plots] WHERE [Plots].[PlanID] = " + str(_r.PlanID))
            _rows=_cur.fetchall()
            for _row in _rows:
              _ret = DatasetPlot(self.filename,_row[0])
              if _ret.read() == 0:
                  return 0
              self.plot_list.append(_ret)
        except Exception as _err:
            _s = "can not read DataSet {0} \n" \
                 " {1}".format (self.filename,str(_err))
            QMessageBox.information(None, 'TMV3',_s, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1

class Dataset(object):
    def __init__(self,filename):
        self.filename = filename
        self.db = None
        pass

    def read(self):
        self.db = DatasetPlan(self.filename)
        if self.db.read():
            return self
        else:
            return 0
        #print(self.db.read())
        pass

    def copy(self, dest):

        try:
            _new_db = lite.connect(dest) # create a memory database
            _old_db = lite.connect(self.filename)

            query = "".join(line for line in _old_db.iterdump())

            _new_db.executescript(query)
            _new_db.commit()
            _new_db.close()
            _old_db.close()
        except Exception as _err:
            _s = "can not copy DataSet {0} \n" \
                 " {1}".format (self.filename,str(_err))
            QMessageBox.information(None, 'TMV3',_s, QMessageBox.Ok)
            logging.exception(_err)
            return 0

class RegFieldNames(object):
        def __init__(self, cursor, row):
            for (attr, val) in zip((d[0] for d in cursor.description), row):
                setattr(self, attr, val)


#y=Dataset("test5.db")
#print (Filename)
#y.read()

__author__ = 'HS'
