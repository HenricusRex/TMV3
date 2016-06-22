__author__ = 'Heinz'

import pypyodbc
import sys,getopt
import sqlite3 as lite
import shutil
import os.path
from datetime import datetime

class ImportLimits():
    def __init__(self):
        pass

    #ts = os.path.getmtime(inputFile)
    #mDate = datetime.fromtimestamp(ts)
    def read(self,sourceDB):

        _conq = pypyodbc.win_connect_mdb(sourceDB)
        _curq = _conq.cursor()
        _curq.execute('SELECT [tTitle],[tComment],[lLimitID] from LIMITS')
        x = _curq.fetchall()
        for n in x:
            _curq.execute('SELECT [dXValue],[dYValue] from LIMITVALUES where [lLimitID] = {0} ORDER by [dXValue]'.format(str(n[2])))
            y = _curq.fetchall()
            print(x,y)

        _conq.close()

