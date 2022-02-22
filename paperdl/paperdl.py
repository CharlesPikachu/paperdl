'''
Function:
    Paperdl: Search and download paper from specific websites
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import sys
import copy
import warnings
import threading
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
    download: input IDs (e.g., '1, 2') to download multi papers
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
    '''run'''
    def run(self, target_srcs=None):
        while True:
            print(BASICINFO % (__version__, self.config.get('savedir')))
            # search paper
            user_input = self.dealInput('Input the title of the paper: ')
            target_srcs = [
                'arxiv'
            ] if target_srcs is None else target_srcs
            search_results = self.search(user_input, target_srcs)
            # print search results
            title = ['ID', 'Title', 'First Author', 'Source']
            items, records, idx = [], {}, 0
            for key, values in search_results.items():
                for value in values:
                    items.append([str(idx), value['title'], value['authors'].split(',')[0], value['source']])
                    records.update({str(idx): value})
                    idx += 1
            printTable(title, items)
            # download papers
            user_input = self.dealInput('Input the paper ID you want to download: ')
            need_download_numbers = user_input.replace(' ', '').split(',')
            paperinfos = []
            for item in need_download_numbers:
                paperinfo = records.get(item, '')
                if paperinfo: paperinfos.append(paperinfo)
            self.download(paperinfos)
    '''search paper'''
    def search(self, keyword, target_srcs):
        def threadSearch(search_api, keyword, target_src, search_results):
            try:
                search_results.update({target_src: search_api(keyword)})
            except Exception as err:
                self.logger_handle.error(str(err), True)
                self.logger_handle.warning(f'Fail to search {keyword} from {target_src}')
        task_pool, search_results = [], {}
        for target_src in target_srcs:
            task = threading.Thread(
                target=threadSearch,
                args=(getattr(self, target_src).search, keyword, target_src, search_results)
            )
            task_pool.append(task)
            task.start()
        for task in task_pool:
            task.join()
        return search_results
    '''download paper'''
    def download(self, paperinfos):
        for paperinfo in paperinfos:
            getattr(self, paperinfo['source']).download([paperinfo])
    '''initialize all sources'''
    def initializeAllSources(self):
        supported_sources = {
            'arxiv': Arxiv,
            'scihub': SciHub,
        }
        for key, value in supported_sources.items():
            setattr(self, key, value(copy.deepcopy(self.config), self.logger_handle))
        return supported_sources
    '''deal with user inputs'''
    def dealInput(self, tip=''):
        user_input = input(tip)
        if user_input.lower() == 'q':
            self.logger_handle.info('ByeBye')
            sys.exit()
        elif user_input.lower() == 'r':
            self.initializeAllSources()
            self.run()
        else:
            return user_input


'''run'''
if __name__ == '__main__':
    client = Paperdl('config.json')
    client.run()