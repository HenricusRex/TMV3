__author__ = 'heinz'
from PyQt4 import uic,QtGui
from PyQt4.QtCore import *
import configparser
import subprocess
import os
from pydispatch import dispatcher
from NeedfullThings import *
import queue
import random
import sys


class TableModel(QAbstractTableModel):
    def __init__(self, headerdata, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.headers = headerdata
        self.data = []

    def rowCount(self, parent=QModelIndex()) :
        return len(self.data)


    def columnCount(self, parent=QModelIndex()) :
        return len(self.headers)

    def data(self, index, role) :
        if not index.isValid() :
            return None #With sip v 1.0 used to be QVariant()
        elif role != Qt.DisplayRole :
            return None

        if index.column() == 1 :
            return self.data[index.row()].name
        elif index.column() == 2 :
            return self.data[index.row()].description
        elif index.column() == 0 :
            return QDateTime.fromMSecsSinceEpoch(self.events[index.row()].created)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal :
                return self.headers[section]
            elif orientation == Qt.Vertical :
                return self.headers[section]
        return None
    def addData(self,data):
        self.data.append(data)

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
      #  self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))


