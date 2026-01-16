# URL Shortener

Short links that expire automatically.

**Problem:** You need short URLs that delete themselves after a week. Running a database server 24/7 for this is expensive.

**Why DynamoDB:** Pay only when someone clicks a link. TTL deletes expired links for free. Scales to millions of URLs without config.

## Architecture

```
Client → API Gateway → Lambda → DynamoDB
```

- **API Gateway:** HTTP API with routes for create and redirect
- **Lambda:** Python 3.13 with pydynox and Powertools
- **DynamoDB:** Single table with TTL enabled

## Features

- Create short URLs with 7-day expiry
- Redirect to original URL
- Track click count (atomic increment)
- Auto-delete expired links via TTL

## Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Python 3.13
- uv (Python package manager)

## Quick start

1. Clone the repo:
```bash
git clone https://github.com/leandrodamascena/pydynox-url-shortener
cd pydynox-url-shortener
```

2. Install dependencies:
```bash
uv sync
```

3. Deploy to AWS:
```bash
sam build
sam deploy --guided
```

4. Test the API:
```bash
# Create short URL
curl -X POST https://xxx.execute-api.us-east-1.amazonaws.com/urls \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path"}'

# Response:
# {"short_code": "2QXYZ...", "expires_in_days": 7}

# Redirect (use the short_code from response)
curl -I https://xxx.execute-api.us-east-1.amazonaws.com/2QXYZ...
# Returns 302 redirect to original URL

# Get stats
curl https://xxx.execute-api.us-east-1.amazonaws.com/urls/2QXYZ.../stats
# {"short_code": "2QXYZ...", "clicks": 5, "expires_at": "2024-01-22T10:30:00Z"}
```

## Local development

Start local API:
```bash
sam local start-api
```

Run tests:
```bash
uv run pytest tests/ -v
```

Run linter:
```bash
uv run ruff check .
```

## Cleanup

Delete all AWS resources:
```bash
sam delete
```

This removes:
- Lambda function
- API Gateway
- DynamoDB table
- IAM roles

## Why pydynox?

This project uses [pydynox](https://github.com/leandrodamascena/pydynox) for DynamoDB operations.

**Features used:**

- `TTLAttribute` with `ExpiresIn.days(7)` - links expire automatically
- `AutoGenerate.ksuid()` - sortable unique short codes
- Atomic `clicks.add(1)` - safe counter increment
- `Model.create_table()` - table setup from model schema
- `pydynox_memory_backend` - test without DynamoDB

**Code comparison:**

boto3:
```python
table.update_item(
    Key={'short_code': code},
    UpdateExpression='SET clicks = clicks + :inc',
    ExpressionAttributeValues={':inc': 1}
)
```

pydynox:
```python
url.update(atomic=[ShortUrl.clicks.add(1)])
```

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| POST | /urls | Create short URL |
| GET | /{code} | Redirect to original |
| GET | /urls/{code}/stats | Get click stats |

### POST /urls

Create a new short URL.

**Request:**
```json
{
  "url": "https://example.com/long/path",
  "expires_in_days": 7
}
```

**Response (201):**
```json
{
  "short_code": "2QXYZabc123",
  "expires_in_days": 7
}
```

### GET /{code}

Redirect to original URL. Increments click counter.

**Response:** 302 redirect with `Location` header.

### GET /urls/{code}/stats

Get URL statistics.

**Response (200):**
```json
{
  "short_code": "2QXYZabc123",
  "original_url": "https://example.com/long/path",
  "clicks": 42,
  "expires_at": "2024-01-22T10:30:00Z"
}
```

## License

MIT
