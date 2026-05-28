'''
Function:
    Implementation of BioRxivPaperClient and MedRxivPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
import aiofiles
from pathlib import Path
from datetime import date
from contextlib import suppress
from typing import Any, Optional
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError, PaperRequestError


'''BioRxivPaperClient'''
class BioRxivPaperClient(BasePaperClient):
    source = "BioRxivPaperClient"
    SERVER = "biorxiv"
    API_URL = "https://api.biorxiv.org/details"
    DEFAULT_FROM_DATE = "2024-01-01"
    DEFAULT_API_PAGE_SIZE = 100
    PDF_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "Cache-Control": "max-age=0", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1",
    }
    def __init__(self, *, timeout: float = 60.0, concurrency: int = 3, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True, browser_fallback: bool = True, browser_headless: bool = True, browser_channel: Optional[str] = None, browser_user_data_dir: Optional[str | Path] = None, browser_wait_seconds: float = 8.0) -> None:
        super(BioRxivPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.browser_fallback = browser_fallback
        self.browser_headless = browser_headless
        self.browser_channel = browser_channel
        self.browser_user_data_dir = Path(browser_user_data_dir) if browser_user_data_dir else None
        self.browser_wait_seconds = browser_wait_seconds if isinstance(browser_wait_seconds, (int, float)) else 8.0
    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, from_date: str = DEFAULT_FROM_DATE, to_date: Optional[str] = None, max_scan_results: Optional[int] = 5000, page_size: int = DEFAULT_API_PAGE_SIZE, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        if not from_date: from_date = self.DEFAULT_FROM_DATE
        try: page_size = max(1, int(page_size))
        except Exception: page_size = self.DEFAULT_API_PAGE_SIZE
        actual_to_date = to_date or date.today().isoformat(); paper_infos: list[PaperInfo] = []; seen_keys: set[str] = set()
        cursor, fetched, matched = 0, 0, 0; task_id = self.addtask(f"Searching {self.SERVER}: {(query or 'all')[:60]}", total=None, kind="generic")
        self.log(f"Start searching {self.SERVER}: query={query!r}, from_date={from_date}, to_date={to_date}.")
        try:
            while len(paper_infos) < int(total_results):
                if max_scan_results is not None and fetched >= max_scan_results: break
                payload = await self.querypage(from_date=from_date, to_date=actual_to_date, cursor=cursor, show_progress=False)
                if not isinstance((collection := payload.get("collection") or []), list) or not collection: break
                fetched += len(collection)
                for item in collection:
                    if not isinstance(item, dict): continue
                    paper_info = self.itemtopaperinfo(item, query=query, rank=len(paper_infos) + 1)
                    if query and not paper_info.matchkeyword(query): continue
                    if deduplicate and paper_info.identity_key in seen_keys: continue
                    seen_keys.add(paper_info.identity_key); matched += 1; paper_infos.append(paper_info)
                    if len(paper_infos) >= int(total_results): break
                cursor += len(collection)
                self.updatetask(task_id, description=f"Searching {self.SERVER}: fetched={fetched}, matched={matched}")
                total_available = self.extracttotal(payload)
                if (total_available is not None and cursor >= total_available) or (len(collection) <= 0): break
            self.log(f"Finished {self.SERVER} search. Found {len(paper_infos)} papers.")
            return paper_infos[:int(total_results)]
        finally:
            self.removetask(task_id)
    '''querypage'''
    async def querypage(self, *, from_date: str, to_date: str, cursor: int = 0, show_progress: bool = False) -> dict[str, Any]:
        url = f"{self.API_URL}/{self.SERVER}/{from_date}/{to_date}/{int(cursor)}"
        payload = await self.requestjson(url, progress_description=(f"Fetching {self.SERVER} records: {cursor}" if show_progress else None))
        if not isinstance(payload, dict): raise PaperRequestError(f"Invalid {self.SERVER} response: {type(payload)}")
        return payload
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not (url := paper_info.download_url): raise PaperDownloadError(f"No download URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        short_title = paper_info.title[:67] + "..." if paper_info.title and len(paper_info.title) > 70 else paper_info.title
        headers = {**self.PDF_HEADERS, "Referer": paper_info.article_url or f"https://www.{self.SERVER}.org/"}
        try:
            return await self.downloadvalidatedpdf(url, path, overwrite=overwrite, headers=headers, progress_description=f"Downloading: {short_title}", show_detail=show_detail, min_bytes=4 * 1024, min_pages=1)
        except Exception as exc:
            if path.exists(): path.unlink(missing_ok=True)
            if not self.browser_fallback: raise RuntimeError(f"Normal {self.SERVER} PDF download failed.")
            self.log(f"Normal {self.SERVER} PDF download failed, fallback to browser download. Reason: {exc}")
        return await self.downloadpdfwithbrowser(url, path, overwrite=overwrite, progress_description=f"Downloading with browser: {short_title}", show_detail=show_detail)
    '''downloadpdfwithbrowser'''
    async def downloadpdfwithbrowser(self, url: str, target_path: str | Path, *, overwrite: bool = False, progress_description: Optional[str] = None, show_detail: bool = True) -> Path:
        if (target_path := Path(target_path)).exists() and not overwrite:
            result = self.validatepdffile(target_path, min_bytes=4 * 1024, min_pages=1)
            if result.valid: return target_path
            target_path.unlink(missing_ok=True)
        task_id = self.addtask(progress_description or f"Downloading {target_path.name}", total=None, kind="generic") if show_detail else None
        try:
            try: from playwright.async_api import async_playwright
            except ImportError as exc: raise PaperDownloadError(f"{self.SERVER} PDF download is blocked for normal HTTP clients. Install Playwright with: pip install playwright && python -m playwright install chromium") from exc
            target_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_target_path = target_path.with_suffix(target_path.suffix + ".part")
            body, content_type = await self.fetchpdfwithbrowser(url)
            async with aiofiles.open(tmp_target_path, "wb") as fp: await fp.write(body)
            tmp_target_path.replace(target_path); result = self.validatepdffile(target_path, min_bytes=4 * 1024, min_pages=1)
            if not result.valid: target_path.unlink(missing_ok=True); raise PaperDownloadError(f"Browser download did not return a valid PDF. Content-Type={content_type!r}, reason={result.reason}")
            return target_path
        finally:
            if task_id is not None and self.progress_mode != "detailed": self.removetask(task_id)
    '''fetchpdfwithbrowser'''
    async def fetchpdfwithbrowser(self, url: str) -> tuple[bytes, str]:
        from playwright.async_api import async_playwright
        browser, context, launch_kwargs = None, None, {"headless": self.browser_headless}
        context_kwargs = {"user_agent": self.PDF_HEADERS["User-Agent"], "locale": "zh-CN", "accept_downloads": True}
        if self.browser_channel: launch_kwargs["channel"] = self.browser_channel
        if self.proxy: launch_kwargs["proxy"] = {"server": self.proxy}
        try:
            async with async_playwright() as p:
                if self.browser_user_data_dir: self.browser_user_data_dir.mkdir(parents=True, exist_ok=True); persistent_kwargs = {**launch_kwargs, **context_kwargs}; context = await p.chromium.launch_persistent_context(user_data_dir=str(self.browser_user_data_dir), **persistent_kwargs)
                else: browser = await p.chromium.launch(**launch_kwargs); context = await browser.new_context(**context_kwargs)
                page = await context.new_page(); resp = await page.goto(url, wait_until="commit", timeout=int(self.timeout * 1000))
                if resp is None: raise PaperDownloadError(f"No browser response returned for: {url}")
                content_type = resp.headers.get("content-type", "").lower(); body = await resp.body()
                if self.lookslikecloudflarechallenge(body, content_type):
                    await page.wait_for_timeout(int(max(self.browser_wait_seconds, 0) * 1000))
                    resp = await page.goto(url, wait_until="commit", timeout=int(self.timeout * 1000))
                    if resp is None: raise PaperDownloadError(f"No browser response returned after retry for: {url}")
                    content_type = resp.headers.get("content-type", "").lower(); body = await resp.body()
                return body, content_type
        finally:
            with suppress(Exception): await context.close() if context is not None else None
            with suppress(Exception): await browser.close() if browser is not None else None
    '''itemtopaperinfo'''
    def itemtopaperinfo(self, item: dict[str, Any], *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        doi, version, title = self.cleandoi(item.get("doi")), self.cleanversion(item.get("version")), item.get("title") or "notitle"
        abstract, authors, category = item.get("abstract"), self.parseauthors(item.get("authors")), item.get("category")
        date_value = item.get("date") or item.get("published") or item.get("server_date")
        article_url, download_url = self.articleurlfromdoi(doi, version), self.pdfurlfromdoi(doi, version)
        return PaperInfo(
            source=self.source, title=title, abstract=abstract, authors=authors, article_url=article_url, download_url=download_url, doi=doi, venue=category, publisher=self.publishername(), published_at=date_value, updated_at=item.get("published") or date_value, source_id=doi, query=query, 
            rank=rank, categories=[category] if category else [], tags=[self.SERVER], is_open_access=True, extra={"server": self.SERVER, "version": version, "license": item.get("license"), "jatsxml": item.get("jatsxml"), "server_date": item.get("server_date"), "raw": item}
        )
    '''extracttotal'''
    @staticmethod
    def extracttotal(payload: dict[str, Any]) -> Optional[int]:
        if isinstance((messages := payload.get("messages") or []), dict): candidates = [messages]
        elif isinstance(messages, list): candidates = [x for x in messages if isinstance(x, dict)]
        else: candidates = []
        for message in candidates:
            for key in ("total", "count_total", "total_count"):
                if (value := message.get(key)) in (None, ""): continue
                try: return int(float(value))
                except Exception: continue
        return None
    '''lookslikecloudflarechallenge'''
    @staticmethod
    def lookslikecloudflarechallenge(body: bytes, content_type: str = "") -> bool:
        if not body: return False
        if b"%pdf-" in (head := body[:4096].lower())[:64]: return False
        return (b"just a moment" in head or b"cf-browser-verification" in head or b"cf-chl" in head or (b"cloudflare" in head and b"<html" in head) or ("text/html" in content_type and b"<title>just a moment" in head))
    '''parseauthors'''
    @staticmethod
    def parseauthors(value: Any) -> list[str]:
        if value is None: return []
        if isinstance(value, list): return [str(name).strip() for item in value for name in ([item.get("name") or item.get("full_name") or item.get("author")] if isinstance(item, dict) else [item]) if str(name).strip()]
        if not (text := str(value).strip()): return []
        if ";" in text: return [x.strip() for x in text.split(";") if x.strip()]
        return [text]
    '''cleandoi'''
    @staticmethod
    def cleandoi(value: Any) -> Optional[str]:
        if not value: return None
        text = str(value).strip().split("doi.org/", 1)[-1].strip().strip("/")
        if match := re.search(r"10\.1101/[^\s?#]+", text): return match.group(0).strip().strip("/")
        return text or None
    '''cleanversion'''
    @staticmethod
    def cleanversion(value: Any) -> Optional[str]:
        if value is None or value == "": return None
        try: return str(int(float(value)))
        except Exception: return str(value).strip() or None
    '''articleurlfromdoi'''
    @classmethod
    def articleurlfromdoi(cls, doi: Optional[str], version: Optional[str] = None) -> Optional[str]:
        if not doi: return None
        suffix = f"v{version}" if version else ""
        return f"https://www.{cls.SERVER}.org/content/{doi}{suffix}"
    '''pdfurlfromdoi'''
    @classmethod
    def pdfurlfromdoi(cls, doi: Optional[str], version: Optional[str] = None) -> Optional[str]:
        if not doi: return None
        suffix = f"v{version}" if version else ""
        return f"https://www.{cls.SERVER}.org/content/{doi}{suffix}.full.pdf"
    '''publishername'''
    @classmethod
    def publishername(cls) -> str:
        return "bioRxiv" if cls.SERVER == "biorxiv" else "medRxiv"


'''MedRxivPaperClient'''
class MedRxivPaperClient(BioRxivPaperClient):
    source = "MedRxivPaperClient"
    SERVER = "medrxiv"
    DEFAULT_FROM_DATE = "2024-01-01"