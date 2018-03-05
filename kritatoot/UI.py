
import os
import sys
import inspect

if sys.version_info < (3,):
    from PySide.QtGui import *
    from PySide.QtCore import *
else:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *

from .UploadTab import UploadTab
from .AccountsTab import AccountsTab

from .App import KritaToot



class KritaTootUI(QDialog):
    """
    Main dialog for KritaToot
    """

    def __init__(self, parent=None):
        super(KritaTootUI, self).__init__(parent) # Py2
        
        thisscript = inspect.getfile(KritaTootUI)
        parentfolder = os.path.dirname(thisscript)
        
        self.tabwidget = QTabWidget()
        
        self.uploadtab = UploadTab()
        self.tabwidget.addTab(self.uploadtab, "Upload")
        
        self.accountstab = AccountsTab()
        self.tabwidget.addTab(self.accountstab, "Accounts")
        
        self.statusbar = QStatusBar()
        
        vertLayout = QVBoxLayout()
        
        vertLayout.addWidget(self.tabwidget)
        vertLayout.addWidget(self.statusbar)

        self.setLayout(vertLayout)
        
        self.mainapp = KritaToot()
        self.mainapp.loadAccounts()
        
        
        # tabs need access to the following objs/props
        self.uploadtab.setApp(self.mainapp)
        self.accountstab.setApp(self.mainapp)
        
        
        self.uploadtab.refreshURLList()
        
        
        if self.mainapp.getAccountsLength() < 1:
            self.tabwidget.setCurrentWidget(self.accountstab)
            
            self.accountstab.addAccount(back_enabled=False)
            
        
        # slots
        self.tabwidget.currentChanged.connect(self.updateTab)
        
    
    
    def updateTab(self):
        """
        """
        
        if self.tabwidget.currentWidget() == self.uploadtab:
            # accounts may have changed. update
            self.uploadtab.refreshURLList()
        
    
    
    





if __name__ == '__main__':
    
    
    app = QApplication(sys.argv)
    
    dialog = KritaTootUI()
    dialog.show()
    
    app.exec_()
    
    
    
    
    
    
    
    




