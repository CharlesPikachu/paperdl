<div align="center">
  <img src="https://raw.githubusercontent.com/CharlesPikachu/paperdl/main/docs/logo.png" width="600" alt="paperdl logo" />
  <br />

  <a href="https://paperdl.readthedocs.io/">
    <img src="https://img.shields.io/badge/docs-latest-blue" alt="Docs" />
  </a>
  <a href="https://pypi.org/project/paperdl/">
    <img src="https://img.shields.io/pypi/pyversions/paperdl" alt="PyPI - Python Version" />
  </a>
  <a href="https://pypi.org/project/paperdl">
    <img src="https://img.shields.io/pypi/v/paperdl" alt="PyPI" />
  </a>
  <a href="https://github.com/CharlesPikachu/paperdl/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-PolyForm--Noncommercial--1.0.0-blue" alt="License" />
  </a>
  <a href="https://pypi.org/project/paperdl/">
    <img src="https://static.pepy.tech/badge/paperdl" alt="PyPI - Downloads (total)">
  </a>
  <a href="https://pypi.org/project/paperdl/">
    <img src="https://static.pepy.tech/badge/paperdl/month" alt="PyPI - Downloads (month)">
  </a>
  <a href="https://pypi.org/project/paperdl/">
    <img src="https://static.pepy.tech/badge/paperdl/week" alt="PyPI - Downloads (week)">
  </a>
  <a href="https://github.com/CharlesPikachu/musicsquare/actions/workflows/pages/pages-build-deployment">
    <img src="https://github.com/CharlesPikachu/musicsquare/actions/workflows/pages/pages-build-deployment/badge.svg" alt="Pages-Build-Deployment">
  </a>
  <a href="https://github.com/CharlesPikachu/paperdl/issues">
    <img src="https://isitmaintained.com/badge/resolution/CharlesPikachu/paperdl.svg" alt="Issue Resolution" />
  </a>
  <a href="https://github.com/CharlesPikachu/paperdl/issues">
    <img src="https://isitmaintained.com/badge/open/CharlesPikachu/paperdl.svg" alt="Open Issues" />
  </a>
</div>

<p align="center">
	<a href="https://paperdl.readthedocs.io/" target="_blank"><strong>📚 Documents: paperdl.readthedocs.io</strong></a>
</p>


# Introduction

A simple and extensible toolkit for searching, organizing, and downloading academic papers from specific websites.

If this project helps your research workflow, please consider giving it a star ⭐. Your support helps more people discover the project and motivates future improvements.


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


# ⭐ Recommended Projects

| Project                                                    | ⭐ Stars                                                                                                                                               | 📦 Version                                                                                                 | ⏱ Last Update                                                                                                                                                                   | 🛠 Repository                                                        |
| -------------                                              | ---------                                                                                                                                             | -----------                                                                                                | ----------------                                                                                                                                                                 | --------                                                             |
| 🎵 **Musicdl**<br/>轻量级无损音乐下载器                    | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/musicdl?style=flat-square)](https://github.com/CharlesPikachu/musicdl)                   | [![Version](https://img.shields.io/pypi/v/musicdl)](https://pypi.org/project/musicdl)                      | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/musicdl?style=flat-square)](https://github.com/CharlesPikachu/musicdl/commits/master)                   | [🛠 Repository](https://github.com/CharlesPikachu/musicdl)           |
| 🎬 **Videodl**<br/>轻量级高清无水印视频下载器              | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/videodl?style=flat-square)](https://github.com/CharlesPikachu/videodl)                   | [![Version](https://img.shields.io/pypi/v/videofetch)](https://pypi.org/project/videofetch)                | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/videodl?style=flat-square)](https://github.com/CharlesPikachu/videodl/commits/master)                   | [🛠 Repository](https://github.com/CharlesPikachu/videodl)           |
| 🖼️ **Imagedl**<br/>轻量级海量图片搜索下载器                | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/imagedl?style=flat-square)](https://github.com/CharlesPikachu/imagedl)                   | [![Version](https://img.shields.io/pypi/v/pyimagedl)](https://pypi.org/project/pyimagedl)                  | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/imagedl?style=flat-square)](https://github.com/CharlesPikachu/imagedl/commits/main)                     | [🛠 Repository](https://github.com/CharlesPikachu/imagedl)           |
| 🖼️ **Paperdl**<br/>轻量级学术论文搜索下载器                | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/paperdl?style=flat-square)](https://github.com/CharlesPikachu/paperdl)                   | [![Version](https://img.shields.io/pypi/v/paperdl)](https://pypi.org/project/paperdl)                      | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/paperdl?style=flat-square)](https://github.com/CharlesPikachu/paperdl/commits/main)                     | [🛠 Repository](https://github.com/CharlesPikachu/paperdl)           |
| 🌐 **FreeProxy**<br/>全球海量高质量免费代理采集器          | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/freeproxy?style=flat-square)](https://github.com/CharlesPikachu/freeproxy)               | [![Version](https://img.shields.io/pypi/v/pyfreeproxy)](https://pypi.org/project/pyfreeproxy)              | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/freeproxy?style=flat-square)](https://github.com/CharlesPikachu/freeproxy/commits/master)               | [🛠 Repository](https://github.com/CharlesPikachu/freeproxy)         |
| 🌐 **MusicSquare**<br/>简易音乐搜索下载和播放网页          | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/musicsquare?style=flat-square)](https://github.com/CharlesPikachu/musicsquare)           | [![Version](https://img.shields.io/pypi/v/musicdl)](https://pypi.org/project/musicdl)                      | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/musicsquare?style=flat-square)](https://github.com/CharlesPikachu/musicsquare/commits/main)             | [🛠 Repository](https://github.com/CharlesPikachu/musicsquare)       |
| 🌐 **FreeGPTHub**<br/>真正免费的GPT统一接口                | [![Stars](https://img.shields.io/github/stars/CharlesPikachu/FreeGPTHub?style=flat-square)](https://github.com/CharlesPikachu/FreeGPTHub)             | [![Version](https://img.shields.io/pypi/v/freegpthub)](https://pypi.org/project/freegpthub)                | [![Last Commit](https://img.shields.io/github/last-commit/CharlesPikachu/FreeGPTHub?style=flat-square)](https://github.com/CharlesPikachu/FreeGPTHub/commits/main)               | [🛠 Repository](https://github.com/CharlesPikachu/FreeGPTHub)        |


# 📚 Citation

If you use this project in your research, please cite the repository.

```
@misc{musicdl2020,
    author = {Zhenchao Jin},
    title = {Paperdl: Search and download paper from specific websites},
    year = {2022},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/CharlesPikachu/paperdl}},
}
```


# 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=CharlesPikachu/paperdl&type=date&legend=top-left)](https://www.star-history.com/#CharlesPikachu/paperdl&type=date&legend=top-left)


# ☕ Appreciation (赞赏 / 打赏)

| WeChat Appreciation QR Code (微信赞赏码)                                                                                       | Alipay Appreciation QR Code (支付宝赞赏码)                                                                                     |
| :--------:                                                                                                                     | :----------:                                                                                                                   |
| <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/wechat_reward.jpg" width="260" />   | <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/alipay_reward.png" width="260" />   |


# 📢 WeChat Official Account (微信公众号):

Charles的皮卡丘 (*Charles_pikachu*)  
![img](https://raw.githubusercontent.com/CharlesPikachu/paperdl/main/docs/pikachu.jpg)