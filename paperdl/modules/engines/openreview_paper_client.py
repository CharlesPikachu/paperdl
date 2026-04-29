'''
Function:
    Implementation of OpenReviewPaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import aiofiles
import openreview
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone
from openreview.api import OpenReviewClient
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''OpenReviewPaperClient'''
class OpenReviewPaperClient(BasePaperClient):
    source = "OpenReviewPaperClient"
    def __init__(self, *, baseurl: str = "https://api2.openreview.net", username: Optional[str] = None, password: Optional[str] = None, api_version: int = 2, timeout: float = 60.0, concurrency: int = 5, max_retries: int = 3, retry_backoff: float = 1.5, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, proxy: Optional[str] = None, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True) -> None:
        super(OpenReviewPaperClient, self).__init__(timeout=timeout, concurrency=concurrency, max_retries=max_retries, retry_backoff=retry_backoff, headers=headers, cookies=cookies, cookie_file=cookie_file, proxy=proxy, thread_workers=thread_workers, show_progress=show_progress, progress_mode=progress_mode, max_detail_tasks=max_detail_tasks, verbose=verbose)
        self._or_client: OpenReviewClient = None
        self.baseurl, self.username, self.password, self.api_version = baseurl, username, password, api_version
    '''open'''
    async def open(self) -> None:
        await super().open()
        self._or_client = self._or_client or (await self.runblocking(self.createopenreviewclient, progress_description="Initializing OpenReview client"))
    '''createopenreviewclient'''
    def createopenreviewclient(self) -> Any:
        kwargs = {"baseurl": self.baseurl, **({"username": self.username, "password": self.password} if self.username and self.password else {})}
        return (OpenReviewClient(**kwargs) if self.api_version == 2 else openreview.Client(**kwargs))
    '''login'''
    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.username, self.password = username or self.username, password or self.password
        self._or_client = await self.runblocking(self.createopenreviewclient, progress_description="Logging in to OpenReview")
    '''search'''
    async def search(self, query: Optional[str] = None, *, total_results: int = 100, venue_id: Optional[str] = None, invitation: Optional[str] = None, content: Optional[dict[str, Any]] = None, details: Optional[str] = None, accepted_only: bool = False, client_side_filter: bool = True) -> list["PaperInfo"]:
        await self.open()
        if not isinstance(total_results, (float, int)) or total_results <= 0: return []
        if not invitation and venue_id: invitation = await self.infersubmissioninvitation(venue_id)
        if accepted_only and venue_id: content = {**(content or {}), "venueid": venue_id}
        if not invitation and not content: raise ValueError("OpenReview search requires either `venue_id`, `invitation`, or a `content` filter. For example: venue_id='ICLR.cc/2024/Conference'.")
        task_id = self.addtask(f"Fetching OpenReview notes: {(venue_id or invitation or 'content filter')}", total=None)
        try: notes = await self.getallnotes(invitation=invitation, content=content, details=details)
        finally: self.removetask(task_id)
        paper_infos = [self.notetopaperinfo(note, query=query, rank=i + 1) for i, note in enumerate(notes)]
        if query and client_side_filter: paper_infos = [p for p in paper_infos if query.lower().strip() in " ".join([p.title or "", p.abstract or "", " ".join(p.authors), " ".join(p.keywords), " ".join(p.categories), " ".join(p.tags)]).lower()]
        paper_infos = paper_infos[:total_results]
        self.log(f"OpenReview search finished. Found {len(paper_infos)} papers.")
        return paper_infos
    '''infersubmissioninvitation'''
    async def infersubmissioninvitation(self, venue_id: str) -> str:
        await self.open(); group = await self.runblocking(lambda: self._or_client.get_group(venue_id), progress_description=f"Loading OpenReview venue group: {venue_id}")
        if not (submission_name := self.contentvalue((getattr(group, "content", {}) or {}).get("submission_name"))): submission_name = "Submission"
        return f"{venue_id}/-/{submission_name}"
    '''getallnotes'''
    async def getallnotes(self, *, invitation: Optional[str] = None, content: Optional[dict[str, Any]] = None, details: Optional[str] = None) -> list[Any]:
        await self.open(); kwargs = {k: v for k, v in {"invitation": invitation, "content": content, "details": details}.items() if v}
        return await self.runblocking(self._or_client.get_all_notes, **kwargs)
    '''downloaditem'''
    async def downloaditem(self, paper_info: "PaperInfo", output_dir: str | Path = "paperdl_outputs", *, overwrite: bool = False, show_detail: bool = True, prefer_attachment_api: bool = False, fallback_to_attachment_api: bool = True) -> Path:
        note_id = (paper_info.source_id or paper_info.extra.get("note_id") or paper_info.extra.get("forum"))
        if not note_id: raise PaperDownloadError(f"No OpenReview note id available for: {paper_info.title}")
        if (path := Path(output_dir) / paper_info.filename(suffix=".pdf")).exists() and not overwrite: return path
        if prefer_attachment_api: return await self.downloadbyattachmentapi(note_id, path, overwrite=overwrite, show_detail=show_detail)
        download_url = paper_info.download_url or f"https://openreview.net/pdf?id={note_id}"
        try:
            return await self.downloadfile(download_url, path, overwrite=overwrite, progress_description=f"Downloading OpenReview PDF: {paper_info.title[:70]}", show_detail=show_detail)
        except Exception:
            if not fallback_to_attachment_api: raise PaperDownloadError(f"Fail to access {download_url}")
            return await self.downloadbyattachmentapi(note_id, path, overwrite=overwrite, show_detail=show_detail)
    '''downloadbyattachmentapi'''
    async def downloadbyattachmentapi(self, note_id: str, target_path: str | Path, *, overwrite: bool = False, show_detail: bool = True) -> Path:
        await self.open(); (target_path := Path(target_path)).parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists() and not overwrite: return target_path
        task_id = self.addtask(f"Downloading OpenReview attachment: {target_path.name}", total=None) if show_detail else None
        try:
            pdf_bytes = await self.runblocking(self._or_client.get_attachment, field_name="pdf", id=note_id)
            tmp_target_path = target_path.with_suffix(target_path.suffix + ".part")
            async with aiofiles.open(tmp_target_path, "wb") as fp: await fp.write(pdf_bytes)
            tmp_target_path.replace(target_path); return target_path
        finally:
            self.removetask(task_id)
    '''notetopaperinfo'''
    def notetopaperinfo(self, note: Any, *, query: Optional[str] = None, rank: Optional[int] = None) -> "PaperInfo":
        content, note_id, forum = getattr(note, "content", {}) or {}, getattr(note, "id", None), getattr(note, "forum", None)
        number, invitations = getattr(note, "number", None), getattr(note, "invitations", None) or []
        title, abstract = self.contentvalue(content.get("title")) or "notitle", self.contentvalue(content.get("abstract"))
        authors = [authors] if isinstance((authors := self.contentvalue(content.get("authors")) or []), str) else authors
        keywords = [keywords] if isinstance((keywords := self.contentvalue(content.get("keywords")) or []), str) else keywords
        venueid, pdf_field = self.contentvalue(content.get("venueid")), self.contentvalue(content.get("pdf"))
        return PaperInfo(
            source=self.source, title=title, abstract=abstract, authors=authors, article_url=f"https://openreview.net/forum?id={forum or note_id}" if (forum or note_id) else None, download_url=f"https://openreview.net/pdf?id={note_id}" if note_id else None, source_id=note_id, query=query, rank=rank, venue=venueid, publisher="OpenReview", published_at=self.openreviewtimetoiso(getattr(note, "cdate", None)), 
            updated_at=self.openreviewtimetoiso(getattr(note, "mdate", None)), keywords=keywords, categories=[venueid] if venueid else [], tags=["openreview"], is_open_access=True, extra={"note_id": note_id, "forum": forum, "number": number, "invitations": invitations, "venueid": venueid, "pdf_field": pdf_field},
        )
    '''contentvalue'''
    @staticmethod
    def contentvalue(value: Any) -> Any:
        return value.get("value") if isinstance(value, dict) and "value" in value else value
    '''openreviewtimetoiso'''
    @staticmethod
    def openreviewtimetoiso(value: Any) -> Optional[str]:
        if value is None: return None
        try: return datetime.fromtimestamp((v / 1000 if (v := int(value)) > 10_000_000_000 else v), tz=timezone.utc).isoformat()
        except Exception: return str(value)