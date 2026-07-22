# WF-09 — manual publish package

- Faza: `MVP`
- Status: `specified`
- Okidač: Approved time reached or manual request
- Ulazi: Approved version and final media
- Obavezna kontrola: Approval remains valid immediately before packaging
- Izlaz: Exact caption, media and checklist
- Sigurno ponašanje: Revoked approval or wrong version blocks output

## Vizual

```mermaid
flowchart LR
    N1[Approved post]
    N2[Recheck gate]
    N3[Assemble package]
    N4[Log handoff]
    N5[Manual publish]
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## Implementacijska napomena

Svako izvršenje mora otvoriti i zatvoriti `workflow_runs` zapis, koristiti korelacijski ID i zapisati audit događaj za promjenu poslovnog stanja. Tehnički retry mora biti ograničen i idempotentan; poslovna blokada zahtijeva ljudsku odluku.

