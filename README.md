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

- 2026-05-31: Paperdl has received a major upgrade: all code has been rewritten to be asynchronous, with support for paper search and download across seven major platforms, including arXiv, OpenReview, ACL Anthology, bioRxiv, medRxiv, PMLR, and PMC OA. The documentation has also been comprehensively optimized.


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

Paperdl is a unified asynchronous toolkit for scholarly paper search and PDF download. It can be used in two main ways:

- Command line: powered by `PaperClientCMD`, suitable for quick searches, saved results, and batch downloads.
- Python package: powered by `PaperClient`, suitable for scripts, scheduled jobs, and research workflows.

Built-in client names: `arxiv`, `openreview`, `acl_anthology`, `biorxiv`, `medrxiv`, `pmlr`, and `pmc_oa`. The default client is `arxiv`.

#### Command Line Usage

The examples below use the `paperdl` command. If your development environment has not registered the console script, replace `paperdl` with:

```bash
python -m paperdl.paperdl
```

(1) List Available Clients

```bash
paperdl clients
```

(2) Search Papers

Search the default arXiv source:

```bash
paperdl search "diffusion model" -n 10
```

Search multiple sources:

```bash
paperdl search "large language model" -c arxiv,pmlr,acl_anthology -n 5
```

Search all registered sources:

```bash
paperdl search "retrieval augmented generation" -c all -n 3 \
  --client-search-param openreview.venue_id=ICLR.cc/2024/Conference \
  --client-search-param biorxiv.max_scan_results=500 \
  --client-search-param medrxiv.max_scan_results=500 \
  --client-search-param pmlr.max_volumes=120
```

When using `-c all`, client-specific search parameters may be required. For example, OpenReview needs a search scope such as `venue_id`, while clients such as bioRxiv, medRxiv, and PMLR may need scan limits to keep the search fast.

Print JSON or JSONL:

```bash
paperdl search "transformer" -c arxiv -n 5 --format json
paperdl search "transformer" -c arxiv -n 5 --format jsonl
```

Save search results for later download:

```bash
paperdl search "graph neural network" -c arxiv,pmlr -n 10 --output-json outputs/search_results.json
```

Show only the first few rows in the terminal while saving all results:

```bash
paperdl search "multimodal large language model" -c arxiv -n 50 --limit 10 --output-json outputs/mllm.json
```

Pass common search parameters to every selected client:

```bash
paperdl search "large language model" -c arxiv -n 20 --search-param sort_by=relevance --search-param page_size=20
```

Pass per-client search parameters. For macOS/Linux/Git Bash:

```bash
paperdl search "diffusion" -c arxiv,pmlr -n 3 \
  --client-search-param 'arxiv.categories=["cs.CV","cs.LG"]' \
  --client-search-param pmlr.max_volumes=30
```

For Windows cmd:

```cmd
paperdl search "diffusion" -c arxiv,pmlr -n 3 ^
  --client-search-param "arxiv.categories=[\"cs.CV\",\"cs.LG\"]" ^
  --client-search-param pmlr.max_volumes=30
```

You can also pass per-client parameters as JSON. For macOS/Linux/Git Bash:

```bash
paperdl search "diffusion" -c arxiv,pmlr -n 3 \
  --client-search-kwargs '{"arxiv":{"categories":["cs.CV","cs.LG"]},"pmlr":{"max_volumes":30}}'
```

For Windows cmd:

```cmd
paperdl search "diffusion" -c arxiv,pmlr -n 3 ^
  --client-search-kwargs "{\"arxiv\":{\"categories\":[\"cs.CV\",\"cs.LG\"]},\"pmlr\":{\"max_volumes\":30}}"
```

On Windows cmd, do not use single quotes around JSON-like values. Use double quotes around the whole argument and escape inner double quotes with `\"`.

(3) Download Papers

Search and download all returned papers:

```bash
paperdl download "diffusion model" -c arxiv -n 5 -o papers
```

Download only the first three results:

```bash
paperdl download "diffusion model" -c arxiv -n 20 --select top3 -o papers
```

Download selected result indices shown in the preview table:

```bash
paperdl download "diffusion model" -c arxiv -n 20 --select 1,3-5 -o papers
```

