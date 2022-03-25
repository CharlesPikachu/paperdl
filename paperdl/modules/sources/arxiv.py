'''
Function:
    Seach and download papers from arxiv
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
from .base import Base
from bs4 import BeautifulSoup


'''Seach and download papers from arxiv'''
class Arxiv(Base):
    def __init__(self, config=None, logger_handle=None, **kwargs):
        super(Arxiv, self).__init__(config, logger_handle, **kwargs)
        self.source = 'arxiv'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
    '''search paper'''
    def search(self, keyword):
        # search
        keyword = keyword.replace(' ', '+')
        search_url = 'https://arxiv.org/search/?'
        params = {
            'query': keyword,
            'searchtype': 'all',
            'abstracts': 'show',
            'order': '-announced_date_first',
            'size': '50',
        }
        response = self.session.get(search_url, params=params, headers=self.headers)
        # parse
        soup = BeautifulSoup(response.text, features='lxml')
        paperinfos = []
        for item in soup.find('ol').find_all('li', attrs={'class': 'arxiv-result'}):
            try: title = item.find('p', attrs={'class': 'title'}).text.strip()
            except: title = ''
            try: authors = self.cleantext(item.find('p', attrs={'class': 'authors'}).text.strip()).replace('Authors:', '')
            except: authors = ''
            try: url = item.find('p', attrs={'class': 'list-title'}).find('a').attrs['href']
            except: url = ''
            paperinfo = {
                'source': self.source,
                'savedir': self.config['savedir'],
                'ext': 'pdf',
                'savename': title,
                'title': title,
                'authors': authors,
                'download_url': url.replace('abs', 'pdf') + '.pdf',
            }
            paperinfos.append(paperinfo)
            if len(paperinfos) == self.config['search_size_per_source']: break
        # return
        return paperinfos
    '''clean text'''
    def cleantext(self, text):
        text = text.replace('\n', '')
        text, text_clean = text.split(' '), []
        for item in text:
            if item: text_clean.append(item)
        text = ' '.join(text_clean)
        return text