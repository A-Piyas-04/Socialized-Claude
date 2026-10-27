## The client timeout decides when a call gives up

```toml
[client]
timeout = 30
```

Raise it when the server is slow but healthy, because a short timeout turns slow replies into failures.
