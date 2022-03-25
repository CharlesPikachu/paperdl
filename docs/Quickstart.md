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

Here is a screenshot:

<div align="center">
  <img src="https://raw.githubusercontent.com/CharlesPikachu/paperdl/main/docs/screenshot.gif" width="600"/>
</div>
<br />

#### Calling EXE

You can directly leverage paperdl in the terminal, and the usage is as follow:

```sh
```

Here is an example:

```sh
```