# This is a sample Python script.
import requests
from bs4 import BeautifulSoup
import os
import json
from utils import get_data_path, get_novels_path
from novelparse import NovelParse
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce
from multiprocessing import Pool
import numpy as np
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

webHead = 'http://www.87shuwu.info'

def get_novels():
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    novels = [{'name': '大明天下', 'url': 'http://www.87shuwu.info/2/2643/'}]
    for novel in novels:
        print('下载小说%s, 链接: %s' % (novel['name'], novel['url']))
        novel_html = requests.get(novel['url'])
        tempPath = os.path.join(get_data_path(), 'temp.html')
        with open(tempPath, 'w+') as file:
            file.write(novel_html.text)
        soup = BeautifulSoup(novel_html.text, 'lxml')

def parsenovel(novel, dictJson):
    print('下载小说%s, 链接: %s' % (novel['name'], novel['url']))
    parser = NovelParse(webHead, novel, dictJson, 0)
    parser.parsePage(novel['url'], True)
    print('Novel %s download complete' % novel['name'])

def parse_novels1(novels):
    dictPath = os.path.join(get_data_path(), 'dict.json')
    dictJson = {}
    try:
        with open(dictPath, 'r') as file:
            dictArray = json.load(file)
            for item in dictArray:
                dictJson[item[0]] = item[1]
    except Exception as e:
        print('Read dict json file erropr: ' + str(e))

    for novel in novels:
        parsenovel(novel, dictJson)

def parse_novels(novels):
    pool = Pool(4)
    # tempPath = os.path.join(get_data_path(), 'temp.html')
    dictPath = os.path.join(get_data_path(), 'dict.json')
    dictJson = {}
    try:
        with open(dictPath, 'r') as file:
            dictArray = json.load(file)
            for item in dictArray:
                dictJson[item[0]] = item[1]
    except Exception as e:
        print('Read dict json file erropr: ' + str(e))
    for novel in novels:
        pool.apply_async(parsenovel, args=(novel, dictJson))
        # with open(tempPath, 'r') as file:
        #     context = file.read()
        #     soup = BeautifulSoup(context, 'lxml')
        #     charpertext = format('%s章节列表' % novel['name'])
        #     heads = soup.find('h4', text=charpertext)
        #     charpers = heads.parent.find_next_sibling('div')
        #     chaperlist = charpers.find_all('a')
        #     for item in chaperlist:
        #         print('href: %s chaper name: %s' % (item.get('href'), item.text))
        #     firstPage = soup.find('a', class_='indexPage')
        #     endPage = soup.find('a', class_='endPage')
        #     firstId = firstPage.get('href')[0: -1].split('_')
        #     endId = endPage.get('href')[0: -1].split('_')
        #     for i in range(int(firstId[1]), int(endId[1])):
        #         href = format('%s_%s' % (firstId[0], i))
        #         print(href)
        #     print(heads)
    pool.close()
    pool.join()
    print('Complete')

