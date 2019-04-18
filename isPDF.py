import os
import tarfile
import shutil
from PyPDF2 import PdfFileReader
def isValidPDF(filename):
    try:
        read = PdfFileReader(filename)
    except:
        return False
    return True

def iter_files(path):
    """Walk through all files located under a root path."""
    if os.path.isfile(path):
        yield path
    elif os.path.isdir(path):
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                yield os.path.join(dirpath, f)
    else:
        raise RuntimeError('Path %s is invalid' % path)


des_path = r'E:\PDF\tmp'
sou_path = r'E:\PDF\ICCV'

for id, file in  enumerate(iter_files(sou_path)):
    if not isValidPDF(file):
        shutil.move(file,des_path)
        print(file)
    print(id)