import shutil
import random
from os.path import exists,join
import collections
import io
import os
import pickle as pkl
import tarfile
import json
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


def minus(src, des):
    """src: path of
       des: path of remove items
    """
    src_items = []
    des_items = []
    old = os.path.dirname(des) + '_OLD'

    for file in os.listdir(src):
        file, src_ext = os.path.splitext(os.path.basename(file))
        src_items.append(file)
    for file in os.listdir(des):
        file, des_ext = os.path.splitext(os.path.basename(file))
        des_items.append(file)

    src_items = set(src_items)
    des_items = set(des_items)

    move_items = des_items - src_items
    move_items = des_items - move_items
    print(len(move_items))
    if not os.path.exists(old):
        os.makedirs(old)

    for item in move_items:
        print(item)
        try:
            shutil.move(os.path.join(os.path.dirname(des), "%s%s" % (item, des_ext)), old)
        except Exception as e:
            print(e)

def split(src,des,ratio=0.94):
    files = list(iter_files(src))
    random.shuffle(files)
    len_train = int(len(files)*ratio)
    len_val =  int(len(files)*(1-ratio)/2)
    len_test = len(files)-len_train-len_val
    train = files[:len_train]
    val = files[len_train:len_train+len_val]
    test = files[-len_test:]

    if not exists(join(des,'train')):os.makedirs(join(des,'train'))
    if not exists(join(des, 'test')): os.makedirs(join(des, 'test'))
    if not exists(join(des, 'val')): os.makedirs(join(des, 'val'))
    for each in train:
        shutil.copy(each,join(des,'train'))
    for each in test:
        shutil.copy(each,join(des,'test'))
    for each in val:
        shutil.copy(each,join(des,'val'))


def make_vocab(input, output):

    vocab_counter = collections.Counter()

    files = list(iter_files(input))

    for file in tqdm(files):
        paper = json.load(open(file))
        art_tokens = ' '.join(paper['article']).split()
        abs_tokens = ' '.join(paper['abstract']).split()
        con_tokens = ' '.join(paper['conclusion']).split()
        tokens = art_tokens + abs_tokens + con_tokens
        tokens = [t.strip() for t in tokens]  # strip
        tokens = [t for t in tokens if t != ""]  # remove empty
        vocab_counter.update(tokens)
    for each in ['<unk>','<pad>','<start>','<end>']:
        if each in vocab_counter:
            vocab_counter.pop(each)
    print("Writing vocab file...")
    with open(os.path.join(output, "vocab_cnt.pkl"),
              'wb') as vocab_file:
        pkl.dump(vocab_counter, vocab_file)
    print("Finished writing vocab file")

