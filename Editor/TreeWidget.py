__author__ = 'heinz'

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal
from copy import deepcopy
PLAN_TYPE, PLOT_TYPE, ROUTINE_TYPE, LIMIT_TYPE, SETTING_TYPE, TRACE_TYPE, ROUTE_TYPE = range(1001, 1008)


class TreeWidgetItem(QtGui.QTreeWidgetItem):
     def __init__(self, parent, type, title, id):
         QtGui.QTreeWidgetItem.__init__(self, parent, type)
         self.type = type
         self.id = id
         self.title = title


         if type == TRACE_TYPE:
             text, flags = 'Trace', ~QtCore.Qt.ItemIsDropEnabled
         else:
             self.setChildIndicatorPolicy(self.ShowIndicator)
             self.setExpanded(True)
             if type == PLAN_TYPE:
                 text, flags = 'Plan', ~QtCore.Qt.ItemIsDropEnabled
             elif type == PLOT_TYPE:
                 text, flags = 'Plot', ~QtCore.Qt.ItemIsDropEnabled
             elif type == ROUTINE_TYPE:
                 text, flags = 'Routine', ~QtCore.Qt.ItemIsDropEnabled
             elif type == ROUTINE_TYPE:
                 text, flags = 'Routine', ~QtCore.Qt.ItemIsDropEnabled
             elif type == LIMIT_TYPE:
                 text, flags = 'Limit', ~QtCore.Qt.ItemIsDropEnabled
             elif type == SETTING_TYPE:
                 text, flags = 'Setting', ~QtCore.Qt.ItemIsDropEnabled
             elif type == ROUTE_TYPE:
                 text, flags = 'Route', ~QtCore.Qt.ItemIsDropEnabled
             else:
                 text,flags = 'test',None

         text = text + title
         self.setText(0, title)
         self.setFlags(self.flags() & flags)




class TreeWidget(QtGui.QTreeWidget):
    copied = pyqtSignal()
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.header().setHidden(False)
        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(self.InternalMove)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.invisibleRootItem().setFlags(QtCore.Qt.NoItemFlags)

#        TreeWidgetItem(self, PLAN_TYPE,0)

    def rowsInserted(self, parent, start, end):


       QtGui.QTreeWidget.rowsInserted(self, parent, start, end)
       return
       #  item = self.itemFromIndex(parent)
       # #  print (parent,start,end)
       #
       #  if item is not None and item.childCount() > 0:
       #      print (item,item.text(0),  item.childCount())
       #      if (item is not None and  item.type() == PLOT_TYPE and   item.child(start).type() == TRACE_TYPE):
       #          child = item.takeChild(start)
       #          if item.folder is None:
       #              item.folder = TreeWidgetItem(item, ROUTINE_TYPE)
       #              item.folder.addChild(child)
       #          pass

    def addItem(self, parent, type, title, id):
        if parent == None:
            item = TreeWidgetItem(self, type, title, id)
        else:
            item = TreeWidgetItem(parent, type, title, id)
        return item
    def delItem(self,item):
        _root = self.invisibleRootItem()
        for item in self.selectedItems():
            (item.parent() or _root).removeChild(item)
        pass

    def setFlags(self,type):

        it = QtGui.QTreeWidgetItemIterator(self)
        while (it.value()):
            item = it.value()
          #  print(item)
            if item.type == type:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsDropEnabled )
            else:
                _flags = item.flags() & ~QtCore.Qt.ItemIsDropEnabled
                item.setFlags(_flags)
            it += 1
            # if item.flags() & QtCore.Qt.ItemIsDropEnabled:
            #     print (item.text(0), 'True')
            # else:
            #     print (item.text(0), 'False')

    def dropMimeData(self, parent, row, data, action):
         if action == QtCore.Qt.MoveAction:
             print('..')
             return self.moveSelection(parent, row)
         if action == QtCore.Qt.CopyAction:
             return self.copySelection(parent, row)
         return False

    def moveSelection(self, parent, position):
	# save the selected items
         if parent.type == None:
            return
         selection = [QtCore.QPersistentModelIndex(i)
                      for i in self.selectedIndexes()]
         parent_index = self.indexFromItem(parent)
         if parent_index in selection:
             return False
         # save the drop location in case it gets moved
         target = self.model().index(position, 0, parent_index).row()
         if target < 0:
             target = position
         # remove the selected items
         taken = []
         for index in reversed(selection):
             item = self.itemFromIndex(QtCore.QModelIndex(index))
             if item is None or item.parent() is None:
                 taken.append(self.takeTopLevelItem(index.row()))
             else:
                 taken.append(item.parent().takeChild(index.row()))
         # insert the selected items at their new positions
         while taken:
             if position == -1:
                 # append the items if position not specified
                 if parent_index.isValid():
                     parent.insertChild(
                         parent.childCount(), taken.pop(0))
                 else:
                     self.insertTopLevelItem(
                         self.topLevelItemCount(), taken.pop(0))
             else:
		 # insert the items at the specified position
                 if parent_index.isValid():
                     parent.insertChild(min(target,
                         parent.childCount()), taken.pop(0))
                 else:
                     self.insertTopLevelItem(min(target,
                         self.topLevelItemCount()), taken.pop(0))
         return True
    def copySelection(self, parent, position):

         selection = [QtCore.QPersistentModelIndex(i)
                      for i in self.selectedIndexes()]
         parent_index = self.indexFromItem(parent)
         if parent_index in selection:
             return False
         # save the drop location in case it gets moved
         target = self.model().index(position, 0, parent_index).row()
         if target < 0:
             target = position
         # copy the selected items
         taken = []
         for index in reversed(selection):
              item = self.itemFromIndex(QtCore.QModelIndex(index))
              if item is None or item.parent() is None:
                 _item = self.topLevelItem(index.row()).clone()
                 _item.type = self.topLevelItem(index.row()).type
               #  _text = self.self.topLevelItem(index.row()).text(0)
                #  _text = _text + " c"
                #  _item.setText(0, _text)
                 taken.append(_item)
              else:
                  _item = item.parent().child(index.row()).clone()
                  _item.type = item.parent().child(index.row()).type
                #  _text = item.parent().child(index.row()).text(0)
                #  _text = _text + " c"
                #  _item.setText(0, _text)
                  taken.append(_item)
          # insert the selected items at their new positions
         for i in taken:
              self.addCind(i)

         while taken:
              if position == -1:
                  # append the items if position not specified
                  if parent_index.isValid():
                      parent.insertChild(parent.childCount(), taken.pop(0))
                  else:
                      self.insertTopLevelItem(self.topLevelItemCount(), taken.pop(0))
              else:
		         # insert the items at the specified position
                 if parent_index.isValid():
                     parent.insertChild(min(target,
                         parent.childCount()), taken.pop(0))
                 else:
                     self.insertTopLevelItem(min(target,
                         self.topLevelItemCount()), taken.pop(0))
         self.copied.emit()
         return True

    def addCind(self,item):
        _text = item.text(0)
        _text = _text + ' c'
#        print(_text,item.type)
        item.setText(0,_text)
        if item.childCount() > 0:
            for i in range(item.childCount()):
                self.addCind(item.child(i))

