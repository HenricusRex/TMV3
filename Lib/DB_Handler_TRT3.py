# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 15:42:53 2013

@author: HS
"""
import sqlite3 as lite
import sys
import logging
from EngFormat import Format


from PyQt4.QtGui import QMessageBox

class Route(object):
    def __init__(self,filename,id):
        self.rt_id = id
        self.filename = filename
        self.alias = ''
        self.antenna = ''
        self.antenna_id = 0
        self.cable = ''
        self.cable_id = 0
        self.adapter = ''
        self.adapter_id = 0
        self.device = ''
        self.device_id = 0
        self.rt_ids = []
    def read(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Route] " +
                  "WHERE [Route].[ID] = " + str(self.rt_id))
            _rt = _cur.fetchone()
            _r = RegFieldNames(_cur,_rt)
            self.alias = _r.Alias
            self.antenna = _r.Antenna
            self.antenna_id = _r.AntenneID
            self.cable = _r.Cable
            self.cable_id = _r.CableID
            self.adapter = _r.Adapter
            self.adapter_id = _r.AdatperID
            self.device = _r.Device
            self.device_id = _r.DeviceID
        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

    def getIDs(self):
        #get all IDs of routes
        try:
            _con = lite.connect(self.filename)
            _con.row_factory = lambda cursor, row: row[0]
            _cur = _con.cursor()
            _cur.execute ("SELECT [ID] FROM [Route]")
            self.rt_ids = _cur.fetchall()
        except  Exception as _err:
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)
class Matrix(object):
    #all lines like Limits, CorrectionLines, etc
    #will be added by 'add Plan'; selected by Name and Version
    #Plot gets LineID as Link
    def __init__(self,filename,id):
        self.mtrx_id = id
        self.filename = filename
        self.device = ""
        self.port = ""
        self.command = ""

    def read(self):
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Matrix] " +
                  "WHERE [Matrix].[ID] = " + str(self.mtrx_id))
            _mtrx = _cur.fetchone()
            _r = RegFieldNames(_cur,_mtrx)
            self.device = _r.Device
            self.port = _r.Port
            self.command = _r.Command
        except  Exception as _err:
            #QMessageBox.information(None, 'TMV3',
            #_error_text % self.filename, QMessageBox.Ok)
            print (_err)
            logging.exception(_err)
            return (0)

        _con.close()
        return(1)

class RegFieldNames(object):
        def __init__(self, cursor, row):
            for (attr, val) in zip((d[0] for d in cursor.description), row):
                setattr(self, attr, val)


#y=Dataset("test5.db")
#print (Filename)
#y.read()

__author__ = 'HS'
