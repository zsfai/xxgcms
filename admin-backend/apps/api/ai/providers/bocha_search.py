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


class BochaSearchProvider(SearchProvider):
    def search(self, req: SearchRequest, config: ResolvedProvider) -> SearchResult:
        items = []
        seen_urls = set()
        max_results = req.max_results_per_query or config.params.get('max_results', 5)
        for query in req.queries:
            url = '%s/v1/web-search' % config.base_url.rstrip('/')
            if not url.endswith('/v1/web-search'):
                url = config.base_url.rstrip('/') + '/v1/web-search'
            body = {
                'query': query,
                'summary': True,
                'count': max_results,
            }
            if req.freshness:
                body['freshness'] = req.freshness
            headers = {
                'Authorization': 'Bearer %s' % config.api_key,
                'Content-Type': 'application/json',
            }
            resp = requests.post(url, json=body, headers=headers, timeout=30)
            if resp.status_code >= 400:
                raise RuntimeError('博查 API 错误: %s %s' % (resp.status_code, resp.text[:300]))
            data = resp.json()
            pages = data.get('data', {}).get('webPages', {}).get('value', [])
            if not pages and isinstance(data.get('results'), list):
                pages = data['results']
            for page in pages:
                link = page.get('url') or page.get('link') or ''
                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)
                items.append(SearchResultItem(
                    title=(page.get('name') or page.get('title') or '')[:200],
                    url=link,
                    snippet=(page.get('summary') or page.get('snippet') or page.get('content') or '')[:500],
                    published_at=page.get('datePublished') or page.get('published_date'),
                ))
        return SearchResult(items=items, provider='bocha', raw_response={'query_count': len(req.queries)})


register_search_provider('bocha', BochaSearchProvider)
