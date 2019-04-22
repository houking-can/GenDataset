import os
import json
import shutil
import random
from nltk.tokenize import sent_tokenize
import re
from os.path import exists,join


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


def clean_abs(sent):

    sent = sent.strip()
    sent = sent.lower()
    sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
    sent = re.sub('-\s+','',sent)
    sent = sent_tokenize(sent)
    res = []
    for each in sent:
        if "keywords:" in each:
            continue
        res.append(each)
    return res


def clean_text(sent):

    sent = sent.strip()
    sent = sent.lower()
    sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
    # sent = re.sub('\[.*et\s*al.*\]', ' @cite', sent)
    sent = re.sub('\(.*et\s*al.*\)', ' @cite', sent)
    sent = re.sub('\[.*\]', ' @cite', sent)
    sent = re.sub('\(.*\d{4}.*\)', ' @cite', sent)
    sent = re.sub('-\s+', '', sent)

    sent = re.sub('e\s*\.g\s*\.\s*,', ' e.g., ', sent)
    sent = re.sub('e\s*\.g\s*\.\s*', ' e.g., ', sent)
    sent = re.sub('etc\s*\.', ' etc. ', sent)
    sent = re.sub('et\s*al\s*\.\s*,', ' et al., ', sent)
    sent = re.sub('i\s*\.e\s*\.\s*,', ' i.e., ', sent)
    sent = re.sub('[;|:]', '. ', sent)
    sent = re.sub(',[\s|,]*,', ', ', sent)
    sent = re.sub('\s*\.\s*', '. ', sent)
    res = []
    sent = sent_tokenize(sent)
    for each in sent:
        if len(each.split())<4:
            continue
        res.append(each)

    return res


def extract_json(src,des):
    i = 0
    files = list(iter_files(src))
    length = len(files)
    for id,file in enumerate(files):
        print("%d/%d" % (id,length))
        paper = json.load(open(file))

        a = len(paper['abstract'].split())
        b = len(paper['article'].split())
        if a > b:
            continue

        abs_len = len(paper["abstract"].split())
        if abs_len > 210: continue

        abstract = clean_abs(paper['abstract'])
        if len(abstract)<2:continue
        article = clean_text(paper["article"])
        if len(article)<2:continue


        conclusion = clean_text(paper["conclusion"])


        paper["abstract"] = abstract
        paper["article"] = article
        paper["conclusion"] = conclusion
        paper.pop("html")

        json.dump(paper, open(os.path.join(des, "%d.json" % i), 'w'),indent=4)
        i += 1

    print(i)

def split(src,ratio=0.94):
    files = list(iter_files(src))
    random.shuffle(files)
    len_train = int(len(files)*ratio)
    len_val =  int(len(files)*(1-ratio)/2)
    len_test = len(files)-len_train-len_val
    train = files[:len_train]
    val = files[len_train:len_train+len_val]
    test = files[-len_test:]

    if not exists(join(src,'train')):os.makedirs(join(src,'train'))
    if not exists(join(src, 'test')): os.makedirs(join(src, 'test'))
    if not exists(join(src, 'val')): os.makedirs(join(src, 'val'))
    for each in train:
        shutil.move(each,join(src,'train'))
    for each in test:
        shutil.move(each,join(src,'test'))
    for each in val:
        shutil.move(each,join(src,'val'))

if __name__ == "__main__":
    path = r'E:\JSON'
    des = r"E:\conference"
    if not exists(des):
        os.makedirs(des)

    extract_json(path,des)
    # split(des)


