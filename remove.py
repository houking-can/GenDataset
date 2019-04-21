from bs4 import BeautifulSoup
import os
import multiprocessing
import time
import shutil
from tqdm import tqdm

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


def extract(file):
    global save_path
    text = open(file, encoding='utf-8').read()
    soup = BeautifulSoup(text, "html.parser")
    body = soup.body.text
    paragraphs = soup.find_all(['p', 'h', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'])

    abstract = ''
    article = ''
    conclusion = ''

    attrs = None
    tag_name = None

    flags = {'abstract': False, 'introduction': False, "conclusion": False}

    for i in range(0, len(paragraphs)):

        if paragraphs[i].text.startswith("Abstract") or paragraphs[i].text.startswith("ABSTRACT"):
            flags["abstract"] = True
            continue
        if "Introduction" in paragraphs[i].text or "INTRODUCTION" in paragraphs[i].text:
            flags["introduction"] = True
            tag_name = paragraphs[i].name
            attrs = paragraphs[i].attrs
            break
    if not flags["abstract"] or not flags["introduction"]:
        shutil.move(file,save_path)
        print(file)




if __name__ == "__main__":

    path = r'E:\HTML\ACL'
    save_root = r'E:\HTML\NO'
    global save_path
    save_path = os.path.join(save_root, basename(path))
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    pool = multiprocessing.Pool(processes=8)
    for file in tqdm(list(iter_files(path))):
        extract(file)
        # pool.apply_async(extract, (file,))
    pool.close()
    pool.join()
