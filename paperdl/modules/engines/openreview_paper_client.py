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
from .base_paper_client import BasePaperClient
from ..utils import PaperInfo, PaperDownloadError


'''OpenReviewPaperClient'''
class OpenReviewPaperClient(BasePaperClient):
    source = "OpenReviewPaperClient"
    def __init__(self, *, baseurl: str = "https://api2.openreview.net", username: Optional[str] = None, password: Optional[str] = None,
        api_version: int = 2,
        timeout: float = 60.0,
        concurrency: int = 5,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        cookie_file: Optional[str | Path] = None,
        proxy: Optional[str] = None,
        thread_workers: int = 4,
        show_progress: bool = True,
        progress_mode: str = "auto",
        max_detail_tasks: int = 20,
        verbose: bool = True,
    ) -> None:
        super(OpenReviewPaperClient, self).__init__(
            timeout=timeout,
            concurrency=concurrency,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            headers=headers,
            cookies=cookies,
            cookie_file=cookie_file,
            proxy=proxy,
            thread_workers=thread_workers,
            show_progress=show_progress,
            progress_mode=progress_mode,
            max_detail_tasks=max_detail_tasks,
            verbose=verbose,
        )

        self.baseurl = baseurl
        self.username = username
        self.password = password
        self.api_version = api_version
        self._or_client: Any = None

    async def open(self) -> None:
        """
        Open aiohttp session and initialize the official OpenReview client.
        """
        await super().open()

        if self._or_client is None:
            self._or_client = await self.runblocking(
                self._create_openreview_client,
                progress_description="Initializing OpenReview client",
            )

    def _create_openreview_client(self) -> Any:
        """
        Create official openreview-py client.

        API v2 is used by most current venues. API v1 is retained for old venues.
        """
        try:
            import openreview
        except ImportError as e:
            raise ImportError(
                "Please install OpenReview client first: pip install openreview-py"
            ) from e

        kwargs = {"baseurl": self.baseurl}

        if self.username and self.password:
            kwargs["username"] = self.username
            kwargs["password"] = self.password

        if self.api_version == 2:
            return openreview.api.OpenReviewClient(**kwargs)

        return openreview.Client(**kwargs)

    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Reinitialize OpenReview client with username/password.

        You can either pass username/password here or provide them in __init__.
        """
        if username:
            self.username = username
        if password:
            self.password = password

        self._or_client = await self.run_blocking(
            self._create_openreview_client,
            progress_description="Logging in to OpenReview",
        )

    async def search(
        self,
        query: Optional[str] = None,
        *,
        venue_id: Optional[str] = None,
        invitation: Optional[str] = None,
        content: Optional[dict[str, Any]] = None,
        details: Optional[str] = None,
        max_results: int = 100,
        accepted_only: bool = False,
        client_side_filter: bool = True,
    ) -> list["PaperInfo"]:
        """
        Search OpenReview papers.

        Recommended patterns:

        1. Search by venue:
            await client.search(
                query="diffusion",
                venue_id="ICLR.cc/2024/Conference",
                max_results=100,
            )

        2. Search by invitation:
            await client.search(
                invitation="ICLR.cc/2024/Conference/-/Submission",
                max_results=100,
            )

        Notes:
        - OpenReview is invitation/venue-centric rather than a general Google-like
          full-text search engine.
        - Therefore this method retrieves notes from a venue/invitation first,
          then optionally applies client-side keyword filtering.
        """
        await self.open()

        if max_results <= 0:
            return []

        if not invitation and venue_id:
            invitation = await self._infer_submission_invitation(venue_id)

        if accepted_only and venue_id:
            content = {
                **(content or {}),
                "venueid": venue_id,
            }

        if not invitation and not content:
            raise ValueError(
                "OpenReview search requires either `venue_id`, `invitation`, "
                "or a `content` filter. For example: "
                "venue_id='ICLR.cc/2024/Conference'."
            )

        task_id = self._add_task(
            f"Fetching OpenReview notes: {(venue_id or invitation or 'content filter')}",
            total=None,
        )

        try:
            notes = await self._get_all_notes(
                invitation=invitation,
                content=content,
                details=details,
            )
        finally:
            self._remove_task(task_id)

        papers = [
            self._note_to_paper(note, query=query, rank=i + 1)
            for i, note in enumerate(notes)
        ]

        if query and client_side_filter:
            q = query.lower().strip()
            papers = [
                p for p in papers
                if q in " ".join([
                    p.title or "",
                    p.abstract or "",
                    " ".join(p.authors),
                    " ".join(p.keywords),
                    " ".join(p.categories),
                    " ".join(p.tags),
                ]).lower()
            ]

        papers = papers[:max_results]

        self.log(f"OpenReview search finished. Found {len(papers)} papers.")
        return papers

    async def _infer_submission_invitation(self, venue_id: str) -> str:
        """
        Infer the submission invitation from a venue group.

        For API v2 venues, venue group content usually contains submission_name.
        """
        await self.open()

        def _get_group():
            return self._or_client.get_group(venue_id)

        group = await self.run_blocking(
            _get_group,
            progress_description=f"Loading OpenReview venue group: {venue_id}",
        )

        group_content = getattr(group, "content", {}) or {}
        submission_name = self._content_value(group_content.get("submission_name"))

        if not submission_name:
            submission_name = "Submission"

        return f"{venue_id}/-/{submission_name}"

    async def _get_all_notes(
        self,
        *,
        invitation: Optional[str] = None,
        content: Optional[dict[str, Any]] = None,
        details: Optional[str] = None,
    ) -> list[Any]:
        """
        Call official openreview-py get_all_notes() in a thread.
        """
        await self.open()

        kwargs = {}

        if invitation:
            kwargs["invitation"] = invitation
        if content:
            kwargs["content"] = content
        if details:
            kwargs["details"] = details

        return await self.run_blocking(
            self._or_client.get_all_notes,
            **kwargs,
        )

    async def download_paper(
        self,
        paper: "PaperInfo",
        output_dir: str | Path = "papers",
        *,
        overwrite: bool = False,
        show_detail: bool = True,
        prefer_attachment_api: bool = False,
        fallback_to_attachment_api: bool = True,
    ) -> Path:
        """
        Download an OpenReview PDF.

        Strategy:
        1. If prefer_attachment_api=True, use official get_attachment().
        2. Otherwise, try public PDF URL first:
              https://openreview.net/pdf?id=<note_id>
        3. If URL download fails and fallback_to_attachment_api=True,
           use official get_attachment().
        """
        note_id = (
            paper.source_id
            or paper.extra.get("note_id")
            or paper.extra.get("forum")
        )

        if not note_id:
            raise PaperDownloadError(f"No OpenReview note id available for: {paper.title}")

        path = Path(output_dir) / paper.filename(suffix=".pdf")

        if path.exists() and not overwrite:
            return path

        if prefer_attachment_api:
            return await self._download_by_attachment_api(
                note_id,
                path,
                overwrite=overwrite,
                show_detail=show_detail,
            )

        url = paper.download_url or f"https://openreview.net/pdf?id={note_id}"

        try:
            return await self.download_url(
                url,
                path,
                overwrite=overwrite,
                progress_description=f"Downloading OpenReview PDF: {paper.title[:70]}",
                show_detail=show_detail,
            )
        except Exception:
            if not fallback_to_attachment_api:
                raise

            return await self._download_by_attachment_api(
                note_id,
                path,
                overwrite=overwrite,
                show_detail=show_detail,
            )

    async def _download_by_attachment_api(
        self,
        note_id: str,
        path: str | Path,
        *,
        overwrite: bool = False,
        show_detail: bool = True,
    ) -> Path:
        """
        Download PDF using official openreview-py get_attachment().
        This is useful for private or credential-protected submissions.
        """
        await self.open()

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not overwrite:
            return path

        task_id = None
        if show_detail:
            task_id = self._add_task(
                f"Downloading OpenReview attachment: {path.name}",
                total=None,
            )

        try:
            pdf_bytes = await self.run_blocking(
                self._or_client.get_attachment,
                field_name="pdf",
                id=note_id,
            )

            tmp_path = path.with_suffix(path.suffix + ".part")

            async with aiofiles.open(tmp_path, "wb") as f:
                await f.write(pdf_bytes)

            tmp_path.replace(path)
            return path

        finally:
            self._remove_task(task_id)

    def _note_to_paper(
        self,
        note: Any,
        *,
        query: Optional[str] = None,
        rank: Optional[int] = None,
    ) -> "PaperInfo":
        """
        Convert an OpenReview note into PaperInfo.
        """
        content = getattr(note, "content", {}) or {}

        note_id = getattr(note, "id", None)
        forum = getattr(note, "forum", None)
        number = getattr(note, "number", None)
        invitations = getattr(note, "invitations", None) or []

        title = self._content_value(content.get("title")) or "Untitled"
        abstract = self._content_value(content.get("abstract"))
        authors = self._content_value(content.get("authors")) or []
        keywords = self._content_value(content.get("keywords")) or []
        venueid = self._content_value(content.get("venueid"))
        pdf_field = self._content_value(content.get("pdf"))

        if isinstance(authors, str):
            authors = [authors]

        if isinstance(keywords, str):
            keywords = [keywords]

        paper_url = f"https://openreview.net/forum?id={forum or note_id}" if (forum or note_id) else None
        pdf_url = f"https://openreview.net/pdf?id={note_id}" if note_id else None

        return PaperInfo(
            source=self.source,
            title=title,
            abstract=abstract,
            authors=authors,
            article_url=paper_url,
            download_url=pdf_url,
            source_id=note_id,
            query=query,
            rank=rank,
            venue=venueid,
            publisher="OpenReview",
            published_at=self._openreview_time_to_iso(getattr(note, "cdate", None)),
            updated_at=self._openreview_time_to_iso(getattr(note, "mdate", None)),
            keywords=keywords,
            categories=[venueid] if venueid else [],
            tags=["openreview"],
            is_open_access=True,
            extra={
                "note_id": note_id,
                "forum": forum,
                "number": number,
                "invitations": invitations,
                "venueid": venueid,
                "pdf_field": pdf_field,
            },
        )

    @staticmethod
    def _content_value(value: Any) -> Any:
        """
        Normalize OpenReview API v2 content field.

        API v2 often stores values as:
            {"value": actual_value}

        API v1 or older records may store values directly.
        """
        if isinstance(value, dict) and "value" in value:
            return value.get("value")
        return value

    @staticmethod
    def _openreview_time_to_iso(value: Any) -> Optional[str]:
        """
        OpenReview timestamps are often milliseconds since epoch.
        """
        if value is None:
            return None

        try:
            from datetime import datetime, timezone

            value = int(value)
            if value > 10_000_000_000:
                value = value / 1000

            return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
        except Exception:
            return str(value)