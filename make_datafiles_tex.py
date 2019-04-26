import os
import json
import shutil
import random
from nltk.tokenize import sent_tokenize
import re
from os.path import exists, join
from segtok.segmenter import split_multi
from tqdm import tqdm
from utils import iter_files
from make_datafiles_html import clean_abs, clean_text


def extract_json(src, des):
    i = 0
    files = list(iter_files(src))

    for file in tqdm(files):
        # print(file)
        tmp = json.load(open(file))['paper']
        paper = dict()
        if "abstract" in tmp:
            conclusion = ''
            abs_len = len(' '.join(tmp["abstract"]).split())
            if abs_len > 210: continue
            flag = False
            for sec in tmp['sections']:
                if "introduction" in sec.lower():
                    int_len = len(' '.join(tmp["sections"][sec]).split())
                    if int_len > 1000 or abs_len > int_len:
                        break
                    abstract = clean_abs(' '.join(tmp["abstract"]))

                    if len(abstract) < 2:
                        break
                    introduction = clean_text(' '.join(tmp["sections"][sec]))
                    if len(introduction) < 2:
                        break
                    flag = True

                if "conclusion" in sec.lower() and flag:
                    con_len = len(' '.join(tmp["sections"][sec]).split())
                    if con_len > 800:
                        conclusion = ''
                        break
                    conclusion = clean_text(' '.join(tmp["sections"][sec]))
                    break

            if flag:
                paper["abstract"] = abstract
                paper["article"] = introduction
                paper["conclusion"] = conclusion
                name = os.path.basename(file)
                name, _ = os.path.splitext(name)
                paper["id"] = name

                json.dump(paper, open(os.path.join(des, "%s.json" % name), 'w'),indent=4)
                i += 1


if __name__ == "__main__":
    path = r'F:\Dataset\json_v1'
    des = r"E:\DATASET\arxiv_tex"
    if not exists(des):
        os.makedirs(des)

    extract_json(path, des)
