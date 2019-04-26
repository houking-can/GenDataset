import os
import shutil
import json
from utils import iter_files




path = r'/home/yhj/dataset/emnlp/val'
# for dir in os.listdir(path):
#     tmp_dir = os.path.join(path,dir)
#     for i,file in enumerate(iter_files(tmp_dir)):
#         shutil.move(file,os.path.join(tmp_dir,"%s-%d.html" % (dir,i)))


# save_path = r'/home/yhj/dataset/emnlp'
# start = len(os.listdir(save_path))
# files = iter_files(path)
# for id, file in enumerate(files):
#     paper = json.load(open(file))
#     abstract = paper['abstract']
#     article = paper['article']
#     if len(abstract) < 2 or len(article) < 2:
#         print(file)
#         os.remove(file)

# files = iter_files(path)
# for id, file in enumerate(files):
#     # id = id + start
#     shutil.move(file, os.path.join(path, "(%d).json" % id))

# files = iter_files(path)
# for id, file in enumerate(files):
#     # id = id + start
#     shutil.move(file, os.path.join(path, "%d.json" % id))
