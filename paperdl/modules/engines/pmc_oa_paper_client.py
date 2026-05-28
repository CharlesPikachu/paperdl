'''
Function:
    Implementation of PMCOAPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Optional
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''PMCOAPaperClient'''
class PMCOAPaperClient(BasePaperClient):
    source = "PMCOAPaperClient"
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    OA_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"

    def __init__(self, *, tool: str = "paper-client", email: Optional[str] = None, api_key: Optional[str] = None, api_delay: float = 0.34, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        super(PMCOAPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self.tool, self.email, self.api_key, self.api_delay = tool, email, api_key, api_delay

    '''baseparams'''
    def baseparams(self) -> dict[str, str]:
        params = {"tool": self.tool}
        if self.email: params["email"] = self.email
        if self.api_key: params["api_key"] = self.api_key
        return params

    '''queryids'''
    async def queryids(self, query: Optional[str], *, retstart: int = 0, retmax: int = 100, sort: str = "relevance") -> tuple[list[str], int]:
        term = f"({query}) AND open access[filter]" if query else "open access[filter]"
        payload = await self.requestjson(self.ESEARCH_URL, params={**self.baseparams(), "db": "pmc", "term": term, "retmode": "json", "retstart": int(retstart), "retmax": int(retmax), "sort": sort})
        result = payload.get("esearchresult", {}) or {}
        return result.get("idlist", []) or [], int(result.get("count") or 0)

    '''fetchsummaries'''
    async def fetchsummaries(self, ids: list[str]) -> list[dict[str, Any]]:
        if not ids: return []
        payload = await self.requestjson(self.ESUMMARY_URL, params={**self.baseparams(), "db": "pmc", "id": ",".join(ids), "retmode": "json"})
        result, summaries = payload.get("result", {}) or {}, []
        for uid in result.get("uids", []) or []:
            if isinstance(item := result.get(uid), dict): summaries.append(item)
        return summaries

    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, page_size: int = 50, sort: str = "relevance", require_pdf: bool = True, deduplicate: bool = True) -> list["PaperInfo"]:
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        page_size, retstart, paper_infos, total_count = max(1, min(int(page_size), 200)), 0, [], None
        task_id = self.addtask(f"Searching PMC OA: {(query or 'all')[:60]}", total=None, kind="generic")
        self.log(f"Start searching PMC OA: query={query!r}, total_results={total_results}, page_size={page_size}.")
        while len(paper_infos) < total_results:
            if retstart > 0 and self.api_delay > 0: await asyncio.sleep(self.api_delay)
            self.updatetask(task_id, description=f"Searching PMC OA start={retstart}: {(query or 'all')[:50]}")
            ids, total_count = await self.queryids(query, retstart=retstart, retmax=page_size, sort=sort)
            if not ids: break
            page_infos = [self.summarytopaperinfo(item, query=query, rank=retstart + idx + 1) for idx, item in enumerate(await self.fetchsummaries(ids))]
            if require_pdf:
                page_infos = [p for p in await asyncio.gather(*[self.attachoadownloadurl(p) for p in page_infos]) if p and p.download_url]
            paper_infos.extend(page_infos)
            retstart += page_size
            if total_count is not None and retstart >= total_count: break
            if retstart >= page_size * 50 and len(paper_infos) == 0: break
        if deduplicate: paper_infos = list({p.identity_key: p for p in paper_infos}.values())
        paper_infos = paper_infos[:int(total_results)]
        self.updatetask(task_id, completed=1, description=f"Finished PMC OA search: {len(paper_infos)} papers found")
        if self.progress_mode != "detailed": self.removetask(task_id)
        self.log(f"Finished PMC OA search. Found {len(paper_infos)} papers.")
        return paper_infos

    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        if not paper_info.download_url:
            paper_info = await self.attachoadownloadurl(paper_info)
        if not (url := paper_info.download_url): raise PaperDownloadError(f"No PMC OA PDF URL available for: {paper_info.title}")
        path = Path(output_dir) / paper_info.filename(suffix=".pdf")
        short_title = paper_info.title[:67] + "..." if paper_info.title and len(paper_info.title) > 70 else paper_info.title
        return await self.downloadvalidatedpdf(url, path, overwrite=overwrite, progress_description=f"Downloading: {short_title}", show_detail=show_detail, min_bytes=4 * 1024, min_pages=1)

    '''attachoadownloadurl'''
    async def attachoadownloadurl(self, paper_info: "PaperInfo") -> "PaperInfo":
        pmcid = paper_info.source_id or paper_info.extra.get("pmcid")
        if not pmcid: return paper_info
        try:
            pdf_url, license_name = await self.getoadownloadurl(pmcid)
        except Exception:
            return paper_info
        paper_info.download_url = pdf_url or paper_info.download_url
        paper_info.license = license_name or paper_info.license
        return paper_info

    '''getoadownloadurl'''
    async def getoadownloadurl(self, pmcid: str) -> tuple[Optional[str], Optional[str]]:
        xml_text = await self.requesttext(self.OA_URL, params={"id": pmcid})
        root = ET.fromstring(xml_text)
        record = root.find(".//record")
        license_name = record.attrib.get("license") if record is not None else None
        for link in root.findall(".//link"):
            if link.attrib.get("format") == "pdf" and link.attrib.get("href"):
                href = link.attrib["href"]
                if href.startswith("ftp://ftp.ncbi.nlm.nih.gov/"):
                    href = "https://ftp.ncbi.nlm.nih.gov/" + href.split("ftp://ftp.ncbi.nlm.nih.gov/", 1)[-1]
                return href, license_name
        return None, license_name

    '''summarytopaperinfo'''
    def summarytopaperinfo(self, item: dict[str, Any], *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        pmcid = item.get("pmcid") or (f"PMC{item.get('uid')}" if item.get("uid") else None)
        authors = [a.get("name") for a in item.get("authors", []) if isinstance(a, dict) and a.get("name")]
        doi = self.extractdoi(item.get("elocationid"))
        return PaperInfo(
            source=self.source, title=item.get("title") or "notitle", abstract=None, authors=authors, article_url=f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else None, download_url=None, doi=doi, venue=item.get("fulljournalname") or item.get("source"), publisher="PubMed Central", published_at=item.get("pubdate") or item.get("epubdate"), source_id=pmcid, query=query, rank=rank, tags=["pmc", "open-access"], is_open_access=True, extra={"uid": item.get("uid"), "pmcid": pmcid, "pmid": item.get("pmid"), "raw": item},
        )

    '''extractdoi'''
    @staticmethod
    def extractdoi(value: Optional[str]) -> Optional[str]:
        if not value: return None
        text = str(value).strip()
        return text[4:].strip() if text.lower().startswith("doi:") else None
