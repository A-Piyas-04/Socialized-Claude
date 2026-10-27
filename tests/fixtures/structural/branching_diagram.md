A request is served from the replica unless it writes or needs fresh data.

```
request
  |-- write? ----------> primary
  |-- needs fresh? ----> primary
  `-- otherwise -------> replica
```

Writes always go to the primary because only it accepts changes.
