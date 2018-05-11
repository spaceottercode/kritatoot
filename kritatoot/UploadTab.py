
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
    
from .Toot import uploadmedia, postmedia, post
from .TempMedia import saveTempMedia, removeTempMedia



class UploadTab(QWidget):
    """
    A widget representing the Upload/Toot tab where one can:
    
        enter a 500-char max toot message (optional)
        
        specify the toots privacy level (public, unlisted, followers-only, direct)
        
        if the posted media should be censored or not
        
        the (pre-authorized) Mastodon site to post the toot
    """
    
    def __init__(self, parent=None):
        super(UploadTab, self).__init__(parent) # Py2
        
        thisscript = inspect.getfile(UploadTab)
        parentfolder = os.path.dirname(thisscript)
        
        # a ref to the KritaToot app that holds most of the app's logic
        self.app = None
        
        # selected url
        self.activeurl = None
        
        self.icons = {
            'nohide': QIcon( os.path.join(parentfolder, "images/all/nohide.png") ),
            'hide':   QIcon( os.path.join(parentfolder, "images/all/hide.png") ),
            
            'focal':  QIcon( os.path.join(parentfolder, "images/all/focal.png") )
        }
        
        
        # list of sites where the app is registered and authorized
        self.urllabel = QLabel('Mastodon Server')
        self.urllist  = QComboBox()
        
        # max number of chars allowed in a toot
        self.maxchars = 500
        
        
        urlLayout = QVBoxLayout()
        urlLayout.addWidget(self.urllabel)
        urlLayout.addWidget(self.urllist)
        
        self.textlabel = QLabel('Message')
        
        # enter message here
        self.textbox = QPlainTextEdit()
        
        
        # display the number of chars remaining in a toot
        # message before hitting full capacity
        counterLayout = QHBoxLayout()
        self.charcount = QLabel('<b>500</B>')
        
        counterLayout.addWidget(self.charcount)
        counterLayout.insertStretch(0)
        
        self.privacy = QComboBox()
        self.privacy.addItem('Public',         userData={'value':'public'})
        self.privacy.addItem('Unlisted',       userData={'value':'unlisted'})
        self.privacy.addItem('Followers-Only', userData={'value':'private'})
        self.privacy.addItem('Direct',         userData={'value':'direct'})
        
        # button indicating if a warning title card is requested or not
        self.hidden = QToolButton()
        visibleicon = self.icons['nohide']
        self.hidden.setIcon(visibleicon)
        # overriding unused method (button not checkable)
        # when True, a warning title card is requested
        self.hidden.toggled = False
        
        # for possible future inclusion
        self.focalpoint = QToolButton()
        focalicon = self.icons['focal']
        self.focalpoint.setIcon(focalicon)
        self.focalpoint.setEnabled(False)
        
        
        # send toot
        self.tootimg = QToolButton()
        self.tootimg.setStyleSheet("background-color: #2588d0; color: #fff")
        self.tootimg.setText('TOOT!')
        
        self.tootimg.setEnabled(False)
        
        horizLayout = QHBoxLayout()
        
        horizLayout.addWidget(self.privacy)
        horizLayout.addWidget(self.hidden)
        horizLayout.addWidget(self.focalpoint)
        horizLayout.addWidget(self.tootimg)
        
        vertLayout = QVBoxLayout()
        
        vertLayout.addLayout(urlLayout)
        vertLayout.addWidget(self.textlabel)
        vertLayout.addWidget(self.textbox)
        vertLayout.addLayout(counterLayout)
        vertLayout.addLayout(horizLayout)
        
        
        self.setLayout(vertLayout)
        
        
        
        # slots
        self.textbox.textChanged.connect(self.updateCharCount)
        self.hidden.clicked.connect(self.toggleVisibility)
        
        self.tootimg.clicked.connect(self.upload)
    
    
    def setApp(self, app):
        """
        assign a KritaToot object
        """
        
        self.app = app
    
    
    def refreshURLList(self):
        """
        Update the URL dropdown menu
        """
        
        print('refreshing account list')
        
        nitems = 0
        
        # save the current url to and restore
        currtext = self.urllist.currentText()
        
        # sync urls with those stored in the KritaToot app
        if self.app:
            urls = self.app.getAccountURLs()
            
            self.urllist.clear()
            
            for url in urls:
                self.urllist.addItem(url)
                nitems += 1
        
        
        index = -1
        
        if currtext:
            index = self.urllist.findText(currtext)
        
        if index >= 0:
            self.urllist.setCurrentIndex(index)
        
        
        if nitems:
            self.tootimg.setEnabled(True)
    
    
    def updateCharCount(self):
        """
        every time the contents of the text box changes, update our char count label
        """
        
        text = self.textbox.toPlainText()
        nchars = len(text)
        
        remaining = self.maxchars - nchars
        
        self.charcount.setText('<b>%i</B>' % remaining)
        
        if remaining > 0:
            self.charcount.setStyleSheet("color: #fff")
            
            nurls = 0
            
            if self.app:
                nurls = self.app.getAccountsLength()
            
            if nurls:
                self.tootimg.setEnabled(True)
                
        else:
            # red alert. exceeded allowed char count
            # disable toot button
            self.charcount.setStyleSheet("color: #a53232")
            self.tootimg.setEnabled(False)
        
        
    
    def toggleVisibility(self):
        """
        Toggles the eye button widget.
        
        Note - if widget.toggled is True: warning title card is requested
        """
        
        if self.hidden.toggled:
            self.hidden.toggled = False
            
            visibleicon = self.icons['nohide']
            self.hidden.setIcon(visibleicon)
            
        else:
            self.hidden.toggled = True
            
            visibleicon = self.icons['hide']
            self.hidden.setIcon(visibleicon)
    
    
    
    def upload(self):
        """
        """
        
        url = self.urllist.currentText()
        
        if not url:
            print('No URL chosen')
            return False
        
        message = self.textbox.toPlainText()
        nchars = len(message)
        
        
        if nchars > self.maxchars:
            print('Max Chars exceeded')
            return False
        
        # hide media?
        hideme = self.hidden.toggled
        
        # given a disp name, fetch string required in API ('public', 'unlisted', 'private', 'direct')
        visindex = self.privacy.currentIndex()
        visdata = self.privacy.itemData(visindex)
        visibility = visdata['value']
        
        
        print('At this point the following attrs are set: ')
        print('url    : ' + url)
        print('visible: ' + visibility)
        
        hidestr = 'YES' if visibility else 'NO'
        print('Hide   : ' + hidestr)
        print('message: %s' % message)
        
        
        if self.app:
            
            # grab the access token
            account = self.app.getAccount(url)
            
            if not account:
                print('No account matching ' + url + 'found')
                QMessageBox.warning(self, 'Post Failed', 'Invalid account')
                return
            
            access_token = account.getAccessToken()
            
            if not access_token:
                print('No access token')
                QMessageBox.warning(self, 'Post Failed', 'No access token')
                return
            
            # export a copy of the current doc to upload before posting
            filename = saveTempMedia()
            
            if not filename:
                QMessageBox.warning(self, 'Post Failed', 'could not export')
                print('No temp file possible')
                return
            
            self.tootimg.setEnabled(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            # media must be uploaded prior to posting a toot
            print('uploading media')
            
            try:
                media_id = uploadmedia(url, access_token, filename, description="Uploaded using kritatoot", focus=(0.0,0.0))
                
                if not media_id:
                    QApplication.restoreOverrideCursor()
                    
                    removeTempMedia(filename)
                    
                    QMessageBox.warning(self, 'Post Failed', 'Media could not be uploaded')
                    print('Failed to upload media')
                    return
                
                # post the toot
                print('posting media on mastodon')
                result = postmedia(url, access_token, media_id, message=message, visibility=visibility, spoiler_text=None, sensitive=hideme)
                
                removeTempMedia(filename)
            except Exception:
                print('uncaught error. restoring cursor and exiting')
                QApplication.restoreOverrideCursor()
                return
            
            QApplication.restoreOverrideCursor()
            
            if result:
                # reset certain widgets
                self.textbox.clear()
                
                if self.hidden.toggled:
                    self.hidden.toggled = False
                    visibleicon = self.icons['nohide']
                    self.hidden.setIcon(visibleicon)
                
                QMessageBox.information(self, 'Post Completed', 'Image uploaded')
                print('Post Succeeded')
            else:
                QMessageBox.warning(self, 'Post Failed', 'Image did not upload')
                print('Post Failed')
                
            self.tootimg.setEnabled(True)





if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    dialog = QDialog()
    
    
    upload = UploadTab()
    
    layout = QVBoxLayout()
    layout.addWidget(upload)
    
    dialog.setLayout(layout)
    
    dialog.show()
    dialog.activateWindow()
    

    
    app.exec_()
