from bs4 import BeautifulSoup
import os
import multiprocessing
import time
import shutil
from tqdm import tqdm
import re
import json
import traceback
import threading
from make_datafiles_conference import extract_json,split

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


def basename(path):
    while path.endswith('\\'):
        path = path[:-1]
    return os.path.basename(path)


def transfer(text):
    chs = ['^', '$', '*', '+', '?', '\\', '[', ']', '|', '{', '}', '(', ')']
    if not text: return None
    for ch in chs:
        if ch in text:
            text = text.replace(ch, '\\' + ch)
    return text


def extract(id, file):
    global save_path
    text = open(file, encoding='utf-8').read()
    soup = BeautifulSoup(text, "html.parser")
    body = soup.body.text
    paragraphs = soup.find_all(['p', 'h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'])

    abstract = None
    article = None
    conclusion = ''
    attrs = None
    tag_name = None
    ABS_text = None
    INT = None
    INT_END = None
    INT_text = None
    INT_END_text = None
    CON = None
    CON_text = None
    CON_END_text = None
    marks = None

    for i in range(0, len(paragraphs)):
        if paragraphs[i].text.startswith("Abstract"):
            ABS_text = "Abstract"
            continue
        if paragraphs[i].text.startswith("ABSTRACT"):
            ABS_text = "ABSTRACT"
            continue

        if len(paragraphs[i].text.split()) < 5:
            if "Introduction" in paragraphs[i].text or "INTRODUCTION" in paragraphs[i].text:
                INT = i + 1
                INT_text = paragraphs[i].text
                tag_name = paragraphs[i].name
                attrs = paragraphs[i].attrs
                break
    if tag_name:
        if 'h' in tag_name:
            heads = soup.find_all(tag_name)
            marks = [head.text for head in heads]

        else:
            ps = soup.find_all(tag_name, attrs=attrs)
            marks = [p.text for p in ps]

    if marks:
        try:
            for i in range(len(marks)):
                if INT_text == marks[i]:
                    INT_END_text = marks[i + 1]
                if 'conclu' in marks[i].lower():
                    CON_text = marks[i]
                    CON_END_text = marks[i + 1]
        except IndexError:
            pass

    if INT_END_text:
        for i in range(INT, len(paragraphs)):
            if paragraphs[i].text == INT_END_text:
                INT_END = i
                continue
            if CON_text and paragraphs[i].text == CON_text:
                CON = i
                break

    if not CON_END_text:
        if "Acknowledgement" in body:
            CON_END_text = "Acknowledgement"
        elif "ACKNOWLEDGEMENT" in body:
            CON_END_text = "ACKNOWLEDGEMENT"
        elif not CON_END_text and "References" in body:
            CON_END_text = "References"
        elif not CON_END_text and "REFERENCES" in body:
            CON_END_text = "REFERENCES"

    ABS_text = transfer(ABS_text)
    # INT = transfer(INT)
    # INT_END = transfer(INT_END)
    CON_END_text = transfer(CON_END_text)

    if ABS_text and INT_text:
        tmp = re.findall('%s(.*?)%s' % (ABS_text, INT_text), body)
        if len(tmp) != 0: abstract = tmp[0]
    if INT and INT_END:
        tmp = ''
        for p in paragraphs[INT:INT_END]:
            if "class" in p.attrs:
                continue
            if "style" in p.attrs:
                if "text-align: center" in p.attrs["style"]:
                    continue
            # if len(p.text.split())<3:
            #     continue
            tmp += p.text + ' '
        if tmp!='':
            article = tmp
        # tmp = re.findall('%s(.*)%s' % (INT, INT_END), body)
        # if len(tmp) != 0: article = tmp[0]
    if CON and CON_END_text:
        body = ' '.join([p.text for p in paragraphs[CON:]])
        tmp = re.findall('%s(.*?)%s' % (CON_text, CON_END_text), body)
        if len(tmp) != 0: conclusion = tmp[0]

    yes = True
    if abstract and article:
        if len(article.split()) < 1000:
            if conclusion and len(conclusion.split()) > 800:
                conclusion=''
            json.dump({"abstract": abstract,
                       "article": article,
                       "conclusion": conclusion,
                       "html": file}, open(os.path.join(save_path, "%d.json" % id), 'w'), indent=4)
            yes = False
    if yes:
        with open(os.path.join(save_path, "%d.skip" % id), 'w') as f:
            f.write('skip')

def delete_skip(path):
    for file in iter_files(path):
        if file.endswith('skip'):
            os.remove(file)

if __name__ == "__main__":

    # # path = 'E:\\HTML\\ICML'
    # save_root = 'E:\\JSON'
    # root_path = r'E:\HTML\conference'
    #
    # global save_path
    # for path in os.listdir(root_path):
    #     path = os.path.join(root_path, path)
    #     print(path)
    #
    #     save_path = os.path.join(save_root, basename(path))
    #     if not os.path.exists(save_path):
    #         os.makedirs(save_path)
    #
    #     start = len(os.listdir(save_path))
    #     print("start with %d" % start)
    #     files = list(iter_files(path))
    #     start_time = time.time()
    #     threads = []
    #     for i in tqdm(range(start, len(files))):
    #         # if time.time() - start_time > 5:
    #         #     for thread in threads:
    #         #         thread.join()
    #         #     threads = []
    #         #     start_time = time.time()
    #         # thread = threading.Thread(target=extract, args=(i,files[i]))
    #         # thread.start()
    #         # threads.append(thread)
    #         extract(i,files[i])
    #
    #     for thread in threads:
    #         thread.join()
    #
    # delete_skip(save_root)
    #
    # d_path = r'E:\JSON\ACL'
    # files = iter_files(d_path)
    # for id, file in enumerate(files):
    #     if file.endswith('.json'):
    #         tmp = json.load(open(file))
    #         abstract = tmp["abstract"]
    #         if "title and abstract" in abstract.lower():
    #             abstract = re.sub("title and abstract.*$", '', abstract, flags=re.I)
    #             tmp["abstract"] = abstract
    #             json.dump(tmp, open(file, 'w'), indent=4)
    #             print(file)
    #
    # path = r'E:\JSON'
    # des = r"E:\conference"
    # if not os.path.exists(des):
    #     os.makedirs(des)
    # extract_json(path, des)
    #
    # path = r'E:\conference'
    # for file in iter_files(path):
    #     paper = json.load(open(file))
    #     a = len(' '.join(paper['abstract']))
    #     b = len(' '.join(paper['article']))
    #     c = len(' '.join(paper['conclusion']))
    #     if a > c + b + 50:
    #         shutil.move(file, r'E:\tmp\conference')
    #         print(file)

    split(r'E:\conference')