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


# 🎉 What's New

- 2026-05-30: 


# 🧠 Introduction

A simple and extensible toolkit for searching, organizing, and downloading academic papers from specific websites.

If this project helps your research workflow, please consider giving it a star ⭐. Your support helps more people discover the project and motivates future improvements.


# 🛡️ Project Disclaimer

This repository is intended for lawful, educational, academic, and research-related purposes only, such as learning Python, exploring academic paper search workflows, and assisting non-profit research or study.

Users are solely responsible for ensuring that their use of this project complies with applicable laws, website terms of service, copyright rules, publisher policies, institutional requirements, and third-party rights. This project must not be used for illegal purposes, copyright infringement, unauthorized access, abusive downloading, or any activity that may harm authors, publishers, platforms, or institutions.

This project is released under the Apache License 2.0. The authors and contributors provide no warranty, commercial authorization, indemnity, or liability commitment beyond the license terms, and are not responsible for any misuse or consequences arising from the use, modification, redistribution, or commercial application of this project.


# 📚 Supported Paper Clients

| Client                                                       | Description                                                                                                                                                           | 🔎 Search | ⬇️ Download    | Code Snippet                                                                                                                               |
| ----------------------------------------------------         | ------------------------------------------------------------------------------------------------------------------------------------------                            | --------: | ----------:   | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [ArxivPaperClient](https://arxiv.org/)                       | arXiv preprint search and PDF download.<br>arXiv 预印本论文搜索与 PDF 下载。                                                                                          |    ✅     |     ✅        | [arxiv_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/arxiv_paper_client.py)                 |
| [OpenReviewPaperClient](https://openreview.net/)             | OpenReview paper search and PDF download, especially for conference submissions and reviews.<br>OpenReview 论文搜索与 PDF 下载，适合会议投稿与评审数据。              |    ✅     |     ✅        | [openreview_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/openreview_paper_client.py)       |
| [ACLAnthologyPaperClient](https://aclanthology.org/)         | ACL Anthology paper search and PDF download for NLP and computational linguistics papers.<br>ACL Anthology 论文搜索与 PDF 下载，主要面向 NLP 和计算语言学论文。       |    ✅     |     ✅        | [acl_anthology_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/acl_anthology_paper_client.py) |
| [BioRxivPaperClient](https://www.biorxiv.org/)               | bioRxiv preprint search and PDF download for biology-related papers.<br>bioRxiv 生物学预印本论文搜索与 PDF 下载。                                                     |    ✅     |     ✅        | [biorxiv_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/biorxiv_paper_client.py)             |
| [MedRxivPaperClient](https://www.medrxiv.org/)               | medRxiv preprint search and PDF download for medical and health science papers.<br>medRxiv 医学与健康科学预印本论文搜索与 PDF 下载。                                  |    ✅     |     ✅        | [biorxiv_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/biorxiv_paper_client.py)             |
| [PMLRPaperClient](https://proceedings.mlr.press/)            | PMLR paper search and PDF download for machine learning proceedings.<br>PMLR 机器学习会议论文集搜索与 PDF 下载。                                                      |    ✅     |     ✅        | [pmlr_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/pmlr_paper_client.py)                   |
| [PMCOAPaperClient](https://pmc.ncbi.nlm.nih.gov/)            | PubMed Central Open Access paper search and PDF download.<br>PubMed Central 开放获取论文搜索与 PDF 下载。                                                             |    ✅     |     ✅        | [pmc_oa_paper_client.py](https://github.com/CharlesPikachu/paperdl/blob/main/paperdl/modules/engines/pmc_oa_paper_client.py)               |


# ⚙️ Installation

Paperdl requires Python 3.10+. Using a virtual environment is recommended to avoid dependency conflicts.

Install from PyPI:

```bash
python -m pip install -U paperdl
```

Or install the latest version from GitHub:

```bash
python -m pip install -U git+https://github.com/CharlesPikachu/paperdl.git@main
```

For local development:

```bash
git clone https://github.com/CharlesPikachu/paperdl.git
cd paperdl
python -m pip install -e .
```

Most paper clients work without browser dependencies. However, some bioRxiv / medRxiv PDF downloads may require the optional Playwright-based browser fallback.

Install with browser support:

```bash
python -m pip install -U "paperdl[browser]"
python -m playwright install chromium
```

For local development with browser support:

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

On some Linux servers, Playwright may also require system dependencies:

```bash
python -m playwright install-deps chromium
```


# 🚀 Quick Start



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
    title = {Paperdl: A Unified Asynchronous Framework for Scholarly Paper Search and Download},
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