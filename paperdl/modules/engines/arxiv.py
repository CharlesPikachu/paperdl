'''
Function:
    Implementation of ArxivPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import re
import asyncio
import feedparser
from pathlib import Path
from .base import BasePaperClient
from typing import Optional, Sequence
from feedparser.util import FeedParserDict
from ..utils import PaperInfo, PaperDownloadError, PaperRequestError


'''ArxivPaperClient'''
class ArxivPaperClient(BasePaperClient):
    source = "ArxivPaperClient"
    API_URL = "https://export.arxiv.org/api/query"
    VALID_SORT_BY = {"relevance", "lastUpdatedDate", "submittedDate"}
    VALID_SORT_ORDER = {"ascending", "descending"}
    def __init__(self, *, api_delay: float = 3.0, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        super(ArxivPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.api_delay = api_delay if isinstance(api_delay, (int, float)) else None
    '''searchpaper'''
    async def searchpaper(self, query: str, *, max_results: int = 20, start: int = 0, categories: Optional[Sequence[str]] = None, search_field: str = "all", sort_by: str = "submittedDate", sort_order: str = "descending", raw_query: bool = False, show_progress: bool = False) -> list["PaperInfo"]:
        # basic judgement for valid search
        if sort_by not in self.VALID_SORT_BY: raise ValueError(f"Invalid sort_by: {sort_by}")
        if sort_order not in self.VALID_SORT_ORDER: raise ValueError(f"Invalid sort_order: {sort_order}")
        if not isinstance(max_results, (float, int)) or max_results <= 0: return []
        # send request
        search_query = query if raw_query else self.buildquery(query=query, categories=categories, search_field=search_field)
        params = {"search_query": search_query, "start": int(start), "max_results": int(max_results), "sortBy": sort_by, "sortOrder": sort_order}
        xml = await self.requesttext(self.API_URL, params=params, progress_description=(f"Searching arXiv: {query[:60]}" if show_progress else None))
        # return
        return await self.parsefeed(xml, query=search_query, start=start)
    '''search'''
    async def search(self, query: str, *, total_results: int = 100, page_size: int = 50, categories: Optional[Sequence[str]] = None, search_field: str = "all", sort_by: str = "submittedDate", sort_order: str = "descending", raw_query: bool = False, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        page_size = max(1, min(page_size, total_results)); total_pages = (total_results + page_size - 1) // page_size
        paper_infos: list[PaperInfo] = []; search_task = self.addtask(f"Searching arXiv: {query[:60]}", total=total_pages, kind="generic")
        self.log(f"Start searching arXiv: query={query!r}, total_results={total_results}, page_size={page_size}.")
        for page_idx, start in enumerate(range(0, total_results, page_size), start=1):
            current_size = min(page_size, total_results - start)
            if start > 0 and self.api_delay > 0: await asyncio.sleep(self.api_delay)
            self.updatetask(search_task, description=f"Searching arXiv page {page_idx}/{total_pages}: {query[:50]}")
            page_paper_infos = await self.searchpaper(query=query, max_results=current_size, start=start, categories=categories, search_field=search_field, sort_by=sort_by, sort_order=sort_order, raw_query=raw_query, show_progress=False)
            paper_infos.extend(page_paper_infos); self.updatetask(search_task, advance=1)
            if len(page_paper_infos) < current_size: break
        if deduplicate: paper_infos = list({p.identity_key: p for p in paper_infos}.values())
        self.updatetask(search_task, completed=total_pages, description=f"Finished arXiv search: {len(paper_infos)} papers found")
        if self.progress_mode != "detailed": self.removetask(search_task)
        self.log(f"Finished arXiv search. Found {len(paper_infos)} papers.")
        return paper_infos
    '''getbyid'''
    async def getbyid(self, arxiv_id: str) -> Optional["PaperInfo"]:
        paper_infos = await self.searchbyids([arxiv_id])
        return paper_infos[0] if paper_infos else None
    '''searchbyids'''
    async def searchbyids(self, arxiv_ids: Sequence[str]) -> list["PaperInfo"]:
        if not (ids := [x for x in [self.cleanarxivid(x) for x in arxiv_ids if x] if x]): return []
        xml = await self.requesttext(self.API_URL, params={"id_list": ",".join(ids), "max_results": len(ids)}, progress_description=f"Fetching {len(ids)} arXiv IDs")
        return await self.parsefeed(xml, query=f"id_list:{','.join(ids)}", start=0)
    '''downloadpaper'''
    async def downloadpaper(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not (url := paper_info.download_url or self.pdfurlfromarxivid(paper_info.arxiv_id)): raise PaperDownloadError(f"No download URL available for: {paper_info.title}")
        path, short_title = Path(output_dir) / paper_info.filename(suffix=".pdf"), paper_info.title
        short_title = short_title[:67] + "..."  if len(short_title) > 70 else short_title
        return await self.downloadurl(url, path, overwrite=overwrite, progress_description=f"Downloading: {short_title}", show_detail=show_detail)
    '''buildquery'''
    def buildquery(self, *, query: str, categories: Optional[Sequence[str]] = None, search_field: str = "all") -> str:
        categories, query, parts = [c.strip() for c in (categories or []) if c and c.strip()], (query or "").strip(), []
        if query: parts.append(f'{search_field}:"{query}"')
        if categories: cat_query = " OR ".join(f"cat:{c}" for c in categories); parts.append(f"({cat_query})")
        if not parts: raise ValueError("Either query or categories must be provided.")
        return " AND ".join(parts)
    '''parsefeed'''
    async def parsefeed(self, xml: str, *, query: Optional[str] = None, start: int = 0) -> list["PaperInfo"]:
        feed: FeedParserDict = await self.runblocking(feedparser.parse, xml, progress_description=None); paper_infos: list[PaperInfo] = []
        if getattr(feed, "bozo", False) and not feed.entries: raise PaperRequestError(f"Failed to parse arXiv feed: {feed.bozo_exception}")
        for idx, entry in enumerate(feed.entries):
            if str(entry.get("title", "")).lower() == "error": continue
            paper_infos.append(self.entrytopaperinfo(entry, query=query, rank=start + idx + 1))
        return paper_infos
    '''entrytopaperinfo'''
    def entrytopaperinfo(self, entry: dict, *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        article_url, download_url = self.extractarticleurl(entry), self.extractpdfurl(entry)
        arxiv_id = self.extractarxivid(entry.get("id") or article_url)
        authors = [a.get("name") for a in entry.get("authors", []) if isinstance(a, dict) and a.get("name")]
        categories = [t.get("term") for t in entry.get("tags", []) if isinstance(t, dict) and t.get("term")]
        if (primary_category := self.extractprimarycategory(entry)) and primary_category not in categories: categories.insert(0, primary_category)
        doi = (entry.get("arxiv_doi") or entry.get("doi") or self.extractdoifromlinks(entry))
        journal_ref, comment = entry.get("arxiv_journal_ref"), entry.get("arxiv_comment")
        return PaperInfo(
            source=self.source, title=entry.get("title") or "notitle", abstract=entry.get("summary"), authors=authors, article_url=article_url, download_url=download_url, doi=doi, arxiv_id=arxiv_id, venue=journal_ref, publisher="arXiv", published_at=entry.get("published"), 
            updated_at=entry.get("updated"), source_id=entry.get("id"), query=query, rank=rank, categories=categories, tags=["arxiv"], is_open_access=True, extra={"primary_category": primary_category, "comment": comment, "journal_ref": journal_ref, "raw_id": entry.get("id")},
        )
    '''extractarticleurl'''
    @staticmethod
    def extractarticleurl(entry: dict) -> Optional[str]:
        for link in entry.get("links", []):
            if (isinstance(link, dict) or hasattr(link, 'get')) and (link.get("rel") == "alternate"): return link.get("href")
        return entry.get("id")
    '''extractpdfurl'''
    @staticmethod
    def extractpdfurl(entry: dict) -> Optional[str]:
        for link in entry.get("links", []):
            if (isinstance(link, dict) or hasattr(link, 'get')) and (link.get("title") == "pdf" or link.get("type") == "application/pdf"): return link.get("href")
        return ArxivPaperClient.pdfurlfromarxivid(ArxivPaperClient.extractarxivid(entry.get("id")))
    '''extractdoifromlinks'''
    @staticmethod
    def extractdoifromlinks(entry: dict) -> Optional[str]:
        for link in entry.get("links", []):
            if "doi.org/" in (href := link.get("href", "") if isinstance(link, dict) or hasattr(link, 'get') else link): return str(href).rstrip("/").split("doi.org/")[-1]
        return None
    '''extractprimarycategory'''
    @staticmethod
    def extractprimarycategory(entry: dict) -> Optional[str]:
        if isinstance((primary := entry.get("arxiv_primary_category")), dict): return primary.get("term")
        return None
    '''extractarxivid'''
    @staticmethod
    def extractarxivid(value: Optional[str]) -> Optional[str]:
        if not value or not ((text := str(value).strip())): return None
        text = (text.split("/abs/", 1)[-1] if "/abs/" in text else text.split("/pdf/", 1)[-1] if "/pdf/" in text else text).replace(".pdf", "").strip("/")
        if (new_style := re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?", text)): return new_style.group(1)
        if (old_style := re.search(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", text)): return old_style.group(1)
        return text or None
    '''cleanarxivid'''
    @staticmethod
    def cleanarxivid(value: str) -> str:
        return ArxivPaperClient.extractarxivid(value) or str(value).strip()
    '''pdfurlfromarxivid'''
    @staticmethod
    def pdfurlfromarxivid(arxiv_id: Optional[str]) -> Optional[str]:
        if not arxiv_id: return None
        return f"https://arxiv.org/pdf/{arxiv_id}"