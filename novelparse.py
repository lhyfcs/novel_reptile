
from utils import get_data_path, get_novel_path
import os
import requests
from bs4 import BeautifulSoup
from charperparse import ChaperParse
import json

class NovelParse:
    def __init__(self, webHead, novel, dictJson, charperIndex = 0):
        self.novel = novel
        self.charperIndex = charperIndex
        self.webHead = webHead
        self.dictJson = dictJson
        try:
            folderPath = get_novel_path(novel)
            if not os.path.exists(folderPath):
                os.makedirs(folderPath)
        except Exception as e:
            print('Create folder error:' + str(e))

    def parse_context(self, soup, novleUrl):
        context = ''
        data = soup.find('div', class_='page-content')
        p = data.find('p')
        for child in p.contents:
            if len(child) == 4 and child[0] == '\xa0':
                continue
            elif child.name == 'br':
                continue
            elif child.name == 'img':
                imgUrl = child.get('src')
                if self.dictJson.get(imgUrl):
                    c = self.dictJson.get(imgUrl)
                else:
                    c = 'liu'
                    self.dictJson[imgUrl] = 'liu'
                context += c
            elif child.name == 'font':
                continue
            else:
                context += child
        print(context)
        # parse other subpage
        subpage = soup.find('div', class_='page-control')
        subpage = subpage.find_next_sibling('div')
        items = subpage.find_all('a')
        for item in items:
            print(novleUrl + item.get('href'))


    def parsePage(self, pageUrl, first = False):
        if (first):
            pageUrl = self.novel['url']
        novel_html = requests.get(pageUrl)
        soup = BeautifulSoup(novel_html.text, 'lxml')
        charpertext = format('%s章节列表' % self.novel['name'])
        heads = soup.find('h4', text=charpertext)
        charpers = heads.parent.find_next_sibling('div')
        chaperlist = charpers.find_all('a')
        for item in chaperlist:
            print('href: %s chaper name: %s' % (item.get('href'), item.text))
            # charper = requests.get(self.webHead + item.get('href'))
            # charpPath = os.path.join(get_data_path(), 'charper.html')
            # with open(charpPath, 'w') as file:
            #     file.write(charper.text)
            # with open(charpPath) as file:
            #     context = file.read()
            #     soupC = BeautifulSoup(context, 'lxml')
            #     self.parse_context(soupC, pageUrl)

            chaper = ChaperParse(self.webHead + item.get('href'), self.novel['url'], self.novel['name'], item.text, self.charperIndex, self.dictJson)
            chaper.parseCharper()
            dictPath = os.path.join(get_data_path(), 'dict.json')
            sortArr = sorted(self.dictJson.items(), key=lambda x: x[0])
            sortArr = sorted(sortArr, key=lambda x: x[1])
            with open(dictPath, 'w') as file:
                imgDict = json.dumps(sortArr)
                file.write(imgDict)
            self.charperIndex += 1
        if first:
            firstPage = soup.find('a', class_='indexPage')
            endPage = soup.find('a', class_='endPage')
            firstId = firstPage.get('href')[0: -1].split('_')
            endId = endPage.get('href')[0: -1].split('_')
            for i in range(int(firstId[1]) + 1, int(endId[1]) + 1):
                href = format('%s_%s/' % (firstId[0], i))
                self.parsePage(self.webHead + href, False)




