"""Functional tests for Lambda handlers."""

import json

from app import handler
from models import ShortUrl


def test_create_url(pydynox_memory_backend, api_event, lambda_context):
    """Test creating a short URL."""
    event = api_event(
        method="POST",
        path="/urls",
        body={"url": "https://example.com/long/path"},
    )

    response = handler(event, lambda_context)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "short_code" in body
    assert body["expires_in_days"] == 7


def test_create_url_custom_expiry(pydynox_memory_backend, api_event, lambda_context):
    """Test creating a short URL with custom expiry."""
    event = api_event(
        method="POST",
        path="/urls",
        body={"url": "https://example.com", "expires_in_days": 30},
    )

    response = handler(event, lambda_context)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["expires_in_days"] == 30


def test_create_url_missing_url(pydynox_memory_backend, api_event, lambda_context):
    """Test create with missing url field."""
    event = api_event(
        method="POST",
        path="/urls",
        body={},
    )

    response = handler(event, lambda_context)

    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body


def test_redirect(pydynox_memory_backend, api_event, lambda_context):
    """Test redirect to original URL."""
    # First create a URL
    create_event = api_event(
        method="POST",
        path="/urls",
        body={"url": "https://example.com/redirect-test"},
    )
    create_response = handler(create_event, lambda_context)
    short_code = json.loads(create_response["body"])["short_code"]

    # Then redirect
    redirect_event = api_event(
        method="GET",
        path=f"/{short_code}",
        path_params={"code": short_code},
    )

    response = handler(redirect_event, lambda_context)

    assert response["statusCode"] == 302
    # REST API uses multiValueHeaders
    headers = response.get("headers") or response.get("multiValueHeaders", {})
    location = headers.get("Location")
    if isinstance(location, list):
        location = location[0]
    assert location == "https://example.com/redirect-test"


def test_redirect_not_found(pydynox_memory_backend, api_event, lambda_context):
    """Test redirect with invalid code."""
    event = api_event(
        method="GET",
        path="/invalid123",
        path_params={"code": "invalid123"},
    )

    response = handler(event, lambda_context)

    assert response["statusCode"] == 404


def test_get_stats(pydynox_memory_backend, api_event, lambda_context):
    """Test getting URL statistics."""
    # First create a URL
    create_event = api_event(
        method="POST",
        path="/urls",
        body={"url": "https://example.com/stats-test"},
    )
    create_response = handler(create_event, lambda_context)
    short_code = json.loads(create_response["body"])["short_code"]

    # Get stats
    stats_event = api_event(
        method="GET",
        path=f"/urls/{short_code}/stats",
        path_params={"code": short_code},
    )

    response = handler(stats_event, lambda_context)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["short_code"] == short_code
    assert body["original_url"] == "https://example.com/stats-test"
    assert body["clicks"] == 0


def test_click_counter_increments(pydynox_memory_backend, api_event, lambda_context):
    """Test that click counter increments on redirect."""
    # Create a URL
    create_event = api_event(
        method="POST",
        path="/urls",
        body={"url": "https://example.com/click-test"},
    )
    create_response = handler(create_event, lambda_context)
    short_code = json.loads(create_response["body"])["short_code"]

    # Click 3 times
    for _ in range(3):
        redirect_event = api_event(
            method="GET",
            path=f"/{short_code}",
            path_params={"code": short_code},
        )
        handler(redirect_event, lambda_context)

    # Check stats
    stats_event = api_event(
        method="GET",
        path=f"/urls/{short_code}/stats",
        path_params={"code": short_code},
    )
    response = handler(stats_event, lambda_context)
    body = json.loads(response["body"])

    assert body["clicks"] == 3


def test_stats_not_found(pydynox_memory_backend, api_event, lambda_context):
    """Test stats for non-existent URL."""
    event = api_event(
        method="GET",
        path="/urls/nonexistent/stats",
        path_params={"code": "nonexistent"},
    )

    response = handler(event, lambda_context)

    assert response["statusCode"] == 404
