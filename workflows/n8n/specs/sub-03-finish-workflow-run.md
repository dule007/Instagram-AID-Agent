# SUB-03 — finish workflow run

- Vrsta: zajednički n8n podworkflow
- Status: `specified`
- Svrha: Close an execution consistently
- Ulazi: workflow_run_id, final status, safe output or error
- Izlaz: Completed workflow run and optional alert event

## Vizual

```mermaid
flowchart LR
    N1[Result]
    N2[Redact]
    N3[Update run]
    N4[Notify if needed]
    N1 --> N2
    N2 --> N3
    N3 --> N4
```

## Ugovor

Pozivatelj mora proslijediti `workflow_run_id` i `correlation_id` kada već postoje. Podworkflow ne smije sakriti poslovnu blokadu, upisati tajnu u log niti samostalno promijeniti odobrenje sadržaja.

