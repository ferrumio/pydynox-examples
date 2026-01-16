"""Test fixtures for URL Shortener."""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

# Add src to path so imports work like in Lambda
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set environment variables before importing models
os.environ["TABLE_NAME"] = "urls"
os.environ["DYNAMODB_ENDPOINT_URL"] = "http://localhost:8000"  # Will be ignored by memory backend


@dataclass
class FakeLambdaContext:
    """Fake Lambda context for testing."""

    function_name: str = "test-function"
    function_version: str = "$LATEST"
    invoked_function_arn: str = "arn:aws:lambda:us-east-1:123456789012:function:test"
    memory_limit_in_mb: int = 128
    aws_request_id: str = "test-request-id"
    log_group_name: str = "/aws/lambda/test"
    log_stream_name: str = "2024/01/01/[$LATEST]abc123"

    def get_remaining_time_in_millis(self) -> int:
        return 30000


@pytest.fixture
def lambda_context():
    """Provide a fake Lambda context."""
    return FakeLambdaContext()


@pytest.fixture
def api_event():
    """Factory for API Gateway REST API events."""

    def _make_event(
        method: str = "GET",
        path: str = "/",
        body: dict | None = None,
        path_params: dict | None = None,
    ) -> dict:
        return {
            "resource": path,
            "path": path,
            "httpMethod": method,
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": None,
            "pathParameters": path_params,
            "stageVariables": None,
            "requestContext": {
                "resourcePath": path,
                "httpMethod": method,
                "path": f"/prod{path}",
                "stage": "prod",
                "requestId": "test-request-id",
                "identity": {
                    "sourceIp": "127.0.0.1",
                    "userAgent": "pytest",
                },
            },
            "body": json.dumps(body) if body else None,
            "isBase64Encoded": False,
        }

    return _make_event
