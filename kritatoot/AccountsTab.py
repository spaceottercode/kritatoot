
import os
import sys
import re
import inspect

if sys.version_info < (3,):
    from PySide.QtGui import *
    from PySide.QtCore import *
else:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *


from .ImageBox import ImageBox
import webbrowser

# TODO add signals to this tab
# indicating addition or removal of accounts/urls
# so that parent UI can act accordingly
# ie update URL bar

# TODO maybe add a signal for when user hits finish button
# (a confirmation signal). A signal the parent widget can
# use to switch tabs


class AccountsTab(QWidget):
    """
    A widget that represent the Add/Remove Accounts tab
    """
    
    def __init__(self, parent=None):
        super(AccountsTab, self).__init__(parent) # Py2
        
        self.weburl = None
        self.app = None
        
        self.addpage = 0
        
        
        # this widget holds a 350x350 image
        self.imagebox = ImageBox()
        self.imagebox.setKeyword('homepage')
        self.imagebox.setImage('homepage') # before the signal/slot is set
        
        self.listbox = QListWidget()
        self.listbox.setVisible(False)
        
        urllayout = QHBoxLayout()
        
        self.urllabel = QLabel('URL')
        self.urllabel.setVisible(False)
        
        self.lineedit = QLineEdit()
        #setPlaceholderText()
        self.lineedit.setVisible(False)
        
        urllayout.addWidget(self.urllabel)
        urllayout.addWidget(self.lineedit)
        
        
        horizLayout = QHBoxLayout()
        
        self.delaccount = QPushButton('Remove Account')
        self.addaccount = QPushButton('Add Account')
        
        
        horizLayout.addWidget(self.delaccount)
        horizLayout.addWidget(self.addaccount)
        
        
        vertLayout = QVBoxLayout()
        
        vertLayout.addWidget(self.imagebox)
        vertLayout.addWidget(self.listbox)
        vertLayout.addLayout(urllayout)
        vertLayout.addLayout(horizLayout)
        
        self.setLayout(vertLayout)
        
        
        
        # slots
        self.addaccount.clicked.connect(self.addAccount)
        self.delaccount.clicked.connect(self.showDeletePage)
        
        # roundabout way of ensuring QPixmaps are always set in the main thread
        self.imagebox.signal.changed.connect(self.updateImageBox)
        
    
    
    
    
    def updateImageBox(self):
        """
        Ensure QPixmaps are only being swapped in the main thread.
        Notably allows the OnReady, OnError, OnAbort, calls that run on a separate
        thread, to swap pixmaps
        """
        
        keyword = self.imagebox.keyword()
        
        
        if keyword:
            self.imagebox.setImage(keyword)
    
    
    def setApp(self, app):
        
        self.app = app
    
    
    def showHomePage(self):
        """
        This is the initial page
        except when user has no accounts.
        
        This pae allows user to add and remove accounts
        """
        
        # stop the http server if any
        if self.app:
            self.app.stopHTTPServer()
        
        # hide the url bar
        self.urllabel.setVisible(False)
        self.lineedit.setVisible(False)
        
        self.urllabel.setText('URL')
        self.lineedit.setText('')
        self.lineedit.setPlaceholderText('')
        
        self.imagebox.setVisible(True)
        self.imagebox.setKeyword('homepage')
        
        self.listbox.setVisible(False)
        
        self.addaccount.setText('Add Account')
        self.delaccount.setText('Remove Account')
        
        
        self.addaccount.setEnabled(True)
        self.delaccount.setEnabled(True)
        
        # slots
        self.addaccount.clicked.disconnect()
        self.delaccount.clicked.disconnect()
        
        self.addaccount.clicked.connect(self.addAccount)
        self.delaccount.clicked.connect(self.showDeletePage)
        
        self.addpage = 0
        
    
    def showAddPage(self, pagenum, back_enabled=True):
        """
        Update this tab with widgets needed for adding new
        URLs/accounts
        
        (a wizard that walks you through the process)
        
        pagenum (int) beginning with 1
        """
        
        
        self.addpage = pagenum
        
        
        if back_enabled:
            self.delaccount.setEnabled(True)
        else:
            self.delaccount.setEnabled(False)
        
        
        if pagenum == 1:
            
            #############################
            #  Entering a Mastodon URL  #
            #############################
            
            # show url bar
            self.lineedit.setPlaceholderText('https://mastodon.social')
            
            self.urllabel.setVisible(True)
            self.lineedit.setVisible(True)
            
            self.imagebox.setKeyword('add01')
            
            self.addaccount.setText('Next')
            self.delaccount.setText('Back')
            
            self.addaccount.setEnabled(False)
            
            # slots
            self.addaccount.clicked.disconnect()
            self.delaccount.clicked.disconnect()
            
            self.addaccount.clicked.connect(self.nextAddPage)
            self.delaccount.clicked.connect(self.showHomePage)
            
            self.lineedit.textEdited.connect(self.updateAddButton)
            
            QCoreApplication.processEvents()
            
        elif pagenum == 2:
            
            #############################################
            # Register App + Request Authorization Code #
            #############################################
            
            # fetches auth code via a callback URL.
            
            # now hide the url bar
            self.urllabel.setVisible(False)
            self.lineedit.setVisible(False)
            
            self.imagebox.setKeyword('add02')
            
            self.addaccount.setText('Next')
            self.delaccount.setText('Cancel')
            
            self.addaccount.setEnabled(True)
            
            # slots
            self.addaccount.clicked.disconnect()
            self.delaccount.clicked.disconnect()
            
            self.addaccount.clicked.connect(self.nextAddPage)
            self.delaccount.clicked.connect(self.showHomePage)
            
            
            
            if self.app:
                
                success = False
                
                print('registering app on %s' % self.weburl)
                
                success = self.app.register(self.weburl)
                
                if not success:
                    
                    print('registeration failed')
                    
                    self.imagebox.setKeyword('error01')
                    
                    self.addaccount.setEnabled(False)
                    self.delaccount.setEnabled(True)
                    
                    self.addaccount.clicked.disconnect()
                    self.delaccount.clicked.disconnect()
                    
                    self.addaccount.clicked.connect(self.showHomePage)
                    self.delaccount.clicked.connect(self.showHomePage)
                    
                    return
                
                else:
                    
                    print('running httpd server and await local GET request with code')
                    # run a local server that responds to (local) requests for http://localhost:3000/callback...
                    self.app.runHTTPServer(onready=self.OnReady, onerror=self.OnError)
                    
                    #self.app.requestToken(self.weburl, code)
                    
                    print("launch user's website and wait for user's authorization")
                    
                    # launches web page where user must authorize or deny app
                    success = self.app.authorize(self.weburl)
                    
                    self.delaccount.setText('Launch Again')
                    
                    self.delaccount.clicked.disconnect()
                    self.delaccount.clicked.connect(self.launchAuthURL)
            
            
        elif pagenum == 3:
            
            #####################################
            #   Waiting For User Authorization  #
            #####################################
            
            
            self.imagebox.setKeyword('add03')
            
            self.addaccount.setText('Next')
            self.delaccount.setText('Cancel')
            
            # no more pages
            # Authorizing app via the web should trigger the tokenCallback( ) call
            # which will be responsible for displaying the final good or bad page
            self.addaccount.setEnabled(False)
            
            # slots
            self.addaccount.clicked.disconnect()
            self.delaccount.clicked.disconnect()
            
            self.addaccount.clicked.connect(self.showHomePage)
            self.delaccount.clicked.connect(self.showHomePage)
            
        
        else:
            print('Page Not Found')
            return False
        
        
        
        return True
        
    
    
    def nextAddPage(self):
        """
        """
        
        if self.addpage == 1:
            
            # save url
            text = self.lineedit.text()
            
            if re.match('https://(\w+\.)*?\w+\.\w+', text):
                self.weburl = text
            elif re.match('(\w+\.)*?\w+\.\w+', text):
                self.weburl = 'https://' + text
                
        
        
        self.showAddPage(self.addpage + 1)
    
    def updateAddButton(self):
        """
        enable/disble the next button based on what's in the the line edit
        """
        
        if self.addpage == 1:
            
            text = self.lineedit.text()
            
            if re.match('^(https://)?(\w+\.)*?\w+\.\w+$', text):
                self.addaccount.setEnabled(True)
            else:
                self.addaccount.setEnabled(False)
            
            
    
    
    def addAccount(self, back_enabled=True):
        """
        """
        
        self.showAddPage(1, back_enabled=back_enabled)
        
    
    def launchAuthURL(self):
        """
        From time to time, webbrowser.open_new() fails to open/launch a web page.
        Use this to manually invoke webbrowser 
        """
        
        if self.app:
            authurl = self.app.getAuthURL()
            
            if authurl:
                webbrowser.open_new(authurl)
    
    
    
    def OnReady(self, authcode):
        """
        async call that gets invoked when the HTTP server running in the BG 
        receives the anticipated GET request with auth code. 
        """
        
        if self.app:
                
            success = False
            
            # code should be set to a string, but just in case
            if authcode:
                
                print('received auth code')
                print('requesting token from %s' % self.weburl)
                #print('Auth Code is ' + authcode)
                
                success = self.app.requestToken(self.weburl, authcode)
            
            
            if not success:
                
                # failed to get token
                print('token request failed')
                
                self.imagebox.setKeyword('error01')
                
                self.addaccount.setEnabled(False)
                self.delaccount.setEnabled(True)
                
                self.addaccount.clicked.disconnect()
                self.delaccount.clicked.disconnect()
                
                self.addaccount.clicked.connect(self.showHomePage)
                self.delaccount.clicked.connect(self.showHomePage)
                
                return
            else:
                
                # recvd token
                print('access token received')
                print('account complete')
                
                # setup next/final page
                self.imagebox.setKeyword('complete')
                
                self.addaccount.setText('Finish')
                self.delaccount.setText('Cancel')
                
                self.addaccount.setEnabled(True)
                
                # slots
                self.addaccount.clicked.disconnect()
                self.delaccount.clicked.disconnect()
                
                self.addaccount.clicked.connect(self.showHomePage)
                self.delaccount.clicked.connect(self.showHomePage)
                
                return
    
    def OnError(self, errcode, message):
        """
        async call that gets invoked when the HTTP server running in the BG 
        fails to receives the auth code or encounters an error in the process. 
        """
        
        if self.app:
            
            print('Error: ' + message)
            self.imagebox.setKeyword('error01')
            
            self.addaccount.setText('Restart')
            self.delaccount.setText('Cancel')
            
            
            self.addaccount.setEnabled(False)
            self.delaccount.setEnabled(True)
            
            self.addaccount.clicked.disconnect()
            self.delaccount.clicked.disconnect()
            
            self.addaccount.clicked.connect(self.showHomePage)
            self.delaccount.clicked.connect(self.showHomePage)
    
    
    
    
    def showDeletePage(self):
        """
        Update this tab with widgets needed to list and remove accounts
        """
        
        # hide the imagebox
        self.imagebox.setVisible(False)
        
        # show the listbox that holds all existing URLs
        self.listbox.setVisible(True)
        
        if self.app:
            urls = self.app.getAccountURLs()
            
            self.listbox.clear()
            
            for url in urls:
                self.listbox.addItem(url)
        
        
        self.addaccount.setText('Remove')
        self.delaccount.setText('Back')
        
        
        self.addaccount.clicked.disconnect()
        self.delaccount.clicked.disconnect()
        
        self.addaccount.clicked.connect(self.deleteAccount)
        self.delaccount.clicked.connect(self.showHomePage)
        
        
    
    def deleteAccount(self):
        """
        remove the currently selected url/account, if any
        """
        
        item = self.listbox.currentItem()
        
        if item:
            url = item.text()
            
            if self.app:
                self.app.removeAccount(url)
                self.app.saveAccounts()
                
                #self.listbox.removeItemWidget(item)
                
                row = self.listbox.currentRow()
                self.listbox.takeItem(row)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    dialog = QDialog()
    
    
    accounts = AccountsTab()
    
    layout = QVBoxLayout()
    layout.addWidget(accounts)
    
    dialog.setLayout(layout)
    
    dialog.show()
    dialog.activateWindow()
    
    
    app.exec_()