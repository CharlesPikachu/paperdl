import asyncio
import re
from pathlib import Path
from typing import Any, Optional, Sequence

import feedparser


class ArxivPaperClient(BasePaperClient):
    """
    Async arXiv client with search, parsing, download, and progress display.
    """

    source = "arXiv"
    API_URL = "https://export.arxiv.org/api/query"

    VALID_SORT_BY = {
        "relevance",
        "lastUpdatedDate",
        "submittedDate",
    }

    VALID_SORT_ORDER = {
        "ascending",
        "descending",
    }

    def __init__(
        self,
        *,
        api_delay: float = 3.0,
        timeout: float = 60.0,
        concurrency: int = 5,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
        user_agent: str = "PaperClient/arXiv/0.1",
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
        super().__init__(
            timeout=timeout,
            concurrency=concurrency,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            user_agent=user_agent,
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
        self.api_delay = api_delay

    async def search(
        self,
        query: str,
        *,
        max_results: int = 20,
        start: int = 0,
        categories: Optional[Sequence[str]] = None,
        search_field: str = "all",
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
        raw_query: bool = False,
        show_progress: bool = False,
    ) -> list["PaperInfo"]:
        """
        Search one page of arXiv papers.
        """
        if sort_by not in self.VALID_SORT_BY:
            raise ValueError(f"Invalid sort_by: {sort_by}")

        if sort_order not in self.VALID_SORT_ORDER:
            raise ValueError(f"Invalid sort_order: {sort_order}")

        if max_results <= 0:
            return []

        search_query = query if raw_query else self._build_query(
            query=query,
            categories=categories,
            search_field=search_field,
        )

        params = {
            "search_query": search_query,
            "start": int(start),
            "max_results": int(max_results),
            "sortBy": sort_by,
            "sortOrder": sort_order,
        }

        xml = await self.request_text(
            self.API_URL,
            params=params,
            progress_description=(
                f"Searching arXiv: {query[:60]}"
                if show_progress
                else None
            ),
        )

        return await self._parse_feed(xml, query=search_query, start=start)

    async def search_all(
        self,
        query: str,
        *,
        total_results: int = 100,
        page_size: int = 50,
        categories: Optional[Sequence[str]] = None,
        search_field: str = "all",
        sort_by: str = "submittedDate",
        sort_order: str = "descending",
        raw_query: bool = False,
        deduplicate: bool = True,
    ) -> list["PaperInfo"]:
        """
        Search multiple pages with progress display.
        """
        if total_results <= 0:
            return []

        page_size = max(1, min(page_size, total_results))
        total_pages = (total_results + page_size - 1) // page_size

        papers: list[PaperInfo] = []

        search_task = self._add_task(
            f"Searching arXiv: {query[:60]}",
            total=total_pages,
        )

        self.log(
            f"Start searching arXiv: query={query!r}, "
            f"total_results={total_results}, page_size={page_size}."
        )

        for page_idx, start in enumerate(range(0, total_results, page_size), start=1):
            current_size = min(page_size, total_results - start)

            if start > 0 and self.api_delay > 0:
                await asyncio.sleep(self.api_delay)

            self._update_task(
                search_task,
                description=f"Searching arXiv page {page_idx}/{total_pages}: {query[:50]}",
            )

            page = await self.search(
                query=query,
                max_results=current_size,
                start=start,
                categories=categories,
                search_field=search_field,
                sort_by=sort_by,
                sort_order=sort_order,
                raw_query=raw_query,
                show_progress=False,
            )

            papers.extend(page)

            self._update_task(search_task, advance=1)

            if len(page) < current_size:
                break

        if deduplicate:
            papers = list({p.identity_key: p for p in papers}.values())

        self._update_task(
            search_task,
            completed=total_pages,
            description=f"Finished arXiv search: {len(papers)} papers found",
        )

        if self.progress_mode != "detailed":
            self._remove_task(search_task)

        self.log(f"Finished arXiv search. Found {len(papers)} papers.")

        return papers

    async def get_by_id(self, arxiv_id: str) -> Optional["PaperInfo"]:
        papers = await self.search_by_ids([arxiv_id])
        return papers[0] if papers else None

    async def search_by_ids(self, arxiv_ids: Sequence[str]) -> list["PaperInfo"]:
        ids = [self._clean_arxiv_id(x) for x in arxiv_ids if x]
        ids = [x for x in ids if x]

        if not ids:
            return []

        params = {
            "id_list": ",".join(ids),
            "max_results": len(ids),
        }

        xml = await self.request_text(
            self.API_URL,
            params=params,
            progress_description=f"Fetching {len(ids)} arXiv IDs",
        )

        return await self._parse_feed(
            xml,
            query=f"id_list:{','.join(ids)}",
            start=0,
        )

    async def download_paper(
        self,
        paper: "PaperInfo",
        output_dir: str | Path = "papers",
        *,
        overwrite: bool = False,
        show_detail: bool = True,
    ) -> Path:
        """
        Download one arXiv PDF with optional progress display.
        """
        url = paper.download_url or self._pdf_url_from_arxiv_id(paper.arxiv_id)

        if not url:
            raise PaperDownloadError(f"No download URL available for: {paper.title}")

        path = Path(output_dir) / paper.filename(suffix=".pdf")

        short_title = paper.title
        if len(short_title) > 70:
            short_title = short_title[:67] + "..."

        return await self.download_url(
            url,
            path,
            overwrite=overwrite,
            progress_description=f"Downloading: {short_title}",
            show_detail=show_detail,
        )

    # ------------------------------------------------------------------
    # arXiv-specific helpers
    # ------------------------------------------------------------------

    def _build_query(
        self,
        *,
        query: str,
        categories: Optional[Sequence[str]] = None,
        search_field: str = "all",
    ) -> str:
        query = (query or "").strip()
        categories = [c.strip() for c in (categories or []) if c and c.strip()]

        parts = []

        if query:
            parts.append(f'{search_field}:"{query}"')

        if categories:
            cat_query = " OR ".join(f"cat:{c}" for c in categories)
            parts.append(f"({cat_query})")

        if not parts:
            raise ValueError("Either query or categories must be provided.")

        return " AND ".join(parts)

    async def _parse_feed(
        self,
        xml: str,
        *,
        query: Optional[str] = None,
        start: int = 0,
    ) -> list["PaperInfo"]:
        feed = await self.run_blocking(
            feedparser.parse,
            xml,
            progress_description=None,
        )

        if getattr(feed, "bozo", False) and not feed.entries:
            raise PaperRequestError(f"Failed to parse arXiv feed: {feed.bozo_exception}")

        papers: list[PaperInfo] = []

        for idx, entry in enumerate(feed.entries):
            if str(entry.get("title", "")).lower() == "error":
                continue

            papers.append(
                self._entry_to_paper(
                    entry,
                    query=query,
                    rank=start + idx + 1,
                )
            )

        return papers

    def _entry_to_paper(
        self,
        entry: Any,
        *,
        query: Optional[str] = None,
        rank: Optional[int] = None,
    ) -> "PaperInfo":
        article_url = self._extract_article_url(entry)
        download_url = self._extract_pdf_url(entry)
        arxiv_id = self._extract_arxiv_id(entry.get("id") or article_url)

        authors = [
            a.get("name")
            for a in entry.get("authors", [])
            if isinstance(a, dict) and a.get("name")
        ]

        categories = [
            t.get("term")
            for t in entry.get("tags", [])
            if isinstance(t, dict) and t.get("term")
        ]

        primary_category = self._extract_primary_category(entry)

        if primary_category and primary_category not in categories:
            categories.insert(0, primary_category)

        doi = (
            entry.get("arxiv_doi")
            or entry.get("doi")
            or self._extract_doi_from_links(entry)
        )

        journal_ref = entry.get("arxiv_journal_ref")
        comment = entry.get("arxiv_comment")

        return PaperInfo(
            source=self.source,
            title=entry.get("title") or "Untitled",
            abstract=entry.get("summary"),
            authors=authors,
            article_url=article_url,
            download_url=download_url,
            doi=doi,
            arxiv_id=arxiv_id,
            venue=journal_ref,
            publisher="arXiv",
            published_at=entry.get("published"),
            updated_at=entry.get("updated"),
            source_id=entry.get("id"),
            query=query,
            rank=rank,
            categories=categories,
            tags=["arxiv"],
            is_open_access=True,
            extra={
                "primary_category": primary_category,
                "comment": comment,
                "journal_ref": journal_ref,
                "raw_id": entry.get("id"),
            },
        )

    @staticmethod
    def _extract_article_url(entry: Any) -> Optional[str]:
        for link in entry.get("links", []):
            if link.get("rel") == "alternate":
                return link.get("href")

        return entry.get("id")

    @staticmethod
    def _extract_pdf_url(entry: Any) -> Optional[str]:
        for link in entry.get("links", []):
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                return link.get("href")

        arxiv_id = ArxivPaperClient._extract_arxiv_id(entry.get("id"))
        return ArxivPaperClient._pdf_url_from_arxiv_id(arxiv_id)

    @staticmethod
    def _extract_doi_from_links(entry: Any) -> Optional[str]:
        for link in entry.get("links", []):
            href = link.get("href", "")
            if "doi.org/" in href:
                return href.rstrip("/").split("doi.org/")[-1]
        return None

    @staticmethod
    def _extract_primary_category(entry: Any) -> Optional[str]:
        primary = entry.get("arxiv_primary_category")

        if isinstance(primary, dict):
            return primary.get("term")

        return None

    @staticmethod
    def _extract_arxiv_id(value: Optional[str]) -> Optional[str]:
        if not value:
            return None

        text = str(value).strip()

        if "/abs/" in text:
            text = text.split("/abs/", 1)[-1]
        elif "/pdf/" in text:
            text = text.split("/pdf/", 1)[-1]

        text = text.replace(".pdf", "").strip("/")

        new_style = re.search(r"(\d{4}\.\d{4,5})(?:v\d+)?", text)
        if new_style:
            return new_style.group(1)

        old_style = re.search(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", text)
        if old_style:
            return old_style.group(1)

        return text or None

    @staticmethod
    def _clean_arxiv_id(value: str) -> str:
        return ArxivPaperClient._extract_arxiv_id(value) or str(value).strip()

    @staticmethod
    def _pdf_url_from_arxiv_id(arxiv_id: Optional[str]) -> Optional[str]:
        if not arxiv_id:
            return None

        return f"https://arxiv.org/pdf/{arxiv_id}"