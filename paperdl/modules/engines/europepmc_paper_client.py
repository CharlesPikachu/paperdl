'''
Function:
    Implementation of EuropePmcPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import asyncio
import random
import aiohttp
import aiofiles
from pathlib import Path
from typing import Any, Optional, Sequence
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''EuropePmcPaperClient'''
class EuropePmcPaperClient(BasePaperClient):
    source = "EuropePmcPaperClient"
    API_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    EUROPEPMC_PDF_URL = "https://europepmc.org/backend/ptpmcrender.fcgi"
    PMC_PDF_URL = "https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"
    def __init__(self, *, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        default_headers = {"User-Agent": "Mozilla/5.0 (compatible; EuropePmcPaperClient/1.0; +https://europepmc.org/)", "Accept": "application/pdf,application/octet-stream,*/*;q=0.8"}
        super(EuropePmcPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers={**default_headers, **(headers or {})}, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
    '''search'''
    async def search(self, query: str, *, total_results: int = 100, page_size: int = 25, result_type: str = "core", synonym: bool = True, sort: Optional[str] = None, deduplicate: bool = True, require_pdf_url: bool = False) -> list["PaperInfo"]:
        if not query or not query.strip() or not isinstance(total_results, (int, float)) or total_results <= 0: return []
        page_size, cursor_mark = max(1, min(int(page_size), 1000)), "*"; paper_infos: list[PaperInfo] = []
        task_id = self.addtask(f"Searching Europe PMC: {query[:60]}", total=None, kind="generic")
        while len(paper_infos) < total_results:
            params: dict[str, Any] = {"query": query, "format": "json", "resultType": result_type, "pageSize": min(page_size, int(total_results) - len(paper_infos)), "cursorMark": cursor_mark, "synonym": str(bool(synonym)).lower(), **({"sort": sort} if sort else {})}
            data: dict = await self.requestjson(self.API_URL, params=params, progress_description=None); start_rank = len(paper_infos) + 1
            for idx, item in enumerate((batch := ((data.get("resultList") or {}).get("result") or []))):
                paper_info = self.itemtopaperinfo(item, query=query, rank=start_rank + idx)
                if not require_pdf_url or self.pdfurlcandidates(paper_info): paper_infos.append(paper_info)
            self.updatetask(task_id, advance=1, description=f"Searching Europe PMC: {len(paper_infos)} papers fetched")
            if not batch or not (next_cursor := data.get("nextCursorMark")) or next_cursor == cursor_mark: break
            cursor_mark = next_cursor
        if deduplicate: paper_infos = list({p.identity_key: p for p in paper_infos}.values())
        self.updatetask(task_id, description=f"Finished Europe PMC search: {len(paper_infos)} papers found")
        if self.progress_mode != "detailed": self.removetask(task_id)
        self.log(f"Europe PMC search finished. Found {len(paper_infos)} papers.")
        return paper_infos[:int(total_results)]
    '''getbydoi'''
    async def getbydoi(self, doi: str) -> Optional["PaperInfo"]:
        if not doi: return None
        papers = await self.search(f'DOI:"{doi}"', total_results=1, page_size=1, synonym=False)
        return papers[0] if papers else None
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not (urls := self.pdfurlcandidates(paper_info)): raise PaperDownloadError(f"No legal open-access PDF URL available for: {paper_info.title}")
        if (path := Path(output_dir) / paper_info.filename(suffix=".pdf")).exists() and not overwrite:
            if self.localfileispdf(path): return path
            path.unlink(missing_ok=True)
        errors: list[str] = []
        for url in urls:
            try: return await self.downloadpdffile(url, path, overwrite=True, progress_description=f"Downloading Europe PMC PDF: {paper_info.title[:70]}", show_detail=show_detail)
            except Exception as exc: errors.append(f"{url} -> {type(exc).__name__}: {exc}"); self.log(f"Europe PMC PDF candidate failed: {errors[-1]}")
        raise PaperDownloadError(f"All Europe PMC PDF candidates failed for {paper_info.title}: {'; '.join(errors[:3])}")
    '''downloadpdffile'''
    async def downloadpdffile(self, url: str, target_path: str | Path, *, overwrite: bool = False, chunk_size: int = 1024 * 128, progress_description: Optional[str] = None, show_detail: bool = True) -> Path:
        await self.open(); (target_path := Path(target_path)).parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists() and not overwrite:
            if self.localfileispdf(target_path): return target_path
            target_path.unlink(missing_ok=True)
        tmp_target_path = target_path.with_suffix(target_path.suffix + ".part"); last_error: Optional[BaseException] = None
        task_id = self.addtask(progress_description or f"Downloading {target_path.name}", total=None, kind="download") if show_detail else None
        try:
            for attempt in range(self.max_retries + 1):
                try:
                    if attempt > 0 and task_id is not None: self.updatetask(task_id, completed=0, description=f"{progress_description or target_path.name} | retry {attempt}/{self.max_retries}")
                    async with self._semaphore:
                        async with self.session.get(url, proxy=self.proxy) as resp:
                            if resp.status in self.retry_statuses: raise PaperDownloadError(f"Temporary HTTP {resp.status}: {url}")
                            if resp.status >= 400: content = await resp.read(); raise PaperDownloadError(f"HTTP {resp.status}: {content[:200]!r}")
                            content_type, first_chunk = (resp.headers.get("Content-Type") or "").lower(), await resp.content.read(chunk_size); downloaded = len(first_chunk)
                            if not first_chunk.startswith(b"%PDF-"): preview = first_chunk[:120].decode("utf-8", errors="replace").replace("\n", " "); raise PaperDownloadError(f"URL did not return a PDF. content_type={content_type!r}, first_bytes={preview!r}")
                            if task_id is not None: self.updatetask(task_id, total=resp.content_length)
                            async with aiofiles.open(tmp_target_path, "wb") as fp:
                                await fp.write(first_chunk)
                                if task_id is not None: self.updatetask(task_id, advance=len(first_chunk))
                                async for chunk in resp.content.iter_chunked(chunk_size):
                                    if not chunk: continue
                                    await fp.write(chunk); downloaded += len(chunk)
                                    if task_id is not None: self.updatetask(task_id, advance=len(chunk))
                    if not self.localfileispdf(tmp_target_path): raise PaperDownloadError(f"Downloaded file is not a valid PDF: {url}")
                    tmp_target_path.replace(target_path)
                    if task_id is not None: self.updatetask(task_id, completed=downloaded, description=f"Downloaded {target_path.name}")
                    return target_path
                except (aiohttp.ClientError, asyncio.TimeoutError, PaperDownloadError) as exc:
                    last_error = exc
                    if tmp_target_path.exists(): tmp_target_path.unlink(missing_ok=True)
                    if attempt >= self.max_retries: break
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt) + random.random() * 0.2)
            raise PaperDownloadError(f"Verified PDF download failed: {url}") from last_error
        finally:
            if task_id is not None and self.progress_mode != "detailed": self.removetask(task_id)
    '''itemtopaperinfo'''
    def itemtopaperinfo(self, item: dict[str, Any], *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        grants = ((item.get("grantsList") or {}).get("grant") or [])
        pdf_url = self.pickpdfurl((full_text_urls := ((item.get("fullTextUrlList") or {}).get("fullTextUrl") or [])))
        keywords = [k.get("keyword") if isinstance(k, dict) else k for k in (((item.get("keywordList") or {}).get("keyword") or []))]
        authors = [a.get("fullName") or a.get("collectiveName") for a in (((item.get("authorList") or {}).get("author") or [])) if isinstance(a, dict) and (a.get("fullName") or a.get("collectiveName"))]
        article_url = item.get("fullTextUrl") or (item.get("doi") and f"https://doi.org/{item.get('doi')}") or (item.get("id") and f"https://europepmc.org/article/{item.get('source')}/{item.get('id')}")
        return PaperInfo(
            source=self.source, title=item.get("title") or "notitle", abstract=item.get("abstractText"), authors=authors, article_url=article_url, download_url=pdf_url, doi=item.get("doi"), venue=item.get("journalTitle"), publisher="Europe PMC", published_at=item.get("firstPublicationDate") or item.get("pubYear"), source_id=item.get("id"), query=query, rank=rank, keywords=keywords, categories=[item.get("source")] if item.get("source") else [], 
            tags=PaperInfo.uniquelist(["europepmc", item.get("pubType"), item.get("source")]), citation_count=item.get("citedByCount"), is_open_access=str(item.get("isOpenAccess", "")).upper() == "Y" if item.get("isOpenAccess") is not None else None, language=item.get("language"), license=item.get("license"), extra={"pmid": item.get("pmid"), "pmcid": item.get("pmcid"), "grants": grants, "full_text_urls": full_text_urls, "raw": item},
        )
    '''pickpdfurl'''
    @staticmethod
    def pickpdfurl(full_text_urls: Sequence[dict[str, Any]]) -> Optional[str]:
        for item in full_text_urls or []:
            if not isinstance(item, dict): continue
            style, url = (item.get("documentStyle") or "").lower(), item.get("url", "") or ""
            if url and ("pdf" in style or str(url).lower().split("?", 1)[0].endswith(".pdf")): return url
        return None
    '''pdfurlcandidates'''
    def pdfurlcandidates(self, paper_info: "PaperInfo") -> list[str]:
        pmcid = self.cleanpmcid(paper_info.extra.get("pmcid") or (paper_info.extra.get("raw", {}) or {}).get("pmcid"))
        urls: list[str] = [f"{self.EUROPEPMC_PDF_URL}?accid={pmcid}&blobtype=pdf", self.PMC_PDF_URL.format(pmcid=pmcid)] if pmcid else []
        if paper_info.download_url: urls.append(paper_info.download_url)
        for item in paper_info.extra.get("full_text_urls", []) or []:
            if not isinstance(item, dict): continue
            url, style = item.get("url"), (item.get("documentStyle") or "").lower()
            if url and ("pdf" in style or str(url).lower().split("?", 1)[0].endswith(".pdf")): urls.append(url)
        return self.uniquelist(urls)
    '''cleanpmcid'''
    @staticmethod
    def cleanpmcid(value: Any) -> Optional[str]:
        if not value: return None
        text = str(value).strip().upper()
        return text if text.startswith("PMC") else f"PMC{text}" if text.isdigit() else None
    '''localfileispdf'''
    @staticmethod
    def localfileispdf(path: str | Path) -> bool:
        try:
            with open(path, "rb") as fp: return fp.read(5) == b"%PDF-"
        except Exception:
            return False
    '''uniquelist'''
    @staticmethod
    def uniquelist(values: Sequence[str]) -> list[str]:
        seen, results = set(), []
        for value in (values or []):
            if not value: continue
            if (key := value.strip()) and key not in seen: seen.add(key); results.append(key)
        return results