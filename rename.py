import os
import shutil
import json


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


path = r'F:\EMNLP\test'
files = iter_files(path)
for id, file in enumerate(files):
    paper = json.load(open(file))
    abstract = paper['abstract']
    article = paper['article']
    if len(abstract) < 2 or len(article) < 2:
        print(file)
        os.remove(file)

files = iter_files(path)
for id, file in enumerate(files):
    shutil.move(file, os.path.join(path, "(%d).json" % id))

files = iter_files(path)
for id, file in enumerate(files):
    shutil.move(file, os.path.join(path, "%d.json" % id))
