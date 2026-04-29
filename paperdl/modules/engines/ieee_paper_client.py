from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional, Sequence


class IEEEPaperClient(BasePaperClient):
    """
    Async IEEE Xplore Metadata API client.

    Important:
    - IEEE Xplore Metadata API requires an API key.
    - Metadata search may return records outside your subscription.
    - PDF download depends on accessType, institutional access, cookies,
      and whether IEEE returns a usable pdf_url.
    """

    source = "IEEE Xplore"
    API_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        api_key_env: str = "IEEE_XPLORE_API_KEY",
        timeout: float = 60.0,
        concurrency: int = 5,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
        user_agent: str = "PaperClient/IEEE/0.1",
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        cookie_file: Optional[str | Path] = None,
        proxy: Optional[str] = None,
        thread_workers: int = 4,
        show_progress: bool = True,
        progress_mode: str = "auto",
        max_detail_tasks: int = 20,
        verbose: bool = True,
        use_stamp_pdf_fallback: bool = False,
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

        self.api_key = api_key or os.getenv(api_key_env)
        self.use_stamp_pdf_fallback = use_stamp_pdf_fallback

    async def search(
        self,
        query: Optional[str] = None,
        *,
        max_results: int = 25,
        start_record: int = 1,
        article_title: Optional[str] = None,
        abstract: Optional[str] = None,
        author: Optional[str] = None,
        publication_title: Optional[str] = None,
        publication_year: Optional[int | str] = None,
        content_type: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        open_access_only: bool = False,
        extra_params: Optional[dict[str, Any]] = None,
    ) -> list["PaperInfo"]:
        """
        Search one page from IEEE Xplore Metadata API.

        Common examples:

            await client.search("medical imaging", max_results=20)

            await client.search(
                article_title="foundation model",
                publication_year=2024,
                max_results=50,
            )

        IEEE API max_records is commonly limited to 200 per page.
        """
        self._require_api_key()

        if max_results <= 0:
            return []

        params = self._build_search_params(
            query=query,
            max_results=max_results,
            start_record=start_record,
            article_title=article_title,
            abstract=abstract,
            author=author,
            publication_title=publication_title,
            publication_year=publication_year,
            content_type=content_type,
            sort_field=sort_field,
            sort_order=sort_order,
            extra_params=extra_params,
        )

        data = await self.request_json(
            self.API_URL,
            params=params,
            progress_description=f"Searching IEEE Xplore: {(query or article_title or publication_title or '')[:60]}",
        )

        articles = data.get("articles") or []

        papers = [
            self._article_to_paper(
                article,
                query=query or article_title or abstract or publication_title,
                rank=start_record + idx,
            )
            for idx, article in enumerate(articles)
        ]

        if open_access_only:
            papers = [
                p for p in papers
                if str(p.extra.get("access_type", "")).lower() == "open access"
                or p.is_open_access is True
            ]

        self.log(f"IEEE search finished. Found {len(papers)} papers in this page.")
        return papers

    async def search_all(
        self,
        query: Optional[str] = None,
        *,
        total_results: int = 200,
        page_size: int = 100,
        article_title: Optional[str] = None,
        abstract: Optional[str] = None,
        author: Optional[str] = None,
        publication_title: Optional[str] = None,
        publication_year: Optional[int | str] = None,
        content_type: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        open_access_only: bool = False,
        deduplicate: bool = True,
        extra_params: Optional[dict[str, Any]] = None,
    ) -> list["PaperInfo"]:
        """
        Search multiple IEEE pages with progress.
        """
        if total_results <= 0:
            return []

        page_size = max(1, min(page_size, 200))
        total_pages = (total_results + page_size - 1) // page_size

        papers: list[PaperInfo] = []

        task_id = self._add_task(
            f"Searching IEEE Xplore: {(query or article_title or publication_title or '')[:60]}",
            total=total_pages,
        )

        for page_idx in range(total_pages):
            start_record = page_idx * page_size + 1
            current_size = min(page_size, total_results - page_idx * page_size)

            self._update_task(
                task_id,
                description=f"Searching IEEE page {page_idx + 1}/{total_pages}",
            )

            page = await self.search(
                query=query,
                max_results=current_size,
                start_record=start_record,
                article_title=article_title,
                abstract=abstract,
                author=author,
                publication_title=publication_title,
                publication_year=publication_year,
                content_type=content_type,
                sort_field=sort_field,
                sort_order=sort_order,
                open_access_only=open_access_only,
                extra_params=extra_params,
            )

            papers.extend(page)
            self._update_task(task_id, advance=1)

            if len(page) < current_size:
                break

        if deduplicate:
            papers = list({p.identity_key: p for p in papers}.values())

        self._update_task(
            task_id,
            completed=total_pages,
            description=f"Finished IEEE search: {len(papers)} papers found",
        )

        if self.progress_mode != "detailed":
            self._remove_task(task_id)

        return papers

    async def get_by_article_number(self, article_number: str | int) -> Optional["PaperInfo"]:
        """
        Fetch a paper by IEEE article_number.
        """
        papers = await self.search(
            max_results=1,
            extra_params={
                "article_number": str(article_number),
            },
        )

        return papers[0] if papers else None

    async def download_paper(
        self,
        paper: "PaperInfo",
        output_dir: str | Path = "papers",
        *,
        overwrite: bool = False,
        show_detail: bool = True,
    ) -> Path:
        """
        Download IEEE PDF if a usable PDF URL is available.

        By default, this method only uses paper.download_url.
        If `use_stamp_pdf_fallback=True`, it tries IEEE's web PDF endpoint:
            https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=<article_number>

        This fallback may require cookies, institutional access, or login.
        """
        url = paper.download_url

        if not url and self.use_stamp_pdf_fallback and paper.source_id:
            url = self._stamp_pdf_url(paper.source_id)

        if not url:
            raise PaperDownloadError(
                "No IEEE PDF URL is available. The paper may be locked, "
                "or the Metadata API did not return pdf_url. "
                "Try `use_stamp_pdf_fallback=True` with valid cookies or institutional access."
            )

        path = Path(output_dir) / paper.filename(suffix=".pdf")

        return await self.download_url(
            url,
            path,
            overwrite=overwrite,
            progress_description=f"Downloading IEEE PDF: {paper.title[:70]}",
            show_detail=show_detail,
        )

    def _require_api_key(self) -> None:
        if not self.api_key:
            raise ValueError(
                "IEEE Xplore API key is required. Pass `api_key=...` "
                "or set environment variable IEEE_XPLORE_API_KEY."
            )

    def _build_search_params(
        self,
        *,
        query: Optional[str],
        max_results: int,
        start_record: int,
        article_title: Optional[str],
        abstract: Optional[str],
        author: Optional[str],
        publication_title: Optional[str],
        publication_year: Optional[int | str],
        content_type: Optional[str],
        sort_field: Optional[str],
        sort_order: Optional[str],
        extra_params: Optional[dict[str, Any]],
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "apikey": self.api_key,
            "format": "json",
            "max_records": min(int(max_results), 200),
            "start_record": int(start_record),
        }

        if query:
            params["querytext"] = query
        if article_title:
            params["article_title"] = article_title
        if abstract:
            params["abstract"] = abstract
        if author:
            params["author"] = author
        if publication_title:
            params["publication_title"] = publication_title
        if publication_year:
            params["publication_year"] = str(publication_year)
        if content_type:
            params["content_type"] = content_type
        if sort_field:
            params["sort_field"] = sort_field
        if sort_order:
            params["sort_order"] = sort_order

        if extra_params:
            params.update(extra_params)

        return params

    def _article_to_paper(
        self,
        article: dict[str, Any],
        *,
        query: Optional[str] = None,
        rank: Optional[int] = None,
    ) -> "PaperInfo":
        """
        Convert IEEE API article metadata into PaperInfo.
        """
        article_number = article.get("article_number")
        access_type = article.get("accessType") or article.get("access_type")

        article_url = (
            article.get("html_url")
            or article.get("abstract_url")
            or self._document_url(article_number)
        )

        download_url = article.get("pdf_url")

        authors = self._parse_ieee_authors(article.get("authors"))
        keywords = self._parse_ieee_keywords(article)

        publication_title = article.get("publication_title")
        publication_date = article.get("publication_date") or article.get("publication_year")
        publisher = article.get("publisher") or "IEEE"

        citation_count = article.get("citing_paper_count")

        content_type = article.get("content_type")
        categories = [x for x in [content_type, publication_title] if x]

        return PaperInfo(
            source=self.source,
            title=article.get("title") or "Untitled",
            abstract=article.get("abstract"),
            authors=authors,
            article_url=article_url,
            download_url=download_url,
            doi=article.get("doi"),
            venue=publication_title,
            publisher=publisher,
            published_at=publication_date,
            updated_at=article.get("insert_date"),
            source_id=str(article_number) if article_number else None,
            query=query,
            rank=article.get("rank") or rank,
            score=None,
            keywords=keywords,
            categories=categories,
            tags=["ieee"],
            citation_count=citation_count,
            is_open_access=str(access_type).lower() == "open access",
            extra={
                "article_number": article_number,
                "access_type": access_type,
                "html_url": article.get("html_url"),
                "abstract_url": article.get("abstract_url"),
                "pdf_url": article.get("pdf_url"),
                "publication_number": article.get("publication_number"),
                "publication_year": article.get("publication_year"),
                "conference_dates": article.get("conference_dates"),
                "conference_location": article.get("conference_location"),
                "volume": article.get("volume"),
                "issue": article.get("issue"),
                "start_page": article.get("start_page"),
                "end_page": article.get("end_page"),
                "isbn": article.get("isbn"),
                "issn": article.get("issn"),
                "raw": article,
            },
        )

    @staticmethod
    def _parse_ieee_authors(value: Any) -> list[str]:
        """
        IEEE authors may appear as:
        - {"authors": [{"full_name": "..."}]}
        - [{"full_name": "..."}]
        - string
        """
        if not value:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, dict):
            value = value.get("authors") or value.get("author") or []

        authors = []

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    name = (
                        item.get("full_name")
                        or item.get("name")
                        or item.get("preferred_name")
                    )
                    if name:
                        authors.append(name)
                elif item:
                    authors.append(str(item))

        return authors

    @staticmethod
    def _parse_ieee_keywords(article: dict[str, Any]) -> list[str]:
        """
        Extract keywords from IEEE metadata.

        Handles common fields:
        - index_terms
        - author_terms
        - ieee_terms
        """
        results: list[str] = []

        def add_terms(x: Any) -> None:
            if not x:
                return

            if isinstance(x, str):
                results.append(x)
                return

            if isinstance(x, list):
                for item in x:
                    add_terms(item)
                return

            if isinstance(x, dict):
                if "terms" in x:
                    add_terms(x["terms"])
                else:
                    for v in x.values():
                        add_terms(v)

        add_terms(article.get("index_terms"))
        add_terms(article.get("author_terms"))
        add_terms(article.get("ieee_terms"))

        seen = set()
        unique = []

        for item in results:
            item = str(item).strip()
            key = item.lower()

            if item and key not in seen:
                seen.add(key)
                unique.append(item)

        return unique

    @staticmethod
    def _document_url(article_number: Any) -> Optional[str]:
        if not article_number:
            return None
        return f"https://ieeexplore.ieee.org/document/{article_number}"

    @staticmethod
    def _stamp_pdf_url(article_number: Any) -> Optional[str]:
        if not article_number:
            return None
        return f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={article_number}"