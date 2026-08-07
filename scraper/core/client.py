"""HTTP client with pagination, retries, and polite delays."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from scraper.utils.jsonio import loads


class FetchError(RuntimeError):
    """Raised for HTTP/API failures that may be retried."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class WPClient:
    def __init__(
        self,
        *,
        base_url: str,
        user_agent: str,
        timeout_seconds: float = 30.0,
        max_retries: int = 5,
        min_delay_ms: int = 250,
    ) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.min_delay_ms = min_delay_ms
        self._last_request_at = 0.0
        self._client = httpx.Client(
            headers={
                "User-Agent": user_agent,
                "Accept": "application/json",
                # Mild browser-ish hints; some WAFs dislike bare script UAs intermittently.
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=httpx.Timeout(timeout_seconds, connect=min(15.0, timeout_seconds)),
            follow_redirects=True,
        )
        self._max_retries = max(1, max_retries)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> WPClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _throttle(self) -> None:
        if self.min_delay_ms <= 0:
            return
        elapsed = (time.monotonic() - self._last_request_at) * 1000
        remaining = self.min_delay_ms - elapsed
        if remaining > 0:
            time.sleep(remaining / 1000.0)

    @staticmethod
    def _describe_payload(payload: Any) -> str:
        if isinstance(payload, dict):
            code = payload.get("code")
            message = payload.get("message")
            keys = list(payload.keys())[:8]
            if code or message:
                return f"dict code={code!r} message={message!r} keys={keys}"
            return f"dict keys={keys}"
        return type(payload).__name__

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> tuple[Any, httpx.Headers]:
        url = path if path.startswith("http") else urljoin(self.base_url, path.lstrip("/"))

        @retry(
            reraise=True,
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1.5, min=1, max=45),
            retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException, FetchError)),
        )
        def _do() -> tuple[Any, httpx.Headers]:
            self._throttle()
            try:
                response = self._client.get(url, params=params)
            except httpx.TimeoutException as exc:
                raise FetchError(f"timeout from {url}: {exc}") from exc
            self._last_request_at = time.monotonic()

            status = response.status_code
            # Rate limit / temporary blocks
            if status in {429, 502, 503, 504} or status >= 500:
                raise FetchError(f"{status} from {url}: {response.text[:300]}")
            if status >= 400:
                # 4xx other than 429: still surface body; retry a couple times in case of flaky WAF
                raise FetchError(f"{status} from {url}: {response.text[:300]}")

            content_type = (response.headers.get("content-type") or "").lower()
            raw = response.content
            if "json" not in content_type and raw[:1] not in (b"{", b"["):
                raise FetchError(
                    f"non-JSON from {url} (content-type={content_type!r}): {raw[:200]!r}"
                )

            try:
                payload = loads(raw)
            except Exception as exc:
                raise FetchError(f"invalid JSON from {url}: {exc}; body={raw[:200]!r}") from exc

            # WordPress REST errors are often HTTP 200 with {"code": "...", "message": "..."}.
            # Only treat WP-style error envelopes as failures (real resources use id/title/etc.).
            if isinstance(payload, dict) and isinstance(payload.get("code"), str):
                raise FetchError(
                    f"API error object from {url}: {self._describe_payload(payload)}"
                )

            return payload, response.headers

        return _do()

    def paginate(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        per_page: int = 100,
        max_pages: int | None = None,
    ) -> list[Any]:
        query = dict(params or {})
        query["per_page"] = per_page
        page = int(query.get("page") or 1)
        items: list[Any] = []

        while True:
            query["page"] = page
            payload, headers = self.get_json(path, params=query)

            if isinstance(payload, dict):
                # Collection endpoints must be lists; dict usually means WAF/error/html-as-json.
                raise FetchError(
                    f"Expected list from {path}, got {self._describe_payload(payload)}"
                )
            if not isinstance(payload, list):
                raise FetchError(
                    f"Expected list from {path}, got {type(payload).__name__}"
                )
            if not payload:
                break
            items.extend(payload)

            total_pages_raw = headers.get("X-WP-TotalPages") or headers.get("x-wp-totalpages")
            total_pages = int(total_pages_raw) if total_pages_raw else page
            if page >= total_pages:
                break
            if max_pages is not None and page >= max_pages:
                break
            page += 1

        return items
