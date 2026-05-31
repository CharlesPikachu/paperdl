# Paperdl Clients

This document summarizes the built-in Paperdl clients, their search/download arguments, and practical examples.
For a short usage-oriented introduction, read `QuickStart.md` first.

## 1. Common Model

All built-in clients inherit from `BasePaperClient` and follow the same basic pattern:

```python
import asyncio
from paperdl.modules import ArxivPaperClient

async def main():
    async with ArxivPaperClient(verbose=False, show_progress=False) as client:
        papers = await client.search("diffusion model", total_results=5)
        paths = await client.download(papers, output_dir="papers")
        print(paths)

asyncio.run(main())
```

Common download API:

```python
paths = await client.download(
    papers,
    output_dir="paperdl_outputs",
    overwrite=False,
    return_exceptions=False,
)
```

Common constructor arguments:

| Parameter                                             | Description                                                                                                     |
| ---                                                   | ---                                                                                                             |
| `timeout`                                             | Total HTTP request timeout.                                                                                     |
| `concurrency`                                         | Internal per-client concurrency for requests and downloads.                                                     |
| `max_retries`                                         | Number of retries after request or download failures.                                                           |
| `retry_backoff`                                       | Base wait time for exponential backoff.                                                                         |
| `headers`                                             | Custom HTTP headers.                                                                                            |
| `cookies` / `cookie_file`                             | Cookies passed directly, or a cookie file to load and save.                                                     |
| `proxy`                                               | Proxy URL, for example `http://127.0.0.1:7890`.                                                                 |
| `thread_workers`                                      | Thread pool size for blocking tasks.                                                                            |
| `show_progress`                                       | Whether to show rich progress bars.                                                                             |
| `progress_mode`                                       | Progress mode: `auto`, `summary`, `detailed`, or `none`.                                                        |
| `max_detail_tasks`                                    | Maximum number of detailed tasks shown in `auto` mode.                                                          |
| `verbose`                                             | Whether to print logs.                                                                                          |

`download(...)` calls the client-specific `downloaditem(...)` internally, so direct calls to `downloaditem` are rarely needed.

## 2. ArxivPaperClient

Registered name: `arxiv`

Import:

```python
from paperdl.modules import ArxivPaperClient
```

#### Search arguments

```python
await client.search(
    query,
    total_results=100,
    page_size=50,
    categories=None,
    search_field="all",
    sort_by="submittedDate",
    sort_order="descending",
    raw_query=False,
    deduplicate=True,
)
```

| Parameter                                                        | Description                                                                               |
| ---                                                              | ---                                                                                       |
| `query`                                                          | Search keywords.                                                                          |
| `total_results`                                                  | Maximum number of returned papers.                                                        |
| `page_size`                                                      | Number of results requested per API page.                                                 |
| `categories`                                                     | arXiv categories, for example `['cs.CL', 'cs.CV']`.                                       |
| `search_field`                                                   | arXiv search field. Default: `all`.                                                       |
| `sort_by`                                                        | `relevance`, `lastUpdatedDate`, or `submittedDate`.                                       |
| `sort_order`                                                     | `ascending` or `descending`.                                                              |
| `raw_query`                                                      | If `True`, use the raw arXiv query string without automatic field/category composition.   |
| `deduplicate`                                                    | Deduplicate by `PaperInfo.identity_key`.                                                  |

#### Examples

Search recent arXiv papers in selected categories:

```python
async with ArxivPaperClient(verbose=False) as client:
    papers = await client.search(
        "large language model",
        total_results=20,
        categories=["cs.CL", "cs.AI"],
        sort_by="submittedDate",
    )
```

Use a raw arXiv query:

```python
papers = await client.search(
    'cat:cs.CL AND all:"retrieval augmented generation"',
    total_results=10,
    raw_query=True,
    sort_by="relevance",
)
```

Query by arXiv ID:

```python
paper = await client.getbyid("1706.03762")
papers = await client.searchbyids(["1706.03762", "2307.09288"])
```

Download results:

```python
paths = await client.download(papers[:3], output_dir="papers/arxiv")
```

