
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

from krita import *

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
        
class focalPointWidget(QWidget):
    """
    A widget which draws an image and you can select a focal point.
    """
    
    def __init__(self, parent = None):
        super(focalPointWidget, self).__init__(parent)
        self.focalPoint =  [0.0, 0.0]
        self.image = QImage()
        self.mouseIn = False
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        
    def setImage(self, image = QImage()):
        self.image = image
        self.update()
    
    def paintEvent(self, event):
        
        painter = QPainter(self)
        
        image = self.image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        imageOffsetLeft = (self.width()-image.width())/2
        imageOffsetTop = (self.height()-image.height())/2
        
        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.drawImage(imageOffsetLeft, imageOffsetTop, image)
        
        painter.save()
        # Let's make this super fancy and setup an area of interest!
        
        focalXY = QPointF(((self.focalPoint[0] + 1.0) / 2), (((-1.0*self.focalPoint[1]) + 1.0) / 2))
        aoi = 0.333 # The area of interest is ~ a third of the image.
        offset = QPointF(aoi/2, aoi/2)
        topleft = focalXY - offset
        bottomright = focalXY + offset

        
        # First let's draw the whiteish square in the middle.
        # This is necessary for very dark images.
        
        white = QRect( QPoint( (topleft.x()*image.width()) + imageOffsetLeft, (topleft.y() * image.height())+imageOffsetTop), QPoint((bottomright.x()*image.width())+imageOffsetLeft, (bottomright.y()*image.height())+imageOffsetTop))
        painter.setBrush(Qt.white)
        painter.setOpacity(0.3)
        painter.drawRect(white)
        
        # Then draw 4 black sections to indicate the non-visible area.
        # This is for very bright images.
        
        painter.setBrush(Qt.black)
        painter.drawRect(QRect(QPoint(0, 0), white.topLeft()))
        painter.drawRect(QRect(white.bottomRight(), QPoint(self.width(), self.height())))
        painter.drawRect(QRect(QPoint(0, white.bottom()), QPoint(white.left(), self.height())))
        painter.drawRect(QRect(QPoint(white.right(), 0), QPoint(self.width(), white.top())))
        
        painter.setBrush(Qt.white)
        painter.setPen(Qt.white)
        painter.setOpacity(1.0)
        painter.drawText(5, self.height()-10, str(", ").join(format(x, "1.2f") for x in self.focalPoint))

        painter.restore()
        
        
    def setFocalPointFromMousePos(self, pos = QPoint()):
        
        image = QSize(self.width(), self.height())
        if self.image.width() != 0 and self.image.height() != 0:
            if self.image.width() > self.image.height():
                image = QSize(self.width(), (self.image.height()/self.image.width()) * self.height())
            else:
                image = QSize((self.image.width()/self.image.height()) * self.width(), self.height())

        imageOffsetLeft = (self.width()  - image.width() ) / 2
        imageOffsetTop  = (self.height() - image.height()) / 2
        
        x = (((pos.x() - imageOffsetLeft) / image.width() ) * 2 ) - 1.0
        y = (((pos.y() - imageOffsetTop) / image.height() ) * 2 ) - 1.0
        self.focalPoint = [x, y * -1.0]
        print(self.focalPoint)
        self.update()
    
    def mousePressEvent(self, event):
        
        self.mouseIn = True
        self.setFocalPointFromMousePos(event.pos())
        
        event.accept()
        
    def mouseReleaseEvent(self, event):
        
        self.mouseIn = False
        self.setFocalPointFromMousePos(event.pos())
        
        event.accept()
        
    def mouseMoveEvent(self, event):
        if (self.mouseIn == True):
            self.setFocalPointFromMousePos(event.pos())
            event.accept()

    def sizeHint(self):
        return QSize(256, 256)
    
    def setFocalPoint(self, x, y):
        self.focalPoint = [x, y]
        self.update()
        
    def getFocalPoint(self):
        return self.focalPoint
        

class FocalPointDialog(QDialog):
    """
    A modal dialogbox for users to supply a focal point: a location that acts
    like an achor or pivot.
    """
    
    def __init__(self, parent = None, focal = (0, 0), image = QImage()):
        """
        focal   - (tuple) or None
        image   - (QImage) or None
        """
        
        super(FocalPointDialog, self).__init__(parent) # Py2
        
        self.setModal(True)        
        self.setWindowTitle('Set Image Focalpoint')
        
        self.focalcoords = focal
        
        self.focallabel = QLabel('Choose a focal point (anchor)')
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.focallabel)

        self.imageWidget = focalPointWidget()
        self.imageWidget.setImage(image)
        self.imageWidget.setFocalPoint(self.focalcoords[0], self.focalcoords[1])
        mainLayout.addWidget(self.imageWidget)
        
        
        # controls
        # Let's replace this with a QDialogButtonBox, then that sorts itself for differences between Desktop Enviroments :)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.addfocal)
        buttons.rejected.connect(self.accept)
        
        mainLayout.addWidget(buttons)
        
        self.setLayout(mainLayout)
    
    def addfocal(self):
        """
        """
        focal = self.imageWidget.getFocalPoint()
        self.focalcoords = (focal[0], focal[1])
        
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
        image = QImage()
        doc = Krita.instance().activeDocument()
        if doc is not None:
            image = doc.projection(0, 0, doc.width(), doc.height())
            if doc.width() > 512 and doc.height() > 512:
                # This is probably not pixel art.
                    image = image.scaled(512, 512, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        focalui = FocalPointDialog(self, self.focalcoords, image);
        focalui.exec_()
        
        self.focalcoords = focalui.focalcoords
        if self.focalcoords[0] != 0.0 and self.focalcoords[1] != 0.0:
            focalicon = self.icons['focal']
            self.focalpoint.setIcon(focalicon)
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
