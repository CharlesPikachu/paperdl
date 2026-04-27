'''
Function:
    Implementation of Exceptions
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''


class PaperClientError(RuntimeError):
    """Base exception for all paper clients."""


class PaperRequestError(PaperClientError):
    """Raised when an HTTP request fails."""


class PaperDownloadError(PaperClientError):
    """Raised when downloading a file fails."""