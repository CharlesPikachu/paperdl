'''
Function:
    Downloader
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import os
import requests
from .misc import touchdir
from alive_progress import alive_bar


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
        with session.get(paperinfo['download_url'], headers=headers, stream=True) as response:
            if response.status_code not in [200]: return False
            total_size, chunk_size, downloaded_size = int(response.headers['content-length']), paperinfo.get('chunk_size', 1024), 0
            savepath = os.path.join(paperinfo['savedir'], f"{paperinfo['savename']}.{paperinfo['ext']}")
            text, fp = '[FileSize]: %0.2fMB/%0.2fMB', open(savepath, 'wb')
            with alive_bar(manual=True) as bar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if not chunk: continue
                    fp.write(chunk)
                    downloaded_size += chunk_size
                    bar.text(text % (downloaded_size / 1024 / 1024, total_size / 1024 / 1024))
                    bar(min(downloaded_size / total_size, 1))
        return True
    '''set request headers'''
    def __setheaders(self, source):
        if hasattr(self, f'{source}_headers'):
            self.headers = getattr(self, f'{source}_headers')
        else:
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
            }