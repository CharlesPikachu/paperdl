'''initialize'''
from __future__ import annotations
import re
from typing import Any, Optional
from collections.abc import Sequence
from dataclasses import dataclass, field
from .base_paper_client import BasePaperClient
from .pmlr_paper_client import PMLRPaperClient
from .arxiv_paper_client import ArxivPaperClient
from .pmc_oa_paper_client import PMCOAPaperClient
from .openreview_paper_client import OpenReviewPaperClient
from .acl_anthology_paper_client import ACLAnthologyPaperClient
from .biorxiv_paper_client import BioRxivPaperClient, MedRxivPaperClient


'''constants'''
PAPER_CLIENT_REGISTRY: dict[str, type[BasePaperClient]] = {}
PAPER_CLIENT_ALIASES: dict[str, str] = {}
DEFAULT_PAPER_CLIENTS: tuple[str, ...] = ('arxiv',)


'''PaperClientSpec'''
@dataclass(slots=True)
class PaperClientSpec:
    name: str
    owned: bool = True
    instance: Optional[BasePaperClient] = None
    client_cls: Optional[type[BasePaperClient]] = None
    init_kwargs: dict[str, Any] = field(default_factory=dict)
    search_kwargs: dict[str, Any] = field(default_factory=dict)
    '''client'''
    @property
    def client(self) -> BasePaperClient:
        if self.instance is None and self.client_cls is None: raise ValueError(f"No client class is configured for {self.name!r}.")
        if self.instance is None: self.instance, self.owned = self.client_cls(**self.init_kwargs), True
        return self.instance


'''simpleclientname'''
def simpleclientname(name: str) -> str:
    if not isinstance(name, str) or not name.strip(): raise ValueError('Client name must be a non-empty string.')
    return re.sub(r'[^a-z0-9]+', '_', name.strip().lower()).strip('_')


'''registerpaperclient'''
def registerpaperclient(name: str, client_cls: type[BasePaperClient], *, aliases: Sequence[str] = ()) -> type[BasePaperClient]:
    if not isinstance(client_cls, type) or not issubclass(client_cls, BasePaperClient): raise TypeError('client_cls must be a BasePaperClient subclass.')
    PAPER_CLIENT_REGISTRY[(canonical_name := simpleclientname(name))] = client_cls
    for alias in aliases: PAPER_CLIENT_ALIASES[simpleclientname(alias)] = canonical_name
    PAPER_CLIENT_ALIASES[simpleclientname(client_cls.__name__)] = canonical_name
    if getattr(client_cls, 'source', None): PAPER_CLIENT_ALIASES[simpleclientname(str(client_cls.source))] = canonical_name
    return client_cls


'''normalizepaperclientname'''
def normalizepaperclientname(name: str) -> str:
    key = PAPER_CLIENT_ALIASES.get((key := simpleclientname(name)), key)
    if key not in PAPER_CLIENT_REGISTRY: valid = ', '.join(availablepaperclients()); raise ValueError(f'Unknown paper client {name!r}. Available clients: {valid}.')
    return key


'''availablepaperclients'''
def availablepaperclients() -> list[str]:
    return sorted(PAPER_CLIENT_REGISTRY)


'''getpaperclientclass'''
def getpaperclientclass(name: str) -> type[BasePaperClient]:
    return PAPER_CLIENT_REGISTRY[normalizepaperclientname(name)]


'''register'''
registerpaperclient('arxiv', ArxivPaperClient, aliases=('arxiv_paper_client', 'arxivpaperclient'))
registerpaperclient('openreview', OpenReviewPaperClient, aliases=('open_review', 'openreview_paper_client', 'openreviewpaperclient'))
registerpaperclient('acl_anthology', ACLAnthologyPaperClient, aliases=('acl', 'acl_anthology_paper_client', 'aclanthology', 'aclanthologypaperclient'))
registerpaperclient('biorxiv', BioRxivPaperClient, aliases=('bio_rxiv', 'biorxiv_paper_client', 'biorxivpaperclient'))
registerpaperclient('medrxiv', MedRxivPaperClient, aliases=('med_rxiv', 'medrxiv_paper_client', 'medrxivpaperclient'))
registerpaperclient('pmlr', PMLRPaperClient, aliases=('pmlr_paper_client', 'pmlrpaperclient'))
registerpaperclient('pmc_oa', PMCOAPaperClient, aliases=('pmc', 'pmcoa', 'pmc_oa_paper_client', 'pmcoapaperclient', 'pubmed', 'pubmed_central'))