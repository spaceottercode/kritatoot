
import os
import sys
import inspect
from functools import partial

if sys.version_info < (3,):
    from PySide.QtGui import *
    from PySide.QtCore import *
    
else:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    
from .Toot import uploadmedia, postmedia, post
from .TempMedia import saveTempMedia, removeTempMedia



class AltTextDialog(QDialog):
    """
    A modal dialogbox for users to supply altenative text to their images
    """
    
    def __init__(self, parent=None, text=None):
        super(AltTextDialog, self).__init__(parent) # Py2
        
        self.setModal(True)
        
        self.alttext = text
        
        
        self.boxlabel = QLabel('Image Description')
        
        # enter text here
        self.textbox = QPlainTextEdit()
        
        if self.alttext:
            self.textbox.setPlainText(self.alttext)
        
        self.addbutton = QToolButton()
        self.addbutton.setText('Add')
        
        self.exitbutton = QToolButton()
        self.exitbutton.setText('Cancel')
        
        controlsLayout = QHBoxLayout()
        controlsLayout.addStretch(1)
        controlsLayout.addWidget(self.exitbutton)
        controlsLayout.addWidget(self.addbutton)
        
        
        mainLayout = QVBoxLayout()
        
        mainLayout.addWidget(self.boxlabel)
        mainLayout.addWidget(self.textbox)
        mainLayout.addLayout(controlsLayout)
        
        self.setLayout(mainLayout)
        
        # slots
        self.addbutton.clicked.connect(self.addtext)
        self.exitbutton.clicked.connect(self.accept)
        
    def addtext(self):
        """
        """
        
        text = self.textbox.toPlainText()
        
        self.alttext = text
        
        self.accept()


