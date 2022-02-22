'''
Function:
    Some utils related with logging
Author:
    Charles
WeChat public account:
    Charles_pikachu
'''
import logging
from prettytable import PrettyTable


'''Logger'''
class Logger():
    def __init__(self, logfilepath, **kwargs):
        setattr(self, 'logfilepath', logfilepath)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[logging.FileHandler(logfilepath), logging.StreamHandler()],
        )
    @staticmethod
    def log(level, message):
        logging.log(level, message)
    def debug(self, message, disable_print=False):
        if disable_print:
            fp = open(self.logfilepath, 'a')
            fp.write(message + '\n')
        else:
            Logger.log(logging.DEBUG, message)
    def info(self, message, disable_print=False):
        if disable_print:
            fp = open(self.logfilepath, 'a')
            fp.write(message + '\n')
        else:
            Logger.log(logging.INFO, message)
    def warning(self, message, disable_print=False):
        if disable_print:
            fp = open(self.logfilepath, 'a')
            fp.write(message + '\n')
        else:
            Logger.log(logging.WARNING, message)
    def error(self, message, disable_print=False):
        if disable_print:
            fp = open(self.logfilepath, 'a')
            fp.write(message + '\n')
        else:
            Logger.log(logging.ERROR, message)


'''print table'''
def printTable(title, items):
    assert isinstance(title, list) and isinstance(items, list), 'title and items should be list...'
    table = PrettyTable(title)
    for item in items: table.add_row(item)
    print(table)
    return table