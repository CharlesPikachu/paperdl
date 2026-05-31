'''title'''
__title__ = 'paperdl'
'''description'''
__description__ = 'PaperDL: A Unified Asynchronous Framework for Scholarly Paper Search and Download'
'''url'''
__url__ = 'https://github.com/CharlesPikachu/paperdl'
'''version'''
__version__ = '0.2.0'
'''author'''
__author__ = 'Zhenchao Jin'
'''email'''
__email__ = 'charlesblwx@gmail.com'
'''license'''
__license__ = 'Apache License 2.0'
'''copyright'''
__copyright__ = 'Copyright 2022-2026 Zhenchao Jin'
'''import'''
from .paperdl import PaperClient, PaperClientCMD, main
from .modules import ArxivPaperClient, OpenReviewPaperClient, ACLAnthologyPaperClient, BioRxivPaperClient, MedRxivPaperClient, PMLRPaperClient, PMCOAPaperClient
'''all'''
__all__ = [
    '__title__', '__description__', '__url__', '__version__', '__author__', '__email__', '__license__', '__copyright__', 'PaperClient', 'PaperClientCMD', 'main',
    'ArxivPaperClient', 'OpenReviewPaperClient', 'ACLAnthologyPaperClient', 'BioRxivPaperClient', 'MedRxivPaperClient', 'PMLRPaperClient', 'PMCOAPaperClient',
]