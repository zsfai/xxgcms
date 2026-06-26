# coding: utf-8
"""AI provider abstract types."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResolvedProvider:
    code: str
    base_url: str
    api_key: str
    default_model: str = ''
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TextGenerateRequest:
    system_prompt: str
    user_prompt: str
    model_id: str = ''
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TextGenerateResult:
    content: str
    tokens_input: int = 0
    tokens_output: int = 0
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class ImageGenerateRequest:
    prompt: str
    model_id: str = ''
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImageGenerateResult:
    image_bytes: bytes
    mime_type: str = 'image/png'
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class SearchResultItem:
    title: str
    url: str
    snippet: str
    published_at: Optional[str] = None


@dataclass
class SearchRequest:
    queries: List[str]
    max_results_per_query: int = 5
    freshness: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    items: List[SearchResultItem]
    provider: str = ''
    raw_response: Optional[Dict[str, Any]] = None


class TextProvider(ABC):
    @abstractmethod
    def generate(self, req: TextGenerateRequest, config: ResolvedProvider) -> TextGenerateResult:
        ...


class ImageProvider(ABC):
    @abstractmethod
    def generate(self, req: ImageGenerateRequest, config: ResolvedProvider) -> ImageGenerateResult:
        ...


class SearchProvider(ABC):
    @abstractmethod
    def search(self, req: SearchRequest, config: ResolvedProvider) -> SearchResult:
        ...
