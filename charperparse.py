
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce
from utils import get_chaper_path, get_img_save_path
import threading
import urllib.request
import os
webHead = 'http://www.87shuwu.info'

class ChaperParse:
    def __init__(self, url, pageUrl, novelName, name, index, dictJson):
        self.index = index
        self.url = url
        self.name = name
        self.novelName = novelName
        self.pageUrl = pageUrl
        self.dictJson = dictJson
        self.lock = threading.RLock()
        self.threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="page download")

    def saveImage(self, url):
        filePath = get_img_save_path(url)
        if os.path.exists(filePath):
            return
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
        request = urllib.request.Request(url=webHead + url, headers=headers)
        pic = urllib.request.urlopen(request)

        with open(filePath, 'wb') as localFile:
            localFile.write(pic.read())

    def parseData(self, object, soup = None, first = False):
        url = object['url']
        index = object['index']
        if not first:
            soup = BeautifulSoup(requests.get(url).text, 'lxml')
        data = soup.find('div', class_='page-content')
        context = ''
        p = data.find('p')
        for child in p.contents:
            try:
                if len(child) == 4 and child[0] == '\xa0':
                    continue
                elif child.name == 'br':
                    if len(context) > 1 and context[-1] == '\n':
                        continue
                    context += '\n'
                elif child.name == 'img':
                    imgUrl = child.get('src')
                    if not imgUrl:
                        continue
                    if self.dictJson.get(imgUrl):
                        c = self.dictJson.get(imgUrl)
                    else:
                        c = 'liu'
                        self.lock.acquire()
                        self.dictJson[imgUrl] = 'liu'
                        self.saveImage(imgUrl)
                        self.lock.release()
                    context += c
                elif child.name == 'font':
                    continue
                elif not child.name:
                    if child[0] == '\xa0':
                        context += child[4:].strip()
                    else:
                        context += child.strip()
                else:
                    pass
            except Exception as e:
                print("error when parse context: " + str(e))
        return context, index

    def parseCharper(self):
        soup = BeautifulSoup(requests.get(self.url).text, 'lxml')
        context, index = self.parseData({'url': '', 'index': 0}, soup, True)
        pageContext = [];
        pageContext.append({'index': index, 'context': context})
        # parse other subpage
        subpage = soup.find('div', class_='page-control')
        subpage = subpage.find_next_sibling('div')
        items = subpage.find_all('a')
        # {'url': items[i+1].get('href'), 'index': i + 1}
        tasks = [self.threadPool.submit(self.parseData, ({'url': self.pageUrl + items[i+1].get('href'), 'index': i + 1})) for i in range(len(items[1:]))]
        for future in as_completed(tasks):
            context, index = future.result()
            pageContext.append({'index': index, 'context': context })
        pageContext.sort(key=lambda c: c['index'])
        result = reduce(lambda pre, item: pre + item['context'], pageContext, '')
        novelPath = get_chaper_path(self.novelName, self.name + '_' + str(self.index) + '.txt')
        try:
            with open(novelPath, 'w') as file:
                file.write(result)
        except Exception as e:
            print('Save file exception: %s' % novelPath)