Download from a saved search result file:

```bash
paperdl download --input-json outputs/search_results.json --select top10 -o papers
```

Overwrite existing PDF files:

```bash
paperdl download "attention is all you need" -c arxiv -n 1 -o papers --overwrite
```

Run in quiet mode:

```bash
paperdl download "diffusion" -c arxiv,pmlr -n 5 --quiet -o papers
```

Stop immediately when any selected client fails:

```bash
paperdl download "diffusion" -c arxiv,pmlr -n 5 --raise-on-error
```

(4) Common CLI Options

| Option                                               | Purpose                                                                                                  |
| ---                                                  | ---                                                                                                      |
| `-c, --clients`                                      | Comma-separated client names, or `all`. Default: `arxiv`.                                                |
| `-n, --total-results`                                | Default number of results per client.                                                                    |
| `--output-json`                                      | Save `search` results to a JSON file.                                                                    |
| `--input-json`                                       | Load paper records from JSON when running `download`.                                                    |
| `--format`                                           | Output format: `table`, `json`, or `jsonl`.                                                              |
| `--select`                                           | Download selection, such as `all`, `top10`, or `1,3-5`.                                                  |
| `-o, --output-dir`                                   | Output directory for PDFs.                                                                               |
| `--overwrite`                                        | Overwrite existing PDF files.                                                                            |
| `--no-dedupe`                                        | Disable cross-client deduplication.                                                                      |
| `--quiet`                                            | Disable verbose logs and progress output where possible.                                                 |
| `--search-concurrency`                               | Number of clients searched concurrently.                                                                 |
| `--init-param` / `--search-param`                    | Constructor or search parameter applied to all clients.                                                  |
| `--client-init-param` / `--client-search-param`      | Constructor or search parameter applied to one client.                                                   |
| `--init-kwargs` / `--search-kwargs`                  | JSON object applied to all clients.                                                                      |
| `--client-init-kwargs` / `--client-search-kwargs`    | JSON object keyed by client name.                                                                        |

#### Python Package Usage

(1) Minimal Search Example

```python
import asyncio
from paperdl import PaperClient

async def main():
    async with PaperClient(["arxiv"], default_init_kwargs={"verbose": False}) as client:
        papers = await client.search("diffusion model", total_results=5)
        for paper in papers:
            print(paper.title, paper.article_url, paper.download_url)

asyncio.run(main())
```

`client.search(...)` returns a list of `PaperInfo` objects. Common fields include `title`, `abstract`, `authors`, `article_url`, `download_url`, `doi`, `arxiv_id`, `venue`, `published_at`, and `source`.

(2) Search Multiple Sources

```python
import asyncio
from paperdl import PaperClient

async def main():
    async with PaperClient(["arxiv", "pmlr", "acl_anthology"]) as client:
        papers = await client.search("large language model", total_results=5)
        print(f"found {len(papers)} papers")

asyncio.run(main())
```

Return results grouped by client:

```python
results = await client.search(
    "large language model",
    total_results=5,
    return_by_client=True,
)
print(results["arxiv"])
print(results["pmlr"])
```

(3) Search and Download

```python
import asyncio
from paperdl import PaperClient

async def main():
    async with PaperClient(["arxiv"]) as client:
        papers = await client.search("attention is all you need", total_results=1)
        paths = await client.download(papers, output_dir="papers")
        print(paths)

asyncio.run(main())
```

Run search and download in one call:

```python
papers, paths = await client.searchanddownload(
    "diffusion model",
    clients=["arxiv"],
    total_results=5,
    output_dir="papers",
)
```

(4) Save and Load Search Results

```python
from paperdl import PaperClient

PaperClient.saveresults(papers, "outputs/search_results.json")
loaded_papers = PaperClient.loadresults("outputs/search_results.json")
```

Loaded results can be downloaded later:

```python
async with PaperClient(["arxiv", "pmlr", "acl_anthology"]) as client:
    loaded_papers = PaperClient.loadresults("outputs/search_results.json")
    paths = await client.download(loaded_papers, output_dir="papers")
```

(5) Configure Different Clients Differently

