'''
Function:
    Implementation of BasePaperClient
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import json
import random
import aiohttp
import asyncio
import aiofiles
from pathlib import Path
from functools import partial
from rich.console import Console
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Sequence, Callable
from ..utils import PaperInfo, PaperRequestError, PaperDownloadError, cookies2dict
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn, TimeElapsedColumn, MofNCompleteColumn


'''BasePaperClient'''
class BasePaperClient(ABC):
    source: str = "BasePaperClient"
    def __init__(
        self,
        *,
        timeout: float = 60.0,
        concurrency: int = 8,
        max_retries: int = 3,
        retry_backoff: float = 1.5,
        retry_statuses: Optional[set[int]] = None,
        user_agent: str = "PaperClient/0.1",
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        cookie_file: Optional[str | Path] = None,
        bearer_token: Optional[str] = None,
        basic_auth: Optional[tuple[str, str] | aiohttp.BasicAuth] = None,
        proxy: Optional[str] = None,
        trust_env: bool = True,
        thread_workers: int = 4,

        # Progress and logging
        show_progress: bool = True,
        progress_mode: str = "auto",  # none / summary / detailed / auto
        max_detail_tasks: int = 20,
        verbose: bool = True,
        progress_transient: bool = False,
    ) -> None:
        self.timeout = timeout
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.retry_statuses = retry_statuses or {429, 500, 502, 503, 504}

        self.user_agent = user_agent
        self.proxy = proxy
        self.trust_env = trust_env
        self.thread_workers = thread_workers

        self.show_progress = show_progress and progress_mode != "none"
        self.progress_mode = progress_mode
        self.max_detail_tasks = max_detail_tasks
        self.verbose = verbose
        self.progress_transient = progress_transient

        self.console = Console() if Console else None
        self._progress: Optional[Progress] = None
        self._progress_started = False

        self.cookie_file = Path(cookie_file) if cookie_file else None
        self.cookie_jar = aiohttp.CookieJar()

        if cookies:
            self.cookie_jar.update_cookies(cookies)

        if self.cookie_file and self.cookie_file.exists():
            self.load_cookies(self.cookie_file)

        self.headers = {
            "User-Agent": user_agent,
            **(headers or {}),
        }

        if bearer_token:
            self.headers["Authorization"] = f"Bearer {bearer_token}"

        if isinstance(basic_auth, tuple):
            self.basic_auth = aiohttp.BasicAuth(*basic_auth)
        else:
            self.basic_auth = basic_auth

        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(concurrency)
        self._executor: Optional[ThreadPoolExecutor] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def open(self) -> None:
        """Open aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers,
                cookie_jar=self.cookie_jar,
                auth=self.basic_auth,
                trust_env=self.trust_env,
            )

    async def close(self) -> None:
        """Close session, thread pool, and progress display."""
        if self.cookie_file:
            self.save_cookies(self.cookie_file)

        if self._session and not self._session.closed:
            await self._session.close()

        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = None

        self._stop_progress()

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Client session is not open. Use `async with client:` "
                "or call `await client.open()` first."
            )
        return self._session

    # ------------------------------------------------------------------
    # Progress and logging
    # ------------------------------------------------------------------

    def log(self, message: str) -> None:
        """Print a status message if verbose=True."""
        if not self.verbose:
            return

        if self.console:
            self.console.log(message)
        else:
            print(message)

    def _ensure_progress(self) -> Optional[Progress]:
        """Create and start rich progress lazily."""
        if not self.show_progress or Progress is None:
            return None

        if self._progress is None:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                console=self.console,
                transient=self.progress_transient,
            )

        if not self._progress_started:
            self._progress.start()
            self._progress_started = True

        return self._progress

    def _stop_progress(self) -> None:
        """Stop rich progress safely."""
        if self._progress and self._progress_started:
            self._progress.stop()

        self._progress = None
        self._progress_started = False

    def _add_task(
        self,
        description: str,
        *,
        total: Optional[float] = None,
        visible: bool = True,
    ) -> Optional[int]:
        progress = self._ensure_progress()

        if progress is None:
            return None

        return progress.add_task(
            description,
            total=total,
            visible=visible,
        )

    def _update_task(
        self,
        task_id: Optional[int],
        *,
        advance: Optional[float] = None,
        completed: Optional[float] = None,
        total: Optional[float] = None,
        description: Optional[str] = None,
        visible: Optional[bool] = None,
    ) -> None:
        if task_id is None or self._progress is None:
            return

        kwargs = {}

        if advance is not None:
            kwargs["advance"] = advance
        if completed is not None:
            kwargs["completed"] = completed
        if total is not None:
            kwargs["total"] = total
        if description is not None:
            kwargs["description"] = description
        if visible is not None:
            kwargs["visible"] = visible

        self._progress.update(task_id, **kwargs)

    def _remove_task(self, task_id: Optional[int]) -> None:
        if task_id is None or self._progress is None:
            return

        try:
            self._progress.remove_task(task_id)
        except Exception:
            pass

    def _should_show_detail_tasks(self, n_items: int) -> bool:
        if not self.show_progress:
            return False

        if self.progress_mode == "detailed":
            return True

        if self.progress_mode == "summary":
            return False

        return n_items <= self.max_detail_tasks

    # ------------------------------------------------------------------
    # Cookie/header/account utilities
    # ------------------------------------------------------------------

    def set_header(self, key: str, value: str) -> None:
        self.headers[key] = value

        if self._session and not self._session.closed:
            self._session.headers[key] = value

    def set_bearer_token(self, token: str) -> None:
        self.set_header("Authorization", f"Bearer {token}")

    def update_cookies(self, cookies: dict[str, str]) -> None:
        self.cookie_jar.update_cookies(cookies)

    def export_cookies(self, url: Optional[str] = None) -> dict[str, str]:
        if url:
            cookies = self.cookie_jar.filter_cookies(url)
            return {k: v.value for k, v in cookies.items()}

        return {
            cookie.key: cookie.value
            for cookie in self.cookie_jar
        }

    def save_cookies(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.export_cookies(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_cookies(self, path: str | Path) -> None:
        path = Path(path)

        if not path.exists():
            return

        data = json.loads(path.read_text(encoding="utf-8"))

        if isinstance(data, dict):
            self.cookie_jar.update_cookies(data)

    async def login(self, *args, **kwargs) -> None:
        """
        Optional login hook.

        Subclasses can override this method for platforms that require login.
        """
        return None

    # ------------------------------------------------------------------
    # Thread pool support
    # ------------------------------------------------------------------

    @property
    def executor(self) -> ThreadPoolExecutor:
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.thread_workers)
        return self._executor

    async def run_blocking(
        self,
        func: Callable,
        *args,
        progress_description: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """
        Run blocking code in a thread pool.

        Useful for:
        - feedparser.parse
        - BeautifulSoup parsing for large HTML
        - legacy synchronous libraries
        """
        task_id = None

        if progress_description:
            task_id = self._add_task(progress_description, total=None)

        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                self.executor,
                partial(func, *args, **kwargs),
            )
        finally:
            self._remove_task(task_id)

    # ------------------------------------------------------------------
    # HTTP request utilities
    # ------------------------------------------------------------------

    async def request_bytes(
        self,
        url: str,
        *,
        method: str = "GET",
        params: Optional[dict[str, Any]] = None,
        data: Any = None,
        json_data: Any = None,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        auth: Optional[aiohttp.BasicAuth] = None,
        proxy: Optional[str] = None,
        allow_statuses: Optional[set[int]] = None,
        progress_description: Optional[str] = None,
    ) -> bytes:
        """
        Send an HTTP request and return raw bytes.

        Includes retry, concurrency control, and optional spinner progress.
        """
        await self.open()

        last_error: Optional[BaseException] = None
        allow_statuses = allow_statuses or set()
        task_id = None

        if progress_description:
            task_id = self._add_task(progress_description, total=None)

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    if attempt > 0 and task_id is not None:
                        self._update_task(
                            task_id,
                            description=f"{progress_description} | retry {attempt}/{self.max_retries}",
                        )

                    async with self._semaphore:
                        async with self.session.request(
                            method,
                            url,
                            params=params,
                            data=data,
                            json=json_data,
                            headers=headers,
                            cookies=cookies,
                            auth=auth,
                            proxy=proxy or self.proxy,
                        ) as resp:
                            content = await resp.read()

                            if resp.status in allow_statuses:
                                return content

                            if resp.status in self.retry_statuses:
                                raise PaperRequestError(
                                    f"Temporary HTTP {resp.status}: {content[:300]!r}"
                                )

                            if resp.status >= 400:
                                raise PaperRequestError(
                                    f"HTTP {resp.status}: {content[:300]!r}"
                                )

                            return content

                except (aiohttp.ClientError, asyncio.TimeoutError, PaperRequestError) as e:
                    last_error = e

                    if attempt >= self.max_retries:
                        break

                    sleep_time = self.retry_backoff * (2 ** attempt) + random.random() * 0.2
                    await asyncio.sleep(sleep_time)

            raise PaperRequestError(f"Request failed: {url}") from last_error

        finally:
            self._remove_task(task_id)

    async def request_text(
        self,
        url: str,
        *,
        encoding: str = "utf-8",
        errors: str = "replace",
        **kwargs,
    ) -> str:
        content = await self.request_bytes(url, **kwargs)
        return content.decode(encoding, errors=errors)

    async def request_json(self, url: str, **kwargs) -> Any:
        text = await self.request_text(url, **kwargs)
        return json.loads(text)

    # ------------------------------------------------------------------
    # Download utilities
    # ------------------------------------------------------------------

    async def download_url(
        self,
        url: str,
        path: str | Path,
        *,
        overwrite: bool = False,
        chunk_size: int = 1024 * 128,
        headers: Optional[dict[str, str]] = None,
        cookies: Optional[dict[str, str]] = None,
        proxy: Optional[str] = None,
        progress_description: Optional[str] = None,
        show_detail: bool = True,
    ) -> Path:
        """
        Stream-download a URL to a local path.

        Features:
        - async streaming
        - retry
        - atomic .part file
        - optional detailed progress bar
        """
        await self.open()

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists() and not overwrite:
            return path

        tmp_path = path.with_suffix(path.suffix + ".part")
        last_error: Optional[BaseException] = None

        task_id = None

        if show_detail:
            task_id = self._add_task(
                progress_description or f"Downloading {path.name}",
                total=None,
            )

        try:
            for attempt in range(self.max_retries + 1):
                try:
                    if attempt > 0 and task_id is not None:
                        self._update_task(
                            task_id,
                            completed=0,
                            description=f"{progress_description or path.name} | retry {attempt}/{self.max_retries}",
                        )

                    async with self._semaphore:
                        async with self.session.get(
                            url,
                            headers=headers,
                            cookies=cookies,
                            proxy=proxy or self.proxy,
                        ) as resp:
                            if resp.status in self.retry_statuses:
                                raise PaperDownloadError(f"Temporary HTTP {resp.status}: {url}")

                            if resp.status >= 400:
                                content = await resp.read()
                                raise PaperDownloadError(
                                    f"HTTP {resp.status}: {content[:300]!r}"
                                )

                            total = resp.content_length

                            if task_id is not None:
                                self._update_task(task_id, total=total)

                            downloaded = 0

                            async with aiofiles.open(tmp_path, "wb") as f:
                                async for chunk in resp.content.iter_chunked(chunk_size):
                                    if not chunk:
                                        continue

                                    await f.write(chunk)
                                    downloaded += len(chunk)

                                    if task_id is not None:
                                        self._update_task(
                                            task_id,
                                            advance=len(chunk),
                                        )

                    tmp_path.replace(path)

                    if task_id is not None:
                        self._update_task(
                            task_id,
                            completed=total or downloaded,
                            description=f"Downloaded {path.name}",
                        )

                    return path

                except (aiohttp.ClientError, asyncio.TimeoutError, PaperDownloadError) as e:
                    last_error = e

                    if tmp_path.exists():
                        tmp_path.unlink(missing_ok=True)

                    if attempt >= self.max_retries:
                        break

                    sleep_time = self.retry_backoff * (2 ** attempt) + random.random() * 0.2
                    await asyncio.sleep(sleep_time)

            raise PaperDownloadError(f"Download failed: {url}") from last_error

        finally:
            if task_id is not None and self.progress_mode != "detailed":
                self._remove_task(task_id)

    async def download_many(
        self,
        papers: Sequence["PaperInfo"],
        output_dir: str | Path = "papers",
        *,
        overwrite: bool = False,
        return_exceptions: bool = False,
    ) -> list[Path]:
        """
        Download many papers concurrently.

        Shows:
        - a global progress bar for total downloaded papers
        - detailed per-file progress bars if the number of papers is small
        """
        papers = list(papers)

        if not papers:
            return []

        show_detail = self._should_show_detail_tasks(len(papers))

        master_task = self._add_task(
            f"Downloading papers from {self.source}",
            total=len(papers),
        )

        self.log(
            f"Start downloading {len(papers)} papers from {self.source} "
            f"with concurrency={self.concurrency}."
        )

        async def _download_one(paper: "PaperInfo") -> Path:
            try:
                return await self.download_paper(
                    paper,
                    output_dir=output_dir,
                    overwrite=overwrite,
                    show_detail=show_detail,
                )
            finally:
                self._update_task(master_task, advance=1)

        tasks = [_download_one(paper) for paper in papers]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=return_exceptions,
        )

        self._update_task(
            master_task,
            completed=len(papers),
            description=f"Finished downloading papers from {self.source}",
        )

        if self.progress_mode != "detailed":
            self._remove_task(master_task)

        return results

    # ------------------------------------------------------------------
    # Abstract methods
    # ------------------------------------------------------------------

    @abstractmethod
    async def search(self, *args, **kwargs) -> list["PaperInfo"]:
        """Search papers and return PaperInfo objects."""

    @abstractmethod
    async def download_paper(
        self,
        paper: "PaperInfo",
        output_dir: str | Path = "papers",
        *,
        overwrite: bool = False,
        show_detail: bool = True,
    ) -> Path:
        """Download one paper and return local file path."""