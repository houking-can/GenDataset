from utils import iter_files,make_vocab
import json
import re
import shutil
from tqdm import tqdm
from utils import split
s_path = r'E:\HTML\a'
d_path = r'E:\DATASET\arxiv_json\arxiv_html'

for file in iter_files(s_path):
    try:
        shutil.move(file,d_path)
    except:
        pass
# in_path = '/home/yhj/dataset/conference_json'
# path = '/home/yhj/dataset/emnlp'
# path = r'E:\DATASET\arxiv_tex'
# for file in tqdm(list(iter_files(path))):
#     paper = json.load(open(file))
#     art = paper['article']
#     abs = paper['abstract']
#     con = paper['conclusion']
#     paper['article'] = [' '.join(each.split()) for each in art]
#     paper['abstract'] = [' '.join(each.split()) for each in abs]
#     paper['conclusion'] = [' '.join(each.split()) for each in con]
#     json.dump(paper,open(file,'w'),indent=4)

# split(path,'/home/yhj/dataset/emnlp')



# make_vocab(in_path,path)

