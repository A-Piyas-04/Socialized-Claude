Write-back is faster, so it is the one that can lose data.

| Policy | Write cost | Risk on crash |
|---|---|---|
| Write-through | slow | none |
| Write-back | fast | lost writes |

Pick write-through when a lost write costs more than a slow one.
