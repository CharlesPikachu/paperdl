'''
Function:
    Misc utils
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import os
import re
import json


'''touch dir'''
def touchdir(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
        return False
    return True


'''load config file'''
def loadConfig(filepath='config.json'):
    f = open(filepath, 'r', encoding='utf-8')
    return json.load(f)


'''clear bad characters in filename'''
def filterBadCharacter(string):
    need_removed_strs = ['<em>', '</em>', '<', '>', '\\', '/', '?', ':', '"', '：', '|', '？', '*']
    for item in need_removed_strs:
        string = string.replace(item, '')
    try:
        rule = re.compile(u'[\U00010000-\U0010ffff]')
    except:
        rule = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    string = rule.sub('', string)
    return string.strip().encode('utf-8', 'ignore').decode('utf-8')