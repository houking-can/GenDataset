import os

def readlines(path):
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                break

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
