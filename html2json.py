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
from make_datafiles_html import extract_json_single
from utils import iter_files,split

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
    name = os.path.basename(file)
    name,_ = os.path.splitext(name)
    save_name = os.path.join(save_path,name)

    if soup.body is None:
        with open(save_name+'.skip', 'w') as f:
            f.write('skip')
        return
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

        # if len(paragraphs[i].text.split()) < 5:
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
        try:
            tmp = re.findall('%s(.*?)%s' % (ABS_text, INT_text), body)
            if len(tmp) != 0: abstract = tmp[0]
        except:
            pass
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
        try:
            body = ' '.join([p.text for p in paragraphs[CON:]])
            tmp = re.findall('%s(.*?)%s' % (CON_text, CON_END_text), body)
            if len(tmp) != 0: conclusion = tmp[0]
        except:
            conclusion=''


    yes = True
    if abstract and article:
        article = re.sub('^.*introduction', '', INT_text, flags=re.I) + article
        if len(article.split()) < 1000:
            if isinstance(conclusion,tuple):conclusion=""
            elif conclusion and len(conclusion.split()) > 800:
                conclusion=''
            res = extract_json_single(
                    {"abstract": abstract,
                       "article": article,
                       "conclusion": conclusion,
                       "id": name})
            if  res:
                json.dump(res, open(save_name+'.json', 'w'), indent=4)
                yes = False
    if yes:
        with open(save_name+".skip", 'w') as f:
            f.write('skip')

def delete_skip(path):
    for file in iter_files(path):
        if file.endswith('skip'):
            os.remove(file)

if __name__ == "__main__":

    save_root = '/home/yhj/dataset/conference_json'
    root_path = '/home/yhj/dataset/conference'

    # debug = False

    global save_path
    for path in os.listdir(root_path):
        path = os.path.join(root_path, path)
        print(path)

        save_path = os.path.join(save_root, basename(path))
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        start = len(os.listdir(save_path))

        # if debug:start=0

        print("start with %d" % start)
        files = list(iter_files(path))
        start_time = time.time()
        for i in tqdm(range(start, len(files))):
            extract(i,files[i])

    delete_skip(save_root)

    # split(r'E:\conference')