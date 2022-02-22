'''
Function:
    Paperdl: Search and download paper from specific websites
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import sys
import warnings
if __name__ == '__main__':
    from modules import *
    from __init__ import __version__
else:
    from .modules import *
    from .__init__ import __version__


'''basic info'''
BASICINFO = '''************************************************************
Function: Paperdl V%s
Author: Charles
WeChat public account: Charles_pikachu
Help:
    input r: initialize the program
    input q: quit the program
Savedir:
    The downloaded papers are saved in %s
************************************************************'''


'''Paperdl'''
class Paperdl():
    def __init__(self, configpath=None, config=None, **kwargs):
        assert configpath or config, 'configpath or config should be given...'
        self.config = loadConfig(configpath) if config is None else config
        self.logger_handle = Logger(self.config['logfilepath'])
        self.initializeAllSources()
    '''initialize all sources'''
    def initializeAllSources(self):
        supported_sources = {
            'scihub': SciHub,
        }
        for key, value in supported_sources.items():
            setattr(self, key, value(copy.deepcopy(self.config), self.logger_handle))
        return supported_sources


'''run'''
if __name__ == '__main__':
    config = {
        "logfilepath": "paperdl.log",
        "proxies": {},
        "search_size_per_source": 5,
        "savedir": "downloaded"
    }
    paperinfo = {
        'input': 'https://ieeexplore.ieee.org/abstract/document/9216499',
        'savedir': 'outputs',
        'savename': 'sss',
        'ext': 'pdf'
    }
    logger_handle = Logger(config['logfilepath'])
    SciHub(config=config, logger_handle=logger_handle).dowload([paperinfo])