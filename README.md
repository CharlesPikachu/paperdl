<div align="center">
  <img src="./docs/logo.png" width="600"/>
</div>
<br />

[![docs](https://img.shields.io/badge/docs-latest-blue)](https://paperdl.readthedocs.io/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/paperdl)](https://pypi.org/project/paperdl/)
[![PyPI](https://img.shields.io/pypi/v/paperdl)](https://pypi.org/project/paperdl)
[![license](https://img.shields.io/github/license/CharlesPikachu/paperdl.svg)](https://github.com/CharlesPikachu/paperdl/blob/master/LICENSE)
[![PyPI - Downloads](https://pepy.tech/badge/paperdl)](https://pypi.org/project/paperdl/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/paperdl?style=flat-square)](https://pypi.org/project/paperdl/)
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
|  [baiduwenku](https://wenku.baidu.com/)          |   ✗                |  ✓                   |
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

#### Calling API

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

#### Calling EXE

```sh
Usage: paperdl [OPTIONS]

Options:
  --version               Show the version and exit.
  -m, --mode TEXT         the used mode, support "search" and "download"
  -i, --inp TEXT          the paper to download, the supported format is the
                          same as sci-hub
  -s, --source TEXT       the used source, support "arxiv", "scihub" and
                          "googlescholar", you can use "," to split multi
                          sources
  -d, --savedir TEXT      the directory for saving papers
  -l, --logfilepath TEXT  the logging filepath
  -z, --size INTEGER      search size per source
  -p, --proxies TEXT      the proxies to be adopted
  -a, --area TEXT         your area, support "CN" and "EN"
  -c, --cookie TEXT       the cookie copied from the target website, only used
                          in "baiduwenku"
  --help                  Show this message and exit.
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
- [Sciogovterminal](https://github.com/CharlesPikachu/sciogovterminal): Browse "The State Council Information Office of the People's Republic of China" in the terminal.
- [CodeFree](https://github.com/CharlesPikachu/codefree): Make no code a reality.
- [DeepLearningToys](https://github.com/CharlesPikachu/deeplearningtoys): Some deep learning toys implemented in pytorch.
- [DataAnalysis](https://github.com/CharlesPikachu/dataanalysis): Some data analysis projects in charles_pikachu.
- [Imagedl](https://github.com/CharlesPikachu/imagedl): Search and download images from specific websites.
- [Pytoydl](https://github.com/CharlesPikachu/pytoydl): A toy deep learning framework built upon numpy.


# More

#### WeChat Official Accounts

*Charles_pikachu*  
![img](./docs/pikachu.jpg)