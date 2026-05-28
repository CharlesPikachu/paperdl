'''
Function:
    Implementation of PMLRPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional, Sequence
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''PMLRPaperClient'''
class PMLRPaperClient(BasePaperClient):
    source = "PMLRPaperClient"
    BASE_URL = "https://proceedings.mlr.press"
    def __init__(self, *, api_delay: float = 0.2, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        super(PMLRPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.api_delay = api_delay if isinstance(api_delay, (int, float)) else 0.0
    '''listvolumes'''
    async def listvolumes(self) -> list[int]:
        html_text = await self.requesttext(self.BASE_URL + "/", progress_description="Loading PMLR volumes")
        soup = BeautifulSoup(html_text, "lxml"); volume_ids: set[int] = set()
        for link in soup.find_all("a", href=True):
            for value in (str(link.get("href", "")).strip(), link.get_text(" ", strip=True)):
                if match := re.search(r"(?:^|/|\b)v(\d+)(?:/|$)", value, flags=re.I): volume_ids.add(int(match.group(1)))
                if match := re.search(r"\bVolume\s+(\d+)\b", value, flags=re.I): volume_ids.add(int(match.group(1)))
        return sorted(volume_ids, reverse=True)
    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, volume_ids: Optional[Sequence[int]] = None, max_volumes: Optional[int] = None, enrich_abstracts: bool = True, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        if volume_ids is None: volume_ids = await self.listvolumes(); volume_ids = list(volume_ids)[:max_volumes] if max_volumes is not None else volume_ids
        volume_ids = list(volume_ids); paper_infos: list[PaperInfo] = []; seen_keys: set[str] = set()
        task_id = self.addtask(f"Searching PMLR: {(query or 'all')[:60]}", total=len(volume_ids), kind="generic")
        self.log(f"Start searching PMLR: query={query!r}, volumes={volume_ids[:8]}...")
        try:
            for idx, volume_id in enumerate(volume_ids, start=1):
                if idx > 1 and self.api_delay > 0: await asyncio.sleep(self.api_delay)
                self.updatetask(task_id, description=f"Searching PMLR volume {volume_id}: {(query or 'all')[:50]}")
                page_infos = await self.queryvolume(volume_id=volume_id, query=query, enrich_abstracts=enrich_abstracts)
                for paper_info in page_infos:
                    if deduplicate and paper_info.identity_key in seen_keys: continue
                    seen_keys.add(paper_info.identity_key); paper_infos.append(paper_info)
                    if len(paper_infos) >= int(total_results): break
                self.updatetask(task_id, advance=1)
                if len(paper_infos) >= int(total_results): break
            self.updatetask(task_id, completed=len(volume_ids), description=f"Finished PMLR search: {len((paper_infos := paper_infos[:int(total_results)]))} papers found")
            self.log(f"Finished PMLR search. Found {len(paper_infos)} papers.")
            return paper_infos
        finally:
            if self.progress_mode != "detailed": self.removetask(task_id)
    '''queryvolume'''
    async def queryvolume(self, *, volume_id: int, query: Optional[str] = None, enrich_abstracts: bool = True) -> list["PaperInfo"]:
        soup = BeautifulSoup(await self.requesttext(f"{self.BASE_URL}/v{int(volume_id)}/"), "lxml")
        paper_infos = [self.blocktopaperinfo(block, volume_id=volume_id, query=query) for block in self.extractpaperblocks(soup)]
        paper_infos = [p for p in paper_infos if p.article_url]
        if enrich_abstracts: paper_infos = [p for p in await asyncio.gather(*[self.enrichpaperinfo(p) for p in paper_infos]) if p]
        if query: paper_infos = [p for p in paper_infos if p.matchkeyword(query)]
        return paper_infos
    '''extractpaperblocks'''
    def extractpaperblocks(self, soup: BeautifulSoup) -> list:
        if (blocks := soup.select("div.paper")): return blocks
        links = [a for a in soup.find_all("a", href=True) if a.get_text(" ", strip=True).lower() == "abs"]
        return [a.parent for a in links if a.parent]
    '''blocktopaperinfo'''
    def blocktopaperinfo(self, block: BeautifulSoup, *, volume_id: int, query: Optional[str] = None) -> "PaperInfo":
        title, details, article_url, download_url = self.getblocktext(block, ".title"), self.getblocktext(block, ".details"), None, None
        for link in block.find_all("a", href=True):
            text, href = link.get_text(" ", strip=True).lower(), self.absurl(link["href"], volume_id=volume_id)
            if text == "abs" or href.endswith(".html"): article_url = article_url or href
            if "pdf" in text or href.endswith(".pdf"): download_url = download_url or href
        if not title: title = next((x for x in block.get_text("\n", strip=True).split("\n") if x and not x.lower() in {"abs", "download pdf"}), None)
        authors, year = self.extractauthorsfromdetails(details), self.extractyear(details)
        return PaperInfo(source=self.source, title=title or "notitle", authors=authors, article_url=article_url, download_url=download_url, venue=details, publisher="PMLR", published_at=year, source_id=self.extractpmlrid(article_url), query=query, categories=[f"PMLR v{volume_id}"], tags=["pmlr"], is_open_access=True, extra={"volume_id": volume_id, "details": details})
    '''enrichpaperinfo'''
    async def enrichpaperinfo(self, paper_info: "PaperInfo") -> "PaperInfo":
        if not paper_info.article_url: return paper_info
        try:
            soup = BeautifulSoup(await self.requesttext(paper_info.article_url), "lxml")
            title, abstract, bibtex = self.getblocktext(soup, "h1") or paper_info.title, self.extractabstract(soup), soup.get_text("\n", strip=False)
            paper_info.title, paper_info.abstract = title, abstract or paper_info.abstract
            paper_info.download_url = self.extractbibfield(bibtex, "pdf") or paper_info.download_url
            paper_info.published_at = self.extractbibfield(bibtex, "year") or paper_info.published_at
            if (authors := self.extractbibfield(bibtex, "author")): paper_info.authors = [a.strip() for a in re.split(r"\s+and\s+", authors) if a.strip()]
            return paper_info
        except Exception:
            return paper_info
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not paper_info.download_url: paper_info = await self.enrichpaperinfo(paper_info)
        if not (url := paper_info.download_url): raise PaperDownloadError(f"No PMLR PDF URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        short_title = paper_info.title[:67] + "..." if paper_info.title and len(paper_info.title) > 70 else paper_info.title
        return await self.downloadvalidatedpdf(url, path, overwrite=overwrite, progress_description=f"Downloading: {short_title}", show_detail=show_detail, min_bytes=4 * 1024, min_pages=1)
    '''getblocktext'''
    @staticmethod
    def getblocktext(block: BeautifulSoup, selector: str) -> Optional[str]:
        if not block: return None
        node = block.select_one(selector) if hasattr(block, "select_one") else None
        return node.get_text(" ", strip=True) if node else None
    '''extractabstract'''
    @staticmethod
    def extractabstract(soup: BeautifulSoup) -> Optional[str]:
        marker = next((h for h in soup.find_all(["h2", "h3", "h4"]) if h.get_text(" ", strip=True).lower() == "abstract"), None)
        if marker and marker.find_next_sibling(): return marker.find_next_sibling().get_text(" ", strip=True)
        return None
    '''extractbibfield'''
    @staticmethod
    def extractbibfield(text: str, field: str) -> Optional[str]:
        match = re.search(rf"\b{re.escape(field)}\s*=\s*\{{(.+?)\}}", text, flags=re.I | re.S)
        return re.sub(r"\s+", " ", match.group(1)).strip() if match else None
    '''extractauthorsfromdetails'''
    @staticmethod
    def extractauthorsfromdetails(details: Optional[str]) -> list[str]:
        if not details: return []
        author_part = details.split(";", 1)[0]
        return [x.strip() for x in author_part.split(",") if x.strip()]
    '''extractyear'''
    @staticmethod
    def extractyear(text: Optional[str]) -> Optional[str]:
        return (m.group(0) if text and (m := re.search(r"\b(19|20)\d{2}\b", text)) else None)
    '''extractpmlrid'''
    @staticmethod
    def extractpmlrid(url: Optional[str]) -> Optional[str]:
        if not url: return None
        return Path(url).stem or None
    '''absurl'''
    @classmethod
    def absurl(cls, href: str, *, volume_id: Optional[int] = None) -> str:
        if href.startswith("http://") or href.startswith("https://"): return href
        if href.startswith("/"): return cls.BASE_URL + href
        if volume_id is not None: return f"{cls.BASE_URL}/v{int(volume_id)}/{href.lstrip('/')}"
        return cls.BASE_URL + "/" + href.lstrip("/")