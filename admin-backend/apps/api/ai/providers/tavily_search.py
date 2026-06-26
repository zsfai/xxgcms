# coding: utf-8
import requests

from apps.api.ai.providers.base import (
    ResolvedProvider,
    SearchProvider,
    SearchRequest,
    SearchResult,
    SearchResultItem,
)
from apps.api.ai.providers.registry import register_search_provider


class TavilySearchProvider(SearchProvider):
    def search(self, req: SearchRequest, config: ResolvedProvider) -> SearchResult:
        items = []
        seen_urls = set()
        max_results = req.max_results_per_query or config.params.get('max_results', 5)
        url = config.base_url.rstrip('/') + '/search'
        for query in req.queries:
            body = {
                'api_key': config.api_key,
                'query': query,
                'max_results': max_results,
                'search_depth': 'basic',
            }
            resp = requests.post(url, json=body, timeout=30)
            if resp.status_code >= 400:
                raise RuntimeError('Tavily API 错误: %s %s' % (resp.status_code, resp.text[:300]))
            data = resp.json()
            for page in data.get('results', []):
                link = page.get('url') or ''
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)
                items.append(SearchResultItem(
                    title=(page.get('title') or '')[:200],
                    url=link,
                    snippet=(page.get('content') or '')[:500],
                ))
        return SearchResult(items=items, provider='tavily', raw_response={'query_count': len(req.queries)})


register_search_provider('tavily', TavilySearchProvider)
