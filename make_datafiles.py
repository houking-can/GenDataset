import collections
import io
import json
import os
import pickle as pkl
import tarfile
import json

dm_single_close_quote = '\u2019'  # unicode
dm_double_close_quote = '\u201d'
# acceptable ways to end a sentence
END_TOKENS = ['.', '!', '?', '...', "'", "`", '"',
              dm_single_close_quote, dm_double_close_quote, ")"]


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


def write_to_tar(path, out_file, makevocab=False):
    """Reads the tokenized .story files corresponding to the urls listed in the
       url_file and writes them to a out_file.
    """
    print("Making bin file for URLs listed in {}...".format(path))

    papers = list(iter_files(path))
    num_papers = len(papers)

    if makevocab:
        vocab_counter = collections.Counter()

    with tarfile.open(out_file, 'w') as writer:
        for idx, file in enumerate(papers):
            if idx % 1000 == 0:
                print("Writing paper {} of {}; {:.2f} percent done".format(
                    idx, num_papers, float(idx) * 100.0 / float(num_papers)))
            paper = json.load(open(file))
            paper["id"]=os.path.basename(file).replace('.json','')
            js_serialized = json.dumps(paper, indent=4).encode()
            save_file = io.BytesIO(js_serialized)
            tar_info = tarfile.TarInfo('{}/{}.json'.format(
                os.path.basename(out_file).replace('.tar', ''), idx))
            tar_info.size = len(js_serialized)
            writer.addfile(tar_info, save_file)

            # Write the vocab to file, if applicable
            if makevocab:
                art_tokens = ' '.join(paper['article']).split()
                abs_tokens = ' '.join(paper['abstract']).split()
                tokens = art_tokens + abs_tokens
                tokens = [t.strip() for t in tokens]  # strip
                tokens = [t for t in tokens if t != ""]  # remove empty
                vocab_counter.update(tokens)

    print("Finished writing file {}\n".format(out_file))

    # write vocab to file
    if makevocab:
        print("Writing vocab file...")
        with open(os.path.join(finished_files_dir, "vocab_cnt.pkl"),
                  'wb') as vocab_file:
            pkl.dump(vocab_counter, vocab_file)
        print("Finished writing vocab file")


if __name__ == '__main__':
    root_dir = r'E:\conference'
    all_train = "%s/train" % root_dir
    all_val = "%s/val" % root_dir
    all_test = "%s/test" % root_dir

    finished_files_dir = r"E:\conference"

    # Create some new directories
    if not os.path.exists(finished_files_dir):
        os.makedirs(finished_files_dir)

    # Read the tokenized stories, do a little postprocessing
    # then write to bin files
    write_to_tar(all_test, os.path.join(finished_files_dir, "test.tar"))
    write_to_tar(all_val, os.path.join(finished_files_dir, "val.tar"))
    write_to_tar(all_train, os.path.join(finished_files_dir, "train.tar"),
                 makevocab=True)
