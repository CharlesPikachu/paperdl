'''
Function:
    Seach and download papers from Sci-hub
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import re
from .base import Base
from lxml import etree
from ..utils import Downloader
from urllib.parse import urlparse


'''Seach and download papers from Sci-hub'''
class SciHub(Base):
    def __init__(self, config=None, logger_handle=None, **kwargs):
        super(SciHub, self).__init__(config, logger_handle, **kwargs)
        self.source = 'scihub'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
    '''parse paper infos before dowload paper'''
    def parseinfosbeforedownload(self, paperinfos):
        scihub_sites = [
            'https://sci-hub.st/', 'https://sci-hub.ru/', 'https://sci-hub.se/', 
            'https://sci-hub.shop/', 'http://sci-hub.ren/', 
        ]
        # fetch pdf url
        for paperinfo in paperinfos:
            input_content = paperinfo['input']
            input_type = self.guessinputtype(input_content)
            if input_type == 'pdf': 
                paperinfo['download_url'] = input_content
            elif input_type == 'arxiv':
                paperinfo['download_url'] = input_content.replace('abs', 'pdf') + '.pdf'
            else:
                for scihub_site in scihub_sites:
                    self.headers.update({'Referer': scihub_site})
                    try: response = self.session.get(scihub_site + input_content, headers=self.headers, verify=False)
                    except: continue
                    if response.status_code not in [200]: continue
                    html = etree.HTML(response.content)
                    article = html.xpath('//div[@id="article"]/embed[1]') or html.xpath('//div[@id="article"]/iframe[1]') if html is not None else None
                    if not article: continue
                    pdf_url = urlparse(article[0].attrib['src'], scheme='http').geturl()
                    paperinfo['download_url'] = pdf_url
                    break
            if 'download_url' not in paperinfo: paperinfo['download_url'] = None
            paperinfo['source'] = self.source
        # return
        return paperinfos
    '''guess input type'''
    def guessinputtype(self, input_content):
        input_type, doi_pattern = None, re.compile(r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'])\S)+)\b')
        if input_content.startswith('http') or input_content.startswith('https'):
            if '.pdf' in input_content: input_type = 'pdf'
            elif 'arxiv' in input_content: input_type = 'arxiv'
            else: input_type = 'url'
        elif input_content.isdigit(): input_type = 'pmid'
        elif input_content.startswith('doi:') or doi_pattern.match(input_content): input_type = 'doi'
        else: input_type = 'string'
        return input_type