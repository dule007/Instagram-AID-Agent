# SUB-07 — verify approval gate

- Vrsta: zajednički n8n podworkflow
- Status: `specified`
- Svrha: Verify approval for the exact current version
- Ulazi: Entity, content_version_id and intended action
- Izlaz: Pass or explicit approval block

## Vizual

```mermaid
flowchart LR
    N1[Action request]
    N2[Load current version]
    N3[Load approval]
    N4[Check revocation]
    N5[Pass or block]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Ugovor

Pozivatelj mora proslijediti `workflow_run_id` i `correlation_id` kada već postoje. Podworkflow ne smije sakriti poslovnu blokadu, upisati tajnu u log niti samostalno promijeniti odobrenje sadržaja.

