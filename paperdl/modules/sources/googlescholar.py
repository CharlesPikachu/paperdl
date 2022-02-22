'''
Function:
    Seach and download papers from google scholar
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import random
from .scihub import SciHub
from bs4 import BeautifulSoup


'''Seach and download papers from google scholar'''
class GoogleScholar(SciHub):
    def __init__(self, config=None, logger_handle=None, **kwargs):
        super(GoogleScholar, self).__init__(config, logger_handle, **kwargs)
        self.source = 'googlescholar'
    '''search paper'''
    def search(self, keyword):
        # search
        if self.config.get('area') == 'CN':
            search_url = random.choice([
                'https://xs2.dailyheadlines.cc/scholar',
                'https://scholar.lanfanshu.cn/scholar',
            ])
            params = {
                'hl': 'zh-CN',
                'as_sdt': '0,33',
                'q': keyword,
                'btnG': ''
            }
        else:
            search_url = 'https://scholar.google.com/scholar'
            params = {
                'hl': 'en',
                'as_sdt': '0,5',
                'q': keyword,
                'btnG': ''
            }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
        response = self.session.get(search_url, params=params, headers=headers)
        # parse
        soup = BeautifulSoup(response.text, features='lxml')
        papers = soup.find_all('div', class_='gs_r')
        paperinfos = []
        for paper in papers:
            try:
                pdf = paper.find('div', class_='gs_ggs gs_fl')
                link = paper.find('h3', class_='gs_rt')
                if pdf: input_content = pdf.find('a')['href']
                elif link.find('a'): input_content = link.find('a')['href']
                else: continue
                title = link.text
                authors = paper.find('div', class_='gs_a').text.split('\xa0')[0]
                paperinfo = {
                    'input': input_content,
                    'source': self.source,
                    'savedir': self.config['savedir'],
                    'ext': 'pdf',
                    'savename': title,
                    'title': title,
                    'authors': authors,
                    'download_url': None,
                }
            except:
                continue
            paperinfos.append(paperinfo)
            if len(paperinfos) == self.config['search_size_per_source']: break
        # return
        return paperinfos