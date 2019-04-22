import os
import json
import shutil
import random
from nltk.tokenize import sent_tokenize
import re
from os.path import exists,join
from segtok.segmenter import split_multi

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


def clean_abs(sents):
    res = []
    for sent in sents:

        sent = sent.strip()
        sent = sent.lower()
        if "keywords:" in sent:
            continue
        # sent = sent.replace(';', ' . ')
        sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
        sent = re.sub('{.*}', ' @cite ', sent)
        res.append(' '.join(sent.split()))
    return res


def clean_int(sents):
    introduction = []
    paragraph = []
    for sent in sents:
        sent = sent.lower()

        sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
        sent = re.sub('{.*}', ' @cite', sent)
        sent = re.sub('\(.*\)',' @remark',sent)
        sent = re.sub('\[.*\]', ' @cite', sent)

        sent = re.sub('e\s*\.g\s*\.\s*,', ' e.g., ', sent)
        sent = re.sub('e\s*\.g\s*\.\s*', ' e.g., ', sent)
        sent = re.sub('etc\s*\.', ' etc. ', sent)
        sent = re.sub('et\s*al\s*\.\s*,', ' et al., ', sent)
        sent = re.sub('i\s*\.e\s*\.\s*,', ' i.e., ', sent)
        sent = re.sub('[;|:]', '. ', sent)
        sent = re.sub(',[\s|,]*,', ', ', sent)
        sent = re.sub('\s*\.\s*', '. ',sent)

        tmp = split_multi(sent)

        res = []

        for each in tmp:
            if 'i.e' not in each and 'e.g' not in each:
                x = sent_tokenize(each)
                for y in x:
                    y = y.split()
                    if len(y) < 5: continue
                    y = ' '.join(y)
                    res.append(y)
                continue
            each = each.split()
            if len(each)<5:continue
            each = ' '.join(each)

            res.append(each)
        paragraph.append(len(res))
        introduction.extend(res)
    return introduction, paragraph


def clean_con(sents):
    conclusion = []

    for sent in sents[:3]:
        sent = sent.lower()
        sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
        sent = re.sub('{.*}', ' @cite', sent)
        sent = re.sub('\(.*\)', ' @remark', sent)
        sent = re.sub('\[.*\]', ' @cite', sent)

        sent = re.sub('e\s*\.g\s*\.\s*,', ' e.g., ', sent)
        sent = re.sub('e\s*\.g\s*\.\s*', ' e.g., ', sent)
        sent = re.sub('etc\s*\.', ' etc. ', sent)
        sent = re.sub('et\s*al\s*\.\s*,', ' et al., ', sent)
        sent = re.sub('i\s*\.e\s*\.\s*,', ' i.e., ', sent)
        sent = re.sub('[;|:]', '. ', sent)
        sent = re.sub(',[\s|,]*,', ', ', sent)
        sent = re.sub('\s*\.\s*', '. ', sent)

        tmp = split_multi(sent)

        res = []

        for each in tmp:
            if 'i.e' not in each and 'e.g' not in each:
                x = sent_tokenize(each)
                for y in x:
                    y = y.split()
                    if len(y) < 5: continue
                    y = ' '.join(y)
                    res.append(y)
                continue
            each = each.split()
            if len(each)<5:continue
            each = ' '.join(each)

            res.append(each)

        conclusion.extend(res)
    return conclusion, len(conclusion)

def extract_json(src,des):
    i = 0
    files = iter_files(src)

    for id, file in enumerate(files):
        print(file)
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
                    if int_len > 1000:
                        break
                    abstract = clean_abs(tmp["abstract"])
                    if len(abstract)<2:
                        break
                    introduction, _ = clean_int(tmp["sections"][sec])
                    if len(introduction)<2:
                        break
                    flag = True

                if "conclusion" in sec.lower() and flag:
                    con_len = len(' '.join(tmp["sections"][sec]).split())
                    if con_len>800:
                        break
                    conclusion, _ = clean_con(tmp["sections"][sec])
                    break

            if flag:
                paper["abstract"] = abstract
                paper["article"] = introduction
                paper["conclusion"] = conclusion

                json.dump(paper, open(os.path.join(des, "%d.json" % i), 'w'))
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
    path = r'F:\Dataset\json_v1'
    des = r"E:\ARXIV"
    if not exists(des):
        os.makedirs(des)

    extract_json(path,des)
    # split(des)


