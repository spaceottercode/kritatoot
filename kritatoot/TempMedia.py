
import os
import inspect
from tempfile import gettempdir
import re


from krita import *

def saveTempMedia():
    """
    exports the current doc in Krita to a temp location and returns the file's
    pathname, or None on failure
    """
    #thisscript = inspect.getfile(saveTempMedia)
    #parentfolder = os.path.dirname(thisscript)
    
    #return os.path.join(parentfolder, 'images/all/homepage.png')
    
    try:
        doc =  Krita.instance().activeDocument()
        
        if not doc:
            print('no active doc')
            return None
        
        tempdir = gettempdir()
        
        docname = doc.fileName()
        
        if not docname:
            docname = 'noname.png'
        
        # Check if the file in question is one that can be uploaded to mastodon

        match = re.search(r"\w+\.png|jpeg|gif|jpg", docname)

        # If not, save as a png.
        if match is None:
            docname = re.sub(r"(\.\w+)", ".png", docname, flags=re.IGNORECASE)

        tempbase = os.path.basename(docname)
        pathname = os.path.join(tempdir, tempbase)
        
        batchmode = doc.batchmode()
        doc.setBatchmode(True)
        doc.exportImage(pathname, InfoObject())
        doc.setBatchmode(batchmode)
        
        print('export current doc as %s' % pathname)
        
        if not os.path.exists(pathname):
            print('temp file not found')
            return None
            
    except Exception:
        print('failed to export/create a temp copy of the current doc')
        pathname = None
        
    
    return pathname
    
    
def removeTempMedia(pathname):
    """
    remove a temp file
    """
    
    try:
        os.remove(pathname)
        return True
        
    except Exception:
        print('Failed to remove temp file "%s"' % pathname)
        return False
    
