# Quick Start

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
paperdl search "large language model" -c arxiv --search-param sort_by="relevance" --search-param page_size=20
```

Pass per-client search parameters:

```bash
paperdl search "diffusion" -c arxiv,pmlr -n 3 \
  --client-search-param 'arxiv.categories=["cs.CV","cs.LG"]' \
  --client-search-param pmlr.max_volumes=30
```

You can also pass per-client parameters as JSON:

```bash
paperdl search "diffusion" -c arxiv,pmlr \
  --client-search-kwargs '{"arxiv":{"categories":["cs.CV"]},"pmlr":{"max_volumes":30}}'
```

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

### 2.4 Common CLI options

| Option | Purpose |
| --- | --- |
| `-c, --clients` | Comma-separated client names, or `all`. Default: `arxiv`. |
| `-n, --total-results` | Default number of results per client. |
| `--output-json` | Save `search` results to a JSON file. |
| `--input-json` | Load paper records from JSON when running `download`. |
| `--format` | Output format: `table`, `json`, or `jsonl`. |
| `--select` | Download selection, such as `all`, `top10`, or `1,3-5`. |
| `-o, --output-dir` | Output directory for PDFs. |
| `--overwrite` | Overwrite existing PDF files. |
| `--no-dedupe` | Disable cross-client deduplication. |
| `--quiet` | Disable verbose logs and progress output where possible. |
| `--search-concurrency` | Number of clients searched concurrently. |
| `--init-param` / `--search-param` | Constructor or search parameter applied to all clients. |
| `--client-init-param` / `--client-search-param` | Constructor or search parameter applied to one client. |
| `--init-kwargs` / `--search-kwargs` | JSON object applied to all clients. |
| `--client-init-kwargs` / `--client-search-kwargs` | JSON object keyed by client name. |








#### Python Package Usage

### 3.1 Minimal search example

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

### 3.2 Search multiple sources

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

### 3.3 Search and download

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

### 3.4 Save and load search results

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

### 3.5 Configure different clients differently

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

### 3.6 Error handling

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

### 3.7 Use PaperClientCMD from Python

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


