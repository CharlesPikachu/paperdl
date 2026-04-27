'''
Function:
    Implementation of PaperInfo
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
from __future__ import annotations
import re
import json
import hashlib
from ftfy import fix_text
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathvalidate import sanitize_filename
from dateutil import parser as date_parser
from typing import Any, Optional, ClassVar
from datetime import datetime, date, timezone
from dataclasses import dataclass, field, asdict, fields


'''PaperInfo'''
@dataclass(slots=True)
class PaperInfo:
    # core paper information
    source: str = field(metadata={"desc": "The source platform where the paper was found, such as arXiv, PubMed, Semantic Scholar, Google Scholar, OpenReview, Nature, IEEE, or ACM."})
    title: str = field(metadata={"desc": "The paper title. It should preserve the original semantic meaning and should not be over-sanitized as a filename."})
    abstract: Optional[str] = field(default=None, metadata={"desc": "The paper abstract. Useful for keyword matching, LLM summarization, topic classification, and daily paper analysis."})
    authors: list[str] = field(default_factory=list, metadata={"desc": "The list of paper authors, normalized as plain strings, e.g., ['Ashish Vaswani', 'Noam Shazeer']."})
    article_url: Optional[str] = field(default=None, metadata={"desc": "The paper detail page URL, such as the arXiv abstract page, journal page, OpenReview page, or publisher page."})
    download_url: Optional[str] = field(default=None, metadata={"desc": "The direct download URL, usually a PDF link. Useful for automatic downloading, caching, and full-text parsing."})
    doi: Optional[str] = field(default=None, metadata={"desc": "The Digital Object Identifier. Useful for cross-platform deduplication, citation tracking, and standardized indexing."})
    arxiv_id: Optional[str] = field(default=None, metadata={"desc": "The arXiv identifier, such as 1706.03762. Useful for arXiv deduplication, version tracking, and PDF URL construction."})
    # publication information
    venue: Optional[str] = field(default=None, metadata={"desc": "The publication venue, such as NeurIPS, ICLR, Nature Medicine, Radiology, CVPR Workshop, or a journal name."})
    publisher: Optional[str] = field(default=None, metadata={"desc": "The publisher or hosting organization, such as Elsevier, Springer, IEEE, ACM, Nature Portfolio, or PMLR."})
    published_at: Optional[str] = field(default=None, metadata={"desc": "The publication date or preprint release date. Internally normalized to an ISO-format string when possible."})
    updated_at: Optional[str] = field(default=None, metadata={"desc": "The latest update date, such as an arXiv version update date or an OpenReview revision date."})
    # search metadata
    source_id: Optional[str] = field(default=None, metadata={"desc": "The paper ID used by the source platform, such as Semantic Scholar paperId, PubMed PMID, OpenReview forum ID, or arXiv ID."})
    query: Optional[str] = field(default=None, metadata={"desc": "The search query or keyword that retrieved this paper. Useful for analyzing which queries produced which results."})
    rank: Optional[int] = field(default=None, metadata={"desc": "The paper rank in the current search results. Useful for evaluating search quality or recommendation ranking."})
    score: Optional[float] = field(default=None, metadata={"desc": "The relevance score returned by a search engine, recommender, or custom ranking model."})
    # topic, category, and custom tags
    keywords: list[str] = field(default_factory=list, metadata={"desc": "Paper keywords. They may come from the paper itself, a search platform, an LLM extractor, or user annotations."})
    categories: list[str] = field(default_factory=list, metadata={"desc": "Topic or discipline categories, such as cs.AI, cs.CL, medical imaging, LLM, agent, reasoning, or AI for healthcare."})
    tags: list[str] = field(default_factory=list, metadata={"desc": "User-defined or system-defined tags, such as daily-pick, must-read, survey, benchmark, dataset, or code-available."})
    # impact and bibliographic metrics
    citation_count: Optional[int] = field(default=None, metadata={"desc": "The citation count, usually obtained from Semantic Scholar, Crossref, OpenAlex, Google Scholar, or similar sources."})
    reference_count: Optional[int] = field(default=None, metadata={"desc": "The number of references cited by this paper. Useful for identifying surveys or literature-heavy papers."})
    # availability and license information
    language: Optional[str] = field(default=None, metadata={"desc": "The paper language, such as en or zh. Useful for multilingual paper search and display."})
    license: Optional[str] = field(default=None, metadata={"desc": "The paper license, such as CC-BY, CC-BY-NC, publisher-specific licenses, or arXiv non-exclusive license."})
    is_open_access: Optional[bool] = field(default=None, metadata={"desc": "Whether the paper is open access. Useful for deciding whether full text can be downloaded or prioritized."})
    # system extension information
    fetched_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), metadata={"desc": "The time when this paper record was fetched or created. Useful for cache updates, daily summaries, and incremental synchronization."})
    extra: dict[str, Any] = field(default_factory=dict, metadata={"desc": "Additional source-specific fields that should be preserved to avoid information loss, such as TLDR, embeddings, institution, journal volume, issue, or raw API response fields."})
    FIELD_ALIASES: ClassVar[dict[str, tuple[str, ...]]] = {
        "article_url": ("article_url", "article_link", "url", "link", "paper_url", "html_url"), "download_url": ("download_url", "download_link", "pdf", "pdf_url", "pdf_link"), "published_at": ("published_at", "publication_date", "published_date", "date", "year"), "updated_at": ("updated_at", "update_date", "updated_date"), "source_id": ("source_id", "paper_id", "id", "semantic_scholar_id"),
        "citation_count": ("citation_count", "citations", "num_citations", "citationCount"), "reference_count": ("reference_count", "references", "num_references", "referenceCount"), "abstract": ("abstract", "summary", "description"), "authors": ("authors", "author", "creator", "creators"),
    }
    '''postinit'''
    def __post_init__(self) -> None:
        # core paper information
        self.source, self.title, self.abstract, self.authors = self.cleantext(self.source), self.cleantext(self.title), self.cleantext(self.abstract), self.tostrlist(self.authors)
        self.article_url, self.download_url = self.cleanurl(self.article_url), self.cleanurl(self.download_url)
        self.doi, self.arxiv_id = self.cleantext(self.doi), self.cleantext(self.arxiv_id)
        # publication information
        self.venue, self.publisher = self.cleantext(self.venue), self.cleantext(self.publisher)
        self.published_at, self.updated_at = self.parsedate(self.published_at), self.parsedate(self.updated_at)
        # search metadata
        self.source_id, self.query = self.cleantext(self.source_id), self.cleantext(self.query)
        self.rank, self.score = self.toint(self.rank), self.tofloat(self.score)
        # topic, category, and custom tags
        self.keywords, self.categories, self.tags = self.tostrlist(self.keywords), self.tostrlist(self.categories), self.uniquelist(self.tostrlist(self.tags))
        # impact and bibliographic metrics
        self.citation_count, self.reference_count = self.toint(self.citation_count), self.toint(self.reference_count)
        # availability and license information
        self.language, self.license = self.cleantext(self.language), self.cleantext(self.license)
        # system extension information
        self.extra = {"raw_extra": self.extra} if not isinstance(self.extra, dict) else self.extra
    '''attributedescriptions'''
    @classmethod
    def attributedescriptions(cls) -> dict[str, str]:
        return {f.name: f.metadata.get("desc", "") for f in fields(cls) if f.init}
    '''schema'''
    @classmethod
    def schema(cls) -> dict[str, dict[str, str]]:
        return {f.name: {"type": str(f.type), "desc": f.metadata.get("desc", "")} for f in fields(cls) if f.init}
    '''cleantext'''
    @staticmethod
    def cleantext(value: Any, *, strip_html: bool = True, max_len: Optional[int] = None) -> Optional[str]:
        if value is None: return None
        text = (lambda s: (lambda t: t[:max_len].rstrip() if max_len is not None and len(t) > max_len else t)(re.sub(r"\s+", " ", BeautifulSoup(s, "lxml").get_text(" ") if strip_html else s).strip()))(fix_text(str(value)))
        return text or None
    '''cleanfilename'''
    @classmethod
    def cleanfilename(cls, value: Any, *, max_len: int = 180, default: str = None) -> str:
        default = default if default else f"notitle-{cls.identity_key}"
        name = sanitize_filename(cls.cleantext(value) or default, replacement_text="_")
        name = re.sub(r"_+", "_", name).strip(" ._-") or default
        return name[:max_len].rstrip(" ._-") or default
    '''tostrlist'''
    @classmethod
    def tostrlist(cls, value: Any) -> list[str]:
        if value is None or value == "": return []
        if isinstance(value, str): return cls.uniquelist(cls.cleantext(x) for x in re.split(r";|,|\|", value))
        if isinstance(value, dict): return cls.uniquelist([cls.cleantext((value.get("name") or value.get("full_name") or value.get("author") or value.get("title")))])
        if isinstance(value, (list, tuple, set)): return cls.uniquelist([cls.cleantext((item.get("name") or item.get("full_name") or item.get("author") or item.get("title")) if isinstance(item, dict) else item) for item in value])
        return [cleaned] if (cleaned := cls.cleantext(value)) else []
    '''uniquelist'''
    @staticmethod
    def uniquelist(values: Any) -> list[str]:
        seen, results = set(), []
        for value in values or []:
            if not value: continue
            if (key := (value := str(value).strip()).lower()) not in seen: seen.add(key); results.append(value)
        return results
    '''cleanurl'''
    @classmethod
    def cleanurl(cls, value: Any) -> Optional[str]:
        if (not (url := cls.cleantext(value, strip_html=False))) or ((parsed := urlparse(url)).scheme not in {"http", "https"}) or (not parsed.netloc): return None
        return url
    '''parsedate'''
    @staticmethod
    def parsedate(value: Any) -> Optional[str]:
        if value is None or value == "": return None
        if isinstance(value, datetime): return value.isoformat()
        if isinstance(value, date): return datetime(value.year, value.month, value.day).isoformat()
        if not (text := str(value).strip()): return None
        if re.fullmatch(r"\d{4}", text): return f"{text}-01-01T00:00:00"
        if re.fullmatch(r"\d{4}-\d{1,2}", text): return f"{text}-01T00:00:00"
        try: return date_parser.parse(text, fuzzy=True).isoformat()
        except Exception: return text
    '''toint'''
    @staticmethod
    def toint(value: Any) -> Optional[int]:
        if value is None or value == "": return None
        try: return int(float(value))
        except Exception: return None
    '''tofloat'''
    @staticmethod
    def tofloat(value: Any) -> Optional[float]:
        if value is None or value == "": return None
        try: return float(value)
        except Exception: return None
    '''normalizeinputdict'''
    @classmethod
    def normalizeinputdict(cls, data: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(data)
        for target, aliases in cls.FIELD_ALIASES.items():
            if normalized.get(target) not in (None, ""): continue
            if (v := next((v for alias in aliases if (v := data.get(alias)) not in (None, "")), None)) is not None: normalized[target] = v
        return normalized
    '''year'''
    @property
    def year(self) -> Optional[int]:
        if not self.published_at: return None
        match = re.search(r"\b(19|20)\d{2}\b", self.published_at)
        return int(match.group()) if match else None
    '''main_url'''
    @property
    def main_url(self) -> Optional[str]:
        return self.article_url or self.download_url
    '''short_authors'''
    @property
    def short_authors(self) -> str:
        if not self.authors: return "noauthors"
        if len(self.authors) <= 3: return ", ".join(self.authors)
        return f"{self.authors[0]} et al."
    '''identity_key'''
    @property
    def identity_key(self) -> str:
        raw = (self.doi or self.arxiv_id or self.source_id or self.article_url or f"{self.title.lower()}|{'|'.join(a.lower() for a in self.authors[:3])}")
        return hashlib.md5(raw.encode("utf-8")).hexdigest()
    '''filename'''
    def filename(self, *, suffix: str = ".pdf", max_len: int = 180) -> str:
        year, first_author = self.year or "noyear", self.authors[0] if self.authors else "noauthor"
        safe_name = self.cleanfilename(f"{year}-{first_author}-{self.title}", max_len=max_len)
        return safe_name + (suffix if suffix.startswith(".") else f".{suffix}")
    '''addtag'''
    def addtag(self, *tags: str) -> None:
        self.tags = self.uniquelist([*self.tags, *tags])
    '''hastag'''
    def hastag(self, tag: str) -> bool:
        return bool((tag := self.cleantext(tag)) and tag.lower() in {t.lower() for t in self.tags})
    '''matchkeyword'''
    def matchkeyword(self, keyword: str) -> bool:
        if not (keyword := self.cleantext(keyword)): return False
        text = " ".join([self.title or "", self.abstract or "", " ".join(self.authors), " ".join(self.keywords), " ".join(self.categories), " ".join(self.tags), self.venue or ""]).lower()
        return keyword.lower() in text
    '''todict'''
    def todict(self, *, drop_none: bool = True) -> dict[str, Any]:
        data = asdict(self) if not drop_none else {k: v for k, v in asdict(self).items() if v is not None and v != [] and v != {}}
        return data
    '''fromdict'''
    @classmethod
    def fromdict(cls, data: dict[str, Any]) -> "PaperInfo":
        if not isinstance(data, dict): raise TypeError("PaperInfo.fromdict expects a dict.")
        normalized, valid_fields = cls.normalizeinputdict(data), {f.name for f in fields(cls)}
        kwargs = {key: value for key, value in normalized.items() if key in valid_fields}
        kwargs.setdefault("source", "nosource"); kwargs.setdefault("title", "notitle"); used_keys = set(kwargs.keys())
        alias_keys = {alias for aliases in cls.FIELD_ALIASES.values() for alias in aliases}
        extra = {key: value for key, value in data.items() if key not in used_keys and key not in alias_keys}
        if extra: kwargs["extra"] = {**kwargs.get("extra", {}), **extra}
        return cls(**kwargs)
    '''tojson'''
    def tojson(self, *, ensure_ascii: bool = False, indent: Optional[int] = 2) -> str:
        return json.dumps(self.todict(drop_none=True), ensure_ascii=ensure_ascii, indent=indent)
    '''fromjson'''
    @classmethod
    def fromjson(cls, text: str) -> "PaperInfo":
        return cls.fromdict(json.loads(text))
    '''merge'''
    def merge(self, other: "PaperInfo") -> "PaperInfo":
        if not isinstance(other, PaperInfo): raise TypeError("Can only merge with another PaperInfo.")
        data, other_data = self.todict(drop_none=False), other.todict(drop_none=False)
        data.update({k: v for k, v in other_data.items() if data.get(k) in (None, "", [], {})})
        data["keywords"] = self.uniquelist(self.keywords + other.keywords)
        data["categories"] = self.uniquelist(self.categories + other.categories)
        data["tags"] = self.uniquelist(self.tags + other.tags)
        data["authors"] = self.uniquelist(self.authors + other.authors)
        data["extra"] = {**other.extra, **self.extra}
        return PaperInfo.fromdict(data)
    '''hash'''
    def __hash__(self) -> int:
        return hash(self.identity_key)
    '''eq'''
    def __eq__(self, other: object) -> bool:
        return isinstance(other, PaperInfo) and self.identity_key == other.identity_key