def parseFilterNovels(pageUrl):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    page = requests.get(pageUrl, headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')
    bd1 = soup.find('div', class_='bd')
    items = bd1.find_all('div', class_='right')
    novels = []
    for item in items:
        nameItem = item.find('a')
        words = item.find('span', class_='words')
        if int(words.text.split('：')[1]) > 200000 and '绿' not in nameItem.text:
            novels.append({'name': nameItem.text, 'url': webHead + nameItem.get('href')})
    print('Page %s get novel %d' % (pageUrl, len(novels)))
    return novels

def parseFilterNovelPages(baseUrl, prefix, name):
    # baseUrl = 'http://www.87shuwu.info/shuku/7-lastupdate-0-1.html'
    # 完本小说 http://www.87shuwu.info/shuku/0-lastupdate-2-1.html
    # novelPath = os.path.join(get_data_path(), 'novels.html')
    page = requests.get(baseUrl)
    soup = BeautifulSoup(page.text, 'lxml')
    endPage = soup.find('a', class_='endPage')
    endHref = endPage.get('href')
    endIndex = endHref.split('.')[0].split('-')
    novels = []
    threadPool = ThreadPoolExecutor(max_workers=16, thread_name_prefix='novel_filter')
    tasks = [threadPool.submit(parseFilterNovels, (prefix + str(i) + '.html')) for i in range(1, int(endIndex[-1]) + 1)]
    for future in as_completed(tasks):
        novels.extend(future.result())
    # for i in range(1, int(endIndex[-1]) + 1):
    #     pageUrl = prefix + str(i) + '.html'
    #     pageNovels = parseFilterNovels(pageUrl)
    #     novels.extend(pageNovels)
    #     if i % 10 == 0:
    #         print('parse page: %d' % i)
    #         novelPath = os.path.join(get_data_path(), name + '.json')
    #         with open(novelPath, 'w') as file:
    #             file.write(json.dumps(novels))
    novelPath = os.path.join(get_data_path(), name + '.json')
    with open(novelPath, 'w') as file:
        file.write(json.dumps(novels))
    # firstPage = BeautifulSoup(requests.get(baseUrl).text, 'lxml')

def mergeNovelsName():
    names = []
    # with open(os.path.join(get_data_path(), '小说.json'), 'r') as file:
    #     names.extend(json.load(file))
    # names = list(filter(lambda x: '玄幻灵异' not in x['name'] and '古代架空' not in x['name'] and '网游竞技' not in x['name'], names))
    # with open(os.path.join(get_data_path(), '小说.json'), 'w') as file:
    #     file.write(json.dumps(names))

    for filename in ['完本小说.json', '连载小说.json']:
        filepath = os.path.join(get_data_path(), filename)
        with open(filepath, 'r') as file:
            names.extend(json.load(file))
    def nameCheck(name):
        removeContext = ['CP', 'BL', 'NTR', '玄幻灵异', '绿', '古代架空', '网游竞技', '妻', '穿越重生', '近代现代', '无限流派', '古代架空']
        for item in removeContext:
            if item in name:
                return False
        return True
    names = list(filter(lambda x: nameCheck(x['name']), names))
    s = set()
    newNames = []
    for name in names:
        if name['name'] in s:
            continue
        else:
            newNames.append(name)
            s.add(name['name'])
    with open(os.path.join(get_data_path(), '小说.json'), 'w') as file:
        file.write(json.dumps(newNames))

def mergeNovels():
    list_dirs = os.walk(get_data_path())
    novelsPath = get_novels_path()
    for root, dirs, _ in list_dirs:
        for d in dirs:
            if 'img' in d:
                continue
            sub_dirs = os.walk(os.path.join(root, d))
            charpers = []
            for sub_root, _, files in sub_dirs:
                for file in files:
                    file_path = os.path.join(root, d, file)
                    index = file.split('.')[-2].split('_')[-1]
                    with open(file_path, 'r') as f:
                        charpers.append({'context': f.read(), 'index': int(index)})
            charpers.sort(key=lambda x: x['index'])
            result = reduce(lambda pre, item: pre + item['context'], charpers, '')
            save_path = os.path.join(novelsPath, d + '.txt')
            with open(save_path, 'w') as file:
                file.write(result)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # mergeNovelsName()
    # mergeNovels()
    # parseFilterNovelPages('http://www.87shuwu.info/shuku/7-lastupdate-0-1.html', 'http://www.87shuwu.info/shuku/7-lastupdate-0-', '连载小说')
    # parseFilterNovelPages('http://www.87shuwu.info/shuku/0-lastupdate-2-1.html',
    #                       'http://www.87shuwu.info/shuku/0-lastupdate-2-', '完本小说')
    novels = []
    with open(os.path.join(get_data_path(), '小说.json'), 'r') as file:
        novels = json.load(file)
    novelBase = get_novels_path()
    for _, _, files in os.walk(novelBase):
        names = []
        for file in files:
            names.append(file.split('.')[0])
    print('before: %d' % len(novels))
    novels = list(
        filter(lambda x: x['name'] not in names, novels))
    print('end: %d' % len(novels))
    # dictPath = os.path.join(get_data_path(), 'dict.json')
    # try:
    #     with open(dictPath, 'r') as file:
    #         dictJson = json.load(file)
    #         file.close()
    #     dictJson = sorted(dictJson.items(), key=lambda x: x[0])
    #     with open(dictPath, 'w') as file:
    #         file.write(json.dumps(dictJson))
    # except Exception as e:
    #     print('Read dict json file erropr: ' + str(e))
    parse_novels(novels)
    # parse_novels1(novels)
    # get_novels()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