Pass arXiv parameters through `PaperClient`:

```python
from paperdl import PaperClient

async with PaperClient(
    ["arxiv"],
    client_search_kwargs={"arxiv": {"categories": ["cs.CL"], "sort_by": "relevance"}},
) as client:
    papers = await client.search("transformer", total_results=10)
```

## 3. OpenReviewPaperClient

Registered name: `openreview`

Import:

```python
from paperdl.modules import OpenReviewPaperClient
```

#### Additional constructor parameters

| Parameter                           | Description                                                          |
| ---                                 | ---                                                                  |
| `baseurl`                           | OpenReview API URL. Default: `https://api2.openreview.net`.          |
| `username` / `password`             | Credentials used when login is required.                             |
| `api_version`                       | Default: `2`, using `openreview.api.OpenReviewClient`.               |

#### Search parameters

```python
await client.search(
    query=None,
    total_results=100,
    venue_id=None,
    invitation=None,
    content=None,
    details=None,
    accepted_only=False,
    client_side_filter=True,
)
```

| Parameter                             | Description                                                                                                                      |
| ---                                   | ---                                                                                                                              |
| `query`                               | Optional keyword query. By default, filtering is performed locally on title, abstract, authors, keywords, and related fields.    |
| `venue_id`                            | Venue ID, for example `ICLR.cc/2024/Conference`.                                                                                 |
| `invitation`                          | OpenReview invitation, for example `ICLR.cc/2024/Conference/-/Submission`.                                                       |
| `content`                             | OpenReview content filter, for example `{'venueid': 'ICLR.cc/2024/Conference'}`.                                                 |
| `details`                             | `details` argument passed to OpenReview `get_all_notes`.                                                                         |
| `accepted_only`                       | When used with `venue_id`, return only accepted papers.                                                                          |
| `client_side_filter`                  | Whether to filter locally by `query`.                                                                                            |

At least one of `venue_id`, `invitation`, or `content` must be provided.

#### Examples

Search a conference:

```python
async with OpenReviewPaperClient(verbose=False) as client:
    papers = await client.search(
        "diffusion",
        venue_id="ICLR.cc/2024/Conference",
        total_results=20,
    )
```

Return accepted papers only:

```python
papers = await client.search(
    venue_id="ICLR.cc/2024/Conference",
    accepted_only=True,
    total_results=100,
)
```

Use an invitation:

```python
papers = await client.search(
    "reasoning",
    invitation="ICLR.cc/2024/Conference/-/Submission",
    total_results=20,
)
```

Download results:

```python
paths = await client.download(papers[:5], output_dir="papers/openreview")
```

If the normal PDF URL fails, the client falls back to the OpenReview attachment API.

## 4. ACLAnthologyPaperClient

Registered name: `acl_anthology`

Common aliases: `acl`

Import:

```python
from paperdl.modules import ACLAnthologyPaperClient
```

#### Search parameters

```python
await client.search(
    query=None,
    total_results=100,
    collection_ids=None,
    max_collections=40,
    deduplicate=True,
)
```

| Parameter                                               | Description                                                                               |
| ---                                                     | ---                                                                                       |
| `query`                                                 | Optional keyword query. If empty, papers in the scanned collections are returned.         |
| `collection_ids`                                        | ACL Anthology XML collection IDs, for example `['2024.acl-long']`.                        |
| `max_collections`                                       | When `collection_ids` is not provided, scan this many recent collections.                 |
| `deduplicate`                                           | Deduplicate results.                                                                      |

#### Examples

Search recent collections:

```python
async with ACLAnthologyPaperClient(verbose=False) as client:
    papers = await client.search(
        "machine translation",
        total_results=20,
        max_collections=30,
    )
```

Search selected collections:

```python
papers = await client.search(
    "large language model",
    collection_ids=["2024.acl-long", "2024.findings-acl"],
    total_results=20,
)
```

Download results:

```python
paths = await client.download(papers[:5], output_dir="papers/acl")
```

## 5. BioRxivPaperClient and MedRxivPaperClient