class FocalPointDialog(QDialog):
    """
    A modal dialogbox for users to supply a focal point: a location that acts
    like an achor or pivot.
    """
    
    def __init__(self, parent=None, focal=None):
        """
        focal   - (tuple) or None
        """
        
        super(FocalPointDialog, self).__init__(parent) # Py2
        
        self.setModal(True)
        
        self.MAXROW = 3
        self.MAXCOL = 3
        
        # holds the (row,col) of a currently selected, but uncommitted, focal point.
        # a sel focal point is commited when user clicks add.
        self.tempidx  = focal
        
        # (row,col) of the last commited focal point
        self.focalidx = focal
        
        # the focalidx, (row, col), converted to focal point coordinates (x, y)
        self.focalcoords = (0.0, 0.0)
        
        if self.focalidx:
            self.focalcoords = self.indexToCoordinates(self.focalidx[0], self.focalidx[1])
        
        self.focallabel = QLabel('Choose a focal point (anchor)')
        
        gridLayout = QGridLayout()
        gridLayout.setHorizontalSpacing(0)
        gridLayout.setVerticalSpacing(0)
        
        
        
        self.focalbuttons = [None] * self.MAXROW
        for i in range(self.MAXROW):
            self.focalbuttons[i] = [None] * self.MAXCOL
    
        for i in range(self.MAXROW):
            
            for j in range(self.MAXCOL):
                button = QToolButton()
                button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                
                if self.focalidx and i == self.focalidx[0] and j == self.focalidx[1]:
                    button.setStyleSheet("background-color: #2588d0;")
                
                gridLayout.addWidget(button, i, j)
                
                button.clicked.connect(partial(self.toggleFocal, i, j))
                
                self.focalbuttons[i][j] = button
                
        
        
        
        centerLayout = QHBoxLayout()
        centerLayout.addStretch(1)
        centerLayout.addLayout(gridLayout);
        centerLayout.addStretch(1)
        
        # controls
        self.addbutton = QToolButton()
        self.addbutton.setText('Add')
        
        self.exitbutton = QToolButton()
        self.exitbutton.setText('Cancel')
        
        controlsLayout = QHBoxLayout()
        controlsLayout.addStretch(1)
        controlsLayout.addWidget(self.exitbutton)
        controlsLayout.addWidget(self.addbutton)
        
        
        mainLayout = QVBoxLayout()
        
        mainLayout.addWidget(self.focallabel)
        mainLayout.addLayout(centerLayout)
        mainLayout.addLayout(controlsLayout)
        
        self.setLayout(mainLayout)
        
        self.defaultStyleSheet = self.addbutton.styleSheet()
        
        # slots
        self.addbutton.clicked.connect(self.addfocal)
        self.exitbutton.clicked.connect(self.accept)
    
    def indexToCoordinates(self, row, col):
        """
        Converts a row & col into a corresponding (x,y) tuple in
        focal point space. In focal point space, x = -1.0 to 1.0
        and y = -1.0 to 1.0
        """
        
        
        # Note - hard coded values. assuming 3x3 grid
        # using perimiter values except for center
        if row == 0:
            if col == 0:
                return (-1.0, 1.0)
            elif col == 1:
                return (0.0, 1.0)
            elif col == 2:
                return (1.0, 1.0)
        elif row == 1:
            if col == 0:
                return (-1.0, 0.0)
            elif col == 1:
                return (0.0, 0.0)
            elif col == 2:
                return (1.0, 0.0)
        elif row == 2:
            if col == 0:
                return (-1.0, -1.0)
            elif col == 1:
                return (0.0, -1.0)
            elif col == 2:
                return (1.0, -1.0)
        
        
    
    def toggleFocal(self, row, column):
        """
        """
        #print("CLICKED (" + str(row) + "," + str(column) + ")")
        
        # clear all
        for i in range(self.MAXROW):
            for j in range(self.MAXCOL):
                self.focalbuttons[i][j].setStyleSheet(self.defaultStyleSheet)
        
        if self.focalidx:
            # already selected?
            if row == self.focalidx[0] and column == self.focalidx[1]:
                self.focalbuttons[row][column].setStyleSheet(self.defaultStyleSheet)
                self.tempidx = None
            else:
                self.focalbuttons[row][column].setStyleSheet("background-color: #2588d0;")
                self.tempidx = (row, column)
        else:
            # first time a selection has been made
            self.focalbuttons[row][column].setStyleSheet("background-color: #2588d0;")
            self.tempidx = (row, column)
    
    
    def addfocal(self):
        """
        """
        
        self.focalidx = self.tempidx
        
        if self.focalidx:
            # convert the row/col to actual coordinates
            self.focalcoords = self.indexToCoordinates(self.focalidx[0], self.focalidx[1])
        else:
            self.focalcoords = (0.0, 0.0)
        
        self.accept()




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
            'noalttext': QIcon( os.path.join(parentfolder, "images/all/noalttext.png") ),
            'alttext':   QIcon( os.path.join(parentfolder, "images/all/alttext.png") ),
            
            'nohide': QIcon( os.path.join(parentfolder, "images/all/nohide.png") ),
            'hide':   QIcon( os.path.join(parentfolder, "images/all/hide.png") ),
            
            'nofocal': QIcon( os.path.join(parentfolder, "images/all/nofocal.png") ),
            'focal':   QIcon( os.path.join(parentfolder, "images/all/focal.png") )
        }
        
        # if an alt text is provided
        self.alttext = None
        
        # the selected row and column, if any (otherwise None)
        self.selfocalidx = None
        self.focalcoords = (0.0, 0.0)
        
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
        self.privacy.setToolTip('What type of post is this?')
        
        # add alt-text
        self.alttextbtn = QToolButton()
        alttexticon = self.icons['noalttext']
        self.alttextbtn.setIcon(alttexticon)
        self.alttextbtn.setToolTip('Add a description of your image.')
        
        # button indicating if a warning title card is requested or not
        self.hidden = QToolButton()
        visibleicon = self.icons['nohide']
        self.hidden.setIcon(visibleicon)
        # overriding unused method (button not checkable)
        # when True, a warning title card is requested
        self.hidden.toggled = False
        self.hidden.setToolTip('Hide image. Viewers must click to reveal image. Used for sensitive images.')
        
        # choose a focal point/anchor/pivot
        self.focalpoint = QToolButton()
        focalicon = self.icons['nofocal']
        self.focalpoint.setIcon(focalicon)
        self.focalpoint.setToolTip('Set the pivot point (anchor) for cropped previews/thumbnails')
        
        # send toot
        self.tootimg = QToolButton()
        self.tootimg.setStyleSheet("background-color: #2588d0; color: #fff")
        self.tootimg.setText('TOOT!')
        self.tootimg.setToolTip('Post your image and message.')
        
        self.tootimg.setEnabled(False)
        
        horizLayout = QHBoxLayout()
        
        horizLayout.addWidget(self.privacy)
        horizLayout.addWidget(self.alttextbtn)
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
        
        self.alttextbtn.clicked.connect(self.addAltText)
        self.hidden.clicked.connect(self.toggleVisibility)
        self.focalpoint.clicked.connect(self.addFocalPoint)
        
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
    
    
    def addAltText(self):
        """
        """
        
        alttextui = AltTextDialog(self, self.alttext);
        alttextui.exec_()
        
        self.alttext = alttextui.alttext
        
        if self.alttext:
            #print("ALTTEXT " + self.alttext)
            alttexticon = self.icons['alttext']
            self.alttextbtn.setIcon(alttexticon)
        else:
            alttexticon = self.icons['noalttext']
            self.alttextbtn.setIcon(alttexticon)
    
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
    
    
    def addFocalPoint(self):
        """
        """
        
        focalui = FocalPointDialog(self, self.selfocalidx);
        focalui.exec_()
        
        self.selfocalidx = focalui.focalidx
        
        if self.selfocalidx:
            focalicon = self.icons['focal']
            self.focalpoint.setIcon(focalicon)
            self.focalcoords = focalui.focalcoords
        else:
            focalicon = self.icons['nofocal']
            self.focalpoint.setIcon(focalicon)
            self.focalcoords = (0.0, 0.0)
    
    
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
        
        # include a description?
        description = "Uploaded using kritatoot"
        
        if self.alttext:
            description = self.alttext
        
        # hide media?
        hideme = self.hidden.toggled
        
        # given a disp name, fetch string required in API ('public', 'unlisted', 'private', 'direct')
        visindex = self.privacy.currentIndex()
        visdata = self.privacy.itemData(visindex)
        visibility = visdata['value']
        
        #focal point: None or a tuple (x,y)
        focus = (0.0,0.0)
        
        if self.focalcoords:
            focus = self.focalcoords
        
        
        print('At this point the following attrs are set: ')
        print('url    : ' + url)
        print('visible: ' + visibility)
        
        hidestr = 'YES' if visibility else 'NO'
        print('Hide   : ' + hidestr)
        print('message: %s' % message)
        print('description: %s' % description if description else 'None')
        if focus:
            print('focus: (%.2f, %.2f)' % focus)
        else:
            print('focus: None')
        
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
                media_id = uploadmedia(url, access_token, filename, description=description, focus=focus)
                
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
                
                self.alttext = None
                alttexticon = self.icons['noalttext']
                self.alttextbtn.setIcon(alttexticon)
                
                if self.hidden.toggled:
                    self.hidden.toggled = False
                    visibleicon = self.icons['nohide']
                    self.hidden.setIcon(visibleicon)
                    
                self.selfocalidx = None
                self.focalcoords = (0.0, 0.0)
                focalicon = self.icons['nofocal']
                self.focalpoint.setIcon(focalicon)
                                
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
