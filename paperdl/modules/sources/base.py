'''
Function:
    Base class for the paper sources
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import time
import requests
from ..utils.downloader import Downloader


'''Base class for the paper sources'''
class Base():
    def __init__(self, config, logger_handle, **kwargs):
        default_config = {
            'logfilepath': 'paperdl.log',
            'search_size_per_source': 5,
            'savedir': 'papers'
        }
        for key, value in default_config.items():
            if key not in config: config[key] = value
        self.source = None
        self.session = requests.Session()
        self.session.proxies.update(config['proxies'])
        self.config = config
        self.logger_handle = logger_handle
        if self.logger_handle is None:
            from ..utils import Logger
            self.logger_handle = Logger(config['logfilepath'])
    '''search paper'''
    def search(self, keyword):
        raise NotImplementedError('not to be implemented...')
    '''download paper'''
    def download(self, paperinfos):
        if hasattr(self, 'parseinfosbeforedownload'): paperinfos = self.parseinfosbeforedownload(paperinfos)
        default_config = {
            'savedir': 'papers',
            'savename': f'downloaded_{int(time.time())}',
            'ext': 'pdf',
            'source': self.source,
        }
        for paperinfo in paperinfos:
            for key, value in default_config.items():
                if key not in paperinfo: paperinfo[key] = value
            self.logger_handle.info(f"Downloading {paperinfo['savename']} from {self.source}")
            task = Downloader(paperinfo, self.session)
            if task.start():
                self.logger_handle.info(f"Downloaded {paperinfo['savename']} from {self.source} successfully")
            else:
                self.logger_handle.info(f"Fail to download {paperinfo['savename']} from {self.source}")
    '''repr'''
    def __repr__(self):
        return 'Paper Source: %s' % self.source