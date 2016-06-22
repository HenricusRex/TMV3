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

class Limits(object):
    def __init__(self,filename,id_limit):
        self.id_limit = id_limit
        self.filename = filename
        self.title = ''
        self.date = ''
        self.comment = ''
        self.version = ''
        self.dataXY = []

    def read(self):
        _error_text = 'can not read Data of Limit %s '
        try:
            _con = lite.connect(self.filename)
            _cur = _con.cursor()
            _cur.execute ("SELECT * FROM [Limits] " +
                  "WHERE [Limits].[ID] = " + str(self.id_limit))

            _limit = _cur.fetchone()
            _r = RegFieldNames(_cur,_limit)
            self.title = _r.Title
            self.date = _r.Command
            self.version = _r.Version
            self.comment = _r.Comment
            self.dataXY = _r.DataXY
        except  Exception as _err:
            QMessageBox.information(None, 'TMV3',
            _error_text % self.filename, QMessageBox.Ok)
            logging.exception(_err)
            return 0

        _con.close()
        return 1



class RegFieldNames(object):
        def __init__(self, cursor, row):
            for (attr, val) in zip((d[0] for d in cursor.description), row):
                setattr(self, attr, val)


#y=Dataset("test5.db")
#print (Filename)
#y.read()

__author__ = 'HS'
