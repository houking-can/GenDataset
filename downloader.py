import os
import re
import time
import urllib.parse
import urllib.request
import urllib.request
from copy import deepcopy
from multiprocessing.dummy import Pool as ThreadPool
import shutil
import threading

def readlines(path):
    """ iterate file per line """
    with open(path, 'r') as f:
        while True:
            line = f.readline()
            if line:
                yield line
            else:
                break

def user_proxy(ip, url):
    proxy = urllib.request.ProxyHandler({'https': ip})
    opener = urllib.request.build_opener(proxy, urllib.request.HTTPHandler)
    urllib.request.install_opener(opener)
    try:
        data = urllib.request.urlopen(url).read()
        return data
    except Exception as e:
        global proxy_address
        global new_proxy
        if ip in proxy_address:
            proxy_address.remove(ip)
        if ip in new_proxy:
            new_proxy.remove(ip)
        return None


def get_proxies():
    while True:
        if over: break
        bind_ip_url = 'your bind ip url'

        data = urllib.request.urlopen(bind_ip_url).read()
        print(data.decode('utf-8'))

        ip_url = 'your api url'
        data = urllib.request.urlopen(ip_url).read()
        data = data.decode("utf-8")
        global new_proxy
        tmp = data.split()
        new_proxy += tmp
        FILE['ip'].write('\n'.join(tmp)+'\n')
        FILE['ip'].flush()
        time.sleep(10)


def download(index, url):
    global proxy_address
    global new_proxy
    global start
    index = start + index
    # timeout = 12
    start_time = time.time()
    while new_proxy == [] and proxy_address == []:
        time.sleep(1)
    if time.time() - start_time > 14:
        FILE['log'].write(str(index) + '\n')
        FILE['skip'].write(url + '\n')
        print('proxy is none, skip url: %d' % index)
        return

    # print("processing: " + str(index))
    old_proxy = deepcopy(proxy_address)
    while True:
        if time.time() - start_time > 14: break
        # print(len(new_proxy),len(proxy_address))
        tmp_proxy = deepcopy(proxy_address + new_proxy)
        for proxy in tmp_proxy:
            data = user_proxy(proxy, url)  # use proxy
            if data:
                data = data.decode("utf-8")
                pdf_link = re.findall('href = # onclick.*href=\'(.*)\'', data)
                if len(pdf_link) == 1:
                    if proxy not in proxy_address:
                        proxy_address.append(proxy)
                    link = pdf_link[0].replace('?download=true', '')
                    print(str(index) + " " + link)
                    FILE['pdf'].write(link + '\n')
                    FILE['log'].write(str(index) + '\n')
                    return
        if len(proxy_address) == 0:
            proxy_address = old_proxy
            break

    print('skip url: %d' % index)
    FILE['skip'].write(url + '\n')
    FILE['log'].write(str(index) + '\n')


def downloader(url_path):
    global start
    start = 0
    if os.path.exists('log.txt'):
        start = len(open('log.txt').readlines())
    print("start at %d\n" % start)


    threads = []
    lines = readlines(url_path)
    for _ in range(start): next(lines)
    for id, url in enumerate(lines):
        if len(threads) > 50:
            print('################### join ###################')
            for name, fp in FILE.items():
                fp.flush()
                shutil.copy('./%s.txt' % name, r'E:\PDF')
            for thread in threads:
                thread.join(2)
            threads = []

        url = url.replace('\n', '')
        url = url.strip()
        thread = threading.Thread(target=download, args=(id, "https://sci-hub.tw/" + url))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    global over
    over = True


if __name__ == '__main__':

    global over
    global proxy_address
    global new_proxy

    global old_proxy
    over = False
    proxy_address = []
    new_proxy = []
    old_proxy = []


    FILE_LIST = ['pdf', 'skip', 'log', 'ip']
    FILE = dict()
    for each in FILE_LIST:
        FILE[each] = open('%s.txt' % each, 'a+')

    # url_path = 'url/doi.txt'


    main_pool = ThreadPool(processes=2)
    main_pool.apply_async(get_proxies)

    downloader(url_path = 'url/doi_0.txt')

    main_pool.close()
    main_pool.join()
    for name, fp in FILE.items():
        fp.close()
        shutil.copy('./%s.txt' % name, r'E:\PDF')