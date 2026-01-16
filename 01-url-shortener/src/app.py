"""Lambda handlers for URL Shortener."""

import json

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.exceptions import NotFoundError
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydynox.attributes import ExpiresIn

from models import ShortUrl

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.post("/urls")
@tracer.capture_method
def create_url() -> Response:
    """Create a new short URL."""
    body = app.current_event.json_body or {}

    original_url = body.get("url")
    if not original_url:
        return Response(
            status_code=400,
            content_type="application/json",
            body='{"error": "url is required"}',
        )

    expires_in_days = body.get("expires_in_days", 7)

    url = ShortUrl(
        original_url=original_url,
        expires_at=ExpiresIn.days(expires_in_days),
    )
    url.save()

    logger.info("Created short URL", short_code=url.short_code)

    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"short_code": url.short_code, "expires_in_days": expires_in_days}),
    )


@app.get("/urls/<code>/stats")
@tracer.capture_method
def get_stats(code: str) -> dict:
    """Get URL statistics."""
    url = ShortUrl.get(short_code=code)
    if not url:
        raise NotFoundError(f"URL not found: {code}")

    return {
        "short_code": url.short_code,
        "original_url": url.original_url,
        "clicks": url.clicks,
        "expires_at": url.expires_at.isoformat() if url.expires_at else None,
    }


@app.get("/<code>")
@tracer.capture_method
def redirect(code: str) -> Response:
    """Redirect to original URL and increment click counter."""
    url = ShortUrl.get(short_code=code)
    if not url:
        raise NotFoundError(f"URL not found: {code}")

    # Atomic increment - safe even with concurrent requests
    url.update(atomic=[ShortUrl.clicks.add(1)])

    logger.info("Redirecting", short_code=code, clicks=url.clicks + 1)

    return Response(
        status_code=302,
        content_type="text/html",
        body="",
        headers={"Location": url.original_url},
    )


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def handler(event: dict, context: LambdaContext) -> dict:
    """Main Lambda handler."""
    return app.resolve(event, context)
