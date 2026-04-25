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
import json
import click
import warnings
import threading
if __name__ == '__main__':
    from modules import *
    from __init__ import __version__
else:
    from .modules import *
    from .__init__ import __version__
warnings.filterwarnings('ignore')


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
        assert configpath or config, 'configpath or config should be given'
        self.config = loadConfig(configpath) if config is None else config
        default_config = {
            'logfilepath': 'paperdl.log',
            'search_size_per_source': 5,
            'savedir': 'papers'
        }
        for key, value in default_config.items():
            if key not in self.config: self.config[key] = value
        self.logger_handle = Logger(self.config['logfilepath'])
        self.initializeAllSources()
    '''run'''
    def run(self, target_srcs=None):
        while True:
            print(BASICINFO % (__version__, self.config.get('savedir')))
            # search paper
            user_input = self.dealInput('Input the title of the paper: ')
            target_srcs = [
                'arxiv', 'googlescholar',
            ] if target_srcs is None else target_srcs
            search_results = self.search(user_input, target_srcs)
            # print search results
            title = ['ID', 'Title', 'First Author', 'Source']
            items, records, idx = [], {}, 0
            for key, values in search_results.items():
                for value in values:
                    items.append([
                        colorize(str(idx), 'number'), 
                        colorize(value['title'] if len(value['title']) < 50 else value['title'][:50] + '...', 'title'), 
                        value['authors'].split(',')[0], 
                        value['source'].upper()
                    ])
                    records.update({str(idx): value})
                    idx += 1
            if len(items) < 1: 
                self.logger_handle.error(colorize('No related papers were found', 'red'))
                continue
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
        self.logger_handle.info(f'Searching {colorize(keyword, "highlight")} From {colorize("|".join([c.upper() for c in target_srcs]), "highlight")}')
        def threadSearch(search_api, keyword, target_src, search_results):
            try:
                search_results.update({target_src: search_api(keyword)})
            except Exception as err:
                self.logger_handle.error(str(err), True)
                self.logger_handle.warning(f'Fail to search {colorize(keyword, "highlight")} from {colorize(target_src, "highlight")}')
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
            'baiduwenku': Baiduwenku,
            'googlescholar': GoogleScholar,
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
    '''str'''
    def __str__(self):
        return 'Welcome to use paperdl!\nYou can visit https://github.com/CharlesPikachu/paperdl for more details.'


'''cmd直接运行'''
@click.command()
@click.version_option()
@click.option('-m', '--mode', default='download', help='the used mode, support "search" and "download"')
@click.option('-i', '--inp', default=None, help='the paper to download, the supported format is the same as sci-hub')
@click.option('-s', '--source', default=None, help='the used source, support "arxiv", "scihub" and "googlescholar", you can use "," to split multi sources')
@click.option('-d', '--savedir', default='papers', help='the directory for saving papers')
@click.option('-l', '--logfilepath', default='paperdl.log', help='the logging filepath')
@click.option('-z', '--size', default=5, help='search size per source')
@click.option('-p', '--proxies', default='{}', help='the proxies to be adopted')
@click.option('-a', '--area', default='CN', help='your area, support "CN" and "EN"')
@click.option('-c', '--cookie', default=None, help='the cookie copied from the target website, only used in "baiduwenku"')
def paperdlcmd(mode, inp, source, savedir, logfilepath, size, proxies, area, cookie):
    # prepare
    assert mode in ['search', 'download']
    area = area.upper()
    if mode == 'download': assert inp is not None, 'input url should be specified in download mode'
    config = {
        'logfilepath': logfilepath,
        'savedir': savedir,
        'search_size_per_source': size,
        'proxies': json.loads(proxies),
        'area': area,
    }
    if source is None: 
        target_srcs = ['arxiv', 'googlescholar']
    else:
        target_srcs = [s.strip() for s in source.split(',')]
    client = Paperdl(config=config)
    # if you select the search mode
    if mode == 'search':
        client.run(target_srcs=target_srcs)
    else:
        print(client)
        if source is None: 
            if 'wenku.baidu.com' in inp:
                source = 'baiduwenku'
            else:
                source = 'scihub'
        paperinfo = {
            'savename': inp.strip('/').split('/')[-1],
            'ext': 'pdf',
            'savedir': savedir,
            'input': inp,
            'source': source,
        }
        if source in ['baiduwenku']: paperinfo['cookie'] = cookie
        client.download([paperinfo])


'''run'''
if __name__ == '__main__':
    import os
    rootdir = os.path.split(os.path.abspath(__file__))[0]
    client = Paperdl(os.path.join(rootdir, 'config.json'))
    client.run()