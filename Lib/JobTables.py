import sqlite3 as lite
import os
import configparser
from PyQt4.QtGui import QMessageBox
import logging
import shutil
import pickle


class JobTable (object):
    def __init__(self):
        self.CurrentJob = 0
        self.Active = 0
        self.Name = ""
        self.TreeItem = 0
        self.JobItem = 0
        self.DBIdx = 0
        self.Object = 0
        self.connection = 0
        self.cursor = 0
        self.config = configparser.ConfigParser()
        self.config.read('TMV3.ini')
        self._current_workDir = self.config['Pathes']['workingDir']
        self._jobTablePath = os.path.join(self._current_workDir,'JobTable.TJT3')

    def clean(self):
        try:
            shutil.copyfile("../Templates/TMV3.TJT3",self._jobTablePath)
            con = lite.connect(self._jobTablePath)
            cur = con.cursor()
            cur.execute ("DELETE  FROM Jobs")
            con.commit()
            con.close()
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not clean JobTable ', QMessageBox.Ok)
            logging.exception(err)
            return 0
        return 1

    def resetJobNo(self):
        self.CurrentJob = 0

    def getCurrentJob(self):
        try:
            con = lite.connect(self._jobTablePath)
            cur = con.cursor()
            cur.execute ("SELECT COUNT(*) FROM [Jobs]  WHERE JobItem={0}".format(str(self.CurrentJob)))
            count = cur.fetchone()
           # print("CurrentJob: {0}, {1}".format(str(self.CurrentJob),str(count)))

            if (count[0] == 1) :
                cur.execute ("SELECT * FROM [Jobs]  WHERE JobItem={0}".format(str(self.CurrentJob)))
                job = cur.fetchone()
                r = RegFieldNames(cur,job)
                self.Active = r.Active
                self.Name = r.Name
                self.TreeItem = r.TreeItem
                self.JobItem = r.JobItem
                self.DBIdx = r.DBIdx
                self.Title = r.Title
                self.Object = pickle.loads(r.Object)
            else:
                return False
            con.close()
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not read next Job ', QMessageBox.Ok)
            logging.exception(err)
            return False
        return True

    def getJob(self):

        _found = False
        while not _found:
            _ret = self.getCurrentJob()
            if not _ret: return False
            if self.Active:
                _found = True
            self.CurrentJob += 1
        return  True

    def replaceJob(self):
        if self.CurrentJob > 0 :
            self.CurrentJob -= 1


    def addJob(self,Active,Name,TreeItem,DBIdx,Title,Data):

        dData = pickle.dumps(Data)
        try:
            con = lite.connect(self._jobTablePath)
            cur = con.cursor()
            cur.execute("PRAGMA synchronous = off")
            cur.execute("INSERT INTO Jobs (Active, Name, TreeItem, JobItem, DBIdx,Title,Object) VALUES (?, ?, ?, ?, ?, ?, ?)",(str(Active),Name,str(TreeItem),str(self.CurrentJob),str(DBIdx),Title,dData))
            con.commit()
            con.close()
            self.CurrentJob +=1
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not add Item {0} to JobTable '.format(str(Name)), QMessageBox.Ok)
            logging.exception(err)
            return 0

        return 1

    def beginChangeJob(self):
        try:
            self.connection = lite.connect(self._jobTablePath)
            self.cursor = self.connection.cursor()
            self.cursor.execute("PRAGMA synchronous = off")
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not begin changing JobTable ', QMessageBox.Ok)
            logging.exception(err)
            return 0
        return 1
    def endChangeJob(self):
        self.connection.commit()
        self.connection.close()
    def activateJob(self,JobItem):
        # #print('Activate', JobItem)
        # try:
        #     con = lite.connect(self._jobTablePath)
        #     cur = con.cursor()
        #     cur.execute("PRAGMA synchronous = off")
        #     cur.execute ("UPDATE [Jobs] SET Active = 1 WHERE JobItem = {0}".format(str(JobItem)))
        #     con.commit()
        #     con.close()
        #
        # except  Exception as err:
        #     QMessageBox.information(None, 'TMV3',
        #     'can not activate %s in JobTable ' %JobItem, QMessageBox.Ok)
        #     logging.exception(err)
        #     return 0
        # return 1

        try:
            self.cursor.execute ("UPDATE [Jobs] SET Active = 1 WHERE JobItem = {0}".format(str(JobItem)))
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not activate %s in JobTable ' %JobItem, QMessageBox.Ok)
            logging.exception(err)
            return 0
        return 1


    def deactivateJob(self,JobItem):
        # print('DeActivate', JobItem)
        # try:
        #     con = lite.connect(self._jobTablePath)
        #     cur = con.cursor()
        #     cur.execute("PRAGMA synchronous = off")
        #     cur.execute("UPDATE [Jobs] SET Active = 0 WHERE JobItem = {0}".format(str(JobItem)))
        #     con.commit()
        #     con.close()
        #
        # except  Exception as err:
        #     QMessageBox.information(None, 'TMV3',
        #     'can not deactivate %s in JobTable ' %JobItem, QMessageBox.Ok)
        #     logging.exception(err)
        #     return 0
        # return 1
        try:
            self.cursor.execute ("UPDATE [Jobs] SET Active = 0 WHERE JobItem = {0}".format(str(JobItem)))
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not activate %s in JobTable ' %JobItem, QMessageBox.Ok)
            logging.exception(err)
            return 0
        return 1
    def open(self):
        try:
            self.connection = lite.connect(self._jobTablePath)
            self.cur = self.connection.cursor()
        except  Exception as err:
            QMessageBox.information(None, 'TMV3',
            'can not open JobTable ', QMessageBox.Ok)
            logging.exception(err)
            return 0
        return 1

    def save(self):
        self.connection.close()
        pass
class RegFieldNames(object):
        def __init__(self, cursor, row):
            for (attr, val) in zip((d[0] for d in cursor.description), row):
                setattr(self, attr, val)