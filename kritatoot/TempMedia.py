
import os
import inspect
from tempfile import gettempdir


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
        
        tempbase = os.path.basename(docname)
        pathname = os.path.join(tempdir, tempbase)
        
        doc.exportImage(pathname, InfoObject())
        
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
    