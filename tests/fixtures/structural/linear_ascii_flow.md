A deploy moves through five stages, and each stage waits for the one before it.

```
commit -> build -> test
test -> stage -> release
```

The release stage is the only one users see.
