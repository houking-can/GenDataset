import os
import re
import json


from lxml import html
import argparse
import os
import time
import json
etree = html.etree

class InvalidElementName(Exception):
    def __init__(self, invalid_element_name, tag_name, parent_name):
        self.invalid_element_name = invalid_element_name
        self.tag_name = tag_name
        self.parent_name = parent_name

    def __str__(self):
        return 'Invalid name %s found in tag %s within element %s' % (repr(self.invalid_element_name),
                                                                      repr(self.tag_name),
                                                                      repr(self.parent_name))


def existing_file(filename: str) -> str:
    if os.path.isfile(filename):
        return filename
    else:
        raise argparse.ArgumentTypeError('%s is not a valid input file!' % filename)


def parse_args():
    parser = argparse.ArgumentParser(description='Parse the DBLP XML file and convert it to CSV')
    parser.add_argument('xml_filename', action='store', type=existing_file, help='The XML file that will be parsed',
                        metavar='xml_filename',default='dblp.xml')
    parser.add_argument('dtd_filename', action='store', type=existing_file,
                        help='The DTD file used to parse the XML file', metavar='dtd_filename',default='dblp.dtd')
    parsed_args = parser.parse_args()
    return parsed_args


def get_elements(dtd_file) -> set:
    dtd = etree.DTD(dtd_file)
    elements = set()
    for el in dtd.iterelements():
        if el.type == 'element':
            elements.add(el.name)
    elements.remove('dblp')
    return elements


def parse_xml(xml_file, elements: set):
    writers = dict()
    for each in elements:
        writers[each] = open('./dblp/'+each+'.json','a+')

    context = etree.iterparse(xml_file, dtd_validation=True, events=('start', 'end'))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = next(context)
    data = dict()
    current_tag = None
    unique_id = 0

    for event, elem in context:
        if current_tag is None and event == 'start' and elem.tag in elements:
            current_tag = elem.tag
            data.clear()
            data.update(elem.attrib)

        elif current_tag is not None and event == 'end' and elem.tag in elements:
            data['id'] = unique_id
            tmp = json.dumps(data)
            writers[current_tag].write(tmp + '\n')
            writers[current_tag].flush()
            if unique_id % 10000:
                print(unique_id)
            unique_id += 1
            current_tag = None
        elif elem.tag is not None and elem.text is not None:
            if elem.tag=="author":
                if "author" in data:
                    data[elem.tag].append(elem.text)
                else:
                    data[elem.tag] = [elem.text]
            else:
                data[elem.tag] = elem.text

    root.clear()
    for each in elements:
        writers[each].close()



def readlines(path):
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                break

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


def remove_old(path):
    files = iter_files(path)
    for file in files:
        filename = os.path.basename(file)
        print(filename)
        f = open(os.path.join('./final',filename),'a+')
        lines = readlines(file)
        i = 0
        cnt=0
        for line in lines:
            article = json.loads(line)
            if 'year' in article:
                if int(article['year'])>=2000:
                    if "author" in article:
                        article['author']=list(set(article['author']))
                        tmp = json.dumps(article)
                        f.write(tmp+'\n')
                        f.flush()

                        i += 1
                        # if i % 100000 == 0:
                        #     print(i)
                    else:
                        cnt+=1

            else:
                cnt+=1
        print('%s  skip:%d, save %d' % (filename,cnt,i))




def parse_dblp():
    args = parse_args()
    if args.xml_filename is not None and args.dtd_filename is not None :
        start_time = time.time()
        print('Start!')
        with open(args.dtd_filename, 'rb') as dtd_file:
            print('Reading elements from DTD file...')
            elements = get_elements(dtd_file)

        with open(args.xml_filename, 'rb') as xml_file:
            print('Parsing XML and writing to CSV files...')
            parse_xml(xml_file, elements)

        end_time = time.time()
        print('Done after %f seconds' % (end_time - start_time))
    else:
        print('Invalid input arguments.')
        exit(1)


if __name__ == "__main__":
    remove_old('./dblp')
