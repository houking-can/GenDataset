import os
import json

path = r'/home/yhj/dataset/emnlp/train'


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


i = 0
files = list(iter_files(path))
max_sent_abs = 0
max_sent_art = 0
sum_abs = 0
sum_art = 0
max_abs = 0
max_art = 0
max_abs_full = 0
max_art_full = 0
sum_abs_full = 0
sum_art_full = 0

for file in files:
    paper = json.load(open(file))

    sum_abs += len(paper['abstract'])
    sum_art += len(paper['article'])

    for each in paper['abstract']:
        max_sent_abs = max(max_sent_abs, len(each.split()))

    for each in paper['article']:
        max_sent_art = max(max_sent_art, len(each.split()))

    sum_abs_full += len(' '.join(paper["abstract"]).split())
    sum_art_full += len(' '.join(paper["article"]).split())

    max_abs_full = max(max_abs_full, len(' '.join(paper["abstract"]).split()))
    max_art_full = max(max_art_full, len(' '.join(paper["article"]).split()))

    max_abs = max(len(paper['abstract']), max_abs)
    max_art = max(len(paper['article']), max_art)

print("摘要最长单词数: %d" % max_abs_full)
print("文章最长单词数: %d" % max_art_full)

print("摘要中最长句子数: %d" % max_abs)
print("文章中最长句子数: %d" % max_art)

print("摘要中句子最长单词数 %d" % max_sent_abs)
print("文章中句子最长单词数 %d" % max_sent_art)

print("论文平均摘要句子数: %d" % int(sum_abs / len(files)))
print("论文平均文章句子数: %d" % int(sum_art / len(files)))

print("论文平均摘要单词数: %d" % int(sum_abs_full / len(files)))
print("论文平均文章单词数: %d" % int(sum_art_full / len(files)))
