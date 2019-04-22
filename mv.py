import os
import json
import shutil
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

path = r'E:\ARXIV'
for file in iter_files(path):
    paper= json.load(open(file))
    a= len(' '.join(paper['abstract']))
    b= len(' '.join(paper['article']))
    c=len(' '.join(paper['conclusion']))
    if a>c+b+50:
        shutil.move(file,r'E:\tmp\arxiv')
        print(file)