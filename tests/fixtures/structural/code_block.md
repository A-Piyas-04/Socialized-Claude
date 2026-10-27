Pass the timeout when you create the client, so every request inherits it.

```python
client = httpx.Client(base_url=API_URL, timeout=30)
```

Nothing has been changed yet; run the tests after editing to verify it.
