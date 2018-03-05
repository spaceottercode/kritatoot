
import os
import sys
import inspect

if sys.version_info < (3,):
    from PySide.QtGui import *  # py2
    from PySide.QtCore import * # py2
    pyqtSignal = Signal
else:
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *


class ChangedSignal(QObject):
 
    changed = pyqtSignal()


class ImageBox(QWidget):
    
    """
    This widget was created for the sake of ensuring QPixmaps are swapped on the main thread.
    Imagebox achieves this by ensuring that setImage( ) calls are always invoked by a
    slot-ed callback.
    
    This custom widgets emits a 'changed' signal whenever a keyword is set
    """
    
    def __init__(self, parent=None):
        super(ImageBox, self).__init__(parent) # Py2
        
        
        self.pixmaps = {}
        self._loadImages()
        
        self.ibkeyword = ''
        
        self.label = QLabel()
        
        vertLayout = QVBoxLayout()
        vertLayout.addWidget(self.label)
        self.setLayout(vertLayout)
        
        # custom signal
        self.signal = ChangedSignal() 
        
    
    
    def _loadImages(self):
        """
        encapsulate image loading so that we can later handle
        locales and missing images
        """
        
        thisscript = inspect.getfile(ImageBox)
        parentfolder = os.path.dirname(thisscript)
        
        self.pixmaps = {
        
        'homepage': QPixmap( os.path.join(parentfolder, "images/all/homepage.png") ),
        
        'add01': QPixmap( os.path.join(parentfolder, "images/en/add01.png") ),
        'add02': QPixmap( os.path.join(parentfolder, "images/en/add02.png") ),
        'add03': QPixmap( os.path.join(parentfolder, "images/en/add03.png") ),
        
        'complete': QPixmap( os.path.join(parentfolder, "images/en/complete.png") ),
        
        'error01': QPixmap( os.path.join(parentfolder, "images/en/error01.png") ),
        'error02': QPixmap( os.path.join(parentfolder, "images/en/error02.png") )
        
        }
    
    
    def setKeyword(self, keyword):
        """
        """
        
        self.ibkeyword = keyword
        self.signal.changed.emit()
        
    
    def keyword(self):
        """
        """
        
        return self.ibkeyword
    
    def setImage(self, keyword):
        """
        encapsulate image setting so that we can later handle
        locales and missing images
        """
        
        pixmap = self.pixmaps.get(keyword)
        self.label.setPixmap(pixmap)



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    dialog = QDialog()
    
    
    imgbox = ImageBox()
    imgbox.setImage('homepage')
    
    layout = QVBoxLayout()
    layout.addWidget(imgbox)
    
    dialog.setLayout(layout)
    
    dialog.show()
    dialog.activateWindow()
    
    
    # test the 'changed' signal
    def ibcallback():
        keyword = imgbox.keyword()
        imgbox.setImage(keyword)
    
    imgbox.signal.changed.connect(ibcallback)
    
    
    def timercb():
        # trigger the callback
        imgbox.setKeyword('error01')
    
    timer = QTimer()
    timer.timeout.connect(timercb)
    timer.setSingleShot(True)
    timer.start(2000)
    
    
    
    
    app.exec_()

