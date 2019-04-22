import os

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


# path = r'E:\PDF\tmp'
# for file in iter_files(path):
#     if file.endswith('.pdf.pdf'):
#         print(file)
#         os.remove(file)





import os
import shutil

def minus(src,des):
    """src: path of 
       des: path of remove items
    """
    src_items = []
    des_items = []
    old = os.path.dirname(des)+'_OLD'


    for file in os.listdir(src):
        file, src_ext= os.path.splitext(os.path.basename(file))
        src_items.append(file)
    for file in os.listdir(des):
        file,des_ext= os.path.splitext(os.path.basename(file))
        des_items.append(file)

    src_items = set(src_items)
    des_items = set(des_items)

    move_items = des_items-src_items
    move_items = des_items-move_items
    print(len(move_items))
    if not os.path.exists(old):
        os.makedirs(old)
    
    for item in move_items:
        print(item)
        try:
            shutil.move(os.path.join(os.path.dirname(des),"%s%s" % (item,des_ext)) ,old)
        except Exception as e:
            print(e)

src_path = r'C:\Users\Houking\Desktop\introduction\decoded'
des_path = r'C:\Users\Houking\Desktop\baseline\decoded'
src_path +='\\'
des_path+='\\'
minus(src_path,des_path)