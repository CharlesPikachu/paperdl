# Paperdl Installation

#### Environment Requirements

- Operating system: Linux, macOS, or Windows.
- Python version: Python 3.10 or later.
- Package manager: `pip` is required. We recommend using the latest `pip`, `setuptools`, and `wheel` before installation.
- Network access: most Paperdl engines search or download papers from remote academic websites, so a stable network connection is required.
- Optional browser runtime: Playwright + Chromium is only needed for browser fallback downloads, mainly for bioRxiv / medRxiv PDF pages that block normal HTTP clients.

#### Recommended Environment Setup

Although Paperdl can be installed directly into your global Python environment, we recommend installing it in a virtual environment to avoid dependency conflicts with other projects.

For Linux / macOS:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
```

For Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
```

If PowerShell refuses to activate the virtual environment because script execution is disabled, run the following command once and then activate the environment again:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Installation Instructions

You have several installation methods to choose from.

```bash
# from PyPI
python -m pip install -U paperdl

# from GitHub repository
python -m pip install -U git+https://github.com/CharlesPikachu/paperdl.git@main

# from local source code
git clone https://github.com/CharlesPikachu/paperdl.git
cd paperdl
python -m pip install -U .

# editable install for development
python -m pip install -e .
```

For modern Python projects based on `pyproject.toml`, `python -m pip install .` is preferred over `python setup.py install`. The latter is deprecated and this repository may not include a `setup.py` file.

#### Optional Browser Installation

Most Paperdl engines work with the normal installation above. However, some bioRxiv / medRxiv PDF downloads may be blocked for normal HTTP clients. Paperdl includes an optional Playwright-based browser fallback for these cases.

To enable this feature when installing from PyPI:

```bash
python -m pip install -U "paperdl[browser]"
python -m playwright install chromium
```

To enable it from local source code:

```bash
python -m pip install -e ".[browser]"
python -m playwright install chromium
```

On some Linux servers, Playwright may also need system-level browser dependencies:

```bash
python -m playwright install-deps chromium
```

You can skip this optional browser installation if you only use engines such as arXiv, ACL Anthology, OpenReview, PMLR, or PMC OA, or if normal bioRxiv / medRxiv HTTP downloads work in your environment.