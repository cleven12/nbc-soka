from scraper.core.client import FetchError, WPClient


def test_describe_payload_dict():
    text = WPClient._describe_payload({"code": "rest_no_route", "message": "No route"})
    assert "rest_no_route" in text
    assert "No route" in text


def test_fetch_error_retryable_flag():
    err = FetchError("boom")
    assert err.retryable is True
