import sys
import json
from krita import *

from .UI import KritaTootUI


class MyExtension(Extension):
    """
    Add a 'Post on Mastodon' menu option under tools.
    
    Allows users to post the *current* document on a Maston site.
    
    A copy of the current document is always exported and posted.
    
    If the current document has never been saved, the exported image
    defaults to a PNG.
    
    A toot message, toot privacy, and hiding media content are supported.
    Toot message is optional. However when no toot message is given,
    the following text will appear:
    
        posted with KritaToot
    
    Limitations:
    
    Only one image per toot is supported.
    
    Specifiying a focal point is currently not supported
    
    File size and file types as set by the Mastodon server
    
    """

    def __init__(self, parent):
        super().__init__(parent)

    
    def toot(self):
        """
        Invoked when user selects menu option
        """

        self.main = QWidget()
        dialog = KritaTootUI(self.main)
        dialog.exec_()

        #QMessageBox.information(QWidget(), "Toot", 'toot')


    def setup(self):
        """
        Creates a menu action/option for uploading and posting a copy of the current doc on Mastodon.
        
        Also enables/disables logging for troubleshooting bugs in this phase of development.
        Log files are saved in <HOME>/.krita, where HOME is your home directory.
        
        Standard messages are saved in a logfile named 'logfile' and errors in 'logerr'
        """
        
        debug = True
        
        if debug:
            
            appdir = os.path.join( os.path.expanduser('~'), '.kritatoot')
            if not os.path.exists(appdir):
                os.mkdir(appdir)
                
            logfile = os.path.join(appdir, 'logfile.txt')
            logerr = os.path.join(appdir, 'logerr.txt')
            
            sys.stdout = open(logfile, 'w')
            sys.stderr = open(logerr, 'w')
        
        action = Krita.instance().createAction("kritatoot", "Post on Mastodon")
        action.triggered.connect(self.toot)

# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance())) 


