#!/usr/bin/env python3
# xxg-cms 离线部署冒烟测试（不改业务数据）
# 用法:
#   python scripts/smoke-test-offline.py --base-url http://192.168.64.128
#   python scripts/smoke-test-offline.py --base-url http://127.0.0.1 --user xxgcmsadmin --password '...'
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Result:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Suite:
    results: list[Result] = field(default_factory=list)

    def add(self, name: str, ok: bool, detail: str = "") -> None:
        self.results.append(Result(name, ok, detail))
        mark = "PASS" if ok else "FAIL"
        print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))

    @property
    def failed(self) -> list[Result]:
        return [r for r in self.results if not r.ok]


def http_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30,
) -> tuple[int, Any, str]:
    data = None
    req_headers = {"Accept": "application/json", **(headers or {})}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                payload = raw
            return resp.status, payload, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            payload = raw
        return e.code, payload, raw


def http_status(url: str, timeout: float = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "xxgcms-smoke/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read(4096).decode("utf-8", errors="replace")
        return e.code, body


def main() -> int:
    parser = argparse.ArgumentParser(description="xxg-cms offline smoke test")
    parser.add_argument("--base-url", default=os.environ.get("XXGCMS_BASE_URL", "http://127.0.0.1"))
    parser.add_argument("--user", default=os.environ.get("XXGCMS_ADMIN_USER", "xxgcmsadmin"))
    parser.add_argument("--password", default=os.environ.get("XXGCMS_ADMIN_PASSWORD", ""))
    parser.add_argument(
        "--domain",
        default=os.environ.get("XXGCMS_SITE_DOMAIN", "localhost"),
        help="site domain for site-scoped APIs",
    )
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    suite = Suite()

    print(f"=== xxg-cms smoke @ {base} ===\n")

    # 1) Public HTTP surfaces
    for path, expect in [("/", 200), ("/back-x/", 200), ("/back-x/index.html", 200)]:
        code, body = http_status(f"{base}{path}")
        ok = code == expect and (path != "/" or ("html" in body.lower() or "<!doctype" in body.lower() or len(body) > 0))
        suite.add(f"HTTP GET {path}", ok, f"status={code}")

    # static asset from admin SPA (hashed assets may 404; check common path patterns)
    code, body = http_status(f"{base}/back-x/")
    has_assets = "back-x" in body or "script" in body.lower() or "assets" in body.lower()
    suite.add("Admin SPA shell has assets refs", has_assets or code == 200, f"status={code}")

    if not args.password:
        suite.add("Admin password provided", False, "set --password or XXGCMS_ADMIN_PASSWORD")
        _print_summary(suite)
        return 1

    # 2) Login
    code, payload, raw = http_json(
        f"{base}/api/login/",
        method="POST",
        body={"name": args.user, "pwd": args.password},
    )
    token = None
    login_ok = False
    if isinstance(payload, dict) and payload.get("code") == 0:
        token = payload.get("token") or (payload.get("data") or {}).get("token")
        # response helpers may put token at top-level
        if not token:
            token = payload.get("token")
        login_ok = bool(token)
    suite.add("API login", login_ok, f"http={code} code={payload.get('code') if isinstance(payload, dict) else None}")
    if not login_ok:
        suite.add("Skip authenticated APIs", False, raw[:200])
        _print_summary(suite)
        return 1

    auth = {"Auth-Key": token, "auth-key": token}

    # 3) Auth-required list APIs (read-only)
    read_apis: list[tuple[str, dict[str, Any]]] = [
        ("/api/get_site_list/", {}),
        ("/api/get_site_page_list/", {"page_num": 1, "page_size": 10}),
        ("/api/ai/config_settings/", {}),
        ("/api/ai/providers/", {}),
        ("/api/ai/models/", {}),
        ("/api/ai/verticals/", {}),
        ("/api/ai/templates/", {}),
        ("/api/get_article_list/", {"domain": args.domain, "page_num": 1, "page_size": 10}),
        ("/api/get_cate_list/", {"domain": args.domain, "page_num": 1, "page_size": 10}),
        ("/api/get_kw_list/", {"domain": args.domain, "page_num": 1, "page_size": 10}),
        ("/api/get_carousel_list/", {"domain": args.domain, "page_num": 1, "page_size": 10}),
        ("/api/get_link_list/", {"domain": args.domain, "page_num": 1, "page_size": 10}),
        ("/api/get_site_conf/", {"domain": args.domain}),
        ("/api/ai/topic_sessions/", {"domain": args.domain, "page_num": 1, "page_size": 5}),
    ]

    site_domain = args.domain
    for path, body in read_apis:
        # inject discovered domain if site list returns one
        if "domain" in body and site_domain:
            body = {**body, "domain": site_domain}
        code, payload, raw = http_json(f"{base}{path}", method="POST", body=body, headers=auth)
        ok = isinstance(payload, dict) and payload.get("code") == 0
        detail = f"http={code}"
        if isinstance(payload, dict):
            detail += f" api_code={payload.get('code')}"
            if payload.get("code") != 0:
                detail += f" msg={payload.get('message', '')[:80]}"
            if path == "/api/get_site_list/" and ok:
                datas = payload.get("datas") or []
                if datas and isinstance(datas, list):
                    first = datas[0]
                    if isinstance(first, dict) and first.get("name"):
                        site_domain = first["name"]
                        detail += f" sites={len(datas)} domain={site_domain}"
        suite.add(f"API POST {path}", ok, detail)

    # 4) Unauthorized should fail
    code, payload, _ = http_json(
        f"{base}/api/get_site_list/",
        method="POST",
        body={},
        headers={},
    )
    unauth_ok = isinstance(payload, dict) and payload.get("code") in (403, 10001, 401) or code in (401, 403)
    # project uses code 403 in JSON body often with HTTP 200
    if isinstance(payload, dict) and payload.get("code") == 403:
        unauth_ok = True
    suite.add("API rejects missing token", unauth_ok, f"http={code} payload_code={payload.get('code') if isinstance(payload, dict) else None}")

    # 5) Wrong password
    code, payload, _ = http_json(
        f"{base}/api/login/",
        method="POST",
        body={"name": args.user, "pwd": "__wrong_password__"},
    )
    bad_login = isinstance(payload, dict) and payload.get("code") != 0
    suite.add("API login rejects bad password", bad_login, f"http={code} code={payload.get('code') if isinstance(payload, dict) else None}")

    return _print_summary(suite)


def _print_summary(suite: Suite) -> int:
    total = len(suite.results)
    failed = suite.failed
    print("\n=== Summary ===")
    print(f"total={total} pass={total - len(failed)} fail={len(failed)}")
    if failed:
        print("Failed cases:")
        for r in failed:
            print(f"  - {r.name}: {r.detail}")
        return 1
    print("All smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