```python
import asyncio
from paperdl import PaperClient

async def main():
    async with PaperClient(
        ["arxiv", "pmlr"],
        default_init_kwargs={"verbose": False, "show_progress": False},
        client_search_kwargs={
            "arxiv": {"categories": ["cs.CL", "cs.AI"], "sort_by": "submittedDate"},
            "pmlr": {"max_volumes": 30, "enrich_abstracts": True},
        },
        search_concurrency=2,
    ) as client:
        papers = await client.search("large language model", total_results=10)
        await client.download(papers[:5], output_dir="papers")

asyncio.run(main())
```

Override search parameters for a single call:

```python
papers = await client.search(
    "diffusion",
    total_results=10,
    client_search_kwargs={
        "arxiv": {"categories": ["cs.CV"]},
        "pmlr": {"max_volumes": 20},
    },
)
```

(6) Error Handling

By default, a failed client does not stop other clients. Search errors are stored in `client.last_errors`.

```python
papers = await client.search("diffusion", total_results=5)
if client.last_errors:
    for name, err in client.last_errors.items():
        print(name, err)
```

Raise immediately on failure:

```python
papers = await client.search("diffusion", total_results=5, raise_on_error=True)
paths = await client.download(papers, output_dir="papers", raise_on_error=True)
```

Keep download exceptions in the returned list:

```python
results = await client.download(
    papers,
    output_dir="papers",
    return_exceptions=True,
)
```

(7) Use PaperClientCMD from Python

`PaperClientCMD` is the Python wrapper behind the command line interface. It is useful when you want to reuse CLI behavior inside another script:

```python
from paperdl import PaperClientCMD

PaperClientCMD(["clients"]).run()
PaperClientCMD(["search", "diffusion model", "-c", "arxiv", "-n", "5"]).run()
PaperClientCMD(["download", "diffusion model", "-c", "arxiv", "-n", "3", "-o", "papers"]).run()
```

#### Next Steps

- For quick usage, start with the CLI and `PaperClient` examples in this file.
- For source-specific search options, see `Clients.md`.
- To add a new paper source, subclass `BasePaperClient`, implement `search` and `downloaditem`, and register it in the client registry.


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

<a href="https://www.star-history.com/?type=date&legend=top-left&repos=CharlesPikachu%2Fpaperdl">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=CharlesPikachu/paperdl&type=date&theme=dark&legend=top-left&sealed_token=zPDma2kfAWTEyIk6BTvjoF4X8xNmojKB9agKrHU0vU-I3mxfo5Lcu5mjER5ai76vIAPjj0wUB9j89Z-lLPEinavU23J6qqF4LNmjsc-3yOlvdUpldHuF1g" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=CharlesPikachu/paperdl&type=date&legend=top-left&sealed_token=zPDma2kfAWTEyIk6BTvjoF4X8xNmojKB9agKrHU0vU-I3mxfo5Lcu5mjER5ai76vIAPjj0wUB9j89Z-lLPEinavU23J6qqF4LNmjsc-3yOlvdUpldHuF1g" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=CharlesPikachu/paperdl&type=date&legend=top-left&sealed_token=zPDma2kfAWTEyIk6BTvjoF4X8xNmojKB9agKrHU0vU-I3mxfo5Lcu5mjER5ai76vIAPjj0wUB9j89Z-lLPEinavU23J6qqF4LNmjsc-3yOlvdUpldHuF1g" />
 </picture>
</a>


# ☕ Appreciation (赞赏 / 打赏)

| WeChat Appreciation QR Code (微信赞赏码)                                                                                       | Alipay Appreciation QR Code (支付宝赞赏码)                                                                                     |
| :--------:                                                                                                                     | :----------:                                                                                                                   |
| <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/wechat_reward.jpg" width="260" />   | <img src="https://raw.githubusercontent.com/CharlesPikachu/musicdl/master/.github/pictures/alipay_reward.png" width="260" />   |


# 📢 WeChat Official Account (微信公众号):

Charles的皮卡丘 (*Charles_pikachu*)  
![img](https://raw.githubusercontent.com/CharlesPikachu/paperdl/main/docs/pikachu.jpg)