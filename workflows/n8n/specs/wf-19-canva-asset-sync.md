# WF-19 — canva asset sync

- Faza: `Later`
- Status: `blocked-integration`
- Okidač: Approved Canva export event or manual request
- Ulazi: Canva design reference and content version
- Obavezna kontrola: Provider capability, version and checksum are valid
- Izlaz: Versioned media asset reference
- Sigurno ponašanje: New asset never replaces approved asset silently

## Vizual

```mermaid
flowchart LR
    N1[Canva asset]
    N2[Validate]
    N3[Sync metadata]
    N4[Checksum]
    N5[Approval gate]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

