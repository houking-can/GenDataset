import os
import shutil
import json
import re
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

d_path = r'E:\JSON\ACL'


files = iter_files(d_path)
for id,file in enumerate(files):
    if file.endswith('.json'):
        tmp = json.load(open(file))
        abstract = tmp["abstract"]
        if "title and abstract" in abstract.lower():
            abstract = re.sub("title and abstract.*$",'',abstract,flags=re.I)
            tmp["abstract"] =abstract
            json.dump(tmp,open(file,'w'),indent=4)
            print(file)


# files = iter_files(path)
# for id,file in enumerate(files):
# 	shutil.move(file,os.path.join(path,"%d_decoded.txt" % id))
