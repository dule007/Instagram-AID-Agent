# WF-03 — content plan

- Faza: `MVP`
- Status: `specified`
- Okidač: Approved strategy or manual request
- Ulazi: Approved strategy version and editorial capacity
- Obavezna kontrola: Strategy approval is valid
- Izlaz: Content ideas in idea status
- Sigurno ponašanje: Unapproved strategy blocks generation

## Vizual

```mermaid
flowchart LR
    N1[Strategy]
    N2[Validate]
    N3[Generate plan]
    N4[Save ideas]
    N5[Editorial backlog]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

