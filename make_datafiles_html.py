import os
import json
import shutil
import random
from nltk.tokenize import sent_tokenize
import re
from os.path import exists, join
from utils import iter_files


def clean_abs(sent):
    sent = sent.lower()
    sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
    sent = re.sub("title and abstract.*$", '', sent)
    sent = re.sub('-\s+', '', sent)
    sent = re.sub('\{.*?\}','@cite',sent)
    sent = re.sub('etc\s*\.', ' etc. ', sent)

    # sent = re.sub('e\s*\.\s*g\s*\.\s*,', ' e.g., ', sent)
    sent = re.sub('e\s*\.\s*g\s*\.\s*', ' e.g., ', sent)

    # sent = re.sub('et\s*al\s*\.\s*,', ' et al., ', sent)
    sent = re.sub('et\s*al\s*\.\s*', ' et al., ', sent)

    # sent = re.sub('i\s*\.\s*e\s*\.\s*,', ' i.e., ', sent)
    sent = re.sub('i\s*\.\s*e\s*\.\s*', ' i.e., ', sent)

    sent = re.sub('[;|:]', '. ', sent)
    sent = re.sub(',[\s|,]*,', ', ', sent)

    sent = sent_tokenize(sent)
    res = []
    for each in sent:
        if "keywords:" in each:
            continue
        each = each.strip()
        each = each.lstrip(',')
        each = each.lstrip('.')
        each = ' '.join(each.split())
        res.append(each)
    return res


def clean_text(sent):
    sent = sent.lower()
    sent = re.sub('[~|\'|\"|``|\t|\n]', ' ', sent)
    # sent = re.sub('\[.*et\s*al.*\]', ' @cite', sent)
    # sent = re.sub('\(.*et\s*al.*?\)', ' @cite', sent)
    sent = re.sub('\[.*?\]', ' @cite', sent)
    sent = re.sub('\{.*?\}', '@cite', sent)
    # sent = re.sub('\(.*?\d{4}.*?\)', ' @cite', sent)
    sent = re.sub('-\s+', '', sent)

    sent = re.sub('etc\s*\.', ' etc. ', sent)

    # sent = re.sub('e\s*\.\s*g\s*\.\s*,', ' e.g., ', sent)
    sent = re.sub('e\s*\.\s*g\s*\.\s*', ' e.g., ', sent)

    # sent = re.sub('et\s*al\s*\.\s*,', ' et al., ', sent)
    sent = re.sub('et\s*al\s*\.\s*', ' et al., ', sent)

    # sent = re.sub('i\s*\.\s*e\s*\.\s*,', ' i.e., ', sent)
    sent = re.sub('i\s*\.\s*e\s*\.\s*', ' i.e., ', sent)

    sent = re.sub('[;|:]', '. ', sent)
    sent = re.sub(',[\s|,]*,', ', ', sent)

    cites = re.findall('\(.*?\)', sent)
    for cite in cites:
        if re.match('\(.*?\d{4}.*?\)', cite) or re.match('\(.*?et al.*?\)', cite):
            sent = sent.replace(cite, ' @cite')

    res = []
    sent = sent_tokenize(sent)
    for each in sent:
        if len(each.split()) < 4:
            continue
        each = each.strip()
        each = each.lstrip(',')
        each = each.lstrip('.')
        each = ' '.join(each.split())
        res.append(each)

    return res


def extract_json_dir(src, des):
    i = 0
    files = list(iter_files(src))
    length = len(files)
    for id, file in enumerate(files):
        print("%d/%d" % (id, length))
        paper = json.load(open(file))

        a = len(paper['abstract'].split())
        b = len(paper['article'].split())
        if a > b:
            continue

        abs_len = len(paper["abstract"].split())
        if abs_len > 210: continue

        abstract = clean_abs(paper['abstract'])
        if len(abstract) < 2: continue
        article = clean_text(paper["article"])
        if len(article) < 2: continue

        conclusion = clean_text(paper["conclusion"])

        paper["abstract"] = abstract
        paper["article"] = article
        paper["conclusion"] = conclusion

        json.dump(paper, open(os.path.join(des, "%d.json" % i), 'w'), indent=4)
        i += 1


def extract_json_single(paper):
    abs_len = len(paper['abstract'].split())
    art_len = len(paper['article'].split())
    if abs_len > art_len:
        return None

    if abs_len > 210: return None

    abstract = clean_abs(paper['abstract'])
    if len(abstract) < 2: return None
    article = clean_text(paper["article"])
    if len(article) < 2: return None

    conclusion = clean_text(paper["conclusion"])

    paper["abstract"] = abstract
    paper["article"] = article
    paper["conclusion"] = conclusion

    return paper


def split(src, ratio=0.94):
    files = list(iter_files(src))
    random.shuffle(files)
    len_train = int(len(files) * ratio)
    len_val = int(len(files) * (1 - ratio) / 2)
    len_test = len(files) - len_train - len_val
    train = files[:len_train]
    val = files[len_train:len_train + len_val]
    test = files[-len_test:]

    if not exists(join(src, 'train')): os.makedirs(join(src, 'train'))
    if not exists(join(src, 'test')): os.makedirs(join(src, 'test'))
    if not exists(join(src, 'val')): os.makedirs(join(src, 'val'))
    for each in train:
        shutil.move(each, join(src, 'train'))
    for each in test:
        shutil.move(each, join(src, 'test'))
    for each in val:
        shutil.move(each, join(src, 'val'))
