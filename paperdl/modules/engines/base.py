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
    def __init__(self, *, timeout: float = 60.0, concurrency: int = 8, max_retries: int = 3, retry_backoff: float = 1.5, retry_statuses: Optional[set[int]] = None, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, cookie_file: Optional[str | Path] = None, basic_auth: Optional[tuple[str, str] | aiohttp.BasicAuth] = None, proxy: Optional[str] = None, trust_env: bool = True, thread_workers: int = 4, show_progress: bool = True, progress_mode: str = "auto", max_detail_tasks: int = 20, verbose: bool = True, progress_transient: bool = False) -> None:
        # http request retries settings
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.retry_statuses = retry_statuses or {429, 500, 502, 503, 504}
        # multi threading related settings
        self.concurrency = concurrency
        self.thread_workers = thread_workers
        # cookies related settings
        self.cookie_jar = aiohttp.CookieJar()
        self.cookie_jar.update_cookies(cookies2dict(cookies))
        self.cookie_file = Path(cookie_file) if cookie_file else None
        if self.cookie_file and self.cookie_file.exists(): self.loadcookies(self.cookie_file)
        # progress / logging related settings
        self.verbose = verbose
        self.progress_mode = progress_mode
        self.max_detail_tasks = max_detail_tasks
        self.progress_transient = progress_transient
        self.console = Console() if Console else None
        self.show_progress = show_progress and progress_mode != "none"
        self._progress_started = False
        self._progress: Optional[Progress] = None
        # request headers
        self.headers = headers or {}
        # auth settings
        self.basic_auth = aiohttp.BasicAuth(*basic_auth) if isinstance(basic_auth, tuple) else basic_auth
        # misc settings
        self.proxy = proxy
        self.timeout = timeout
        self.trust_env = trust_env
        # instance some classes
        self._session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(concurrency)
        self._executor: Optional[ThreadPoolExecutor] = None
    '''aenter'''
    async def __aenter__(self):
        await self.open()
        return self
    '''aexit'''
    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
    '''open'''
    async def open(self) -> None:
        if self._session is None or self._session.closed: self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout), headers=self.headers, cookie_jar=self.cookie_jar, auth=self.basic_auth, trust_env=self.trust_env)
    '''close'''
    async def close(self) -> None:
        if self.cookie_file: self.savecookies(self.cookie_file)
        if self._session and not self._session.closed: await self._session.close()
        if self._executor: self._executor.shutdown(wait=False, cancel_futures=True); self._executor = None
        self.stopprogress()
    '''session'''
    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed: raise RuntimeError("Client session is not open. Use `async with client:` or call `await client.open()` first.")
        return self._session
    '''log'''
    def log(self, message: str) -> None:
        if not self.verbose: return
        if self.console: self.console.log(message)
        else: print(message)
    '''ensureprogress'''
    def ensureprogress(self) -> Optional[Progress]:
        if not self.show_progress or Progress is None: return None
        if self._progress is None: self._progress = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), MofNCompleteColumn(), DownloadColumn(), TransferSpeedColumn(), TimeElapsedColumn(), TimeRemainingColumn(), console=self.console, transient=self.progress_transient)
        if not self._progress_started: self._progress.start(); self._progress_started = True
        return self._progress
    '''stopprogress'''
    def stopprogress(self) -> None:
        if self._progress and self._progress_started: self._progress.stop()
        self._progress, self._progress_started = None, False
    '''addtask'''
    def addtask(self, description: str, *, total: Optional[float] = None, visible: bool = True) -> Optional[int]:
        if (progress := self.ensureprogress()) is None: return None
        return progress.add_task(description, total=total, visible=visible)
    '''updatetask'''
    def updatetask(self, task_id: Optional[int], *, advance: Optional[float] = None, completed: Optional[float] = None, total: Optional[float] = None, description: Optional[str] = None, visible: Optional[bool] = None) -> None:
        if task_id is None or self._progress is None: return
        kwargs = {k: v for k, v in {"advance": advance, "completed": completed, "total": total, "description": description, "visible": visible}.items() if v is not None}
        self._progress.update(task_id, **kwargs)
    '''removetask'''
    def removetask(self, task_id: Optional[int]) -> None:
        if task_id is None or self._progress is None: return
        try: self._progress.remove_task(task_id)
        except Exception: pass
    '''shouldshowdetailtasks'''
    def shouldshowdetailtasks(self, n_items: int) -> bool:
        if not self.show_progress: return False
        if self.progress_mode == "detailed": return True
        if self.progress_mode == "summary": return False
        return n_items <= self.max_detail_tasks
    '''setheader'''
    def setheader(self, key: str, value: str) -> None:
        self.headers[key] = value
        if self._session and not self._session.closed: self._session.headers[key] = value
    '''updatecookies'''
    def updatecookies(self, cookies: dict[str, str]) -> None:
        self.cookie_jar.update_cookies(cookies)
    '''exportcookies'''
    def exportcookies(self, url: Optional[str] = None) -> dict[str, str]:
        if url: return {k: v.value for k, v in self.cookie_jar.filter_cookies(url).items()}
        return {cookie.key: cookie.value for cookie in self.cookie_jar}
    '''savecookies'''
    def savecookies(self, target_path: str | Path) -> None:
        (target_path := Path(target_path)).parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(self.exportcookies(), ensure_ascii=False, indent=2), encoding="utf-8")
    '''loadcookies'''
    def loadcookies(self, target_path: str | Path) -> None:
        if not (target_path := Path(target_path)).exists(): return
        data = json.loads(target_path.read_text(encoding="utf-8"))
        if isinstance(data, dict): self.cookie_jar.update_cookies(data)
    '''login'''
    async def login(self, *args, **kwargs) -> None:
        return None
    '''executor'''
    @property
    def executor(self) -> ThreadPoolExecutor:
        if self._executor is None: self._executor = ThreadPoolExecutor(max_workers=self.thread_workers)
        return self._executor
    '''runblocking'''
    async def runblocking(self, func: Callable, *args, progress_description: Optional[str] = None, **kwargs) -> Any:
        task_id = self.addtask(progress_description, total=None) if progress_description else None
        try:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(self.executor, partial(func, *args, **kwargs))
        finally:
            self.removetask(task_id)
    '''requestbytes'''
    async def requestbytes(self, url: str, *, method: str = "GET", params: Optional[dict[str, Any]] = None, data: Any = None, json_data: Any = None, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, auth: Optional[aiohttp.BasicAuth] = None, proxy: Optional[str] = None, allow_statuses: Optional[set[int]] = None, progress_description: Optional[str] = None) -> bytes:
        await self.open(); last_error: Optional[BaseException] = None; allow_statuses = allow_statuses or set()
        task_id = self.addtask(progress_description, total=None) if progress_description else None
        try:
            for attempt in range(self.max_retries + 1):
                try:
                    if attempt > 0 and task_id is not None: self.updatetask(task_id, description=f"{progress_description} | retry {attempt}/{self.max_retries}")
                    async with self._semaphore:
                        async with self.session.request(method, url, params=params, data=data, json=json_data, headers=headers, cookies=cookies, auth=auth, proxy=proxy or self.proxy) as resp:
                            content = await resp.read()
                            if resp.status in allow_statuses: return content
                            if resp.status in self.retry_statuses: raise PaperRequestError(f"Temporary HTTP {resp.status}: {content[:300]!r}")
                            if resp.status >= 400: raise PaperRequestError(f"HTTP {resp.status}: {content[:300]!r}")
                            return content
                except (aiohttp.ClientError, asyncio.TimeoutError, PaperRequestError) as last_error:
                    if attempt >= self.max_retries: break
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt) + random.random() * 0.2)
            raise PaperRequestError(f"Request failed: {url}") from last_error
        finally:
            self.removetask(task_id)
    '''requesttext'''
    async def requesttext(self, url: str, *, encoding: str = "utf-8", errors: str = "replace", **kwargs) -> str:
        content = await self.requestbytes(url, **kwargs)
        return content.decode(encoding, errors=errors)
    '''requestjson'''
    async def requestjson(self, url: str, **kwargs) -> Any:
        text = await self.requesttext(url, **kwargs)
        return json.loads(text)
    '''downloadurl'''
    async def downloadurl(self, url: str, target_path: str | Path, *, overwrite: bool = False, chunk_size: int = 1024 * 128, headers: Optional[dict[str, str]] = None, cookies: Optional[dict[str, str]] = None, proxy: Optional[str] = None, progress_description: Optional[str] = None, show_detail: bool = True) -> Path:
        await self.open(); (target_path := Path(target_path)).parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists() and not overwrite: return target_path
        tmp_target_path = target_path.with_suffix(target_path.suffix + ".part"); last_error: Optional[BaseException] = None; downloaded = 0
        task_id = self.addtask(progress_description or f"Downloading {target_path.name}", total=None) if show_detail else None
        try:
            for attempt in range(self.max_retries + 1):
                try:
                    if attempt > 0 and task_id is not None: self.updatetask(task_id, completed=0, description=f"{progress_description or target_path.name} | retry {attempt}/{self.max_retries}")
                    async with self._semaphore:
                        async with self.session.get(url, headers=headers, cookies=cookies, proxy=proxy or self.proxy) as resp:
                            if resp.status in self.retry_statuses: raise PaperDownloadError(f"Temporary HTTP {resp.status}: {url}")
                            if resp.status >= 400: content = await resp.read(); raise PaperDownloadError(f"HTTP {resp.status}: {content[:300]!r}")
                            if task_id is not None: self.updatetask(task_id, total=(total := resp.content_length)); downloaded = 0
                            async with aiofiles.open(tmp_target_path, "wb") as f:
                                async for chunk in resp.content.iter_chunked(chunk_size):
                                    if chunk: await f.write(chunk); downloaded += (n := len(chunk)); self.updatetask(task_id, advance=n) if task_id is not None else None
                    if task_id is not None: self.updatetask(task_id, completed=total or downloaded, description=f"Downloaded {target_path.name}")
                    tmp_target_path.replace(target_path); return target_path
                except (aiohttp.ClientError, asyncio.TimeoutError, PaperDownloadError) as last_error:
                    if tmp_target_path.exists(): tmp_target_path.unlink(missing_ok=True)
                    if attempt >= self.max_retries: break
                    await asyncio.sleep(self.retry_backoff * (2 ** attempt) + random.random() * 0.2)
            raise PaperDownloadError(f"Download failed: {url}") from last_error
        finally:
            if task_id is not None and self.progress_mode != "detailed": self.removetask(task_id)
    '''downloadmany'''
    async def downloadmany(self, papers: Sequence["PaperInfo"], output_dir: str | Path = "papers", *, overwrite: bool = False, return_exceptions: bool = False) -> list[Path]:
        if not (papers := list(papers)): return []
        show_detail, master_task = self.shouldshowdetailtasks(len(papers)), self.addtask(f"Downloading papers from {self.source}", total=len(papers))
        self.log(f"Start downloading {len(papers)} papers from {self.source} with concurrency={self.concurrency}.")
        async def download_one_func(paper: "PaperInfo") -> Path:
            try: return await self.downloadpaper(paper, output_dir=output_dir, overwrite=overwrite, show_detail=show_detail)
            finally: self.updatetask(master_task, advance=1)
        results = await asyncio.gather(*[download_one_func(paper) for paper in papers], return_exceptions=return_exceptions)
        self.updatetask(master_task, completed=len(papers), description=f"Finished downloading papers from {self.source}")
        if self.progress_mode != "detailed": self.removetask(master_task)
        return results
    '''search'''
    @abstractmethod
    async def search(self, *args, **kwargs) -> list["PaperInfo"]:
        """Search papers and return PaperInfo objects."""
    '''downloadpaper'''
    @abstractmethod
    async def downloadpaper(self, paper: "PaperInfo", output_dir: str | Path = "papers", *, overwrite: bool = False, show_detail: bool = True) -> Path:
        """Download one paper and return local file path."""