# SUB-08 — safe retry

- Vrsta: zajednički n8n podworkflow
- Status: `specified`
- Svrha: Retry only transient technical failures
- Ulazi: Error class, attempt number and idempotency key
- Izlaz: Delayed retry or final failure

## Vizual

```mermaid
flowchart LR
    N1[Failure]
    N2[Classify]
    N3[Check attempts]
    N4[Backoff]
    N5[Retry or stop]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Ugovor

Pozivatelj mora proslijediti `workflow_run_id` i `correlation_id` kada već postoje. Podworkflow ne smije sakriti poslovnu blokadu, upisati tajnu u log niti samostalno promijeniti odobrenje sadržaja.

