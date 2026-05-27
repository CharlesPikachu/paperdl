'''
Function:
    Implementation of OalibPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
from pathlib import Path
from typing import Any, Optional
from bs4 import BeautifulSoup
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''OalibPaperClient'''
class OalibPaperClient(BasePaperClient):
    source = "OalibPaperClient"
    BASE_URL = "https://www.oalib.com"
    SEARCH_URL = "https://www.oalib.com/index"
    def __init__(self, *, timeout: float = 60.0, concurrency: int = 3, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        headers = {"User-Agent": "Mozilla/5.0 paper-client/1.0", **(headers or {})}
        super(OalibPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
    '''search'''
    async def search(self, query: str, *, total_results: int = 50, page_size: int = 10, max_pages: Optional[int] = None, deduplicate: bool = True) -> list["PaperInfo"]:
        if not query or not query.strip() or not isinstance(total_results, (int, float)) or total_results <= 0: return []
        results, page = [], 1
        max_pages = max_pages or max(1, (int(total_results) + max(1, page_size) - 1) // max(1, page_size))
        task_id = self.addtask(f"Searching OALib: {query[:60]}", total=max_pages, kind="generic")
        while len(results) < total_results and page <= max_pages:
            html = await self.requesttext(self.SEARCH_URL, params={"kw": query, "page": page}, progress_description=None)
            page_items = self.parse_search_page(html, query=query, start_rank=len(results) + 1)
            results.extend(page_items)
            self.updatetask(task_id, advance=1)
            if not page_items: break
            page += 1
        if deduplicate: results = list({p.identity_key: p for p in results}.values())
        self.updatetask(task_id, completed=max_pages, description=f"Finished OALib search: {len(results)} papers found")
        if self.progress_mode != "detailed": self.removetask(task_id)
        self.log(f"OALib search finished. Found {len(results)} papers.")
        return results[:int(total_results)]
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        url = paper_info.download_url or (self.pdfurlfromid(paper_info.source_id) if paper_info.source_id else None)
        if not url: raise PaperDownloadError(f"No OALib PDF URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        return await self.downloadfile(url, path, overwrite=overwrite, progress_description=f"Downloading OALib PDF: {paper_info.title[:70]}", show_detail=show_detail)
    '''parse_search_page'''
    def parse_search_page(self, html: str, *, query: Optional[str] = None, start_rank: int = 1) -> list["PaperInfo"]:
        soup = BeautifulSoup(html or "", "lxml")
        blocks = []
        for h3 in soup.find_all("h3"):
            if not h3.get_text(strip=True): continue
            block_nodes, node = [h3], h3.find_next_sibling()
            while node and getattr(node, "name", None) != "h3":
                block_nodes.append(node); node = node.find_next_sibling()
            blocks.append(BeautifulSoup("\n".join(str(x) for x in block_nodes), "lxml"))
        results = []
        for idx, block in enumerate(blocks):
            title_tag = block.find("h3")
            link_tag = title_tag.find("a") if title_tag else None
            title = title_tag.get_text(" ", strip=True) if title_tag else "notitle"
            article_url = self.absoluteurl(link_tag.get("href")) if link_tag else None
            text = block.get_text(" ", strip=True)
            doi = self.extractdoi(text)
            source_id = self.extractsourceid(article_url)
            authors = self.extractauthors(block)
            abstract = self.extractabstract(text)
            published_at = self.extractdate(text)
            results.append(PaperInfo(
                source=self.source, title=title, abstract=abstract, authors=authors, article_url=article_url, download_url=self.pdfurlfromid(source_id), doi=doi,
                venue=self.extractvenue(text), publisher="Open Access Library", published_at=published_at, source_id=source_id, query=query, rank=start_rank + idx,
                tags=["oalib", "open-access"], is_open_access=True, extra={"raw_text": text},
            ))
        return results
    '''absoluteurl'''
    def absoluteurl(self, value: Optional[str]) -> Optional[str]:
        if not value: return None
        if value.startswith("http://") or value.startswith("https://"): return value
        return f"{self.BASE_URL}/{value.lstrip('/')}"
    '''pdfurlfromid'''
    def pdfurlfromid(self, source_id: Optional[str]) -> Optional[str]:
        return f"{self.BASE_URL}/paper/pdf/{source_id}" if source_id else None
    '''extractsourceid'''
    @staticmethod
    def extractsourceid(url: Optional[str]) -> Optional[str]:
        if not url: return None
        if (m := re.search(r"/(?:index|articles)/(\d+)", url)): return m.group(1)
        if (m := re.search(r"/paper/pdf/(\d+)", url)): return m.group(1)
        return None
    '''extractdoi'''
    @staticmethod
    def extractdoi(text: str) -> Optional[str]:
        if (m := re.search(r"(?:doi:|Doi:)\s*(?:https?://(?:dx\.)?doi\.org/)?([^\s,;]+)", text, re.I)): return m.group(1).rstrip(".")
        return None
    '''extractdate'''
    @staticmethod
    def extractdate(text: str) -> Optional[str]:
        if (m := re.search(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b", text, re.I)): return m.group(0)
        if (m := re.search(r"\b(19|20)\d{2}\b", text)): return m.group(0)
        return None
    '''extractvenue'''
    @staticmethod
    def extractvenue(text: str) -> Optional[str]:
        if (m := re.search(r"(Open Access Library J\.[^#]*?)(?:Doi:|\b\d{4}\b|Open Access)", text)): return m.group(1).strip()
        return None
    '''extractabstract'''
    @staticmethod
    def extractabstract(text: str) -> Optional[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= 400: return None
        return text[:1200]
    '''extractauthors'''
    @staticmethod
    def extractauthors(block: BeautifulSoup) -> list[str]:
        for tag in block.find_all(["h4", "h5"]):
            names = [x.strip() for x in re.split(r",|;", tag.get_text(" ", strip=True)) if x.strip()]
            if names: return names
        return []
