'''
Function:
    Downloader
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import os
import click
import warnings
import requests
from .misc import touchdir
warnings.filterwarnings('ignore')


'''Downloader'''
class Downloader():
    def __init__(self, paperinfo, session=None, **kwargs):
        self.paperinfo = paperinfo
        self.session = requests.Session() if session is None else session
        self.__setheaders(paperinfo['source'])
    '''start to download according to paperinfo'''
    def start(self):
        paperinfo, session, headers = self.paperinfo, self.session, self.headers
        if not paperinfo['download_url']: return False
        touchdir(paperinfo['savedir'])
        try:
            is_success = False
            with session.get(paperinfo['download_url'], headers=headers, stream=True, verify=False) as response:
                if response.status_code == 200:
                    total_size, chunk_size = int(response.headers['content-length']), 1024
                    label = '[FileSize]: %0.2fMB' % (total_size / 1024 / 1024)
                    with click.progressbar(length=total_size, label=label) as progressbar:
                        with open(os.path.join(paperinfo['savedir'], paperinfo['savename']+'.'+paperinfo['ext']), 'wb') as fp:
                            for chunk in response.iter_content(chunk_size=chunk_size):
                                if chunk:
                                    fp.write(chunk)
                                    progressbar.update(len(chunk))
                    is_success = True
        except:
            is_success = False
        return is_success
    '''set request headers'''
    def __setheaders(self, source):
        self.default_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
        }
        try:
            self.headers = getattr(self, f'{source}_headers')
        except:
            self.headers = self.default_headers