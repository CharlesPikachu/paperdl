<div align="center">
  <img src="./docs/logo.png" width="600"/>
</div>
<br />

[![docs](https://img.shields.io/badge/docs-latest-blue)](https://paperdl.readthedocs.io/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/paperdl)](https://pypi.org/project/paperdl/)
[![PyPI](https://img.shields.io/pypi/v/paperdl)](https://pypi.org/project/paperdl)
[![license](https://img.shields.io/github/license/CharlesPikachu/paperdl.svg)](https://github.com/CharlesPikachu/paperdl/blob/master/LICENSE)
[![PyPI - Downloads](https://pepy.tech/badge/paperdl)](https://pypi.org/project/paperdl/)
[![issue resolution](https://isitmaintained.com/badge/resolution/CharlesPikachu/paperdl.svg)](https://github.com/CharlesPikachu/paperdl/issues)
[![open issues](https://isitmaintained.com/badge/open/CharlesPikachu/paperdl.svg)](https://github.com/CharlesPikachu/paperdl/issues)

Documents: https://paperdl.readthedocs.io/


# Paperdl
```
Search and download paper from specific websites.
You can star this repository to keep track of the project if it's helpful for you, thank you for your support.
```


# Support List
|  Source                                          |   Support Search?  |  Support Download?   |
|  :----:                                          |   :----:           |  :----:              |
|  [scihub](https://sci-hub.st/)                   |   ✗                |  ✓                   |
|  [arxiv](https://arxiv.org/)                     |   ✓                |  ✓                   |
|  [googlescholar](https://scholar.google.com/)    |   ✓                |  ✓                   |


# Install
#### Pip install
```
run "pip install paperdl"
```
#### Source code install
```sh
(1) Offline
Step1: git clone https://github.com/CharlesPikachu/paperdl.git
Step2: cd paperdl -> run "python setup.py install"
(2) Online
run "pip install git+https://github.com/CharlesPikachu/paperdl.git@master"
```


# Quick Start

If you want to search and download papers from arxiv and google scholar, you can write codes as follow:
```python
from paperdl import paperdl

config = {'logfilepath': 'paperdl.log', 'savedir': 'papers', 'search_size_per_source': 5, 'proxies': {}}
target_srcs = ['arxiv', 'googlescholar']
client = paperdl.Paperdl(config=config)
client.run(target_srcs)
```
In addition, if you can not visit google, you can set config as follow:
```python
config = {'logfilepath': 'paperdl.log', 'savedir': 'papers', 'search_size_per_source': 5, 'proxies': {}, 'area': 'CN'}
```
You can also only download papers by using sci-hub as follow:
```python

from paperdl import paperdl

config = {'logfilepath': 'paperdl.log', 'savedir': 'papers', 'search_size_per_source': 5, 'proxies': {}}
client = paperdl.SciHub(config=config, logger_handle=paperdl.Logger('paper.log'))
paperinfo = {
    'savename': '9193963',
    'ext': 'pdf',
    'savedir': 'outputs',
    'input': 'https://ieeexplore.ieee.org/document/9193963/',
    'source': 'scihub',
}
client.download([paperinfo])
```



# Screenshot
![img](./docs/screenshot.gif)


# Projects in Charles_pikachu
- [Games](https://github.com/CharlesPikachu/Games): Create interesting games by pure python.
- [DecryptLogin](https://github.com/CharlesPikachu/DecryptLogin): APIs for loginning some websites by using requests.
- [Musicdl](https://github.com/CharlesPikachu/musicdl): A lightweight music downloader written by pure python.
- [Videodl](https://github.com/CharlesPikachu/videodl): A lightweight video downloader written by pure python.
- [Pytools](https://github.com/CharlesPikachu/pytools): Some useful tools written by pure python.
- [PikachuWeChat](https://github.com/CharlesPikachu/pikachuwechat): Play WeChat with itchat-uos.
- [Pydrawing](https://github.com/CharlesPikachu/pydrawing): Beautify your image or video.
- [ImageCompressor](https://github.com/CharlesPikachu/imagecompressor): Image compressors written by pure python.
- [FreeProxy](https://github.com/CharlesPikachu/freeproxy): Collecting free proxies from internet.
- [Paperdl](https://github.com/CharlesPikachu/paperdl): Search and download paper from specific websites.


# More
#### WeChat Official Accounts
*Charles_pikachu*  
![img](./docs/pikachu.jpg)