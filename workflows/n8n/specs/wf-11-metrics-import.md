# WF-11 — metrics import

- Faza: `MVP`
- Status: `specified`
- Okidač: Scheduled window or manual import
- Ulazi: Publication ID, capture time, available metrics
- Obavezna kontrola: Publication exists and snapshot is not duplicate
- Izlaz: Immutable metric snapshot
- Sigurno ponašanje: Missing means unavailable, never zero

## Vizual

```mermaid
flowchart LR
    N1[Published post]
    N2[Validate]
    N3[Normalize]
    N4[Save snapshot]
    N5[Analysis queue]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