Registered names: `biorxiv`, `medrxiv`

Import:

```python
from paperdl.modules import BioRxivPaperClient, MedRxivPaperClient
```

`MedRxivPaperClient` inherits from `BioRxivPaperClient`. The main difference is that the source server is `medrxiv` instead of `biorxiv`.

#### Additional constructor parameters

| Parameter                                                  | Description                                                                  |
| ---                                                        | ---                                                                          |
| `browser_fallback`                                         | Whether to use a Playwright browser fallback when normal download fails.     |
| `browser_headless`                                         | Whether the fallback browser runs in headless mode.                          |
| `browser_channel`                                          | Chromium channel, for example `chrome`.                                      |
| `browser_user_data_dir`                                    | Browser user data directory.                                                 |
| `browser_wait_seconds`                                     | Wait time before retrying when a challenge page is detected.                 |

#### Search parameters

```python
await client.search(
    query=None,
    total_results=100,
    from_date="2024-01-01",
    to_date=None,
    max_scan_results=5000,
    page_size=100,
    deduplicate=True,
)
```

| Parameter                                                    | Description                                                                                                                 |
| ---                                                          | ---                                                                                                                         |
| `query`                                                      | Optional keyword query. Matching is performed locally on title, abstract, authors, categories, and related fields.          |
| `from_date` / `to_date`                                      | API scan date range in `YYYY-MM-DD` format. `to_date=None` means today.                                                     |
| `max_scan_results`                                           | Maximum number of source records to scan, which prevents very large date ranges from becoming too slow.                     |
| `page_size`                                                  | Number of records per API request.                                                                                          |
| `deduplicate`                                                | Deduplicate results.                                                                                                        |

#### Examples

Search and download from bioRxiv:

```python
async with BioRxivPaperClient(verbose=False) as client:
    papers = await client.search(
        "single cell",
        from_date="2025-01-01",
        total_results=20,
    )
    paths = await client.download(papers[:3], output_dir="papers/biorxiv")
```

Search medRxiv:

```python
async with MedRxivPaperClient(verbose=False) as client:
    papers = await client.search(
        "medical imaging",
        from_date="2025-01-01",
        total_results=20,
    )
```

Disable browser fallback:

```python
async with BioRxivPaperClient(browser_fallback=False) as client:
    papers = await client.search("protein design", total_results=5)
```

## 6. PMLRPaperClient

Registered name: `pmlr`

Import:

```python
from paperdl.modules import PMLRPaperClient
```

#### Search parameters

```python
await client.search(
    query=None,
    total_results=100,
    volume_ids=None,
    max_volumes=None,
    enrich_abstracts=True,
    deduplicate=True,
)
```

| Parameter                              | Description                                                                                                             |
| ---                                    | ---                                                                                                                     |
| `query`                                | Optional keyword query. Matching uses title, abstract, authors, venue, and related fields.                              |
| `volume_ids`                           | Selected PMLR volumes, for example `[235, 238]`.                                                                        |
| `max_volumes`                          | When `volume_ids` is not provided, scan this many recent volumes.                                                       |
| `enrich_abstracts`                     | Visit paper detail pages to enrich abstracts, PDF URLs, authors, year, and other metadata.                              |
| `deduplicate`                          | Deduplicate results.                                                                                                    |

#### Examples

Search recent volumes:

```python
async with PMLRPaperClient(verbose=False) as client:
    papers = await client.search(
        "diffusion",
        max_volumes=30,
        total_results=20,
    )
```

Search selected volumes:

```python
papers = await client.search(
    "reinforcement learning",
    volume_ids=[235, 238],
    total_results=20,
)
```

Run a lightweight search without visiting detail pages:

```python
papers = await client.search(
    "optimization",
    max_volumes=20,
    enrich_abstracts=False,
)
```

Download results:

```python
paths = await client.download(papers[:5], output_dir="papers/pmlr")
```

## 7. PMCOAPaperClient

Registered name: `pmc_oa`

Common aliases: `pmc`, `pubmed`, `pubmed_central`

Import:

```python
from paperdl.modules import PMCOAPaperClient
```

