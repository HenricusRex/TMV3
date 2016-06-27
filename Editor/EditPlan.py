__author__ = 'heinz'

from NeedfullThings import *
from DB_Handler_TDS3 import *
import EditElement

class EditPlan(EditElement.EditElement):
    def __init__(self, parent=None):
        super(EditPlan, self).__init__()

        self.ui = uic.loadUi("EditorPlan.ui", self)

        dispatcher.connect(self.onFillPlanID,signal=self.signals.EDIT_PLANID,sender=dispatcher.Any)

        pass
    pass

    def onFillPlanID(self,par1,par2):
        filename = par1
        ID = par2
        print ('filename,ID',filename,ID)
        _plan = DatasetPlan(filename)
        _plan.read()
        self.setCell('Title',_plan.title)
        self.setCell('Version',_plan.version)
        self.setCell('TMV Version',_plan.tmv_version)
        self.setCell('Company',_plan.company)
        self.setCell('Operator',_plan.operator  )
        self.setCell('Date','?')
        self.setCell('Comment',_plan.comment)







