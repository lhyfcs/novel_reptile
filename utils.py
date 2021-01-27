import os

def get_data_path():
    pwd = os.getcwd()
    return os.path.join(pwd, 'data')

def get_novels_path():
    # pwd = os.getcwd()
    # return os.path.join(pwd, 'novel')
    return '/Users/liujin/personal/novels'

def get_novel_path(novel):
    pwd = os.getcwd()
    return os.path.join(pwd, 'data', novel['name'])

def get_chaper_path(novelName, charperName):
    pwd = os.getcwd()
    return os.path.join(pwd, 'data', novelName, charperName)

def get_img_save_path(url):
    pwd = os.getcwd()
    urlParts = url.split('/')
    return os.path.join(pwd, 'data', 'img', urlParts[-1])