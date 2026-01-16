# pydynox Examples

Real-world examples using [pydynox](https://github.com/ferrumio/pydynox) with AWS Lambda and DynamoDB.

Each example is a complete, deployable project. Clone it, deploy it, learn from it.

## Examples

| # | Name | Description | Features |
|---|------|-------------|----------|
| 01 | [URL Shortener](./01-url-shortener) | Short links that expire | TTL, auto-generated IDs, atomic counters |

## Stack

All examples use:

- Python 3.13
- AWS SAM for deployment
- AWS Lambda Powertools for logging and tracing
- pydynox for DynamoDB

## Getting Started

1. Pick an example
2. Read its README
3. Deploy with `sam build && sam deploy --guided`
4. Play with it
5. Delete with `sam delete`

## Testing

Each example includes tests using `pydynox_memory_backend`. No DynamoDB needed to run tests.

```bash
cd 01-url-shortener
uv sync
uv run pytest tests/ -v
```

## License

MIT
