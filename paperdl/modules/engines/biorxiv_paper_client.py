'''
Function:
    Implementation of BioRxivPaperClient and MedRxivPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''BioRxivPaperClient'''
class BioRxivPaperClient(BasePaperClient):
    source = "BioRxivPaperClient"
    SERVER = "biorxiv"
    API_URL = "https://api.biorxiv.org/details/{server}/{interval}/{cursor}"
    DETAIL_URL = "https://api.biorxiv.org/details/{server}/{doi}/na/json"
    SITE_URL = "https://www.{server}.org"

    def __init__(self, *, api_delay: float = 0.5, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        default_headers = {"User-Agent": "Mozilla/5.0 paper-client/1.0"}
        super(BioRxivPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers={**default_headers, **(headers or {})}, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.api_delay = api_delay if isinstance(api_delay, (int, float)) else 0.0

    '''querypage'''
    async def querypage(self, *, from_date: str = "2024-01-01", to_date: Optional[str] = None, cursor: int = 0, page_size: int = 100, show_progress: bool = False) -> list["PaperInfo"]:
        to_date = to_date or datetime.now(timezone.utc).date().isoformat()
        interval = f"{from_date}/{to_date}"
        url = self.API_URL.format(server=self.SERVER, interval=interval, cursor=int(cursor))
        payload = await self.requestjson(url, progress_description=(f"Searching {self.SERVER}: {interval}" if show_progress else None))
        return [self.recordtopaperinfo(record, rank=cursor + idx + 1) for idx, record in enumerate(payload.get("collection", []) or [])][:page_size]

    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, page_size: int = 100, from_date: str = "2024-01-01", to_date: Optional[str] = None, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        page_size = max(1, min(int(page_size), 100))
        paper_infos: list[PaperInfo] = []
        cursor, total_pages = 0, max(1, (int(total_results) + page_size - 1) // page_size)
        task_id = self.addtask(f"Searching {self.SERVER}: {(query or 'all')[:60]}", total=None, kind="generic")
        self.log(f"Start searching {self.SERVER}: query={query!r}, from_date={from_date}, to_date={to_date}.")
        while len(paper_infos) < total_results:
            if cursor > 0 and self.api_delay > 0: await asyncio.sleep(self.api_delay)
            self.updatetask(task_id, description=f"Searching {self.SERVER} cursor {cursor}: {(query or 'all')[:50]}")
            page_paper_infos = await self.querypage(from_date=from_date, to_date=to_date, cursor=cursor, page_size=page_size, show_progress=False)
            if not page_paper_infos: break
            if query: page_paper_infos = [p for p in page_paper_infos if p.matchkeyword(query)]
            paper_infos.extend(page_paper_infos)
            cursor += page_size
            if len(page_paper_infos) < page_size and not query: break
            if cursor // page_size >= total_pages * 20: break
        if deduplicate: paper_infos = list({p.identity_key: p for p in paper_infos}.values())
        paper_infos = paper_infos[:int(total_results)]
        self.updatetask(task_id, completed=1, description=f"Finished {self.SERVER} search: {len(paper_infos)} papers found")
        if self.progress_mode != "detailed": self.removetask(task_id)
        self.log(f"Finished {self.SERVER} search. Found {len(paper_infos)} papers.")
        return paper_infos

    '''getbydoi'''
    async def getbydoi(self, doi: str) -> Optional["PaperInfo"]:
        if not doi: return None
        url = self.DETAIL_URL.format(server=self.SERVER, doi=str(doi).strip())
        payload = await self.requestjson(url, progress_description=f"Fetching {self.SERVER} DOI: {doi}")
        collection = payload.get("collection", []) or []
        return self.recordtopaperinfo(collection[0], rank=1) if collection else None

    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not (url := paper_info.download_url): raise PaperDownloadError(f"No download URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        short_title = paper_info.title[:67] + "..." if paper_info.title and len(paper_info.title) > 70 else paper_info.title
        return await self.downloadvalidatedpdf(url, path, overwrite=overwrite, progress_description=f"Downloading: {short_title}", show_detail=show_detail, min_bytes=4 * 1024, min_pages=1)

    '''recordtopaperinfo'''
    def recordtopaperinfo(self, record: dict[str, Any], *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        doi = record.get("doi")
        version = record.get("version")
        article_url = self.articleurl(doi, version=version)
        return PaperInfo(
            source=self.source, title=record.get("title") or "notitle", abstract=record.get("abstract"), authors=record.get("authors") or [], article_url=article_url, download_url=self.pdfurl(doi, version=version), doi=doi, venue=self.SERVER, publisher=self.SERVER, published_at=record.get("date"), source_id=doi, query=query, rank=rank, categories=[record.get("category")] if record.get("category") else [], tags=[self.SERVER, "preprint"], language="en", license=record.get("license"), is_open_access=True, extra={k: v for k, v in record.items() if k not in {"title", "abstract", "authors", "doi", "date", "category", "license"}},
        )

    '''articleurl'''
    @classmethod
    def articleurl(cls, doi: Optional[str], *, version: Optional[int | str] = None) -> Optional[str]:
        if not doi: return None
        version_text = f"v{version}" if version else ""
        return f"{cls.SITE_URL.format(server=cls.SERVER)}/content/{doi}{version_text}"

    '''pdfurl'''
    @classmethod
    def pdfurl(cls, doi: Optional[str], *, version: Optional[int | str] = None) -> Optional[str]:
        if not doi: return None
        return f"{cls.articleurl(doi, version=version)}.full.pdf"


'''MedRxivPaperClient'''
class MedRxivPaperClient(BioRxivPaperClient):
    source = "MedRxivPaperClient"
    SERVER = "medrxiv"
