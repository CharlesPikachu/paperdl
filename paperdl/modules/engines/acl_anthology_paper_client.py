'''
Function:
    Implementation of ACLAnthologyPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Optional, Sequence, Any
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''ACLAnthologyPaperClient'''
class ACLAnthologyPaperClient(BasePaperClient):
    source = "ACLAnthologyPaperClient"
    BASE_URL = "https://aclanthology.org"
    XML_INDEX_URL = "https://api.github.com/repos/acl-org/acl-anthology/contents/data/xml"
    XML_RAW_URL = "https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{collection_id}.xml"
    def __init__(self, *, api_delay: float = 0.2, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        default_headers = {"Accept": "application/vnd.github+json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"}
        super(ACLAnthologyPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers={**default_headers, **(headers or {})}, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.api_delay = api_delay if isinstance(api_delay, (int, float)) else 0.0
    '''listxmlcollections'''
    async def listxmlcollections(self) -> list[str]:
        payload = await self.requestjson(self.XML_INDEX_URL, progress_description="Loading ACL Anthology metadata index")
        collection_ids = [Path(item.get("name", "")).stem for item in payload if isinstance(item, dict) and (item.get("name", "") or "").endswith(".xml")]
        return sorted(collection_ids, key=self.collectionsortkey, reverse=True)
    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, collection_ids: Optional[Sequence[str]] = None, max_collections: Optional[int] = 40, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        if collection_ids is None: collection_ids = await self.listxmlcollections(); collection_ids = list(collection_ids)[:max_collections] if max_collections else collection_ids
        paper_infos: list[PaperInfo] = []; task_id = self.addtask(f"Searching ACL Anthology: {(query or 'all')[:60]}", total=len(collection_ids), kind="generic")
        self.log(f"Start searching ACL Anthology: query={query!r}, collections={list(collection_ids)[:8]}...")
        for idx, collection_id in enumerate(collection_ids, start=1):
            if idx > 1 and self.api_delay > 0: await asyncio.sleep(self.api_delay)
            self.updatetask(task_id, description=f"Searching ACL collection {collection_id}: {(query or 'all')[:50]}")
            paper_infos.extend(await self.querycollection(collection_id, query=query)); self.updatetask(task_id, advance=1)
            if len(paper_infos) >= total_results: break
        if deduplicate: paper_infos = list({p.identity_key: p for p in paper_infos}.values())
        self.updatetask(task_id, completed=len(collection_ids), description=f"Finished ACL Anthology search: {len(paper_infos)} papers found")
        if self.progress_mode != "detailed": self.removetask(task_id)
        self.log(f"Finished ACL Anthology search. Found {len((paper_infos := paper_infos[:int(total_results)]))} papers.")
        return paper_infos
    '''querycollection'''
    async def querycollection(self, collection_id: str, *, query: Optional[str] = None) -> list["PaperInfo"]:
        xml_text = await self.requesttext(self.XML_RAW_URL.format(collection_id=collection_id))
        root = ET.fromstring(xml_text); paper_infos: list[PaperInfo] = []
        for volume in root.findall(".//volume"):
            booktitle = self.nodetext(volume.find("./meta/booktitle"))
            for paper in volume.findall("./paper"):
                paper_info = self.papertopaperinfo(paper, collection_id=collection_id, volume_id=volume.attrib.get("id"), booktitle=booktitle)
                if not query or paper_info.matchkeyword(query): paper_infos.append(paper_info)
        return paper_infos
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not (url := paper_info.download_url): raise PaperDownloadError(f"No ACL Anthology PDF URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        short_title = paper_info.title[:67] + "..." if paper_info.title and len(paper_info.title) > 70 else paper_info.title
        return await self.downloadvalidatedpdf(url, path, overwrite=overwrite, progress_description=f"Downloading: {short_title}", show_detail=show_detail, min_bytes=4 * 1024, min_pages=1)
    '''papertopaperinfo'''
    def papertopaperinfo(self, paper: ET.Element, *, collection_id: str, volume_id: Optional[str], booktitle: Optional[str]) -> "PaperInfo":
        paper_id = self.nodetext(paper.find("./url")) or self.buildpaperid(collection_id, volume_id, paper.attrib.get("id"))
        title, abstract = self.nodetext(paper.find("./title")) or "notitle", self.nodetext(paper.find("./abstract"))
        authors = [a for a in [self.authortext(author) for author in paper.findall("./author")] if a]
        return PaperInfo(source=self.source, title=title, abstract=abstract, authors=authors, article_url=f"{self.BASE_URL}/{paper_id}/" if paper_id else None, download_url=f"{self.BASE_URL}/{paper_id}.pdf" if paper_id else None, venue=booktitle, publisher="ACL Anthology", published_at=self.extractyear(paper_id), source_id=paper_id, categories=[collection_id] if collection_id else [], tags=["acl-anthology"], is_open_access=True, extra={"collection_id": collection_id, "volume_id": volume_id, "paper_xml_id": paper.attrib.get("id")})
    '''nodetext'''
    @staticmethod
    def nodetext(node: Optional[ET.Element]) -> Optional[str]:
        if node is None: return None
        text = re.sub(r"\s+", " ", "".join(node.itertext())).strip()
        return text or None
    '''authortext'''
    @classmethod
    def authortext(cls, author: ET.Element) -> Optional[str]:
        first = cls.nodetext(author.find("./first"))
        last = cls.nodetext(author.find("./last"))
        full = " ".join(x for x in [first, last] if x).strip()
        return full or cls.nodetext(author)
    '''buildpaperid'''
    @staticmethod
    def buildpaperid(collection_id: str, volume_id: Optional[str], paper_id: Optional[str]) -> Optional[str]:
        if not collection_id or not volume_id or not paper_id: return None
        if collection_id[:1].isalpha() and collection_id[1:].isdigit(): return f"{collection_id}-{volume_id}{int(paper_id):03d}"
        return f"{collection_id}.{paper_id}"
    '''extractyear'''
    @staticmethod
    def extractyear(value: Any, *, min_year: int = 1900, max_future_years: int = 1) -> Optional[str]:
        if value is None or not (text := str(value).strip()): return None
        max_year = datetime.now().year + max_future_years
        for match in re.finditer(r"(?<!\d)((?:19|20)\d{2})(?!\d)", text):
            if min_year <= (year := int(match.group(1))) <= max_year: return str(year)
        if (match := re.search(r"(?<![A-Za-z0-9])([A-Z])(\d{2})-\d+", text, flags=re.IGNORECASE)):
            short_year, current_short_year = int(match.group(2)), max_year % 100
            year = 2000 + short_year if short_year <= current_short_year else 1900 + short_year
            if min_year <= year <= max_year: return str(year)
        return None
    '''collectionsortkey'''
    @classmethod
    def collectionsortkey(cls, collection_id: str) -> tuple[int, str]:
        year = cls.extractyear(collection_id) or "0"
        return int(year), collection_id