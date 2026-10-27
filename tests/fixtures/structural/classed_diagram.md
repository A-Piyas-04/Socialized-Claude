Blue boxes are caches and grey is storage; the double border marks the layer that fails.

```mermaid
flowchart LR
  App --> L1[L1 cache]
  L1 --> L2[[L2 cache]]
  L2 --> Disk[Disk]
  classDef cache fill:#dbeafe
  classDef store fill:#e5e7eb
  class L1,L2 cache
  class Disk store
```

When the L2 cache fails, every read falls through to the disk, so latency jumps.