#### Additional constructor parameters

| Parameter                            | Description                                 |
| ---                                  | ---                                         |
| `tool`                               | Tool name passed to NCBI E-utilities.       |
| `email`                              | Email passed to NCBI E-utilities.           |
| `api_key`                            | NCBI API key.                               |
| `api_delay`                          | Wait time between paginated API requests.   |

#### Search parameters

```python
await client.search(
    query=None,
    total_results=100,
    page_size=50,
    sort="relevance",
    require_pdf=True,
    deduplicate=True,
)
```

| Parameter                                 | Description                                                                        |
| ---                                       | ---                                                                                |
| `query`                                   | PMC search query. The client automatically applies an open-access filter.          |
| `total_results`                           | Maximum number of returned papers.                                                 |
| `page_size`                               | Number of results per API page. Internally capped at 200.                          |
| `sort`                                    | NCBI search sort field. Default: `relevance`.                                      |
| `require_pdf`                             | Keep only records with an open-access PDF download link.                           |
| `deduplicate`                             | Deduplicate results.                                                               |

#### Examples

Search PMC Open Access:

```python
async with PMCOAPaperClient(email="you@example.com", verbose=False) as client:
    papers = await client.search(
        "cancer immunotherapy",
        total_results=20,
        require_pdf=True,
    )
```

Use an API key:

```python
async with PMCOAPaperClient(
    email="you@example.com",
    api_key="YOUR_NCBI_API_KEY",
    verbose=False,
) as client:
    papers = await client.search("single cell sequencing", total_results=50)
```

Download results:

```python
paths = await client.download(papers[:5], output_dir="papers/pmc")
```

## 8. Combine Multiple Clients with PaperClient

Use a concrete client when you need fine-grained control over one source.
Use `PaperClient` when you want unified search and download across multiple sources:

```python
import asyncio
from paperdl import PaperClient

async def main():
    async with PaperClient(
        ["arxiv", "acl_anthology", "pmlr", "pmc_oa"],
        default_init_kwargs={"verbose": False},
        client_init_kwargs={
            "pmc_oa": {"email": "you@example.com"},
        },
        client_search_kwargs={
            "arxiv": {"categories": ["cs.CL"]},
            "acl_anthology": {"max_collections": 20},
            "pmlr": {"max_volumes": 30},
            "pmc_oa": {"require_pdf": True},
        },
        search_concurrency=4,
    ) as client:
        papers = await client.search("large language model", total_results=10)
        paths = await client.download(papers[:10], output_dir="papers")
        print(len(papers), len(paths))

asyncio.run(main())
```

Return results grouped by source:

```python
results = await client.search(
    "diffusion",
    total_results=10,
    return_by_client=True,
)

for source, papers in results.items():
    print(source, len(papers))
```

## 9. Common PaperInfo Fields

Every search result is a `PaperInfo` object:

| Field                                        | Description                                            |
| ---                                          | ---                                                    |
| `source`                                     | Source client, for example `ArxivPaperClient`.         |
| `title`                                      | Paper title.                                           |
| `abstract`                                   | Abstract text.                                         |
| `authors`                                    | Author list.                                           |
| `article_url`                                | Paper detail page.                                     |
| `download_url`                               | PDF download URL.                                      |
| `doi` / `arxiv_id`                           | DOI or arXiv ID.                                       |
| `venue` / `publisher`                        | Conference, journal, or publisher.                     |
| `published_at` / `updated_at`                | Publication and update timestamps.                     |
| `source_id`                                  | Source-specific internal ID.                           |
| `keywords` / `categories` / `tags`           | Keywords, categories, and tags.                        |
| `extra`                                      | Source-specific metadata.                              |

Useful methods and properties:

```python
paper.year
paper.main_url
paper.short_authors
paper.identity_key
paper.filename()
paper.todict()
paper.tojson()
```

Restore a paper from a dictionary or JSON string:

```python
from paperdl.modules import PaperInfo

paper = PaperInfo.fromdict(data)
paper = PaperInfo.fromjson(text)
```
