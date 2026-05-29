'''
Function:
    Paperdl: A Unified Asynchronous Framework for Scholarly Paper Search and Download
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
import json
import asyncio
import argparse
from rich import box
from pathlib import Path
from itertools import chain
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from typing import Any, Optional, ClassVar
from collections.abc import Mapping, Sequence
try:
    from .modules import (
        PaperInfo, BasePaperClient, PaperClientSpec, DEFAULT_PAPER_CLIENTS, PAPER_CLIENT_REGISTRY, availablepaperclients, getpaperclientclass, normalizepaperclientname,
    )
except ImportError:
    from modules import (
        PaperInfo, BasePaperClient, PaperClientSpec, DEFAULT_PAPER_CLIENTS, PAPER_CLIENT_REGISTRY, availablepaperclients, getpaperclientclass, normalizepaperclientname,
    )


'''PaperClient'''
class PaperClient:
    DEFAULT_CLIENTS: ClassVar[tuple[str, ...]] = DEFAULT_PAPER_CLIENTS
    CLIENT_REGISTRY: ClassVar[dict[str, type[BasePaperClient]]] = PAPER_CLIENT_REGISTRY
    def __init__(self, clients: Optional[Sequence[str | type[BasePaperClient] | BasePaperClient | Mapping[str, Any]] | Mapping[str, Any]] = None, *, default_init_kwargs: Optional[dict[str, Any]] = None, 
                 default_search_kwargs: Optional[dict[str, Any]] = None, client_init_kwargs: Optional[dict[str, dict[str, Any]]] = None, client_search_kwargs: Optional[dict[str, dict[str, Any]]] = None,
                 search_concurrency: Optional[int] = None, close_external_clients: bool = False) -> None:
        self.default_init_kwargs = dict(default_init_kwargs or {})
        self.default_search_kwargs = dict(default_search_kwargs or {})
        self.client_init_kwargs = self.normalizenestedkwargs(client_init_kwargs)
        self.client_search_kwargs = self.normalizenestedkwargs(client_search_kwargs)
        self.search_concurrency = search_concurrency
        self.close_external_clients = close_external_clients
        self.specs = self.normalizespecs(clients or self.DEFAULT_CLIENTS)
        self.last_errors: dict[str, BaseException] = {}
    '''aenter'''
    async def __aenter__(self) -> 'PaperClient':
        await self.open()
        return self
    '''aexit'''
    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()
    '''availableclients'''
    @classmethod
    def availableclients(cls) -> list[str]:
        return availablepaperclients()
    '''canonicalname'''
    @classmethod
    def canonicalname(cls, name: str) -> str:
        return normalizepaperclientname(name)
    '''open'''
    async def open(self, clients: Optional[Sequence[str]] = None) -> None:
        selected = self.selectedspecs(clients)
        await asyncio.gather(*[spec.client.open() for spec in selected])
    '''close'''
    async def close(self) -> None:
        coros = []
        for spec in self.specs.values():
            if spec.instance is None: continue
            if spec.owned or self.close_external_clients: coros.append(spec.instance.close())
        if coros: await asyncio.gather(*coros, return_exceptions=True)
    '''getclient'''
    def getclient(self, name: str) -> BasePaperClient:
        return self.specs[self.canonicalname(name)].client
    '''search'''
    async def search(self, query: Optional[str] = None, *, clients: Optional[Sequence[str]] = None, total_results: Optional[int] = None, client_search_kwargs: Optional[dict[str, dict[str, Any]]] = None, deduplicate: bool = True, return_by_client: bool = False, return_exceptions: bool = False, raise_on_error: bool = False) -> list[PaperInfo] | dict[str, list[PaperInfo] | BaseException]:
        selected, per_call_search_kwargs, self.last_errors = self.selectedspecs(clients), self.normalizenestedkwargs(client_search_kwargs), {}
        await self.open([spec.name for spec in selected]); semaphore = asyncio.Semaphore(self.search_concurrency or max(1, len(selected)))
        async def search_one_func(spec: PaperClientSpec) -> tuple[str, list[PaperInfo] | BaseException]:
            async with semaphore:
                kwargs = {**spec.search_kwargs, **per_call_search_kwargs.get(spec.name, {})}
                if total_results is not None and 'total_results' not in kwargs: kwargs['total_results'] = total_results
                try: return spec.name, await self.callclientsearch(spec.client, query=query, kwargs=kwargs)
                except BaseException as exc: return spec.name, exc
        results = dict(await asyncio.gather(*[search_one_func(spec) for spec in selected]))
        self.last_errors = {name: value for name, value in results.items() if isinstance(value, BaseException)}
        if self.last_errors and raise_on_error: first_name, first_error = next(iter(self.last_errors.items())); raise RuntimeError(f'Search failed for client {first_name!r}: {first_error}') from first_error
        if return_by_client: return results if return_exceptions else {name: ([] if isinstance(value, BaseException) else value) for name, value in results.items()}
        papers = [paper for value in results.values() if not isinstance(value, BaseException) for paper in value]
        return self.deduplicate(papers) if deduplicate else papers
    '''download'''
    async def download(self, paper_infos: Sequence[PaperInfo] | Mapping[str, Sequence[PaperInfo]], output_dir: str | Path = 'paperdl_outputs', *, overwrite: bool = False, return_by_client: bool = False, return_exceptions: bool = False, raise_on_error: bool = False) -> list[Path | BaseException] | dict[str, list[Path | BaseException]]:
        if not (papers := self.flattenpapers(paper_infos)): return {} if return_by_client else []
        groups: dict[str, list[PaperInfo]] = {}; errors: list[BaseException] = []
        for paper in papers:
            try: name = self.clientnameforpaper(paper); groups.setdefault(name, []).append(paper)
            except BaseException as exc: errors.append(exc)
        await self.open(list(groups))
        async def download_group_func(name: str, items: list[PaperInfo]) -> tuple[str, list[Path | BaseException]]:
            try: paths = await self.specs[name].client.download(items, output_dir=output_dir, overwrite=overwrite, return_exceptions=True); return name, list(paths)
            except BaseException as exc: return name, [exc]
        by_client = dict(await asyncio.gather(*[download_group_func(name, items) for name, items in groups.items()]))
        if errors: by_client.setdefault('unmatched', []).extend(errors)
        all_results = [item for values in by_client.values() for item in values]
        if (failures := [item for item in all_results if isinstance(item, BaseException)]) and raise_on_error: raise RuntimeError(f'Download failed: {failures[0]}') from failures[0]
        if not return_exceptions: by_client = {name: [item for item in values if not isinstance(item, BaseException)] for name, values in by_client.items()}; all_results = [item for values in by_client.values() for item in values]
        return by_client if return_by_client else all_results
    '''searchanddownload'''
    async def searchanddownload(self, query: Optional[str] = None, *, output_dir: str | Path = 'paperdl_outputs', clients: Optional[Sequence[str]] = None, total_results: Optional[int] = None, client_search_kwargs: Optional[dict[str, dict[str, Any]]] = None, overwrite: bool = False, deduplicate: bool = True, return_exceptions: bool = False, raise_on_error: bool = False) -> tuple[list[PaperInfo], list[Path | BaseException]]:
        papers = await self.search(query=query, clients=clients, total_results=total_results, client_search_kwargs=client_search_kwargs, deduplicate=deduplicate, raise_on_error=raise_on_error)
        paths = await self.download(papers, output_dir=output_dir, overwrite=overwrite, return_exceptions=return_exceptions, raise_on_error=raise_on_error)
        return papers, paths
    '''saveresults'''
    @staticmethod
    def saveresults(paper_infos: Sequence[PaperInfo], path: str | Path) -> Path:
        (path := Path(path)).parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([p.todict(drop_none=True) for p in paper_infos], ensure_ascii=False, indent=2), encoding='utf-8')
        return path
    '''loadresults'''
    @staticmethod
    def loadresults(path: str | Path) -> list[PaperInfo]:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
        if isinstance(data, dict) and 'papers' in data: data = data['papers']
        if not isinstance(data, list): raise ValueError('Search result JSON must be a list of paper records or a dict with a `papers` list.')
        return [PaperInfo.fromdict(item) for item in data if isinstance(item, dict)]
    '''deduplicate'''
    @staticmethod
    def deduplicate(paper_infos: Sequence[PaperInfo]) -> list[PaperInfo]:
        merged: dict[str, PaperInfo] = {}
        for paper in paper_infos: merged[paper.identity_key] = merged[paper.identity_key].merge(paper) if paper.identity_key in merged else paper
        return list(merged.values())
    '''normalizespecs'''
    def normalizespecs(self, clients: Sequence[Any] | Mapping[str, Any]) -> dict[str, PaperClientSpec]:
        client_items = [{'name': name, **dict(config)} if isinstance(config, Mapping) else {'name': name, 'client': config} for name, config in clients.items()] if isinstance(clients, Mapping) else list(clients)
        specs: dict[str, PaperClientSpec] = {spec.name: spec for spec in (self.normalizespec(item) for item in client_items)}
        if not specs: raise ValueError('At least one paper client must be configured.')
        return specs
    '''normalizespec'''
    def normalizespec(self, item: Any) -> PaperClientSpec:
        if isinstance(item, BasePaperClient): name = self.namefromclient(item); return PaperClientSpec(name=name, instance=item, owned=False, search_kwargs={**self.default_search_kwargs, **self.client_search_kwargs.get(name, {})})
        if isinstance(item, str): name = self.canonicalname(item); return self.buildspec(name=name)
        if isinstance(item, type) and issubclass(item, BasePaperClient): name = self.namefromclass(item); return self.buildspec(name=name, client_cls=item)
        if isinstance(item, Mapping): return self.normalizemappingspec(item)
        raise TypeError(f'Unsupported paper client spec: {item!r}')
    '''normalizemappingspec'''
    def normalizemappingspec(self, item: Mapping[str, Any]) -> PaperClientSpec:
        instance = (data := dict(item)).get('instance') or (data.get('client') if isinstance(data.get('client'), BasePaperClient) else None)
        client_value = data.get('client') if not isinstance(data.get('client'), BasePaperClient) else None
        client_cls = data.get('client_cls') or data.get('class') or (client_value if isinstance(client_value, type) else None)
        name_value = data.get('name') or data.get('source') or (client_value if isinstance(client_value, str) else None)
        if instance is not None:
            name = self.canonicalname(str(name_value)) if name_value else self.namefromclient(instance)
            spec = PaperClientSpec(name=name, instance=instance, owned=False, search_kwargs={**self.default_search_kwargs, **self.client_search_kwargs.get(name, {})})
        else:
            if client_cls is not None:
                if not (isinstance(client_cls, type) and issubclass(client_cls, BasePaperClient)): raise TypeError('`client_cls` must be a BasePaperClient subclass.')
                name = self.canonicalname(str(name_value)) if name_value else self.namefromclass(client_cls)
                spec = self.buildspec(name=name, client_cls=client_cls)
            else:
                if not name_value: raise ValueError('Mapping client spec requires `name`, `client`, `client_cls`, or `instance`.')
                spec = self.buildspec(name=self.canonicalname(str(name_value)))
        spec.init_kwargs.update(data.get('init_kwargs') or {}); spec.search_kwargs.update(data.get('search_kwargs') or {})
        return spec
    '''buildspec'''
    def buildspec(self, *, name: str, client_cls: Optional[type[BasePaperClient]] = None) -> PaperClientSpec:
        name = self.canonicalname(name)
        init_kwargs = {**self.default_init_kwargs, **self.client_init_kwargs.get(name, {})}
        search_kwargs = {**self.default_search_kwargs, **self.client_search_kwargs.get(name, {})}
        return PaperClientSpec(name=name, client_cls=client_cls or getpaperclientclass(name), init_kwargs=init_kwargs, search_kwargs=search_kwargs)
    '''selectedspecs'''
    def selectedspecs(self, clients: Optional[Sequence[str]] = None) -> list[PaperClientSpec]:
        if clients is None: return list(self.specs.values())
        names = [self.canonicalname(name) for name in clients]
        missing = [name for name in names if name not in self.specs]
        if missing: raise ValueError(f'Clients are not configured in this PaperClient instance: {", ".join(missing)}')
        return [self.specs[name] for name in names]
    '''callclientsearch'''
    @staticmethod
    async def callclientsearch(client: BasePaperClient, *, query: Optional[str], kwargs: dict[str, Any]) -> list[PaperInfo]:
        if 'query' in (kwargs := dict(kwargs)): query_arg = kwargs.pop('query'); return await client.search(query_arg, **kwargs)
        if query is None: return await client.search(**kwargs)
        return await client.search(query, **kwargs)
    '''clientnameforpaper'''
    def clientnameforpaper(self, paper_info: PaperInfo) -> str:
        source = (paper_info.source or '').strip().lower()
        for name, spec in self.specs.items():
            client_source = (getattr(spec.client, 'source', '') or '').lower()
            if source in {name.lower(), client_source}: return name
        try:
            if (canonical := self.canonicalname(source)) in self.specs: return canonical
        except Exception:
            pass
        if len(self.specs) == 1: return next(iter(self.specs))
        raise ValueError(f'Cannot find a configured client to download paper from source {paper_info.source!r}: {paper_info.title}')
    '''flattenpapers'''
    @staticmethod
    def flattenpapers(paper_infos: Sequence[PaperInfo] | Mapping[str, Sequence[PaperInfo]]) -> list[PaperInfo]:
        if isinstance(paper_infos, Mapping): return [paper for papers in paper_infos.values() if not isinstance(papers, BaseException) for paper in papers]
        return list(paper_infos)
    '''namefromclient'''
    @classmethod
    def namefromclient(cls, client: BasePaperClient) -> str:
        return cls.namefromclass(type(client))
    '''namefromclass'''
    @classmethod
    def namefromclass(cls, client_cls: type[BasePaperClient]) -> str:
        for name, registered_cls in cls.CLIENT_REGISTRY.items():
            if client_cls is registered_cls: return name
        source = getattr(client_cls, 'source', client_cls.__name__)
        return cls.canonicalname(str(source))
    '''normalizenestedkwargs'''
    @classmethod
    def normalizenestedkwargs(cls, value: Optional[dict[str, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for name, kwargs in (value or {}).items():
            if kwargs is None: kwargs = {}
            if not isinstance(kwargs, Mapping): raise TypeError(f'Keyword configuration for client {name!r} must be a mapping.')
            result[cls.canonicalname(name)] = dict(kwargs)
        return result


'''PaperClientCMD'''
class PaperClientCMD:
    def __init__(self, argv: Optional[Sequence[str]] = None) -> None:
        self.argv = list(argv) if argv is not None else None
        self.console = Console() if Console else None
    '''run'''
    def run(self) -> int:
        parser = self.buildparser()
        args = parser.parse_args(self.argv)
        try: return asyncio.run(self.runasync(args, parser))
        except KeyboardInterrupt: self.print('\nInterrupted.'); return 130
        except Exception as exc: self.print(f'[error] {exc}'); return 1
    '''runasync'''
    async def runasync(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
        if args.command == 'clients': self.renderclients(); return 0
        if args.command == 'search': await self.commandsearch(args, parser); return 0
        if args.command == 'download': await self.commanddownload(args, parser); return 0
        parser.print_help()
        return 1
    '''buildparser'''
    def buildparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog='paperdl', description='Unified paper search and download command line interface.')
        subparsers = parser.add_subparsers(dest='command')
        clients_parser = subparsers.add_parser('clients', help='List available paper clients.')
        clients_parser.set_defaults(command='clients')
        search_parser = subparsers.add_parser('search', help='Search papers and show or save results.')
        self.addcommonargs(search_parser)
        search_parser.add_argument('query_terms', nargs='*', help='Search query, e.g. paperdl search diffusion model.')
        search_parser.add_argument('-q', '--query', default=None, help='Search query. Overrides positional query terms when provided.')
        search_parser.add_argument('-n', '--total-results', type=int, default=10, help='Number of results per client unless overridden by client search kwargs.')
        search_parser.add_argument('--output-json', default=None, help='Save search results to a JSON file.')
        search_parser.add_argument('--format', choices=['table', 'json', 'jsonl'], default='table', help='Output format.')
        search_parser.add_argument('--limit', type=int, default=None, help='Limit the number of rows shown in table output. Saved JSON still contains all results.')
        search_parser.add_argument('--no-dedupe', action='store_true', help='Do not deduplicate merged client results.')
        search_parser.add_argument('--raise-on-error', action='store_true', help='Stop if any configured client fails.')
        search_parser.set_defaults(command='search')
        download_parser = subparsers.add_parser('download', help='Search and download papers, or download from a saved JSON result file.')
        self.addcommonargs(download_parser)
        download_parser.add_argument('query_terms', nargs='*', help='Search query, e.g. paperdl download diffusion model.')
        download_parser.add_argument('-q', '--query', default=None, help='Search query. Required unless --input-json is used. Overrides positional query terms when provided.')
        download_parser.add_argument('-n', '--total-results', type=int, default=10, help='Number of results per client unless overridden by client search kwargs.')
        download_parser.add_argument('--input-json', default=None, help='Load papers from a JSON file generated by `paperdl search`.')
        download_parser.add_argument('-o', '--output-dir', default='paperdl_outputs', help='Directory to save downloaded PDFs.')
        download_parser.add_argument('--select', default='all', help='Paper indices to download, e.g. all, 1,3-5, top10.')
        download_parser.add_argument('--overwrite', action='store_true', help='Overwrite existing PDF files.')
        download_parser.add_argument('--no-dedupe', action='store_true', help='Do not deduplicate merged client results.')
        download_parser.add_argument('--raise-on-error', action='store_true', help='Stop if any search/download error happens.')
        download_parser.set_defaults(command='download')
        return parser
    '''addcommonargs'''
    @staticmethod
    def addcommonargs(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('-c', '--clients', default='arxiv', help='Comma-separated client names, or `all`, e.g. arxiv,pmlr,pmc.')
        parser.add_argument('--init-kwargs', default=None, help='JSON object applied to every client constructor.')
        parser.add_argument('--search-kwargs', default=None, help='JSON object applied to every client search call.')
        parser.add_argument('--client-init-kwargs', default=None, help='JSON object keyed by client name for constructor kwargs.')
        parser.add_argument('--client-search-kwargs', default=None, help='JSON object keyed by client name for search kwargs.')
        parser.add_argument('--init-param', action='append', default=[], metavar='KEY=VALUE', help='Constructor kwarg. Repeatable. VALUE is parsed as JSON when possible.')
        parser.add_argument('--search-param', action='append', default=[], metavar='KEY=VALUE', help='Search kwarg. Repeatable. VALUE is parsed as JSON when possible.')
        parser.add_argument('--client-init-param', action='append', default=[], metavar='CLIENT.KEY=VALUE', help='Per-client constructor kwarg. Repeatable. VALUE is parsed as JSON when possible.')
        parser.add_argument('--client-search-param', action='append', default=[], metavar='CLIENT.KEY=VALUE', help='Per-client search kwarg. Repeatable. VALUE is parsed as JSON when possible.')
        parser.add_argument('--search-concurrency', type=int, default=None, help='Maximum number of clients searched concurrently.')
        parser.add_argument('--quiet', action='store_true', help='Disable verbose client logs and progress where possible.')
    '''commandsearch'''
    async def commandsearch(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
        clients, default_init_kwargs, default_search_kwargs, client_init_kwargs, client_search_kwargs = self.parseclientargs(args, parser)
        if args.quiet: default_init_kwargs = {**default_init_kwargs, 'verbose': False, 'show_progress': False}
        async with PaperClient(clients, default_init_kwargs=default_init_kwargs, default_search_kwargs=default_search_kwargs, client_init_kwargs=client_init_kwargs, client_search_kwargs=client_search_kwargs, search_concurrency=args.search_concurrency) as client:
            papers = await client.search(self.resolvequery(args), total_results=args.total_results, deduplicate=not args.no_dedupe, return_by_client=False, raise_on_error=args.raise_on_error)
            self.printerrors(client.last_errors)
        if args.output_json: PaperClient.saveresults(papers, args.output_json); self.print(f'Saved {len(papers)} search results to {args.output_json}')
        self.renderresults(papers, output_format=args.format, limit=args.limit)
    '''commanddownload'''
    async def commanddownload(self, args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
        clients, default_init_kwargs, default_search_kwargs, client_init_kwargs, client_search_kwargs = self.parseclientargs(args, parser)
        if args.quiet: default_init_kwargs = {**default_init_kwargs, 'verbose': False, 'show_progress': False}
        async with PaperClient(clients, default_init_kwargs=default_init_kwargs, default_search_kwargs=default_search_kwargs, client_init_kwargs=client_init_kwargs, client_search_kwargs=client_search_kwargs, search_concurrency=args.search_concurrency) as client:
            if args.input_json: papers = PaperClient.loadresults(args.input_json)
            else:
                if not (query := self.resolvequery(args)): parser.error('download requires a query unless --input-json is provided.')
                papers = await client.search(query, total_results=args.total_results, deduplicate=not args.no_dedupe, return_by_client=False, raise_on_error=args.raise_on_error)
                self.printerrors(client.last_errors)
            self.renderresults((selected := self.selectpapers(papers, args.select)), output_format='table')
            results = await client.download(selected, output_dir=args.output_dir, overwrite=args.overwrite, return_exceptions=True, raise_on_error=args.raise_on_error)
        ok, failed = [x for x in results if not isinstance(x, BaseException)], [x for x in results if isinstance(x, BaseException)]
        self.print(f'Downloaded {len(ok)} PDFs to {args.output_dir}. Failed: {len(failed)}.')
        for err in failed[:10]: self.print(f'[download error] {err}')
    '''resolvequery'''
    @staticmethod
    def resolvequery(args: argparse.Namespace) -> Optional[str]:
        query = args.query if getattr(args, 'query', None) is not None else ' '.join(getattr(args, 'query_terms', []) or [])
        query = str(query).strip() if query is not None else ''
        return query or None
    '''parseclientargs'''
    def parseclientargs(self, args: argparse.Namespace, parser: Optional[argparse.ArgumentParser]) -> tuple[list[str], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        try:
            clients = self.parseclients(args.clients or 'arxiv')
            default_init_kwargs = {**self.jsondict(args.init_kwargs, '--init-kwargs'), **self.parsekeyvalueitems(args.init_param, '--init-param')}
            default_search_kwargs = {**self.jsondict(args.search_kwargs, '--search-kwargs'), **self.parsekeyvalueitems(args.search_param, '--search-param')}
            client_init_kwargs = self.jsondict(args.client_init_kwargs, '--client-init-kwargs')
            client_search_kwargs = self.jsondict(args.client_search_kwargs, '--client-search-kwargs')
            if not all(isinstance(v, Mapping) for v in client_init_kwargs.values()): raise ValueError('--client-init-kwargs values must be JSON objects.')
            if not all(isinstance(v, Mapping) for v in client_search_kwargs.values()): raise ValueError('--client-search-kwargs values must be JSON objects.')
            client_init_kwargs = self.mergeclientparams(client_init_kwargs, self.parseclientkeyvalueitems(args.client_init_param, '--client-init-param'))
            client_search_kwargs = self.mergeclientparams(client_search_kwargs, self.parseclientkeyvalueitems(args.client_search_param, '--client-search-param'))
            return clients, default_init_kwargs, default_search_kwargs, dict(client_init_kwargs), dict(client_search_kwargs)
        except Exception as exc:
            if parser: parser.error(str(exc))
            raise RuntimeError(f'parse client args errors: {exc}')
    '''parseclients'''
    @staticmethod
    def parseclients(text: str) -> list[str]:
        if not (names := [x.strip() for x in str(text or '').split(',') if x.strip()]): names = ['arxiv']
        if len(names) == 1 and names[0].lower() in {'all', '*'}: return PaperClient.availableclients()
        return [PaperClient.canonicalname(x) for x in names]
    '''mergeclientparams'''
    @staticmethod
    def mergeclientparams(base: Mapping[str, Any], extra: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
        merged = {PaperClient.canonicalname(name): dict(value) for name, value in base.items()}
        for name, values in extra.items(): merged.setdefault(PaperClient.canonicalname(name), {}).update(values)
        return merged
    '''parsekeyvalueitems'''
    @classmethod
    def parsekeyvalueitems(cls, items: Optional[Sequence[str]], option_name: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for item in items or []:
            if '=' not in item: raise ValueError(f'{option_name} expects KEY=VALUE, got {item!r}.')
            key, value = item.split('=', 1); key = key.strip()
            if not key: raise ValueError(f'{option_name} contains an empty key.')
            result[key] = cls.parsevalue(value)
        return result
    '''parseclientkeyvalueitems'''
    @classmethod
    def parseclientkeyvalueitems(cls, items: Optional[Sequence[str]], option_name: str) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for item in items or []:
            if '=' not in item: raise ValueError(f'{option_name} expects CLIENT.KEY=VALUE, got {item!r}.')
            left, value = item.split('=', 1)
            if '.' in left: client_name, key = left.split('.', 1)
            elif ':' in left: client_name, key = left.split(':', 1)
            else: raise ValueError(f'{option_name} expects CLIENT.KEY=VALUE, got {item!r}.')
            client_name, key = PaperClient.canonicalname(client_name.strip()), key.strip()
            if not key: raise ValueError(f'{option_name} contains an empty key.')
            result.setdefault(client_name, {})[key] = cls.parsevalue(value)
        return result
    '''parsevalue'''
    @staticmethod
    def parsevalue(text: str) -> Any:
        if not (value := str(text).strip()): return ''
        try: return json.loads(value)
        except json.JSONDecodeError: return value
    '''renderclients'''
    def renderclients(self) -> None:
        if not (self.console and Table): self.print('Available clients: ' + ', '.join(PaperClient.availableclients())); return
        table = Table(title='PaperDL Engine Registry', box=box.ROUNDED if box else None, header_style='bold cyan')
        table.add_column('Name', style='bold')
        table.add_column('Class')
        table.add_column('Source')
        for name in PaperClient.availableclients(): client_cls = getpaperclientclass(name); table.add_row(name, client_cls.__name__, getattr(client_cls, 'source', ''))
        self.console.print(table)
    '''renderresults'''
    def renderresults(self, papers: Sequence[PaperInfo], *, output_format: str = 'table', limit: Optional[int] = None) -> None:
        papers = list(papers); shown = papers[:limit] if limit else papers
        if output_format == 'json': print(json.dumps([p.todict(drop_none=True) for p in papers], ensure_ascii=False, indent=2)); return
        if output_format == 'jsonl': print('\n'.join(p.tojson(ensure_ascii=False, indent=None) for p in papers)); return
        if not (self.console and Table): self.print('\n'.join(f'[{idx}] {paper.source} | {paper.year or ""} | {paper.title} | {paper.main_url or ""}' for idx, paper in enumerate(shown, start=1))) if shown else None; return
        table = Table(title=f'Search Results ({len(papers)} total)', box=box.ROUNDED if box else None, header_style='bold cyan', show_lines=False, expand=True)
        table.add_column('#', justify='right', no_wrap=True, style='dim', width=4)
        table.add_column('Engine', no_wrap=True, style='bold', overflow='ellipsis', max_width=20)
        table.add_column('Year', justify='right', no_wrap=True, width=6)
        table.add_column('Title', ratio=4, overflow='ellipsis', no_wrap=True)
        table.add_column('Authors', ratio=2, overflow='ellipsis', no_wrap=True)
        table.add_column('Venue', ratio=2, overflow='ellipsis', no_wrap=True)
        table.add_column('Links', justify='center', no_wrap=True, width=10)
        for idx, paper in enumerate(shown, start=1): table.add_row(str(idx), paper.source or '', str(paper.year or ''), self.cleantext(paper.title or ''), self.cleantext(paper.short_authors or ''), self.cleantext(paper.venue or ''), self.paperlinkslabel(paper))
        self.console.print(table)
        if limit and len(papers) > limit: self.console.print(f'[dim]Showing first {limit} of {len(papers)} results.[/dim]')
    '''renderpreview'''
    def renderpreview(self, paper: PaperInfo, *, index: Optional[int] = None) -> None:
        title = f'[{index}] {paper.title}' if index is not None else paper.title
        metadata = [('Source', paper.source or 'N/A'), ('Authors', ', '.join(paper.authors) if paper.authors else 'N/A'), ('Year', str(paper.year or 'N/A')), ('Venue', paper.venue or 'N/A'), ('Article', paper.article_url or 'N/A'), ('PDF', paper.download_url or 'N/A'), ('DOI', paper.doi or 'N/A')]
        body = '\n'.join([f'[bold cyan]{key:<8}[/bold cyan] {value}' for key, value in metadata])
        abstract = paper.abstract or 'No abstract available.'
        text = f'{body}\n\n[bold]Abstract[/bold]\n{abstract}'
        if self.console and Panel: self.console.print(Panel(text, title=title, border_style='magenta', box=box.ROUNDED if box else None))
        else: self.print(title + '\n' + re.sub(r'\[[^\]]+\]', '', text))
    '''selectpapers'''
    @classmethod
    def selectpapers(cls, papers: Sequence[PaperInfo], selection: str) -> list[PaperInfo]:
        indices = cls.parseindices(selection, len((papers := list(papers))))
        return [papers[i - 1] for i in indices]
    '''parseindices'''
    @staticmethod
    def parseindices(selection: str, max_index: int) -> list[int]:
        if (text := (selection or 'all').strip().lower()) in {'all', '*'}: return list(range(1, max_index + 1))
        if match := re.fullmatch(r'top\s*(\d+)', text): return list(range(1, min(int(match.group(1)), max_index) + 1))
        result = list(chain.from_iterable((lambda a, b: range(min(a, b), max(a, b) + 1))(*map(int, part.split('-', 1))) if '-' in part else (int(part),) for part in re.split(r'\s*,\s*', text) if part))
        return [i for i in dict.fromkeys(result) if 1 <= i <= max_index]
    '''jsondict'''
    @staticmethod
    def jsondict(text: Optional[str], option_name: str) -> dict[str, Any]:
        if not text: return {}
        if isinstance(text, str) and text.startswith('@'): text = Path(text[1:]).read_text(encoding='utf-8')
        if not isinstance((value := json.loads(text)), dict): raise ValueError(f'{option_name} must be a JSON object.')
        return value
    '''printerrors'''
    def printerrors(self, errors: Mapping[str, BaseException]) -> None:
        for name, error in errors.items():
            if self.console: self.console.print(f'[yellow][search error][/yellow] [bold]{name}[/bold]: {error}')
            else: self.print(f'[search error] {name}: {error}')
    '''paperlinkslabel'''
    @staticmethod
    def paperlinkslabel(paper: PaperInfo) -> str:
        labels = [label for condition, label in ((paper.download_url, 'PDF'), (paper.article_url or paper.main_url, 'URL'), (paper.doi, 'DOI')) if condition]
        return '+'.join(labels) if labels else '-'
    '''cleantext'''
    @staticmethod
    def cleantext(text: str) -> str:
        return re.sub(r'\s+', ' ', str(text or '')).strip()
    '''print'''
    def print(self, message: str) -> None:
        if self.console: self.console.print(message)
        else: print(message)


'''main'''
def main(argv: Optional[Sequence[str]] = None) -> int:
    return PaperClientCMD(argv).run()


'''run'''
if __name__ == '__main__':
    raise SystemExit(main())