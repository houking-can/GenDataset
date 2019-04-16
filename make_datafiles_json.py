import os
import json
import shutil
import threading
from nltk.tokenize import sent_tokenize
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


def clean_abs(sents):
    res = []
    for sent in sents:

        sent = sent.strip()
        sent = sent.lower()
        if "keywords:" in sent:
            continue
        sent = sent.replace(';', ' . ')
        sent = re.sub('[~|\'|\"|``|\t|\n|-]', ' ', sent)
        sent = re.sub('{.*}', ' @cite ', sent)
        res.append(' '.join(sent.split()))
    return res


def clean_int(sents):
    introduction = []
    paragraph = []
    for sent in sents:
        sent = sent.lower()
        sent = sent.replace(';', ' . ')
        sent = re.sub('[~|\'|\"|``|\t|\n|-]', ' ', sent)
        sent = re.sub('{.*}', ' @cite ', sent)
        tmp = sent_tokenize(sent)
        res = []
        for each in tmp:
            each = each.split()
            if len(each)<5:continue
            each = ' '.join(each)
            res.append(each)
        paragraph.append(len(res))
        introduction.extend(res)
    return introduction, paragraph


if __name__ == "__main__":

    i = 1
    files = iter_files(r'F:\Dataset\json_v1')
    des = r"F:\emnlp"
    for id, file in enumerate(files):
        print(file)
        tmp = json.load(open(file))['paper']
        paper = dict()
        if "abstract" in tmp:
            abs_len = len(' '.join(tmp["abstract"]).split())
            if abs_len > 210: continue
            for sec in tmp['sections']:
                if "introduction" in sec.lower():
                    int_len = len(' '.join(tmp["sections"][sec]).split())
                    if int_len > 1000:
                        break
                    abstract = clean_abs(tmp["abstract"])
                    introduction, paragraph = clean_int(tmp["sections"][sec])
                    paper["abstract"] = abstract
                    paper["introduction"] = introduction
                    paper["paragraph"] = paragraph
                    json.dump(paper, open(os.path.join(des, "%d.json" % i), 'w'))
                    i += 1
        print(i)
