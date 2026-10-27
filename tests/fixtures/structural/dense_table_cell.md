The two policies differ in when the write reaches storage.

| Policy | When the write lands | Risk |
|---|---|---|
| Write-through | The cache forwards every write to storage before it reports success to the caller. | none |
| Write-back | later | lost writes |
