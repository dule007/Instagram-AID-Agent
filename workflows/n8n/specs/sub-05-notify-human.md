# SUB-05 — notify human

- Vrsta: zajednički n8n podworkflow
- Status: `specified`
- Svrha: Send an actionable notification without secrets
- Ulazi: Recipient role, entity, reason and recommended action
- Izlaz: Delivery result linked to workflow run

## Vizual

```mermaid
flowchart LR
    N1[Event]
    N2[Resolve owner]
    N3[Build message]
    N4[Send]
    N5[Log]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Ugovor

Pozivatelj mora proslijediti `workflow_run_id` i `correlation_id` kada već postoje. Podworkflow ne smije sakriti poslovnu blokadu, upisati tajnu u log niti samostalno promijeniti odobrenje sadržaja.

