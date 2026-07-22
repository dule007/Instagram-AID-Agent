# WF-15 — meta publishing

- Faza: `Later`
- Status: `blocked-integration`
- Okidač: Approved scheduled publication
- Ulazi: Valid approval, final asset, Meta credentials
- Obavezna kontrola: Recheck approval, version, schedule and idempotency key
- Izlaz: Instagram publication ID and permalink
- Sigurno ponašanje: Never use Instagram password; API failure cannot generate replacement copy

## Vizual

```mermaid
flowchart LR
    N1[Approved post]
    N2[Approval gate]
    N3[Meta API]
    N4[Persist result]
    N5[Metrics schedule]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

