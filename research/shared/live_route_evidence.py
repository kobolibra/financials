"""Source-neutral browser navigation identity checks for issuer report release evidence.

The actual article URL and the final back-navigation URL MUST be captured at
different points. Cloudflare Pages canonicalizes /CODE.html to /CODE; this is
not a home redirect. This pure module is reusable by every industry adapter.
"""
from __future__ import annotations
from urllib.parse import urlsplit
import re

def verify_issuer_article_url(url: str, *, code: str, origin: str, report_route: str | None = None) -> str:
    if not re.fullmatch(r"\d{6}", str(code)):
        raise AssertionError("INVALID_ISSUER_CODE")
    if not isinstance(url,str) or not url.startswith("https://"):
        raise AssertionError("ARTICLE_URL_NOT_HTTPS")
    u=urlsplit(url)
    home=urlsplit(origin)
    if (u.scheme,u.hostname,u.port)!=(home.scheme,home.hostname,home.port) or u.username or u.password:
        raise AssertionError(f"ARTICLE_ORIGIN_MISMATCH:{url}")
    route=report_route or f"/{code}.html"
    r=urlsplit(route)
    if r.scheme or r.netloc or r.query or r.fragment or not route.startswith('/') or not route.endswith('/'+code+'.html') or '..' in route.split('/'):
        raise AssertionError('INVALID_CANONICAL_ISSUER_ROUTE')
    if u.path not in (route,route[:-5]):
        raise AssertionError(f"ARTICLE_ROUTE_INCORRECT_OR_HOME_REDIRECT:{url}")
    if u.query or u.fragment:
        raise AssertionError(f"ARTICLE_ROUTE_UNEXPECTED_QUERY_OR_FRAGMENT:{url}")
    return url

def verify_back_to_library(url: str, *, origin: str) -> str:
    if not isinstance(url,str) or not url.startswith("https://"):
        raise AssertionError("BACK_URL_NOT_HTTPS")
    u=urlsplit(url)
    home=urlsplit(origin)
    if (u.scheme,u.hostname,u.port)!=(home.scheme,home.hostname,home.port) or u.username or u.password:
        raise AssertionError(f"BACK_ORIGIN_MISMATCH:{url}")
    if u.path!="/" or u.query or u.fragment!="companies":
        raise AssertionError(f"BACK_NOT_PRIMARY_DIRECTORY:{url}")
    return url

def make_live_navigation_receipt(*, report_url: str, back_url: str, code: str, origin: str, report_route: str | None = None) -> dict[str,str]:
    """Separate observed article URL from returned-to-home URL: never conflate."""
    article=verify_issuer_article_url(report_url,code=code,origin=origin,report_route=report_route)
    back=verify_back_to_library(back_url,origin=origin)
    assert article!=back,"ARTICLE_AND_HOME_SAME_URL"
    return {"actual_dedicated_article_final_url":article,"actual_return_to_library_url":back}
