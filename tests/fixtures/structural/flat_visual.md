A read checks each layer in turn until one has the data.

```mermaid
flowchart LR
  App --> L1[L1 cache]
  L1 --> L2[L2 cache]
  L2 --> Disk[Disk]
```
